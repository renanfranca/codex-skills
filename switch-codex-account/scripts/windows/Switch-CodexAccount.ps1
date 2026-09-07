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
        [Parameter(Mandatory = $true)][string]$Message
    )
    $result = [ordered]@{
        timestamp = [DateTimeOffset]::Now.ToString('o')
        operation_id = $OperationId
        target = $TargetAlias
        stage = $Stage
        status = $Status
        message = $Message
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
    param([Parameter(Mandatory = $true)][string]$InstallLocation)
    return @(Get-CimInstance Win32_Process | Where-Object {
        $null -ne $_.ExecutablePath -and (Test-PathUnderRoot -Candidate ([string]$_.ExecutablePath) -Root $InstallLocation)
    })
}

function Stop-CodexPackage {
    param([Parameter(Mandatory = $true)][string]$InstallLocation, [Parameter(Mandatory = $true)][int]$TimeoutSeconds)
    $initial = @(Get-CodexPackageProcesses -InstallLocation $InstallLocation)
    foreach ($item in $initial) {
        $process = Get-Process -Id $item.ProcessId -ErrorAction SilentlyContinue
        if ($null -ne $process -and $process.MainWindowHandle -ne 0) { [void]$process.CloseMainWindow() }
    }
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    do {
        $remaining = @(Get-CodexPackageProcesses -InstallLocation $InstallLocation)
        if ($remaining.Count -eq 0) { return ($initial.Count -gt 0) }
        Start-Sleep -Milliseconds 250
    } while ([DateTime]::UtcNow -lt $deadline)
    foreach ($item in @(Get-CodexPackageProcesses -InstallLocation $InstallLocation)) { Stop-Process -Id $item.ProcessId -Force -ErrorAction Stop }
    Start-Sleep -Milliseconds 500
    if (@(Get-CodexPackageProcesses -InstallLocation $InstallLocation).Count -ne 0) { throw 'The OpenAI.Codex package could not be stopped completely.' }
    return ($initial.Count -gt 0)
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
    if (-not (Test-Path -LiteralPath $wsl -PathType Leaf)) { throw 'WSL was not found.' }
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
        [void](Stop-CodexPackage -InstallLocation ([string]$package.InstallLocation) -TimeoutSeconds ([int]$config.graceful_timeout_seconds))
        Write-Result -OperationId $operationId -TargetAlias $RequestedTarget -Stage 'switch' -Status 'running' -Message 'Codex Desktop stopped; authentication is being switched.'
        $switchAttempted = $true
        [void](Invoke-CodexAuthSwitch -Config $config -Selector ([string]$targetConfig.selector))
        if ((Get-ActiveAccountKey -Config $config) -ne [string]$targetConfig.account_key) { throw 'Active-account verification did not match the requested target.' }
        $switchVerified = $true
        try { Start-CodexPackage -Package $package -AppId ([string]$config.app_id) }
        catch {
            Write-Result -OperationId $operationId -TargetAlias $RequestedTarget -Stage 'launch' -Status 'launch_failed' -Message 'The account switched, but Codex Desktop must be opened manually.'
            throw
        }
        Write-Result -OperationId $operationId -TargetAlias $RequestedTarget -Stage 'complete' -Status 'success' -Message 'The account switched and Codex Desktop reopened.'
    }
    catch {
        $safeMessage = 'The account switch failed before completion.'
        if ($switchAttempted -and -not $switchVerified -and $null -ne $rollbackRoot) {
            try { Restore-RollbackFiles -Config $config -RollbackRoot $rollbackRoot; $safeMessage = 'The switch failed and the previous authentication was restored.' }
            catch {
                $preserveRollback = $true
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
        if (-not $preserveLaunchFailure) { Write-Result -OperationId $operationId -TargetAlias $RequestedTarget -Stage 'failed' -Status 'error' -Message $safeMessage }
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
