$registration = Join-Path (Split-Path -Parent $PSScriptRoot) 'windows\Register-CodexAccountSwitcher.ps1'
. $registration

function Assert-Equal {
    param($Actual, $Expected)
    if ($Actual -ne $Expected) { throw "Expected '$Expected' but received '$Actual'." }
}

Describe 'Codex Account Switcher task definitions' {
    It 'defines exactly two explicit account tasks' {
        $definitions = @(Get-SwitcherTaskDefinitions -Path 'C:\Runtime\Switch-CodexAccount.ps1')
        Assert-Equal $definitions.Count 2
        Assert-Equal $definitions[0].Name 'Account A'
        Assert-Equal $definitions[0].Target 'account-a'
        Assert-Equal $definitions[1].Name 'Account B'
        Assert-Equal $definitions[1].Target 'account-b'
    }

    It 'uses the supplied controller path for every task' {
        $definitions = @(Get-SwitcherTaskDefinitions -Path 'C:\Runtime\Switch-CodexAccount.ps1')
        Assert-Equal (@($definitions | Where-Object ControllerPath -ne 'C:\Runtime\Switch-CodexAccount.ps1').Count) 0
    }
}
