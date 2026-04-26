# C:\Nikolai_0_3\nikolai.ps1
param(
    [string]$PythonPath = "python"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "[Nikolai 0.3] Launching with Python 3.14..." -ForegroundColor Cyan

& $PythonPath ".\nikolai.py"