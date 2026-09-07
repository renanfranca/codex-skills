$controller = Join-Path (Split-Path -Parent $PSScriptRoot) 'windows\Switch-CodexAccount.ps1'
. $controller

function Assert-Equal {
    param($Actual, $Expected)
    if ($Actual -ne $Expected) { throw "Expected '$Expected' but received '$Actual'." }
}

function Assert-Throws {
    param([Parameter(Mandatory = $true)][scriptblock]$Operation)
    $threw = $false
    try { & $Operation } catch { $threw = $true }
    if (-not $threw) { throw 'Expected the operation to throw.' }
}

function Assert-Matches {
    param([string]$Actual, [string]$Pattern, [switch]$Negated)
    $matched = $Actual -match $Pattern
    if (($Negated -and $matched) -or (-not $Negated -and -not $matched)) {
        throw "Unexpected match result for pattern '$Pattern'."
    }
}

Describe 'Codex Account Switcher' {
    BeforeEach {
        $script:TestRoot = Join-Path $env:TEMP ('CodexAccountSwitcher.Tests.' + [guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Path $script:TestRoot | Out-Null
        $script:ControllerRoot = $script:TestRoot
        $script:ResultPath = Join-Path $script:TestRoot 'last-result.json'
        $script:LogPath = Join-Path $script:TestRoot 'switch.log'
    }

    AfterEach {
        Remove-Item -LiteralPath $script:TestRoot -Recurse -Force -ErrorAction SilentlyContinue
    }

    It 'rejects an invalid target' {
        $config = [pscustomobject]@{ accounts = [pscustomobject]@{} }
        Assert-Throws { Get-TargetConfig -Config $config -Alias 'automatic' }
    }

    It 'rejects an unconfigured target' {
        $config = [pscustomobject]@{
            accounts = [pscustomobject]@{
                'account-b' = [pscustomobject]@{ configured = $false; selector = $null; account_key = $null }
            }
        }
        Assert-Throws { Get-TargetConfig -Config $config -Alias 'account-b' }
    }

    It 'matches only executable paths below the Codex package root' {
        Assert-Equal (Test-PathUnderRoot -Candidate 'C:\Program Files\WindowsApps\OpenAI.Codex_1.0_x64\ChatGPT.exe' -Root 'C:\Program Files\WindowsApps\OpenAI.Codex_1.0_x64') $true
        Assert-Equal (Test-PathUnderRoot -Candidate 'C:\Program Files\WindowsApps\OpenAI.ChatGPT-Desktop_1.0_x64\ChatGPT.exe' -Root 'C:\Program Files\WindowsApps\OpenAI.Codex_1.0_x64') $false
    }

    It 'restores a credential file atomically' {
        $backup = Join-Path $script:TestRoot 'backup.json'
        $destination = Join-Path $script:TestRoot 'auth.json'
        [IO.File]::WriteAllText($backup, 'before')
        [IO.File]::WriteAllText($destination, 'after')
        Restore-FileAtomic -BackupPath $backup -DestinationPath $destination
        Assert-Equal (Get-Content -LiteralPath $destination -Raw) 'before'
        Assert-Equal (@(Get-ChildItem -LiteralPath $script:TestRoot -Filter '*.restore').Count) 0
    }

    It 'rejects tokens and email addresses from safe log fields' {
        Assert-Throws { Write-SafeLog -OperationId 'op1' -TargetAlias 'person@example.test' -Stage 'test' -Status 'ok' }
        Assert-Throws { Write-SafeLog -OperationId 'op1' -TargetAlias 'account-a' -Stage 'bearer-token' -Status 'ok' }
        Assert-Equal (Test-Path -LiteralPath $script:LogPath) $false
    }

    It 'writes only safe aliases and state to the log' {
        Write-SafeLog -OperationId 'op1' -TargetAlias 'account-a' -Stage 'complete' -Status 'success'
        $content = Get-Content -LiteralPath $script:LogPath -Raw
        Assert-Matches $content 'account-a'
        Assert-Matches $content '@' -Negated
        Assert-Matches $content 'eyJ' -Negated
    }

    It 'prevents a second process from acquiring the mutex' {
        $mutexName = 'Local\CodexAccountSwitcher.Test.' + [guid]::NewGuid().ToString('N')
        $held = Enter-SwitchMutex -Name $mutexName
        try {
            $job = Start-Job -ScriptBlock {
                param($name)
                $second = New-Object System.Threading.Mutex($false, $name)
                try {
                    if ($second.WaitOne(0, $false)) {
                        $second.ReleaseMutex()
                        'acquired'
                    }
                    else { 'blocked' }
                }
                finally { $second.Dispose() }
            } -ArgumentList $mutexName
            Assert-Equal (Receive-Job -Job $job -Wait) 'blocked'
            Remove-Job -Job $job -Force
        }
        finally {
            $held.ReleaseMutex()
            $held.Dispose()
        }
    }
}
