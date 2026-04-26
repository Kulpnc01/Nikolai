#Requires -RunAsAdministrator
# ---------------------------------------------------------
# Nikolai 0.3 – Advanced Storage & DevDrive Provisioning
# ---------------------------------------------------------

$ErrorActionPreference = "Stop"

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host " NIKOLAI 0.3 STORAGE PROVISIONING SCRIPT              " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "WARNING: This script will WIPE all data currently on the D:\ drive." -ForegroundColor Red
Write-Host "It will reformat D:\ to NTFS, provision two ReFS DevDrives (VHDXs),"
Write-Host "and optimize the remaining space for backups."
Write-Host ""

$confirmation = Read-Host "Are you absolutely sure you want to format D:\? (Type 'YES' to proceed)"
if ($confirmation -cne "YES") {
    Write-Host "Provisioning cancelled by user." -ForegroundColor Yellow
    exit
}

Write-Host "`n[1/6] Formatting Physical Drive D:\ to NTFS..." -ForegroundColor Cyan
Format-Volume -DriveLetter D -FileSystem NTFS -NewFileSystemLabel "Nikolai_Storage" -Confirm:$false | Out-Null
Write-Host "✔ D:\ formatted successfully." -ForegroundColor Green

# --- Provision Nikolai Static DevDrive (1000GB) ---
Write-Host "`n[2/6] Creating Nikolai Static DevDrive (1000GB VHDX). This will take a while..." -ForegroundColor Cyan
$nikolaiVHDX = "D:\Nikolai_DevDrive.vhdx"
New-VHD -Path $nikolaiVHDX -SizeBytes 1000GB -Fixed | Out-Null

Write-Host "Mounting and Formatting Nikolai DevDrive as ReFS (Drive N:)..." -ForegroundColor Cyan
$nDisk = Mount-VHD -Path $nikolaiVHDX -PassThru | Get-Disk
# Clear any existing partitions just in case
$nDisk | Clear-Disk -RemoveData -RemoveOEM -Confirm:$false -ErrorAction SilentlyContinue
$nDisk | Initialize-Disk -PartitionStyle GPT -PassThru | 
    New-Partition -DriveLetter N -UseMaximumSize | 
    Format-Volume -FileSystem ReFS -DevDrive -NewFileSystemLabel "Nikolai_Sandboxed" -Confirm:$false | Out-Null
Write-Host "✔ Nikolai DevDrive (N:) provisioned." -ForegroundColor Green

# --- Provision Android Dynamic DevDrive (500GB) ---
Write-Host "`n[3/6] Creating Android Dynamic DevDrive (500GB Max VHDX)..." -ForegroundColor Cyan
$androidVHDX = "D:\Android_DevDrive.vhdx"
New-VHD -Path $androidVHDX -SizeBytes 500GB -Dynamic | Out-Null

Write-Host "Mounting and Formatting Android DevDrive as ReFS (Drive A:)..." -ForegroundColor Cyan
$aDisk = Mount-VHD -Path $androidVHDX -PassThru | Get-Disk
# Clear any existing partitions just in case
$aDisk | Clear-Disk -RemoveData -RemoveOEM -Confirm:$false -ErrorAction SilentlyContinue
$aDisk | Initialize-Disk -PartitionStyle GPT -PassThru | 
    New-Partition -DriveLetter A -UseMaximumSize | 
    Format-Volume -FileSystem ReFS -DevDrive -NewFileSystemLabel "Android_Sandboxed" -Confirm:$false | Out-Null
Write-Host "✔ Android DevDrive (A:) provisioned." -ForegroundColor Green

# --- Preload File Structures ---
Write-Host "`n[4/6] Preloading Nikolai Sandbox Structures on N:\..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "N:\Nikolai_Sandbox" -Force | Out-Null
New-Item -ItemType Directory -Path "N:\Nikolai_Sandbox\mock_nodes" -Force | Out-Null
New-Item -ItemType Directory -Path "N:\Nikolai_Sandbox\telemetry_dumps" -Force | Out-Null
New-Item -ItemType Directory -Path "N:\Nikolai_Sandbox\module_testing" -Force | Out-Null
New-Item -ItemType Directory -Path "N:\Nikolai_Sandbox\stress_tests" -Force | Out-Null

Write-Host "`n[5/6] Preloading Android Dev Structures on A:\..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "A:\Android_Projects" -Force | Out-Null
New-Item -ItemType Directory -Path "A:\Android_Projects\AISLESNode" -Force | Out-Null
New-Item -ItemType Directory -Path "A:\Android_SDK" -Force | Out-Null
New-Item -ItemType Directory -Path "A:\Gradle_Cache" -Force | Out-Null
New-Item -ItemType Directory -Path "A:\AVD_Emulators" -Force | Out-Null

# --- Configure Backups on D: ---
Write-Host "`n[6/6] Optimizing remaining D:\ space for High-Priority Backups..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "D:\Backups" -Force | Out-Null
New-Item -ItemType Directory -Path "D:\Backups\High_Priority" -Force | Out-Null
New-Item -ItemType Directory -Path "D:\Backups\Nikolai_Core" -Force | Out-Null
New-Item -ItemType Directory -Path "D:\Backups\System_Images" -Force | Out-Null

# Create a ReadMe for the backup drive
$readme = @"
# D:\ Backup Drive

This drive is optimized for high-priority backups. 
The massive VHDX files (Nikolai_DevDrive.vhdx and Android_DevDrive.vhdx) host the ReFS DevDrives.

**DO NOT COMPRESS OR DEFRAGMENT THE VHDX FILES MANUALLY**, as they are actively mounted by the system.
"@
Set-Content "D:\Backups\README.md" $readme

Write-Host "`n======================================================" -ForegroundColor Cyan
Write-Host " PROVISIONING COMPLETE!                               " -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "D:\ is now NTFS and hosts your backups and VHDXs."
Write-Host "N:\ is your 1000GB Fixed ReFS DevDrive for Nikolai."
Write-Host "A:\ is your 500GB Dynamic ReFS DevDrive for Android."
Write-Host "Please ensure your Android Studio settings point the SDK and Gradle paths to A:\"
Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
