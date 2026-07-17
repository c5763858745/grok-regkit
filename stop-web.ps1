# Stop grok-regkit Web
$root = "F:\grok-regkit"
$pidFile = Join-Path $root "server.pid"
if (Test-Path $pidFile) {
  $id = Get-Content $pidFile | Select-Object -First 1
  if ($id) {
    Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
    Get-CimInstance Win32_Process -Filter "ParentProcessId=$id" -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Write-Host "Stopped PID=$id"
  }
  Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
} else { Write-Host "No server.pid" }