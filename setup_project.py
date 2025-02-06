import os
import subprocess

def run_command(command, cwd=None):
    """Execute a shell command and return the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\n{e.stderr}")
        raise

# 1. Check for Python installation and install required packages
def setup_python_env():
    print("\n[1/6] Setting up Python environment...")
    try:
        run_command("sudo apt update && sudo apt install -y python3 python3-pip python3-venv")
    except Exception as e:
        print("Python environment setup failed.")
        raise e

# 2. Setup virtual environment and install dependencies
def setup_virtual_env(project_dir):
    print("\n[2/6] Setting up virtual environment and installing dependencies...")
    venv_dir = os.path.join(project_dir, "venv")
    if not os.path.exists(venv_dir):
        run_command(f"python3 -m venv {venv_dir}")
    run_command(f"{venv_dir}/bin/pip install --upgrade pip")
    requirements_path = os.path.join(project_dir, "requirements.txt")
    if not os.path.exists(requirements_path):
        print("requirements.txt not found. Creating a default one.")
        with open(requirements_path, "w") as f:
            f.write("fastapi\nuvicorn[standard]\nsqlalchemy\npasslib[bcrypt]\n")
    run_command(f"{venv_dir}/bin/pip install -r {requirements_path}")

# 3. Configure systemd service for FastAPI backend
def configure_backend_service(project_dir):
    print("\n[3/6] Configuring backend as a systemd service...")
    service_content = f"""[Unit]
Description=FastAPI Backend Service
After=network.target

[Service]
User={os.getlogin()}
WorkingDirectory={project_dir}
ExecStart={project_dir}/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
"""
    service_path = f"/etc/systemd/system/fastapi-backend.service"
    with open("fastapi-backend.service", "w") as f:
        f.write(service_content)
    run_command(f"sudo mv fastapi-backend.service {service_path}")
    run_command("sudo systemctl daemon-reload && sudo systemctl enable fastapi-backend && sudo systemctl start fastapi-backend")

# 4. Install Node.js and set up Vue.js for the frontend
def setup_frontend(project_dir):
    print("\n[4/6] Setting up Vue.js frontend...")
    run_command("curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -")
    run_command("sudo apt install -y nodejs")

    frontend_dir = os.path.join(project_dir, "frontend")
    if not os.path.exists(frontend_dir):
        run_command("npx create-vue@latest frontend", cwd=project_dir)
    run_command("npm install", cwd=frontend_dir)
    run_command("npm run build", cwd=frontend_dir)

# 5. Configure Nginx for serving the frontend and reverse-proxying the backend
def configure_nginx(project_dir):
    print("\n[5/6] Configuring Nginx to serve frontend and reverse-proxy backend...")
    nginx_config = f"""server {{
    listen 80;

    location / {{
        root {os.path.join(project_dir, 'frontend', 'dist')};
        index index.html;
    }}

    location /api {{
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }}
}}
"""
    nginx_path = "/etc/nginx/sites-available/fastapi-frontend"
    with open("fastapi-frontend", "w") as f:
        f.write(nginx_config)
    run_command(f"sudo mv fastapi-frontend {nginx_path}")
    run_command(f"sudo ln -sf {nginx_path} /etc/nginx/sites-enabled/")
    run_command("sudo nginx -t && sudo systemctl restart nginx")

# 6. Summary and final instructions
def show_completion_message():
    print("\n[6/6] All steps completed successfully!")
    print("Your backend is running on http://<server-ip>:8000")
    print("Your frontend is accessible at http://<server-ip>")

# Main execution flow
def main():
    project_dir = os.getcwd()  # Use the current directory for the project

    try:
        setup_python_env()
        setup_virtual_env(project_dir)
        configure_backend_service(project_dir)
        setup_frontend(project_dir)
        configure_nginx(project_dir)
        show_completion_message()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
