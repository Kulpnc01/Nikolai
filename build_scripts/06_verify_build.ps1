# ---------------------------------------------------------
# Nikolai 0.3 – Build Verification (Fresh Build)
# Runs reflex tests and verifies structural integrity.
# ---------------------------------------------------------

$root = "C:\Nikolai_0_3"

Write-Host "Running Nikolai 0.3 build verification..."
Write-Host ""

# --- 1. Verify Required Files Exist ---
$requiredFiles = @(
    "$root\spine\project_spine.json",
    "$root\spine\decisions.log",

    "$root\brain\identity\Nikolai_0_3.md",

    "$root\brain\core\async_core_runtime.py",
    "$root\brain\core\async_context.py",
    "$root\brain\core\async_event_bridge.py",
    "$root\brain\core\async_intent_engine.py",
    "$root\brain\core\async_task_manager.py",
    "$root\brain\core\async_respond_loop.py",

    "$root\brain\silica\event_loop.py",
    "$root\brain\silica\pipeline_watcher.py",
    "$root\brain\silica\module_loader.py",
    "$root\brain\silica\state_machine.py",
    "$root\brain\silica\node_coordinator.py",
    "$root\brain\silica\bridge_python.py",
    "$root\brain\silica\bridge_san.py",

    "$root\nikolai.py",
    "$root\nikolai.ps1",

    "$root\Docs\Architecture\TECHNICAL_ARCHITECTURE.md",
    "$root\nervous_system\runtime.log",
    "$root\nervous_system\errors.log",

    "$root\reflexes\test_runtime.py"
)

$missing = $false
Write-Host "Checking required files..."
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Missing: $file"
        $missing = $true
    } else {
        Write-Host "✔ Found: $file"
    }
}

# Check for package inits
$packageDirs = @(
    "$root\brain", "$root\brain\core", "$root\brain\silica", "$root\modules"
)
foreach ($dir in $packageDirs) {
    $init = Join-Path $dir "__init__.py"
    if (-not (Test-Path $init)) {
        Write-Host "❌ Missing package init: $init"
        $missing = $true
    }
}

if ($missing) {
    Write-Host ""
    Write-Host "Build verification failed — missing files detected."
    exit 1
}

Write-Host ""
Write-Host "All required files found."
Write-Host ""


# --- 2. Validate JSON Files ---
Write-Host "Validating JSON files..."

$jsonFiles = @(
    "$root\spine\project_spine.json",
    "$root\modules\ShopperModule\pipeline\incoming\module_contract.json",
    "$root\modules\HelpDiagnosticModule\pipeline\incoming\module_contract.json"
)

$jsonError = $false
foreach ($jsonFile in $jsonFiles) {
    if (Test-Path $jsonFile) {
        try {
            Get-Content $jsonFile | ConvertFrom-Json | Out-Null
            Write-Host "✔ Valid JSON: $jsonFile"
        }
        catch {
            Write-Host "❌ Invalid JSON: $jsonFile"
            $jsonError = $true
        }
    }
}

if ($jsonError) {
    Write-Host ""
    Write-Host "Build verification failed — JSON errors detected."
    exit 1
}

Write-Host ""
Write-Host "All JSON validated."
Write-Host ""


# --- 3. Run Reflex Tests ---
Write-Host "Running reflex tests (Python syntax check)..."
Write-Host ""

$python = "python"
$pyFiles = Get-ChildItem -Path "$root\brain" -Filter *.py -Recurse

foreach ($pyFile in $pyFiles) {
    $result = & $python -m py_compile $pyFile.FullName 2>&1
    if ($lastExitCode -ne 0) {
        Write-Host "❌ Syntax Error: $($pyFile.FullName)"
        Write-Host $result
        $syntaxError = $true
    } else {
        Write-Host "✔ Syntax OK: $($pyFile.FullName)"
    }
}

if ($syntaxError) {
    Write-Host ""
    Write-Host "Build verification failed — Python syntax errors detected."
    exit 1
}

Write-Host ""
Write-Host "✔ All Python files verified."
Write-Host ""


# --- Final Result ---
Write-Host "---------------------------------------------"
Write-Host "Nikolai 0.3 build verification successful."
Write-Host "The organism is structurally sound."
Write-Host "---------------------------------------------"
