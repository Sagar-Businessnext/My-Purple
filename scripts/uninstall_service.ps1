# Remove Purple's autostart Scheduled Task.
#   powershell -ExecutionPolicy Bypass -File scripts\uninstall_service.ps1
$ErrorActionPreference = "Stop"
Stop-ScheduledTask -TaskName "Purple" -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "Purple" -Confirm:$false
Write-Host "[ OK ] Removed the 'Purple' scheduled task."
