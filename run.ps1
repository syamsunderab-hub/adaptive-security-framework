$PSScriptRoot = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Set-Location $PSScriptRoot
$env:PYTHONPATH = $PSScriptRoot
$env:PATH = "C:\Users\Acer\AppData\Local\Programs\nodejs;$env:PATH"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Starting Adaptive Security Framework Command Center... " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Open browser after 1.5 seconds
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8000"
} | Out-Null

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
