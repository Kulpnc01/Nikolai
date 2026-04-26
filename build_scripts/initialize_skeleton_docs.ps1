# ---------------------------------------------------------
# Nikolai 0.3 â€?Skeleton Initialization (Fresh Build)
# Populates architecture, memory, and error model documents.
# Enforces VS Codeâ€“friendly Markdown spacing.
# ---------------------------------------------------------

$root = "C:\Nikolai_0_3"

# --- Runtime Architecture ---
$runtimeArch = @"

# Runtime Architecture â€?Nikolai 0.3

## Overview

Nikolai 0.3 is intentionally minimal. The system consists of a core runtime,
a context manager, a decision engine, a project spine, and a coding partner
module referred to as the hands.

## Core Responsibilities

- Interpret user intent  
- Maintain identity and SOP  
- Manage context  
- Log decisions  
- Coordinate the hands module  

## Module Boundaries

- The brain handles reasoning, identity, and decision-making.  
- The hands handle code generation and mechanical tasks.  
- The spine maintains continuity and architectural constraints.  
- The skeleton defines the system's structure and rules.  
- The nervous system handles logs and signals.  

## Architectural Principles

- Minimal surface area  
- Deterministic behavior  
- No drift from defined identity  
- Clear module boundaries  
- Reproducible builds  

"@

Set-Content "$root\skeleton\runtime_architecture.md" $runtimeArch


# --- Memory Model ---
$memoryModel = @"

# Memory Model â€?Nikolai 0.3

## Memory Layers

- **Task Context**  
  Short-lived, cleared when tasks complete.  

- **Project Spine**  
  Persistent architectural decisions and constraints.  

## Exclusions

- No long-term personal memory  
- No autonomous expansion  
- No cross-project bleed  

## Purpose

The memory model ensures coherence without drift. It provides enough
continuity to maintain structure while preventing uncontrolled growth.

"@

Set-Content "$root\skeleton\memory_model.md" $memoryModel


# --- Error Model ---
$errorModel = @"

# Error Model â€?Nikolai 0.3

## Recoverable Errors

- Missing context  
- Conflicting instructions  
- Ambiguous requests  

## Unrecoverable Errors

- Logical contradictions  
- Unsafe operations  
- Invalid architecture  

## Behavior

On recoverable errors, request clarification.  
On unrecoverable errors, halt and escalate.  

"@

Set-Content "$root\skeleton\error_model.md" $errorModel


Write-Host "Nikolai 0.3 skeleton initialized â€?bones are in place."
