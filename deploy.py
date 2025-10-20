#!/usr/bin/env python3
"""
Deployment script for Scrapington
Automatically commits changes and pushes to the scrapington.git repository
"""

import subprocess
import sys
import os
from datetime import datetime


def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(1)
    
    return result


def main():
    """Main deployment function."""
    print("🚀 Starting Scrapington deployment...")
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository. Initializing...")
        run_command("git init -b main")
    
    # Add all files
    print("📁 Adding files to git...")
    run_command("git add .")
    
    # Check if there are changes to commit
    result = run_command("git status --porcelain", check=False)
    if not result.stdout.strip():
        print("✅ No changes to commit")
        return
    
    # Create commit message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Update scrapington - {timestamp}"
    
    # Commit changes
    print("💾 Committing changes...")
    run_command(f'git commit -m "{commit_msg}"')
    
    # Check if remote exists
    result = run_command("git remote -v", check=False)
    if "origin" not in result.stdout:
        print("🔗 Adding remote origin...")
        run_command("git remote add origin https://github.com/jjkssf1/scrapington.git")
    else:
        print("🔗 Updating remote origin...")
        run_command("git remote set-url origin https://github.com/jjkssf1/scrapington.git")
    
    # Push to main branch
    print("⬆️  Pushing to main branch...")
    run_command("git push -u origin main")
    
    print("✅ Deployment complete!")
    print("🌐 Repository: https://github.com/jjkssf1/scrapington")


if __name__ == "__main__":
    main()
