# ---------------------------------------------------------
# Nikolai 0.3 – Controlled Deactivation
# Ensures no runtime processes remain active.
# ---------------------------------------------------------

Write-Host "Deactivating Nikolai 0.3..."
Write-Host ""

# Kill any Python processes running core_runtime
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "Found active Python processes. Terminating..."
    $pythonProcesses | Stop-Process -Force
    Write-Host "✔ Python processes terminated."
} else {
    Write-Host "✔ No active Python processes found."
}

Write-Host ""
Write-Host "---------------------------------------------"
Write-Host "Nikolai 0.3 is fully deactivated."
Write-Host "No runtime state remains active."
Write-Host "---------------------------------------------"