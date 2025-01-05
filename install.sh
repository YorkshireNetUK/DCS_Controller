#!/bin/bash

# Run as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root. Use 'sudo ./install.sh'"
   exit 1
fi

# Variables
REPO_URL="https://github.com/YorkshireNetUK/DCS_Controller.git"
INSTALL_DIR="/opt/yorkshiresvx"
SCRIPT_DIR="/home/pi"
HTML_DIR="/var/www/html"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_FILE="/etc/systemd/system/tone_controller.service"

# Update system packages
echo "Updating system packages..."
apt update -y && apt upgrade -y

# Install required packages
echo "Installing required packages..."
apt install -y python3 python3-pip python3-venv apache2 libapache2-mod-php portaudio19-dev alsa-utils git

# Clone the repository
if [[ ! -d $INSTALL_DIR ]]; then
    echo "Cloning repository..."
    git clone $REPO_URL $INSTALL_DIR
else
    echo "Repository already cloned. Pulling latest changes..."
    cd $INSTALL_DIR && git pull
fi

# Set up the virtual environment
echo "Setting up Python virtual environment..."
if [[ ! -d $VENV_DIR ]]; then
    python3 -m venv $VENV_DIR
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Install Python packages in the virtual environment
echo "Installing Python packages in the virtual environment..."
source $VENV_DIR/bin/activate
pip install numpy scipy pyaudio RPi.GPIO
deactivate

# Move configuration files and web files
echo "Setting up configuration and web files..."
cp $INSTALL_DIR/tones_config.txt $SCRIPT_DIR/
cp $INSTALL_DIR/index.php $HTML_DIR/
cp $INSTALL_DIR/tone_status.json $HTML_DIR/
chmod 777 $HTML_DIR/tone_status.json
chown www-data:www-data $HTML_DIR/tone_status.json

# Set up the systemd service
echo "Setting up systemd service..."
cp $INSTALL_DIR/tone_controller.service $SERVICE_FILE
systemctl daemon-reload
systemctl enable tone_controller.service
systemctl start tone_controller.service

# Delete index.html
rm /var/www/html/index.html
# Restart Apache
echo "Restarting Apache server..."
systemctl restart apache2

# Finish
echo "Installation completed! Open http://<your-pi-ip> in your browser to view the monitor."
