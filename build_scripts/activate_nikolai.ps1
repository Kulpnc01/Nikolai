# ---------------------------------------------------------
# Nikolai 0.3 ‚Ä?Controlled Activation Script (Fresh Build)
# Safely instantiates the runtime and prints activation status.
# Does NOT enter a loop or autonomous mode.
# ---------------------------------------------------------

$root = "C:\Nikolai_0_3"

Write-Host "Activating Nikolai 0.3..."
Write-Host ""

# --- 1. Ensure Build Verification Passed ---
$verifyScript = "$root\build_scripts\verify_build.ps1"

if (-not (Test-Path $verifyScript)) {
    Write-Host "‚ù?Missing verify_build.ps1 ‚Ä?cannot activate."
    exit 1
}

Write-Host "Running build verification..."
Write-Host ""

$verify = Start-Process pwsh -ArgumentList "-File `"$verifyScript`"" -NoNewWindow -PassThru -Wait

if ($verify.ExitCode -ne 0) {
    Write-Host ""
    Write-Host "‚ù?Build verification failed ‚Ä?activation aborted."
    exit 1
}

Write-Host ""
Write-Host "‚ú?Build verified."
Write-Host ""


# --- 2. Activation Python Snippet ---
$activation = @'
from core_runtime import CoreRuntime

try:
    runtime = CoreRuntime()
    print("Nikolai 0.3 activated successfully.")
except Exception as e:
    print("Activation error:", e)
'@

$tempFile = "$root\brain\runtime\_activation_test.py"
Set-Content $tempFile $activation


# --- 3. Run Activation ---
$python = "python"

Write-Host "Running activation test..."
Write-Host ""

$process = Start-Process $python -ArgumentList "`"$tempFile`"" -NoNewWindow -PassThru -Wait

Remove-Item $tempFile -Force

if ($process.ExitCode -ne 0) {
    Write-Host ""
    Write-Host "‚ù?Activation failed ‚Ä?runtime error."
    exit 1
}

Write-Host ""
Write-Host "---------------------------------------------"
Write-Host "Nikolai 0.3 is awake."
Write-Host "Runtime instantiated successfully."
Write-Host "---------------------------------------------"

