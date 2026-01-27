import subprocess
import sys
import os

def run_command(command, cwd=None):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def main():
    repo_path = r"c:\Users\acord\OneDrive\Desktop\paginas web\Jorge Aguirre Flores maquilaje definitivo\jorge_web"
    
    print("--- SYNCING TO GITHUB ---")
    
    if not run_command("git add .", cwd=repo_path):
        return
    
    commit_msg = "fix: senior auto-heal persistence and defensive baileys checks"
    if not run_command(f'git commit -m "{commit_msg}"', cwd=repo_path):
        print("Maybe nothing to commit?")
    
    if not run_command("git push origin main", cwd=repo_path):
        print("Push failed. Check your connection and credentials.")
        return

    print("\n--- DEPLOYMENT SYNCED ---")
    print("Render should now start building the fixed version.")
    print("Monitor the logs at: https://dashboard.render.com/web/evolution-whatsapp-zn13/logs")

if __name__ == "__main__":
    main()
