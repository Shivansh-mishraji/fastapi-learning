import os
import subprocess
import datetime

REPO_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(REPO_PATH, "activity_log.txt")

def make_commits(count=25):
    print(f"Starting generation of {count} commits in {REPO_PATH}...")
    
    # Ensure it's a git repo
    if not os.path.exists(os.path.join(REPO_PATH, ".git")):
        print(f"Error: {REPO_PATH} is not a git repository.")
        return
        
    for i in range(1, count + 1):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Append entry to log file
        with open(LOG_FILE, "a") as f:
            f.write(f"Commit log entry #{i} added at {timestamp}\n")
            
        # Stage the log file
        subprocess.run(["git", "add", "activity_log.txt"], cwd=REPO_PATH, check=True)
        
        # Create commit
        commit_msg = f"chore: auto-update activity log entry #{i} - {timestamp}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_PATH, check=True)
        print(f"Committed {i}/{count}")
        
    print("Pushing all commits to GitHub...")
    push_res = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_PATH, capture_output=True, text=True)
    if push_res.returncode == 0:
        print("Successfully pushed all commits!")
    else:
        print(f"Failed to push commits. Error: {push_res.stderr}")

if __name__ == "__main__":
    make_commits(25)
