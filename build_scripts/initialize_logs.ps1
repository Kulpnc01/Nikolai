# ---------------------------------------------------------
# Nikolai 0.3 – Nervous System Initialization (Fresh Build)
# Initializes runtime and error logs with clean headers.
# ---------------------------------------------------------

$root = "C:\Nikolai_0_3"

# --- Runtime Log Header ---
$runtimeHeader = @"
# Nikolai 0.3 – Runtime Log
# Fresh Build: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

This log records runtime events, state transitions, and internal signals.
Entries should be structured and timestamped.

Format:
[DATE TIME] – [EVENT] – [DETAILS]
"@

Set-Content "$root\nervous_system\runtime.log" $runtimeHeader


# --- Error Log Header ---
$errorHeader = @"
# Nikolai 0.3 – Error Log
# Fresh Build: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

This log records recoverable and unrecoverable errors encountered during
runtime execution. Each entry must include category and context.

Format:
[DATE TIME] – [ERROR TYPE] – [DESCRIPTION]
"@

Set-Content "$root\nervous_system\errors.log" $errorHeader


Write-Host "Nikolai 0.3 nervous system initialized — logs ready."
