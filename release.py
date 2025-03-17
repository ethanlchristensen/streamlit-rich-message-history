#!/usr/bin/env python
import subprocess
import sys
import os
import filecmp
import shutil
import tempfile

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
        
        if result.stdout.strip():
            print(f"Command output: {result.stdout.strip()}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Exit code: {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        if exit_on_error:
            sys.exit(1)
        return None

def get_current_version():
    """Get the current version from Poetry"""
    # For version query, keep using poetry command
    return run_command(["poetry", "version", "-s"])

def backup_file(file_path):
    """Create a temporary backup of a file"""
    if os.path.exists(file_path):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        shutil.copy2(file_path, temp_file.name)
        return temp_file.name
    return None

def check_files_changed(file_path, backup_path):
    """Check if a file has changed compared to its backup"""
    if not backup_path or not os.path.exists(file_path) or not os.path.exists(backup_path):
        return False
    return not filecmp.cmp(file_path, backup_path)

def main():
    # Backup original files
    pyproject_backup = backup_file("pyproject.toml")
    poetry_lock_backup = backup_file("poetry.lock")
    
    # Get the current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    # Get the new version
    new_version = input("New version (patch/minor/major or specific version): ")
    
    # Update the version
    run_command(["poetry", "version", new_version])
    updated_version = get_current_version()
    print(f"New version: {updated_version}")
    
    # Check if files actually changed
    pyproject_changed = check_files_changed("pyproject.toml", pyproject_backup)
    poetry_lock_changed = check_files_changed("poetry.lock", poetry_lock_backup)
    
    print(f"pyproject.toml changed: {pyproject_changed}")
    print(f"poetry.lock changed: {poetry_lock_changed}")
    
    if not pyproject_changed:
        print("Warning: pyproject.toml was not modified by version change!")
        print("This could mean the version change didn't actually update any files.")
    
    # Confirm release
    confirm = input("Create and push release commit? [y/N] ")
    if confirm.lower() != 'y':
        print("Release canceled. Rolling back version...")
        # Roll back to the original version
        if pyproject_backup:
            shutil.copy2(pyproject_backup, "pyproject.toml")
        if poetry_lock_backup:
            shutil.copy2(poetry_lock_backup, "poetry.lock")
        print(f"Version rolled back to {current_version}")
        return
    
    # Run checks
    print("Running checks...")
    try:
        print("Checking Format...")
        # Run tools directly without "poetry run" prefix
        run_command(["black", "--check", "."])
        run_command(["isort", "--check", "."])
        print("Linting...")
        run_command(["flake8"])
        print("Checking Types...")
        run_command(["mypy", "streamlit_rich_message_history"])
        print("Running Tests...")
        run_command(["pytest"])  # Directly use pytest instead of "poetry run test"
    except Exception as e:
        print(f"Checks failed: {e}")
        print("Rolling back version...")
        # Roll back to the original version
        if pyproject_backup:
            shutil.copy2(pyproject_backup, "pyproject.toml")
        if poetry_lock_backup:
            shutil.copy2(poetry_lock_backup, "poetry.lock")
        print(f"Version rolled back to {current_version}")
        return
    
    # Verify git status before committing
    git_status = run_command(["git", "status", "--porcelain"])
    if not git_status:
        print("No changes detected by git! Manually updating files...")
        
        # Force git to recognize changes by making a small modification and then fixing it
        if pyproject_changed:
            with open("pyproject.toml", "a") as f:
                f.write("# Version bump\n")
            run_command(["git", "add", "pyproject.toml"])
            
            # Remove the temporary line
            with open("pyproject.toml", "r") as f:
                content = f.read().rstrip("# Version bump\n")
            with open("pyproject.toml", "w") as f:
                f.write(content)
            run_command(["git", "add", "pyproject.toml"])
        
        if poetry_lock_changed:
            run_command(["git", "add", "poetry.lock"])
        
        # Check again
        git_status = run_command(["git", "status", "--porcelain"])
        if not git_status:
            print("Still no changes detected. Manual intervention required.")
            return
    
    print(f"Files to be committed:\n{git_status}")
    
    # Make sure release.py is not staged if it was modified
    run_command(["git", "restore", "--staged", "release.py"], exit_on_error=False)
    
    # Create and push the release
    try:
        # Make sure the files are added to the staging area
        if pyproject_changed:
            run_command(["git", "add", "pyproject.toml"])
        if poetry_lock_changed:
            run_command(["git", "add", "poetry.lock"])
        run_command(["git", "add", "release.py"])
        
        # Get git user info for the commit
        try:
            git_user = run_command(["git", "config", "user.name"], exit_on_error=False)
            git_email = run_command(["git", "config", "user.email"], exit_on_error=False)
            
            if not git_user or not git_email:
                print("Git user information not configured.")
                print("Setting temporary git identity for this commit...")
                run_command(["git", "config", "user.name", "Release Script"])
                run_command(["git", "config", "user.email", "release@example.com"])
        except Exception as e:
            print(f"Warning when checking git user info: {e}")
        
        # Show what's staged for commit
        print("Files staged for commit:")
        run_command(["git", "diff", "--cached", "--name-only"])
        
        # Try the commit with detailed output
        commit_result = run_command(["git", "commit", "-m", f"Bump version to {updated_version}"])
        print(f"Commit created: {commit_result}")
        
        tag_result = run_command(["git", "tag", f"v{updated_version}"])
        print(f"Tag created: {tag_result}")
        
        push_result = run_command(["git", "push", "origin", "main"])
        print(f"Pushed to main: {push_result}")
        
        tag_push_result = run_command(["git", "push", "origin", "--tags"])
        print(f"Pushed tags: {tag_push_result}")
        
        print(f"Release v{updated_version} created and pushed. GitHub Actions will handle the rest.")
    except Exception as e:
        print(f"Error during git operations: {e}")
        print("You may need to manually roll back the version and any git changes.")
        return
    finally:
        # Clean up backup files
        if pyproject_backup and os.path.exists(pyproject_backup):
            os.unlink(pyproject_backup)
        if poetry_lock_backup and os.path.exists(poetry_lock_backup):
            os.unlink(poetry_lock_backup)

if __name__ == "__main__":
    main()