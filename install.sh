#!/bin/bash
# Installation script for Raspberry Pi Navigation Assistant
# Run this on your Raspberry Pi with Pi OS

echo "====================================="
echo "Navigation Assistant for the Blind"
echo "Installation Script for Raspberry Pi"
echo "====================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    echo "Continue anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-setuptools \
    bluetooth \
    bluez \
    bluez-tools \
    pulseaudio \
    pulseaudio-module-bluetooth \
    libasound2-dev \
    portaudio19-dev \
    libportaudio2 \
    libportaudiocpp0 \
    ffmpeg \
    espeak \
    mpg123 \
    gpsd \
    gpsd-clients \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev

# Enable Bluetooth
echo "Configuring Bluetooth..."
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Configure PulseAudio for Bluetooth
echo "Configuring audio for Bluetooth..."
sudo usermod -a -G bluetooth $USER

# Create PulseAudio Bluetooth configuration
if ! grep -q "load-module module-bluetooth-policy" /etc/pulse/default.pa; then
    echo "load-module module-bluetooth-policy" | sudo tee -a /etc/pulse/default.pa
    echo "load-module module-bluetooth-discover" | sudo tee -a /etc/pulse/default.pa
fi

# Enable and configure GPS
echo "Configuring GPS..."
sudo systemctl enable gpsd
sudo systemctl start gpsd

# Install Python packages
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit the .env file and add your API keys:"
    echo "  nano .env"
    echo ""
fi

# Make Python scripts executable
echo "Setting permissions..."
chmod +x main.py
chmod +x bluetooth_handler.py
chmod +x voice_assistant.py
chmod +x navigation_system.py
chmod +x obstacle_detection.py
chmod +x ai_brain.py

# Create systemd service (optional - run at boot)
echo ""
echo "Would you like to create a systemd service to run the assistant at boot? (y/n)"
read -r create_service

if [[ "$create_service" =~ ^[Yy]$ ]]; then
    SERVICE_FILE="/etc/systemd/system/nav-assistant.service"
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Navigation Assistant for the Blind
After=network.target bluetooth.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable nav-assistant.service
    
    echo "Service created. Start it with: sudo systemctl start nav-assistant"
fi

# Test audio output
echo ""
echo "Testing audio output..."
espeak "Navigation assistant installation complete" 2>/dev/null || echo "Audio test skipped"

echo ""
echo "====================================="
echo "Installation Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys: nano .env"
echo "2. Pair Bluetooth headphones/speaker:"
echo "   - Run: bluetoothctl"
echo "   - Type: scan on"
echo "   - Type: pair [DEVICE_MAC_ADDRESS]"
echo "   - Type: connect [DEVICE_MAC_ADDRESS]"
echo "3. Run the assistant: python3 main.py"
echo ""
echo "Optional flags:"
echo "  --no-bluetooth   : Run without Bluetooth audio"
echo "  --no-camera      : Run without obstacle detection"
echo ""
echo "For automatic startup at boot:"
echo "  sudo systemctl start nav-assistant"
echo ""

