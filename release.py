#!/usr/bin/env python
import subprocess
import sys
import os

def run_command(command, exit_on_error=True):
    """Run a command and return the output"""
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, shell=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error message: {e.stderr}")
        if exit_on_error:
            sys.exit(1)
        return None

def get_current_version():
    """Get the current version from Poetry"""
    return run_command(["poetry", "version", "-s"])

def main():
    # Get the current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    # Get the new version
    new_version = input("New version (patch/minor/major or specific version): ")
    
    # Update the version
    run_command(["poetry", "version", new_version])
    updated_version = get_current_version()
    print(f"New version: {updated_version}")
    
    # Confirm release
    confirm = input("Create and push release commit? [y/N] ")
    if confirm.lower() != 'y':
        print("Release canceled. Rolling back version...")
        # Roll back to the original version
        run_command(["poetry", "version", current_version])
        print(f"Version rolled back to {current_version}")
        return
    
    # Run checks
    print("Running checks...")
    try:
        run_command(["make", "check"])
    except Exception as e:
        print(f"Checks failed: {e}")
        print("Rolling back version...")
        # Roll back to the original version
        run_command(["poetry", "version", current_version])
        print(f"Version rolled back to {current_version}")
        return
    
    # Create and push the release
    try:
        run_command(["git", "add", "pyproject.toml"])
        run_command(["git", "commit", "-m", f"Bump version to {updated_version}"])
        run_command(["git", "tag", f"v{updated_version}"])
        run_command(["git", "push", "origin", "main"])
        run_command(["git", "push", "origin", "--tags"])
        
        print(f"Release v{updated_version} created and pushed. GitHub Actions will handle the rest.")
    except Exception as e:
        print(f"Error during git operations: {e}")
        print("You may need to manually roll back the version and any git changes.")
        return

if __name__ == "__main__":
    main()