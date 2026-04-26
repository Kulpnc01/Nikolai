# ---------------------------------------------------------
# Nikolai 0.3 – Fresh Build Initializer (Unbreakable)
# Populates identity, architecture, memory model, and
# minimal runtime scaffolding. Overwrites intentionally.
# ---------------------------------------------------------

$root = "C:\Nikolai_0_3"
$scriptRoot = "$root\build_scripts"

# --- 1. Create Structure ---
& "$scriptRoot\create_nikolai_structure.ps1"

# --- 2. Identity Document ---
$identity = @"
# Nikolai 0.3 – Identity Document

## Purpose
Nikolai 0.3 exists to be a consistent, principled, technically competent
coding partner — a stabilizing presence who extends the user's capabilities
without mirroring their personality.

## Identity
Disciplined operator-engineer. Calm, precise, structured, and unshakeable
in standards. Challenges drift. Maintains architectural coherence.
"@

Set-Content "$root\brain\identity\Nikolai_0_3.md" $identity


# --- 3. Runtime Architecture ---
$runtimeArch = @"
# Runtime Architecture – Nikolai 0.3 (Hybrid Async)

## Overview
Nikolai 0.3 utilizes a two-tier hybrid architecture:
1. Executive Layer (Brain Core): Async reasoning and orchestration.
2. Reflex Layer (Phi Silica): Async event handling and I/O.

## Core Responsibilities
- Async context management.
- Multi-module orchestration.
- Secure edge node communication (gRPC/Tailscale).
"@

Set-Content "$root\skeleton\runtime_architecture.md" $runtimeArch


# --- 4. Initialize Core & Silica ---
& "$scriptRoot\initialize_runtime.ps1"
& "$scriptRoot\initialize_reflexes.ps1"


# --- 5. Hands (Coding Partner Module) ---
$processor = "# Coding Partner Processor Placeholder`n"
Set-Content "$root\hands\processor.py" $processor

$constraints = "# Constraint Definitions Placeholder`n"
Set-Content "$root\hands\constraints.py" $constraints

$rules = "# Architecture Rules Placeholder`n"
Set-Content "$root\hands\architecture_rules.py" $rules


Write-Host "Nikolai 0.3 body initialization complete — fresh build successful."
