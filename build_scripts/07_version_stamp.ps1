# ---------------------------------------------------------
# Nikolai 0.3 – Version Stamp Script (Unbreakable Edition)
# Repairs spine if empty, null, or invalid. Then stamps version.
# ---------------------------------------------------------

$root = "C:\Nikolai_0_3"
$version = "0.3.$(Get-Date -Format 'yyyyMMddHHmmss')"

Write-Host "Stamping version: $version"
Write-Host ""

# Update VERSION file
Set-Content "$root\VERSION" $version

# Load spine safely
$spinePath = "$root\spine\project_spine.json"

if (-not (Test-Path $spinePath)) {
    Write-Host "❌ Spine file missing — creating new spine."
    $raw = ""
} else {
    $raw = Get-Content $spinePath -Raw
}

# Detect empty or whitespace-only file
if ([string]::IsNullOrWhiteSpace($raw)) {
    Write-Host "⚠ Spine file is empty — rebuilding spine."
    $spine = $null
} else {
    try {
        $spine = $raw | ConvertFrom-Json
    }
    catch {
        Write-Host "❌ Spine JSON invalid — rebuilding spine."
        $spine = $null
    }
}

# If spine is null or not an object, rebuild it
if ($spine -eq $null -or $spine.PSObject.Properties.Count -eq 0) {

    Write-Host "⚠ Creating new spine object."

    $spine = [PSCustomObject]@{
        version     = $version
        created     = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
        purpose     = "Maintain architectural continuity and record decisions."
        constraints = @{
            identity_locked     = $true
            architecture_locked = $true
            no_drift            = $true
        }
        modules = @{
            brain   = @{ status = "initialized" }
            hands   = @{ status = "initialized" }
            skeleton= @{ status = "initialized" }
            nervous_system = @{ status = "initialized" }
        }
        decision_history = @()
    }
}
else {
    # Update or add version field
    if ($spine.PSObject.Properties.Name -notcontains "version") {
        Write-Host "Version field missing — adding it."
        $spine | Add-Member -NotePropertyName "version" -NotePropertyValue $version
    } else {
        Write-Host "Version field found — updating it."
        $spine.version = $version
    }
}

# Write updated JSON back to file
$spine | ConvertTo-Json -Depth 10 | Set-Content $spinePath

Write-Host ""
Write-Host "✔ Version stamped successfully."
Write-Host "Current version: $version"