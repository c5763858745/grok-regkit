# Start grok-regkit Web
$root = "F:\grok-regkit"
$py = Join-Path $root ".venv\Scripts\python.exe"
$pidFile = Join-Path $root "server.pid"
$log = Join-Path $root "uvicorn.log"
$err = Join-Path $root "uvicorn.err"
if (Test-Path $pidFile) {
  $old = Get-Content $pidFile | Select-Object -First 1
  if ($old -and (Get-Process -Id $old -ErrorAction SilentlyContinue)) {
    Write-Host "Already running PID=$old -> http://127.0.0.1:8092"
    exit 0
  }
}
$proc = Start-Process -FilePath $py -ArgumentList "-m","uvicorn","web.server:app","--host","127.0.0.1","--port","8092","--workers","1" -WorkingDirectory $root -RedirectStandardOutput $log -RedirectStandardError $err -WindowStyle Hidden -PassThru
Set-Content -Path $pidFile -Value $proc.Id
Write-Host "Started PID=$($proc.Id)"
Write-Host "Open: http://127.0.0.1:8092"