import os
import subprocess


def run_command(command):
    """Runs a shell command and returns the output."""
    try:
        result = subprocess.run(command, shell=True, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return None


def find_main_file(start_dir):
    """Searches for the main.py file starting from a directory."""
    print("Searching for main.py...")
    for root, dirs, files in os.walk(start_dir):
        if "main.py" in files:
            main_path = os.path.join(root, "main.py")
            print(f"Found main.py at: {main_path}")
            return main_path
    print("main.py not found.")
    return None


def install_requirements(venv_path):
    """Installs Python dependencies from requirements.txt."""
    print("Installing dependencies...")
    requirements_file = os.path.join(os.getcwd(), "requirements.txt")
    if not os.path.exists(requirements_file):
        print("requirements.txt not found. Please ensure it exists in the current directory.")
        return
    run_command(f"{venv_path}/bin/pip install -r {requirements_file}")


def launch_uvicorn(main_path, venv_path):
    """Launches Uvicorn with the specified main.py file."""
    print("Launching Uvicorn...")
    dir_path, main_file = os.path.split(main_path)
    module_name = main_file.replace(".py", "")
    os.chdir(dir_path)
    run_command(f"{venv_path}/bin/uvicorn {module_name}:app --host 0.0.0.0 --port 8000 --reload")


def main():
    project_dir = "/home/backend"  # Default backend directory
    venv_path = os.path.join(project_dir, "venv")

    # Step 1: Verify virtual environment exists
    if not os.path.exists(venv_path):
        print("Virtual environment not found. Creating one...")
        run_command(f"python3 -m venv {venv_path}")

    # Step 2: Install requirements
    install_requirements(venv_path)

    # Step 3: Find main.py
    main_file_path = find_main_file(project_dir)
    if not main_file_path:
        print("main.py is missing. Please create the file and try again.")
        return

    # Step 4: Launch Uvicorn
    launch_uvicorn(main_file_path, venv_path)


if __name__ == "__main__":
    main()
