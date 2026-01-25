import subprocess
import sys
import os

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return None

def get_smart_message():
    """Analiza los cambios para generar un mensaje real"""
    changed_files = run_command("git diff --name-only --cached")
    if not changed_files:
        return None
    
    files = changed_files.split('\n')
    summary = ", ".join(files[:3])
    if len(files) > 3:
        summary += f" and {len(files) - 3} more"
        
    # Clasificación básica
    prefix = "feat"
    if any("test" in f for f in files): prefix = "test"
    if any(f.endswith(".css") or f.endswith(".html") for f in files): prefix = "style"
    if any("fix" in f or "bug" in f for f in files): prefix = "fix"
    if any("docs" in f or f.endswith(".md") for f in files): prefix = "docs"
    
    return f"{prefix}: optimize and update {summary}"

def main():
    print("🚀 Iniciando Git Sync Pro (Senior Level)...")
    
    # 1. Add
    run_command("git add .")
    
    # 2. Generate Message
    msg = get_smart_message()
    if not msg:
        print("⚠️ No hay cambios para subir.")
        return

    print(f"📝 Commit: {msg}")
    
    # 3. Commit
    run_command(f'git commit -m "{msg}"')
    
    # 4. Push
    print("📤 Subiendo a GitHub...")
    run_command("git push")
    print("✅ ¡Sincronización exitosa!")

if __name__ == "__main__":
    main()
