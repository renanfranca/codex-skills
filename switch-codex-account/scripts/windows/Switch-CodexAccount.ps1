[CmdletBinding()]
param(
    [ValidateSet('account-a', 'account-b')]
    [string]$Target,
    [switch]$StatusOnly,
    [switch]$ValidateTargetOnly,
    [switch]$DryRun,
    [string]$ConfigPath
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
    $ConfigPath = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'config.json'
}
$script:ControllerRoot = Split-Path -Parent $ConfigPath
$script:ResultPath = Join-Path $script:ControllerRoot 'last-result.json'
$script:LogPath = Join-Path $script:ControllerRoot 'switch.log'
$script:MutexName = 'Local\CodexAccountSwitcher'

function Read-JsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw 'The switcher configuration is missing.' }
    return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json)
}

function Write-JsonAtomic {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Value
    )
    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory)) { New-Item -ItemType Directory -Path $directory -Force | Out-Null }
    $temporary = Join-Path $directory ('.' + [IO.Path]::GetFileName($Path) + '.' + [guid]::NewGuid().ToString('N') + '.tmp')
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($temporary, ($Value | ConvertTo-Json -Depth 12), $encoding)
    $replaceBackup = $Path + '.' + [guid]::NewGuid().ToString('N') + '.replace-backup'
    try {
        if (Test-Path -LiteralPath $Path) { [IO.File]::Replace($temporary, $Path, $replaceBackup) }
        else { [IO.File]::Move($temporary, $Path) }
    }
    finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force }
        if (Test-Path -LiteralPath $replaceBackup) { Remove-Item -LiteralPath $replaceBackup -Force }
    }
}

