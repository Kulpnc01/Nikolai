# ---------------------------------------------
# Nikolai 0.3 – Body-Based Folder Structure Builder
# Creates the full directory skeleton + placeholder files
# ---------------------------------------------

# Root directory
$root = "C:\Nikolai_0_3"

# Folder map (body metaphor)
$folders = @(
    "$root\brain\core",
    "$root\brain\silica",
    "$root\brain\memory",
    "$root\brain\identity",
    "$root\brain\reasoning",
    "$root\brain\runtime",

    "$root\modules\ShopperModule\pipeline\incoming",
    "$root\modules\ShopperModule\pipeline\outgoing",
    "$root\modules\HelpDiagnosticModule\logic",
    "$root\modules\HelpDiagnosticModule\pipeline\incoming",
    "$root\modules\HelpDiagnosticModule\pipeline\outgoing",

    "$root\hands",
    "$root\spine",
    "$root\nervous_system",
    "$root\skeleton",
    "$root\reflexes",
    "$root\Docs\Architecture",
    "$root\Docs\Guides",
    "$root\Docs\Governance",
    "$root\build_scripts"
)

# Create folders
foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
    }
}

# Ensure __init__.py files for all python packages
$packageDirs = @(
    "$root\brain",
    "$root\brain\core",
    "$root\brain\silica",
    "$root\brain\reasoning",
    "$root\brain\runtime",
    "$root\hands",
    "$root\reflexes",
    "$root\modules",
    "$root\modules\ShopperModule",
    "$root\modules\HelpDiagnosticModule",
    "$root\modules\HelpDiagnosticModule\logic"
)

foreach ($dir in $packageDirs) {
    $initFile = Join-Path $dir "__init__.py"
    if (-not (Test-Path $initFile)) {
        Set-Content -Path $initFile -Value "# Package: $(Split-Path $dir -Leaf)"
    }
}

Write-Host "Nikolai 0.3 folder structure and packages initialized successfully."
