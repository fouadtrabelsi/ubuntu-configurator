#!/bin/bash

# Script d'installation automatique de l'application de configuration Ubuntu Server 22.04
# Auteur: ChatGPT
# Date: $(date +%Y-%m-%d)

set -e  # Stopper l'exécution en cas d'erreur

# Variables
deb_packages=("python3" "python3-venv" "python3-pip" "git" "nginx" "redis" "ufw" "curl" "wget" "nodejs" "npm")

echo "📌 Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

echo "📌 Installation des dépendances requises..."
sudo apt install -y ${deb_packages[@]}

# Installation de Docker
if ! command -v docker &> /dev/null; then
    echo "📌 Installation de Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo systemctl enable --now docker
fi

# Création du répertoire de l'application
APP_DIR="/opt/ubuntu-configurator"
sudo mkdir -p $APP_DIR
cd $APP_DIR

echo "📌 Clonage du projet..."
sudo git clone https://github.com/votre-repo/ubuntu-configurator.git .

# Configuration du backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Configuration du frontend
cd ../frontend
npm install
npm run build

# Configuration des services
sudo cp $APP_DIR/deployment/ubuntu-configurator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ubuntu-configurator
sudo systemctl start ubuntu-configurator

echo "✅ Installation terminée ! Accédez à l'interface sur http://192.168.1.1:8080"