function Write-SafeLog {
    param(
        [Parameter(Mandatory = $true)][string]$OperationId,
        [Parameter(Mandatory = $true)][string]$TargetAlias,
        [Parameter(Mandatory = $true)][string]$Stage,
        [Parameter(Mandatory = $true)][string]$Status
    )
    foreach ($value in @($OperationId, $TargetAlias, $Stage, $Status)) {
        if ($value -match '[\r\n@]' -or $value -match '(?i)token|bearer|eyJ') { throw 'An unsafe value was rejected from the log.' }
    }
    $line = '{0}`t{1}`t{2}`t{3}`t{4}' -f ([DateTimeOffset]::Now.ToString('o')), $OperationId, $TargetAlias, $Stage, $Status
    [IO.File]::AppendAllText($script:LogPath, $line + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
}

function Write-Result {
    param(
        [Parameter(Mandatory = $true)][string]$OperationId,
        [Parameter(Mandatory = $true)][string]$TargetAlias,
        [Parameter(Mandatory = $true)][string]$Stage,
        [Parameter(Mandatory = $true)][string]$Status,
        [Parameter(Mandatory = $true)][string]$Message,
        [string]$Reason
    )
    $result = [ordered]@{
        timestamp = [DateTimeOffset]::Now.ToString('o')
        operation_id = $OperationId
        target = $TargetAlias
        stage = $Stage
        status = $Status
        message = $Message
    }
    if (-not [string]::IsNullOrWhiteSpace($Reason)) {
        if ($Reason -notmatch '^[a-z][a-z0-9_]*$') { throw 'An unsafe result reason was rejected.' }
        $result.reason = $Reason
    }
    Write-JsonAtomic -Path $script:ResultPath -Value $result
    Write-SafeLog -OperationId $OperationId -TargetAlias $TargetAlias -Stage $Stage -Status $Status
}

function Get-TargetConfig {
    param([Parameter(Mandatory = $true)]$Config, [Parameter(Mandatory = $true)][string]$Alias)
    if ($Alias -notin @('account-a', 'account-b')) { throw 'Invalid target. Use account-a or account-b.' }
    $account = $Config.accounts.$Alias
    if ($null -eq $account -or -not $account.configured -or [string]::IsNullOrWhiteSpace([string]$account.selector) -or [string]::IsNullOrWhiteSpace([string]$account.account_key)) {
        throw "$Alias is not configured yet."
    }
    return $account
}

function Get-RegistryPath {
    param([Parameter(Mandatory = $true)]$Config)
    return (Join-Path ([string]$Config.codex_home_windows) 'accounts\registry.json')
}

function Get-ActiveAccountKey {
    param([Parameter(Mandatory = $true)]$Config)
    $registry = Read-JsonFile -Path (Get-RegistryPath -Config $Config)
    return [string]$registry.active_account_key
}

function Get-AliasForAccountKey {
    param([Parameter(Mandatory = $true)]$Config, [string]$AccountKey)
    foreach ($alias in @('account-a', 'account-b')) {
        $account = $Config.accounts.$alias
        if ($null -ne $account -and $account.configured -and [string]$account.account_key -eq $AccountKey) { return $alias }
    }
    return 'unknown'
}

function Get-SafeStatus {
    param([Parameter(Mandatory = $true)]$Config)
    try { $activeAlias = Get-AliasForAccountKey -Config $Config -AccountKey (Get-ActiveAccountKey -Config $Config) }
    catch { $activeAlias = 'unavailable' }
    $lastResult = $null
    if (Test-Path -LiteralPath $script:ResultPath -PathType Leaf) {
        try { $lastResult = Read-JsonFile -Path $script:ResultPath } catch { $lastResult = $null }
    }
    return [ordered]@{
        active = $activeAlias
        accounts = [ordered]@{
            'account-a' = [bool]$Config.accounts.'account-a'.configured
            'account-b' = [bool]$Config.accounts.'account-b'.configured
        }
        last_result = $lastResult
    }
}

function Test-PathUnderRoot {
    param([Parameter(Mandatory = $true)][string]$Candidate, [Parameter(Mandatory = $true)][string]$Root)
    if ([string]::IsNullOrWhiteSpace($Candidate) -or [string]::IsNullOrWhiteSpace($Root)) { return $false }
    $rootPath = [IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'
    $candidatePath = [IO.Path]::GetFullPath($Candidate)
    return $candidatePath.StartsWith($rootPath, [StringComparison]::OrdinalIgnoreCase)
}

function Get-CodexPackage {
    param([Parameter(Mandatory = $true)]$Config)
    $package = Get-AppxPackage -Name ([string]$Config.app_package_name) | Sort-Object Version -Descending | Select-Object -First 1
    if ($null -eq $package -or [string]::IsNullOrWhiteSpace([string]$package.InstallLocation)) { throw 'The OpenAI.Codex package was not found.' }
    return $package
}

function Get-CodexPackageProcesses {
    param(
        [Parameter(Mandatory = $true)][string]$InstallLocation,
        [object[]]$Processes
    )
    if ($null -eq $Processes) { $Processes = @(Get-WindowsProcessSnapshot) }
    return @($Processes | Where-Object {
        $null -ne $_.ExecutablePath -and (Test-PathUnderRoot -Candidate ([string]$_.ExecutablePath) -Root $InstallLocation)
    })
}

function Get-WindowsProcessSnapshot {
    return @(Get-CimInstance Win32_Process)
}

function Get-ProcessCreationKey {
    param([Parameter(Mandatory = $true)]$Process)
    if ($null -eq $Process.CreationDate) { return '' }
    if ($Process.CreationDate -is [DateTime]) {
        return $Process.CreationDate.ToUniversalTime().Ticks.ToString([Globalization.CultureInfo]::InvariantCulture)
    }
    return [string]$Process.CreationDate
}

function New-ProcessIdentity {
    param([Parameter(Mandatory = $true)]$Process, [bool]$IsPackageRoot = $false)
    return [pscustomobject]@{
        ProcessId = [int]$Process.ProcessId
        ParentProcessId = [int]$Process.ParentProcessId
        Name = [string]$Process.Name
        ExecutablePath = [string]$Process.ExecutablePath
        CreationKey = Get-ProcessCreationKey -Process $Process
        IsPackageRoot = $IsPackageRoot
    }
}

function Get-ProcessIdentityKey {
    param([Parameter(Mandatory = $true)]$Process)
    $creationKey = if ($null -ne $Process.PSObject.Properties['CreationKey']) { [string]$Process.CreationKey } else { Get-ProcessCreationKey -Process $Process }
    return ('{0}|{1}' -f [int]$Process.ProcessId, $creationKey)
}

function Get-CodexProcessTreeSnapshot {
    param(
        [Parameter(Mandatory = $true)][string]$InstallLocation,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$Processes
    )
    $packageProcesses = @(Get-CodexPackageProcesses -InstallLocation $InstallLocation -Processes $Processes)
    $packageIds = @{}
    foreach ($process in $packageProcesses) { $packageIds[[string][int]$process.ProcessId] = $true }

    $rootProcesses = @($packageProcesses | Where-Object { -not $packageIds.ContainsKey([string][int]$_.ParentProcessId) })
    $rootIds = @{}
    $includedIds = @{}
    foreach ($process in $rootProcesses) {
        $id = [string][int]$process.ProcessId
        $rootIds[$id] = $true
        $includedIds[$id] = $true
    }

    $changed = $true
    while ($changed) {
        $changed = $false
        foreach ($process in $Processes) {
            $id = [string][int]$process.ProcessId
            if (-not $includedIds.ContainsKey($id) -and $includedIds.ContainsKey([string][int]$process.ParentProcessId)) {
                $includedIds[$id] = $true
                $changed = $true
            }
        }
    }

    $treeProcesses = foreach ($process in $Processes) {
        $id = [string][int]$process.ProcessId
        if ($includedIds.ContainsKey($id)) { New-ProcessIdentity -Process $process -IsPackageRoot ($rootIds.ContainsKey($id)) }
    }
    $packageIdentities = foreach ($process in $packageProcesses) {
        $id = [string][int]$process.ProcessId
        New-ProcessIdentity -Process $process -IsPackageRoot ($rootIds.ContainsKey($id))
    }
    return [pscustomobject]@{
        Roots = @($treeProcesses | Where-Object IsPackageRoot)
        Processes = @($treeProcesses)
        PackageProcesses = @($packageIdentities)
    }
}

function Add-TrackedProcessIdentities {
    param([Parameter(Mandatory = $true)][hashtable]$Tracked, [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$Processes)
    foreach ($process in $Processes) { $Tracked[(Get-ProcessIdentityKey -Process $process)] = $process }
}

function Get-AliveTrackedProcessIdentities {
    param([Parameter(Mandatory = $true)][hashtable]$Tracked, [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$Processes)
    $currentKeys = @{}
    foreach ($process in $Processes) { $currentKeys[(Get-ProcessIdentityKey -Process $process)] = $true }
    return @($Tracked.GetEnumerator() | Where-Object { $currentKeys.ContainsKey([string]$_.Key) } | ForEach-Object { $_.Value })
}

function Get-CodexShutdownState {
    param(
        [Parameter(Mandatory = $true)][string]$InstallLocation,
        [Parameter(Mandatory = $true)][hashtable]$Tracked,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$Processes
    )
    $tree = Get-CodexProcessTreeSnapshot -InstallLocation $InstallLocation -Processes $Processes
    Add-TrackedProcessIdentities -Tracked $Tracked -Processes $tree.Processes
    return [pscustomobject]@{
        Tree = $tree
        AliveTracked = @(Get-AliveTrackedProcessIdentities -Tracked $Tracked -Processes $Processes)
    }
}

function Invoke-CodexProcessTreeTermination {
    param(
        [Parameter(Mandatory = $true)]$Identity,
        [Parameter(Mandatory = $true)][string]$InstallLocation,
        [scriptblock]$ProcessProvider = { Get-WindowsProcessSnapshot },
        [scriptblock]$TaskkillAction = {
            param($path, $arguments)
            $process = Start-Process -FilePath $path -ArgumentList $arguments -WindowStyle Hidden -PassThru
            try {
                if (-not $process.WaitForExit(2000)) {
                    try { $process.Kill(); [void]$process.WaitForExit(500) } catch { }
                    return 1
                }
                return [int]$process.ExitCode
            }
            finally { $process.Dispose() }
        }
    )
    $current = @(& $ProcessProvider | Where-Object { [int]$_.ProcessId -eq [int]$Identity.ProcessId } | Select-Object -First 1)
    if ($current.Count -eq 0) { return $false }
    $currentIdentity = New-ProcessIdentity -Process $current[0] -IsPackageRoot ([bool]$Identity.IsPackageRoot)
    if ([string]::IsNullOrWhiteSpace([string]$Identity.CreationKey) -or (Get-ProcessIdentityKey -Process $currentIdentity) -ne (Get-ProcessIdentityKey -Process $Identity)) { return $false }
    if ([bool]$Identity.IsPackageRoot -and -not (Test-PathUnderRoot -Candidate ([string]$current[0].ExecutablePath) -Root $InstallLocation)) { return $false }
    if ([int]$Identity.ProcessId -eq $PID) { throw 'The detached controller was unexpectedly included in the Codex process tree.' }

    $taskkill = Join-Path $env:SystemRoot 'System32\taskkill.exe'
    try {
        $arguments = @('/PID', [string][int]$Identity.ProcessId, '/T', '/F')
        $exitCode = & $TaskkillAction $taskkill $arguments
        return ([int]$exitCode -eq 0)
    }
    catch { return $false }
}

function Stop-CodexPackage {
    param(
        [Parameter(Mandatory = $true)][string]$InstallLocation,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds,
        [Parameter(Mandatory = $true)][int]$ForceTimeoutSeconds,
        [int]$PollMilliseconds = 250,
        [int]$QuietMilliseconds = 1000,
        [scriptblock]$ProcessProvider = { Get-WindowsProcessSnapshot },
        [scriptblock]$TerminateAction = { param($identity, $installLocation) Invoke-CodexProcessTreeTermination -Identity $identity -InstallLocation $installLocation },
        [scriptblock]$Clock = { [DateTime]::UtcNow },
        [scriptblock]$Delay = { param($milliseconds) Start-Sleep -Milliseconds $milliseconds }
    )
    $initialProcesses = @(& $ProcessProvider)
    $initial = Get-CodexProcessTreeSnapshot -InstallLocation $InstallLocation -Processes $initialProcesses
    if ($initial.PackageProcesses.Count -eq 0) { return $false }
    $tracked = @{}
    Add-TrackedProcessIdentities -Tracked $tracked -Processes $initial.Processes
    foreach ($item in $initial.PackageProcesses) {
        $process = Get-Process -Id $item.ProcessId -ErrorAction SilentlyContinue
        if ($null -ne $process -and $process.MainWindowHandle -ne 0) { [void]$process.CloseMainWindow() }
    }

    $graceDeadline = (& $Clock).AddSeconds($TimeoutSeconds)
    $quietSince = $null
    while ($true) {
        $processes = @(& $ProcessProvider)
        $state = Get-CodexShutdownState -InstallLocation $InstallLocation -Tracked $tracked -Processes $processes
        $now = & $Clock
        if ($state.Tree.PackageProcesses.Count -eq 0 -and $state.AliveTracked.Count -eq 0) {
            if ($null -eq $quietSince) { $quietSince = $now }
            elseif (($now - $quietSince).TotalMilliseconds -ge $QuietMilliseconds) { return $true }
        }
        else { $quietSince = $null }
        if ($now -ge $graceDeadline) { break }
        & $Delay $PollMilliseconds
    }

    $forceDeadline = (& $Clock).AddSeconds($ForceTimeoutSeconds)
    $quietSince = $null
    while ($true) {
        $processes = @(& $ProcessProvider)
        $state = Get-CodexShutdownState -InstallLocation $InstallLocation -Tracked $tracked -Processes $processes
        $now = & $Clock
        if ($state.Tree.PackageProcesses.Count -eq 0 -and $state.AliveTracked.Count -eq 0) {
            if ($null -eq $quietSince) { $quietSince = $now }
            elseif (($now - $quietSince).TotalMilliseconds -ge $QuietMilliseconds) { return $true }
        }
        else {
            $quietSince = $null
            $identity = @($state.Tree.Roots | Select-Object -First 1)
            if ($identity.Count -eq 0) { $identity = @($state.AliveTracked | Select-Object -First 1) }
            if ($identity.Count -gt 0) { [void](& $TerminateAction $identity[0] $InstallLocation) }
        }
        if ((& $Clock) -ge $forceDeadline) { break }
        & $Delay $PollMilliseconds
    }
    throw (New-Object System.TimeoutException('The OpenAI.Codex process tree could not be stopped completely.'))
}

function Start-CodexPackage {
    param([Parameter(Mandatory = $true)]$Package, [Parameter(Mandatory = $true)][string]$AppId)
    $application = 'shell:AppsFolder\{0}!{1}' -f $Package.PackageFamilyName, $AppId
    Start-Process -FilePath 'explorer.exe' -ArgumentList $application | Out-Null
}

function Copy-RollbackFiles {
    param([Parameter(Mandatory = $true)]$Config, [Parameter(Mandatory = $true)][string]$OperationId)
    $authPath = Join-Path ([string]$Config.codex_home_windows) 'auth.json'
    $registryPath = Get-RegistryPath -Config $Config
    if (-not (Test-Path -LiteralPath $authPath -PathType Leaf) -or -not (Test-Path -LiteralPath $registryPath -PathType Leaf)) { throw 'The expected authentication files were not found.' }
    $rollbackRoot = Join-Path ([string]$Config.codex_home_windows) ('accounts\.switch-rollback\' + $OperationId)
    New-Item -ItemType Directory -Path $rollbackRoot -Force | Out-Null
    Copy-Item -LiteralPath $authPath -Destination (Join-Path $rollbackRoot 'auth.json')
    Copy-Item -LiteralPath $registryPath -Destination (Join-Path $rollbackRoot 'registry.json')
    return $rollbackRoot
}

function Restore-FileAtomic {
    param([Parameter(Mandatory = $true)][string]$BackupPath, [Parameter(Mandatory = $true)][string]$DestinationPath)
    $temporary = $DestinationPath + '.' + [guid]::NewGuid().ToString('N') + '.restore'
    Copy-Item -LiteralPath $BackupPath -Destination $temporary
    $replaceBackup = $DestinationPath + '.' + [guid]::NewGuid().ToString('N') + '.replace-backup'
    try {
        if (Test-Path -LiteralPath $DestinationPath) { [IO.File]::Replace($temporary, $DestinationPath, $replaceBackup) }
        else { [IO.File]::Move($temporary, $DestinationPath) }
    }
    finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force }
        if (Test-Path -LiteralPath $replaceBackup) { Remove-Item -LiteralPath $replaceBackup -Force }
    }
}

function Restore-RollbackFiles {
    param([Parameter(Mandatory = $true)]$Config, [Parameter(Mandatory = $true)][string]$RollbackRoot)
    Restore-FileAtomic -BackupPath (Join-Path $RollbackRoot 'auth.json') -DestinationPath (Join-Path ([string]$Config.codex_home_windows) 'auth.json')
    Restore-FileAtomic -BackupPath (Join-Path $RollbackRoot 'registry.json') -DestinationPath (Get-RegistryPath -Config $Config)
}

function Invoke-WslCodexAuth {
    param([Parameter(Mandatory = $true)]$Config, [Parameter(Mandatory = $true)][string[]]$CodexAuthArguments)
    $wsl = Join-Path $env:SystemRoot 'System32\wsl.exe'
    $arguments = @(
        '-d', [string]$Config.distro,
        '--exec', 'env', ('CODEX_HOME=' + [string]$Config.codex_home_linux),
        [string]$Config.node_linux, [string]$Config.codex_auth_js_linux
    ) + $CodexAuthArguments
    foreach ($argument in $arguments) {
        if ([string]::IsNullOrWhiteSpace([string]$argument) -or [string]$argument -notmatch '^[A-Za-z0-9_%@./:=+\-]+$') {
            throw 'The runtime configuration contains an invalid argument.'
        }
    }

    $captureId = [guid]::NewGuid().ToString('N')
    $stdoutPath = Join-Path $env:TEMP ('codex-account-switcher-' + $captureId + '.out')
    $stderrPath = Join-Path $env:TEMP ('codex-account-switcher-' + $captureId + '.err')
    try {
        $process = Start-Process -FilePath $wsl -ArgumentList ($arguments -join ' ') -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -Wait -PassThru
        $captured = ''
        if (Test-Path -LiteralPath $stdoutPath) { $captured += Get-Content -LiteralPath $stdoutPath -Raw }
        if (Test-Path -LiteralPath $stderrPath) { $captured += Get-Content -LiteralPath $stderrPath -Raw }
        return [pscustomobject]@{ ExitCode = $process.ExitCode; Output = $captured }
    }
    finally {
        Remove-Item -LiteralPath $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue
    }
}

function Invoke-CodexAuthSwitch {
    param([Parameter(Mandatory = $true)]$Config, [Parameter(Mandatory = $true)][string]$Selector)
    $result = Invoke-WslCodexAuth -Config $Config -CodexAuthArguments @('switch', $Selector)
    if ($result.ExitCode -ne 0) { throw 'codex-auth did not complete the switch.' }
    return $result.Output
}

function Test-CodexAuthRuntime {
    param([Parameter(Mandatory = $true)]$Config)
    $result = Invoke-WslCodexAuth -Config $Config -CodexAuthArguments @('--version')
    if ($result.ExitCode -ne 0 -or ([string]$result.Output).Trim() -ne [string]$Config.codex_auth_version) {
        throw 'The expected codex-auth version is not available in WSL.'
    }
}

function Enter-SwitchMutex {
    param([string]$Name = $script:MutexName)
    $mutex = New-Object System.Threading.Mutex($false, $Name)
    try { $acquired = $mutex.WaitOne(0, $false) }
    catch [System.Threading.AbandonedMutexException] { $acquired = $true }
    if (-not $acquired) { $mutex.Dispose(); throw 'Another account switch is already in progress.' }
    return $mutex
}

function Test-Preflight {
    param([Parameter(Mandatory = $true)]$Config)
    $package = Get-CodexPackage -Config $Config
    foreach ($path in @([string]$Config.codex_home_windows, [string]$Config.node_linux, [string]$Config.codex_auth_js_linux)) {
        if ([string]::IsNullOrWhiteSpace($path)) { throw 'The runtime configuration is incomplete.' }
    }
    $wsl = Join-Path $env:SystemRoot 'System32\wsl.exe'
    $taskkill = Join-Path $env:SystemRoot 'System32\taskkill.exe'
    if (-not (Test-Path -LiteralPath $wsl -PathType Leaf)) { throw 'WSL was not found.' }
    if (-not (Test-Path -LiteralPath $taskkill -PathType Leaf)) { throw 'The Windows process-tree termination utility was not found.' }
    Test-CodexAuthRuntime -Config $Config
    return $package
}

function Invoke-SwitchMain {
    param([string]$RequestedTarget, [bool]$IsStatusOnly, [bool]$IsValidateOnly, [bool]$IsDryRun)
    $config = Read-JsonFile -Path $ConfigPath
    if ($IsStatusOnly) { Get-SafeStatus -Config $config | ConvertTo-Json -Depth 12; return }
    if ([string]::IsNullOrWhiteSpace($RequestedTarget)) { throw 'Specify account-a or account-b.' }
    $targetConfig = Get-TargetConfig -Config $config -Alias $RequestedTarget
    if ($IsValidateOnly) {
        if ((Get-ActiveAccountKey -Config $config) -eq [string]$targetConfig.account_key) {
            [ordered]@{ status = 'already_active'; target = $RequestedTarget } | ConvertTo-Json -Compress
        }
        else {
            [ordered]@{ status = 'valid'; target = $RequestedTarget } | ConvertTo-Json -Compress
        }
        return
    }

    $operationId = [guid]::NewGuid().ToString('N')
    $mutex = $null
    $rollbackRoot = $null
    $package = $null
    $appWasRunning = $false
    $switchAttempted = $false
    $switchVerified = $false
    $preserveRollback = $false
    $failureStage = 'preflight'
    $failureReason = 'preflight_failed'
    try {
        $mutex = Enter-SwitchMutex
        $activeKey = Get-ActiveAccountKey -Config $config
        if ($activeKey -eq [string]$targetConfig.account_key) {
            Write-Result -OperationId $operationId -TargetAlias $RequestedTarget -Stage 'preflight' -Status 'already_active' -Message 'The requested account is already active; Codex Desktop was not restarted.'
            [ordered]@{ status = 'already_active'; target = $RequestedTarget } | ConvertTo-Json -Compress
            return
        }
        $package = Test-Preflight -Config $config
        if ($IsDryRun) {
            Write-Result -OperationId $operationId -TargetAlias $RequestedTarget -Stage 'preflight' -Status 'dry_run_ok' -Message 'Preflight completed without stopping Codex Desktop or changing credentials.'
            [ordered]@{ status = 'dry_run_ok'; target = $RequestedTarget } | ConvertTo-Json -Compress
            return
        }

        Write-Result -OperationId $operationId -TargetAlias $RequestedTarget -Stage 'queued' -Status 'running' -Message 'Switch accepted; waiting briefly before restarting Codex Desktop.'
        Start-Sleep -Seconds ([int]$config.startup_delay_seconds)
        $rollbackRoot = Copy-RollbackFiles -Config $config -OperationId $operationId
        $appWasRunning = (@(Get-CodexPackageProcesses -InstallLocation ([string]$package.InstallLocation)).Count -gt 0)
        $forceTimeoutSeconds = 10
        if ($null -ne $config.PSObject.Properties['force_timeout_seconds']) { $forceTimeoutSeconds = [int]$config.force_timeout_seconds }
        $failureStage = 'shutdown'
        $failureReason = 'shutdown_failed'
        Write-Result -OperationId $operationId -TargetAlias $RequestedTarget -Stage 'shutdown' -Status 'running' -Message 'Codex Desktop is being stopped before authentication changes.'
        [void](Stop-CodexPackage -InstallLocation ([string]$package.InstallLocation) -TimeoutSeconds ([int]$config.graceful_timeout_seconds) -ForceTimeoutSeconds $forceTimeoutSeconds)
        $failureStage = 'switch'
        $failureReason = 'auth_switch_failed'
        Write-Result -OperationId $operationId -TargetAlias $RequestedTarget -Stage 'switch' -Status 'running' -Message 'Codex Desktop stopped; authentication is being switched.'
        $switchAttempted = $true
        [void](Invoke-CodexAuthSwitch -Config $config -Selector ([string]$targetConfig.selector))
        if ((Get-ActiveAccountKey -Config $config) -ne [string]$targetConfig.account_key) { throw 'Active-account verification did not match the requested target.' }
        $switchVerified = $true
        $failureStage = 'launch'
        $failureReason = 'launch_failed'
        try { Start-CodexPackage -Package $package -AppId ([string]$config.app_id) }
        catch {
            Write-Result -OperationId $operationId -TargetAlias $RequestedTarget -Stage 'launch' -Status 'launch_failed' -Message 'The account switched, but Codex Desktop must be opened manually.'
            throw
        }
        Write-Result -OperationId $operationId -TargetAlias $RequestedTarget -Stage 'complete' -Status 'success' -Message 'The account switched and Codex Desktop reopened.'
    }
    catch {
        $safeMessage = 'The account switch failed before completion.'
        if ($failureStage -eq 'shutdown' -and $_.Exception -is [System.TimeoutException]) {
            $failureReason = 'shutdown_timeout'
            $safeMessage = 'Codex Desktop could not be stopped completely; authentication was not changed.'
        }
        if ($switchAttempted -and -not $switchVerified -and $null -ne $rollbackRoot) {
            try { Restore-RollbackFiles -Config $config -RollbackRoot $rollbackRoot; $safeMessage = 'The switch failed and the previous authentication was restored.' }
            catch {
                $preserveRollback = $true
                $failureReason = 'restore_failed'
                $safeMessage = 'The switch and automatic restore both failed; do not retry before checking the local state.'
            }
        }
        if (-not $switchVerified -and $null -ne $package -and $appWasRunning) {
            try { Start-CodexPackage -Package $package -AppId ([string]$config.app_id) } catch { }
        }
        $preserveLaunchFailure = $false
        if ($switchVerified -and (Test-Path -LiteralPath $script:ResultPath)) {
            try { $preserveLaunchFailure = ((Read-JsonFile -Path $script:ResultPath).status -eq 'launch_failed') } catch { }
        }
        if (-not $preserveLaunchFailure) { Write-Result -OperationId $operationId -TargetAlias $RequestedTarget -Stage $failureStage -Status 'error' -Message $safeMessage -Reason $failureReason }
        throw $safeMessage
    }
    finally {
        if (-not $preserveRollback -and $null -ne $rollbackRoot -and (Test-Path -LiteralPath $rollbackRoot)) { Remove-Item -LiteralPath $rollbackRoot -Recurse -Force -ErrorAction SilentlyContinue }
        if ($null -ne $mutex) { try { $mutex.ReleaseMutex() } catch { }; $mutex.Dispose() }
    }
}

if ($MyInvocation.InvocationName -ne '.') {
    try { Invoke-SwitchMain -RequestedTarget $Target -IsStatusOnly $StatusOnly.IsPresent -IsValidateOnly $ValidateTargetOnly.IsPresent -IsDryRun $DryRun.IsPresent }
    catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }
}
