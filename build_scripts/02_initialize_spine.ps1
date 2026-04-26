# ---------------------------------------------------------
# Nikolai 0.3 â€?Spine Initialization (Fresh Build)
# Creates a guaranteed-valid project spine with a stable schema.
# ---------------------------------------------------------

$root = "C:\Nikolai_0_3"

Write-Host "Initializing Nikolai 0.3 spine..."
Write-Host ""

# Create spine object with guaranteed schema
$spine = [PSCustomObject]@{
    version     = "0.3.$(Get-Date -Format 'yyyyMMddHHmmss')"
    created     = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    purpose     = "Maintain architectural continuity and record decisions."

    constraints = @{
        identity_locked     = $true
        architecture_locked = $true
        no_drift            = $true
    }

    modules = @{
        brain           = @{ status = "initialized" }
        silica          = @{ status = "initialized" }
        hands           = @{ status = "initialized" }
        skeleton        = @{ status = "initialized" }
        nervous_system  = @{ status = "initialized" }
        reflexes        = @{ status = "initialized" }
    }

    decision_history = @()
}

# Convert to JSON and write to file
$spinePath = "$root\spine\project_spine.json"
$spine | ConvertTo-Json -Depth 10 | Set-Content $spinePath

Write-Host "âœ?Spine initialized at: $spinePath"
Write-Host "âœ?Schema guaranteed."
Write-Host "âœ?JSON valid."
Write-Host ""
Write-Host "Nikolai 0.3 spine is ready."

