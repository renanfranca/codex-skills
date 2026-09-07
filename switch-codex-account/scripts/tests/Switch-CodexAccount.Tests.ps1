Describe 'Codex Account Switcher' {
    BeforeAll {
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
    }

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

    It 'scopes shutdown to verified package roots and their descendants' {
        $packageRoot = 'C:\Program Files\WindowsApps\OpenAI.Codex_1.0_x64'
        $processes = @(
            [pscustomobject]@{ ProcessId = 100; ParentProcessId = 10; Name = 'ChatGPT.exe'; ExecutablePath = "$packageRoot\ChatGPT.exe"; CreationDate = '20260907120000.000000-000' },
            [pscustomobject]@{ ProcessId = 101; ParentProcessId = 100; Name = 'ChatGPT.exe'; ExecutablePath = "$packageRoot\ChatGPT.exe"; CreationDate = '20260907120001.000000-000' },
            [pscustomobject]@{ ProcessId = 102; ParentProcessId = 100; Name = 'wsl.exe'; ExecutablePath = 'C:\Windows\System32\wsl.exe'; CreationDate = '20260907120002.000000-000' },
            [pscustomobject]@{ ProcessId = 103; ParentProcessId = 102; Name = 'node.exe'; ExecutablePath = 'C:\Users\example\AppData\Local\OpenAI\Codex\node.exe'; CreationDate = '20260907120003.000000-000' },
            [pscustomobject]@{ ProcessId = 200; ParentProcessId = 10; Name = 'ChatGPT.exe'; ExecutablePath = 'C:\Program Files\WindowsApps\OpenAI.ChatGPT-Desktop_1.0_x64\ChatGPT.exe'; CreationDate = '20260907120004.000000-000' },
            [pscustomobject]@{ ProcessId = 10; ParentProcessId = 1; Name = 'explorer.exe'; ExecutablePath = 'C:\Windows\explorer.exe'; CreationDate = '20260907115900.000000-000' }
        )

        $tree = Get-CodexProcessTreeSnapshot -InstallLocation $packageRoot -Processes $processes

        Assert-Equal $tree.Roots.Count 1
        Assert-Equal $tree.Roots[0].ProcessId 100
        Assert-Equal $tree.Processes.Count 4
        Assert-Equal (@($tree.Processes | Where-Object ProcessId -eq 103).Count) 1
        Assert-Equal (@($tree.Processes | Where-Object ProcessId -eq 200).Count) 0
        Assert-Equal (@($tree.Processes | Where-Object ProcessId -eq 10).Count) 0
    }

    It 'treats an already-exited process identity as a successful termination race' {
        $packageRoot = 'C:\Program Files\WindowsApps\OpenAI.Codex_1.0_x64'
        $identity = [pscustomobject]@{
            ProcessId = 100
            ParentProcessId = 10
            Name = 'ChatGPT.exe'
            ExecutablePath = "$packageRoot\ChatGPT.exe"
            CreationKey = '20260907120000.000000-000'
            IsPackageRoot = $true
        }
        $provider = { @() }

        Assert-Equal (Invoke-CodexProcessTreeTermination -Identity $identity -InstallLocation $packageRoot -ProcessProvider $provider) $false
    }

    It 'rejects a reused PID before invoking taskkill' {
        $packageRoot = 'C:\Program Files\WindowsApps\OpenAI.Codex_1.0_x64'
        $identity = [pscustomobject]@{
            ProcessId = 100
            ParentProcessId = 10
            Name = 'ChatGPT.exe'
            ExecutablePath = "$packageRoot\ChatGPT.exe"
            CreationKey = '20260907120000.000000-000'
            IsPackageRoot = $true
        }
        $replacement = [pscustomobject]@{ ProcessId = 100; ParentProcessId = 10; Name = 'ChatGPT.exe'; ExecutablePath = "$packageRoot\ChatGPT.exe"; CreationDate = '20260907130000.000000-000' }
        $script:TaskkillCalled = $false
        $provider = { @($replacement) }
        $runner = {
            param($path, $arguments)
            $script:TaskkillCalled = $true
            return 0
        }

        Assert-Equal (Invoke-CodexProcessTreeTermination -Identity $identity -InstallLocation $packageRoot -ProcessProvider $provider -TaskkillAction $runner) $false
        Assert-Equal $script:TaskkillCalled $false
    }

    It 'terminates a verified Codex root and its descendants with taskkill tree mode' {
        $packageRoot = 'C:\Program Files\WindowsApps\OpenAI.Codex_1.0_x64'
        $raw = [pscustomobject]@{ ProcessId = 100; ParentProcessId = 10; Name = 'ChatGPT.exe'; ExecutablePath = "$packageRoot\ChatGPT.exe"; CreationDate = '20260907120000.000000-000' }
        $identity = New-ProcessIdentity -Process $raw -IsPackageRoot $true
        $script:TaskkillArguments = @()
        $provider = { @($raw) }
        $runner = {
            param($path, $arguments)
            $script:TaskkillArguments = @($arguments)
            return 0
        }

        Assert-Equal (Invoke-CodexProcessTreeTermination -Identity $identity -InstallLocation $packageRoot -ProcessProvider $provider -TaskkillAction $runner) $true
        Assert-Equal ($script:TaskkillArguments -join ' ') '/PID 100 /T /F'
    }

    It 'retries a replacement package root and waits for stable absence' {
        $packageRoot = 'C:\Program Files\WindowsApps\OpenAI.Codex_1.0_x64'
        $rootOne = [pscustomobject]@{ ProcessId = 100; ParentProcessId = 10; Name = 'ChatGPT.exe'; ExecutablePath = "$packageRoot\ChatGPT.exe"; CreationDate = '20260907120000.000000-000' }
        $rootTwo = [pscustomobject]@{ ProcessId = 200; ParentProcessId = 10; Name = 'ChatGPT.exe'; ExecutablePath = "$packageRoot\ChatGPT.exe"; CreationDate = '20260907120001.000000-000' }
        $script:Snapshots = @(@($rootOne), @($rootOne), @($rootOne), @($rootTwo), @(), @(), @(), @(), @())
        $script:SnapshotIndex = 0
        $script:Terminated = @()
        $script:Clock = [datetime]'2026-09-07T12:00:00Z'
        $provider = {
            $index = [Math]::Min($script:SnapshotIndex, $script:Snapshots.Count - 1)
            $script:SnapshotIndex += 1
            return @($script:Snapshots[$index])
        }
        $terminator = {
            param($identity, $installLocation)
            $script:Terminated += [int]$identity.ProcessId
            return $true
        }
        $clock = {
            return $script:Clock
        }
        $delay = {
            param($milliseconds)
            $script:Clock = $script:Clock.AddMilliseconds($milliseconds)
        }

        Assert-Equal (Stop-CodexPackage -InstallLocation $packageRoot -TimeoutSeconds 0 -ForceTimeoutSeconds 10 -ProcessProvider $provider -TerminateAction $terminator -Clock $clock -Delay $delay) $true
        Assert-Equal (@($script:Terminated | Where-Object { $_ -eq 100 }).Count -gt 0) $true
        Assert-Equal (@($script:Terminated | Where-Object { $_ -eq 200 }).Count -gt 0) $true
        Assert-Equal ($script:SnapshotIndex -ge 8) $true
    }

    It 'times out when a package process remains and never reports success' {
        $packageRoot = 'C:\Program Files\WindowsApps\OpenAI.Codex_1.0_x64'
        $root = [pscustomobject]@{ ProcessId = 100; ParentProcessId = 10; Name = 'ChatGPT.exe'; ExecutablePath = "$packageRoot\ChatGPT.exe"; CreationDate = '20260907120000.000000-000' }
        $provider = { @($root) }
        $terminator = { param($identity, $installLocation) return $false }
        $script:Clock = [datetime]'2026-09-07T12:00:00Z'
        $clock = { return $script:Clock }
        $delay = {
            param($milliseconds)
            $script:Clock = $script:Clock.AddMilliseconds($milliseconds)
        }

        $failure = ''
        try { Stop-CodexPackage -InstallLocation $packageRoot -TimeoutSeconds 0 -ForceTimeoutSeconds 2 -ProcessProvider $provider -TerminateAction $terminator -Clock $clock -Delay $delay }
        catch { $failure = $_.Exception.GetType().FullName + ':' + $_.Exception.Message }
        Assert-Matches $failure 'TimeoutException'
        Assert-Matches $failure 'process tree'
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

    It 'writes a safe machine-readable shutdown reason' {
        Write-Result -OperationId 'op1' -TargetAlias 'account-b' -Stage 'shutdown' -Status 'error' -Message 'Codex Desktop could not be stopped completely.' -Reason 'shutdown_timeout'
        $result = Get-Content -LiteralPath $script:ResultPath -Raw | ConvertFrom-Json
        Assert-Equal $result.stage 'shutdown'
        Assert-Equal $result.reason 'shutdown_timeout'
        Assert-Matches ($result | ConvertTo-Json -Compress) '@' -Negated
    }

    It 'does not invoke codex-auth after a shutdown timeout' {
        Mock Read-JsonFile {
            return [pscustomobject]@{
                startup_delay_seconds = 0
                graceful_timeout_seconds = 15
                force_timeout_seconds = 10
                app_id = 'App'
                accounts = [pscustomobject]@{
                    'account-a' = [pscustomobject]@{ configured = $true; selector = 'first@example.test'; account_key = 'key-a' }
                    'account-b' = [pscustomobject]@{ configured = $true; selector = 'second@example.test'; account_key = 'key-b' }
                }
            }
        }
        Mock Get-ActiveAccountKey { return 'key-a' }
        Mock Test-Preflight { return [pscustomobject]@{ InstallLocation = 'C:\Program Files\WindowsApps\OpenAI.Codex_1.0_x64' } }
        Mock Start-Sleep { }
        Mock Copy-RollbackFiles { return (Join-Path $script:TestRoot 'rollback') }
        Mock Get-CodexPackageProcesses { return @([pscustomobject]@{ ProcessId = 100 }) }
        Mock Stop-CodexPackage { throw (New-Object System.TimeoutException('process tree timeout')) }
        $script:CodexAuthCalled = $false
        Mock Invoke-CodexAuthSwitch { $script:CodexAuthCalled = $true; throw 'codex-auth must not be called' }
        Mock Start-CodexPackage { }

        $failure = ''
        try { Invoke-SwitchMain -RequestedTarget 'account-b' -IsStatusOnly $false -IsValidateOnly $false -IsDryRun $false }
        catch { $failure = $_.Exception.Message }
        Assert-Matches $failure 'stopped'
        Assert-Equal $script:CodexAuthCalled $false
        $result = Get-Content -LiteralPath $script:ResultPath -Raw | ConvertFrom-Json
        Assert-Equal $result.stage 'shutdown'
        Assert-Equal $result.reason 'shutdown_timeout'
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
