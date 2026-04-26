# ---------------------------------------------------------
# Nikolai 0.3 ‚Ä?Activation Preparation (Fresh Build)
# Prepares the environment for safe runtime activation.
# Does NOT activate the runtime.
# ---------------------------------------------------------

$root = "C:\Nikolai_0_3"

Write-Host "Preparing Nikolai 0.3 for activation..."
Write-Host ""


# --- 1. Ensure Logs Exist and Rotate if Needed ---
Write-Host "Checking logs..."

$runtimeLog = "$root\nervous_system\runtime.log"
$errorLog   = "$root\nervous_system\errors.log"

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

foreach ($log in @($runtimeLog, $errorLog)) {

    if (-not (Test-Path $log)) {
        Write-Host "‚ù?Missing log: $log"
        Write-Host "Creating fresh log..."
        Set-Content $log "# Log created during activation prep ($timestamp)"
        continue
    }

    # Rotate if larger than 1MB
    $size = (Get-Item $log).Length
    if ($size -gt 1MB) {
        $backup = "$log.$timestamp.bak"
        Write-Host "‚ö?Log too large, rotating: $log"
        Copy-Item $log $backup
        Clear-Content $log
        Add-Content $log "# Log rotated during activation prep ($timestamp)"
    }

    Write-Host "‚ú?Log OK: $log"
}

Write-Host ""
Write-Host "Logs verified."
Write-Host ""


# --- 2. Validate Spine JSON ---
Write-Host "Validating project spine..."

try {
    Get-Content "$root\spine\project_spine.json" | ConvertFrom-Json | Out-Null
    Write-Host "‚ú?Spine JSON valid."
}
catch {
    Write-Host "‚ù?Spine JSON invalid ‚Ä?activation cannot proceed."
    exit 1
}

Write-Host ""


# --- 3. Run Reflex Tests ---
Write-Host "Running reflex tests..."

$python = "python"
$testPath = "$root\reflexes\test_runtime.py"

$process = Start-Process $python -ArgumentList "`"$testPath`"" -NoNewWindow -PassThru -Wait

if ($process.ExitCode -ne 0) {
    Write-Host ""
    Write-Host "‚ù?Reflex tests failed ‚Ä?activation blocked."
    exit 1
}

Write-Host "‚ú?Reflex tests passed."
Write-Host ""


# --- 4. Attempt to Load Runtime (Dry Run) ---
Write-Host "Performing dry-run runtime load..."

$dryRun = @'
from core_runtime import CoreRuntime

try:
    r = CoreRuntime()
    print("OK")
except Exception as e:
    print("ERROR:", e)
'@

$tempFile = "$root\brain\runtime\_dry_run_test.py"
Set-Content $tempFile $dryRun

$process = Start-Process $python -ArgumentList "`"$tempFile`"" -NoNewWindow -PassThru -Wait

Remove-Item $tempFile -Force

if ($process.ExitCode -ne 0) {
    Write-Host ""
    Write-Host "‚ù?Runtime failed to load ‚Ä?activation blocked."
    exit 1
}

Write-Host "‚ú?Runtime loads cleanly."
Write-Host ""


# --- Final Result ---
Write-Host "---------------------------------------------"
Write-Host "Nikolai 0.3 activation environment prepared."
Write-Host "The organism is ready for safe awakening."
Write-Host "---------------------------------------------"
