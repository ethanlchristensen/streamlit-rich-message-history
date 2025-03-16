#!/usr/bin/env python
import subprocess
import sys
import os
import random
import string

def run_command(command, exit_on_error=True):
    """Run a command and return the output"""
    print(f"Running: {command}")
    try:
        # If already in a poetry environment, don't use "poetry run" prefix
        if isinstance(command, list) and command[0] == "poetry" and command[1] == "run":
            # Execute the command directly without the "poetry run" prefix
            direct_command = command[2:]
            result = subprocess.run(direct_command, check=True, capture_output=True, text=True, shell=False)
        elif isinstance(command, list):
            result = subprocess.run(command, check=True, capture_output=True, text=True, shell=False)
        else:
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
    # For version query, keep using poetry command
    return run_command(["poetry", "version", "-s"])

def get_current_branch():
    """Get the current git branch"""
    return run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])

def generate_branch_name(version):
    """Generate a unique branch name for the release"""
    random_suffix = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
    return f"release-v{version}-{random_suffix}"

def main():
    # Get the current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    # Check if on main branch
    current_branch = get_current_branch()
    if current_branch != "main":
        confirm = input(f"You are not on the main branch (currently on {current_branch}). Continue? [y/N] ")
        if confirm.lower() != 'y':
            print("Release preparation canceled.")
            return
    
    # Make sure we're up to date with remote
    print("Updating from remote...")
    run_command(["git", "fetch", "origin"])
    if current_branch == "main":
        run_command(["git", "pull", "origin", "main"])
    
    # Get the new version
    new_version = input("New version (patch/minor/major or specific version): ")
    
    # Update the version
    run_command(["poetry", "version", new_version])
    updated_version = get_current_version()
    print(f"New version: {updated_version}")
    
    # Confirm release preparation
    confirm = input("Create release branch and PR? [y/N] ")
    if confirm.lower() != 'y':
        print("Release preparation canceled. Rolling back version...")
        # Roll back to the original version
        run_command(["poetry", "version", current_version])
        print(f"Version rolled back to {current_version}")
        return
    
    # Create a new branch for the release
    release_branch = generate_branch_name(updated_version)
    print(f"Creating release branch: {release_branch}")
    run_command(["git", "checkout", "-b", release_branch])
    
    # Run checks
    print("Running checks...")
    try:
        print("Checking Format...")
        run_command(["black", "--check", "."])
        run_command(["isort", "--check", "."])
        print("Linting...")
        run_command(["flake8"])
        print("Checking Types...")
        run_command(["mypy", "streamlit_rich_message_history"])
        print("Running Tests...")
        run_command(["pytest"])
    except Exception as e:
        print(f"Checks failed: {e}")
        print("Rolling back version and returning to original branch...")
        run_command(["poetry", "version", current_version])
        run_command(["git", "checkout", current_branch])
        run_command(["git", "branch", "-D", release_branch])
        print(f"Version rolled back to {current_version}")
        return
    
    # Create and push the release branch
    try:
        run_command(["git", "add", "pyproject.toml"])
        run_command(["git", "add", "poetry.lock"])
        run_command(["git", "commit", "-m", f"Bump version to {updated_version}"])
        run_command(["git", "push", "-u", "origin", release_branch])
        
        # Prepare PR creation
        print(f"\nRelease branch '{release_branch}' has been pushed.")
        print("\nTo create a Pull Request:")
        print(f"1. Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/pull/new/{release_branch}")
        print(f"2. Set the title: 'Release v{updated_version}'")
        print("3. Add release notes in the description")
        print("\nAfter the PR is merged, you can tag the release:")
        print(f"git checkout main && git pull && git tag v{updated_version} && git push origin --tags")
        
        # Optionally, open the PR URL directly
        pr_url = f"https://github.com/YOUR_USERNAME/YOUR_REPO/pull/new/{release_branch}"
        open_browser = input("\nOpen PR creation page in browser? [y/N] ")
        if open_browser.lower() == 'y':
            import webbrowser
            webbrowser.open(pr_url)
            
    except Exception as e:
        print(f"Error during git operations: {e}")
        print("You may need to manually clean up the branch and revert changes.")
        return

if __name__ == "__main__":
    main()