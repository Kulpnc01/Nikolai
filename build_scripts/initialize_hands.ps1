# ---------------------------------------------------------
# Nikolai 0.3 â€?Hands Initialization (Fresh Build)
# Populates the coding partner module with clean scaffolding.
# Enforces VS Codeâ€“friendly Markdown spacing.
# ---------------------------------------------------------

$root = "C:\Nikolai_0_3"

# --- Coding Partner Processor ---
$processor = @"

# Coding Partner Processor â€?Nikolai 0.3

class CodingPartner:
    def __init__(self):
        self.status = "ready"

    def process(self, intent, context):
        \"\"\"
        The hands module performs mechanical tasks such as:
        - code generation
        - refactoring
        - file transformations
        - structural edits

        It does not make architectural decisions.
        It does not override the spine.
        It does not modify identity or SOP.
        \"\"\"

        return {
            "status": "ok",
            "message": "Hands module processed the request.",
            "intent": intent,
            "context": context
        }

"@

Set-Content "$root\hands\processor.py" $processor


# --- Constraint Definitions ---
$constraints = @"

# Constraint Definitions â€?Nikolai 0.3

CONSTRAINTS = {

    "coding_standard": "strict",

    "architecture_integrity": "required",

    "no_drift": true,

    "respect_spine": true,

    "identity_protection": true

}

"@

Set-Content "$root\hands\constraints.py" $constraints


# --- Architecture Rules ---
$rules = @"

# Architecture Rules â€?Nikolai 0.3

RULES = [

    "The hands must never modify identity or SOP.",

    "The hands must never override architectural decisions.",

    "The hands must follow constraints defined in the spine.",

    "The hands must maintain structural consistency.",

    "The hands must not generate modules outside defined boundaries."

]

"@

Set-Content "$root\hands\architecture_rules.py" $rules


Write-Host "Nikolai 0.3 hands initialized â€?mechanical layer ready."
