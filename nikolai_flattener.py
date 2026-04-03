import os
from pathlib import Path

def flatten_nikolai():
    root = Path('C:/HDT/Nikolai')
    output_file = root / 'Nikolai_Logic_Map.md'
    ignore_dirs = {'.git', '__pycache__', 'venv', 'venv_py313', 'node_modules'}
    ignore_exts = {'.pyc', '.exe', '.db', '.key', '.png', '.jpg'}

    print(f"[*] FLATTENING: Project Nikolai -> {output_file}")

    with open(output_file, 'w', encoding='utf-8') as out:
        # 1. Directory Tree
        out.write("# PROJECT ARCHITECTURE: Nikolai\n")
        out.write("```text\n")
        for p in sorted(root.rglob('*')):
            rel = p.relative_to(root)
            if any(d in str(rel) for d in ignore_dirs): continue
            depth = len(p.parts) - len(root.parts)
            out.write("  " * depth + p.name + ("/" if p.is_dir() else "") + "\n")
        out.write("```\n\n")

        # 2. File Contents
        for p in sorted(root.rglob('*')):
            if p.is_dir(): continue
            rel = p.relative_to(root)
            if any(d in str(rel) for d in ignore_dirs): continue
            if p.suffix.lower() in ignore_exts: continue
            if p.name in [output_file.name, 'nikolai_flattener.py']: continue

            print(f"  > Adding: {rel}")
            out.write(f"## FILE: {rel}\n")
            out.write(f"```{p.suffix.replace('.', '')}\n")
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"ERROR READING: {e}")
            out.write("\n```\n\n")

    print("[SUCCESS] Nikolai Logic Map created.")

if __name__ == "__main__":
    flatten_nikolai()
