import subprocess
import sys
import os
import datetime

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        if check:
            print(f"Error executing {command}:\n{result.stderr}")
        return False, result.stdout, result.stderr
    return True, result.stdout, result.stderr

def main():
    repo_path = r"c:\Users\acord\OneDrive\Desktop\paginas web\Jorge Aguirre Flores maquilaje definitivo\jorge_web"
    
    print("--- 🔄 SMART GIT SYNC START ---")
    
    # 1. Add changes
    success, _, _ = run_command("git add .", cwd=repo_path)
    if not success:
        return

    # 2. Check for changes to commit
    # --porcelain gives a machine-readable output. If empty, nothing to commit.
    success, stdout, _ = run_command("git status --porcelain", cwd=repo_path)
    
    if not stdout.strip():
        print("✅ No changes found using 'git status'. Working tree is clean.")
        print("--- NO SYNC REQUIRED ---")
        return

    # 3. Commit changes
    # Use provided argument or default message
    commit_msg = sys.argv[1] if len(sys.argv) > 1 else f"auto: periodic sync {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    print(f"📝 Committing with message: '{commit_msg}'")
    success, _, _ = run_command(f'git commit -m "{commit_msg}"', cwd=repo_path, check=False)
    
    if not success:
        print("⚠️  Commit command returned non-zero code (maybe raciness?). Checking status again...")
        # Fallback check
        success, stdout, _ = run_command("git status --porcelain", cwd=repo_path)
        if stdout.strip():
             print("❌ Fatal: Changes exist but commit failed.")
             return
        else:
             print("✅ False alarm: clean state confirmed.")

    # 4. Push changes
    print("🚀 Pushing to origin main...")
    success, stdout, stderr = run_command("git push origin main", cwd=repo_path)
    
    if success:
        print("\n--- ✅ DEPLOYMENT SYNCED SUCCESSFULLY ---")
        print("Render should now build the new version.")
        print("Monitor: https://dashboard.render.com/web/evolution-whatsapp-zn13/logs")
    else:
        print("\n❌ PUSH FAILED")
        print("Check your internet connection or credentials.")

if __name__ == "__main__":
    main()
