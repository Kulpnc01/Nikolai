# ---------------------------------------------------------
# Nikolai 0.3 â€?Full Build Reset
# Deletes all generated files except build scripts.
# ---------------------------------------------------------

$root = "C:\Nikolai_0_3"

Write-Host "Resetting Nikolai 0.3 build..."
Write-Host ""

$preserve = "$root\build_scripts"

# Delete everything except build_scripts
Get-ChildItem -Path $root | Where-Object {
    $_.FullName -ne $preserve
} | Remove-Item -Recurse -Force

Write-Host "âœ?Build reset complete."
Write-Host "All components removed except build scripts."
Write-Host ""
Write-Host "You may now run the build sequence from Script 1."
