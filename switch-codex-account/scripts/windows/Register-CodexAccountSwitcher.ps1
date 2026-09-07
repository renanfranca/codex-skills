[CmdletBinding()]
param(
    [ValidateSet('Install', 'Uninstall', 'RemoveLegacy')]
    [string]$Mode = 'Install',
    [string]$ControllerPath
)

$ErrorActionPreference = 'Stop'
$taskPath = '\Codex Account Switch\'
$legacyTaskNames = @('Conta A', 'Conta B')

function Get-SwitcherTaskDefinitions {
    param([Parameter(Mandatory = $true)][string]$Path)
    return @(
        [pscustomobject]@{ Name = 'Account A'; Target = 'account-a'; ControllerPath = $Path },
        [pscustomobject]@{ Name = 'Account B'; Target = 'account-b'; ControllerPath = $Path }
    )
}

function Remove-SwitcherTask {
    param([Parameter(Mandatory = $true)][string]$Name)
    $existing = Get-ScheduledTask -TaskName $Name -TaskPath $taskPath -ErrorAction SilentlyContinue
    if ($null -ne $existing) {
        Unregister-ScheduledTask -TaskName $Name -TaskPath $taskPath -Confirm:$false
    }
}

if ($MyInvocation.InvocationName -ne '.') {
    if ($Mode -eq 'Uninstall') {
        foreach ($definition in Get-SwitcherTaskDefinitions -Path 'unused') {
            Remove-SwitcherTask -Name $definition.Name
        }
        Write-Output '{"status":"uninstalled"}'
        exit 0
    }

    if ($Mode -eq 'RemoveLegacy') {
        foreach ($name in $legacyTaskNames) { Remove-SwitcherTask -Name $name }
        Write-Output '{"status":"legacy_tasks_removed"}'
        exit 0
    }

    if ([string]::IsNullOrWhiteSpace($ControllerPath)) {
        throw 'ControllerPath is required for installation.'
    }
    if (-not (Test-Path -LiteralPath $ControllerPath -PathType Leaf)) {
        throw 'The account switcher controller was not found.'
    }

    $powerShell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
    $userId = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -MultipleInstances IgnoreNew
    $principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType Interactive -RunLevel Limited

    foreach ($definition in Get-SwitcherTaskDefinitions -Path $ControllerPath) {
        $arguments = '-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}" -Target {1}' -f $definition.ControllerPath, $definition.Target
        $action = New-ScheduledTaskAction -Execute $powerShell -Argument $arguments -WorkingDirectory (Split-Path -Parent $ControllerPath)
        Register-ScheduledTask -TaskName $definition.Name -TaskPath $taskPath -Action $action -Principal $principal -Settings $settings -Force | Out-Null
    }

    Write-Output '{"status":"installed"}'
}
