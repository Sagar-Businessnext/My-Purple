# Register Purple to start at logon as a hidden, auto-restarting Windows Scheduled Task.
#
#   powershell -ExecutionPolicy Bypass -File scripts\install_service.ps1
#
# Uses pythonw.exe (no console window). Restarts Purple up to 3x/min if it exits.

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent

$py = Join-Path $root ".venv\Scripts\pythonw.exe"
if (-not (Test-Path $py)) { $py = "pythonw" }

$action = New-ScheduledTaskAction -Execute $py -Argument "-m purple.service" -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

Register-ScheduledTask -TaskName "Purple" -Action $action -Trigger $trigger `
    -Settings $settings -Description "Purple - always-on personal assistant" -Force | Out-Null

Write-Host "[ OK ] Registered 'Purple' to start at logon."
Write-Host "Start it now with:  Start-ScheduledTask -TaskName Purple"
Write-Host "Check status with:  purple-service  is reported at http://127.0.0.1:8765/status"
