# Setup Guide for Raspberry Pi Navigation Assistant

## Step-by-Step Setup on Your Laptop

### 1. Prepare the SD Card

If you need to install Pi OS on your SD card:

1. Download **Raspberry Pi Imager**: https://www.raspberrypi.com/software/
2. Insert SD card into your laptop
3. Open Raspberry Pi Imager
4. Choose:
   - OS: Raspberry Pi OS (64-bit recommended)
   - Storage: Your SD card
5. Click the gear icon ⚙️ for advanced options:
   - Set hostname: `raspberrypi`
   - Enable SSH
   - Set username/password: `pi` / your_password
   - Configure WiFi (optional)
6. Click "Write" and wait

### 2. Transfer Project to SD Card

**Option A: Direct Copy (Easiest)**

1. After Pi OS is written, remove and reinsert the SD card
2. Open the SD card in your file explorer
3. Navigate to the `/home/pi/` directory (create if doesn't exist)
4. Copy the entire `Dubhacks_25_T-Mobile` folder to `/home/pi/`

**Option B: Set up Git**

1. Push your code to GitHub:
```bash
cd /Users/aryankhanna/Documents/GitHub/Dubhacks_25_T-Mobile
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

2. You'll clone this on the Pi later

### 3. Hardware Connections

Before powering on the Raspberry Pi:

1. **Insert SD Card** into Raspberry Pi
2. **Connect GPS Module** to USB port
3. **Connect Microphone** (USB microphone or audio adapter)
4. **Connect Camera**:
   - Pi Camera: Insert ribbon cable into camera port
   - USB Camera: Connect to USB port
5. **Power** on the Raspberry Pi

## Step-by-Step Setup on Raspberry Pi

### 4. Initial Pi Configuration

Connect to your Pi via SSH or directly with keyboard/monitor:

```bash
# From your laptop (if using SSH)
ssh pi@raspberrypi.local
# Enter your password
```

Update the system:
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo reboot
```

### 5. Get the Project Files

**If you copied to SD card:**
```bash
cd ~/Dubhacks_25_T-Mobile
```

**If using Git:**
```bash
cd ~
git clone <your-github-repo-url>
cd Dubhacks_25_T-Mobile
```

### 6. Run Installation

```bash
chmod +x install.sh
./install.sh
```

This will install all dependencies (takes 10-20 minutes).

### 7. Configure API Keys

```bash
nano .env
```

Add your API key:
```
OPENAI_API_KEY=sk-your-key-here
AI_SERVICE=openai
```

Save with `Ctrl+X`, `Y`, `Enter`

### 8. Hardware Configuration

#### Configure Camera

For **Pi Camera**:
```bash
sudo raspi-config
# Navigate to: Interface Options -> Camera -> Enable
```

For **USB Camera**, no configuration needed.

Test camera:
```bash
libcamera-hello  # For Pi Camera
# OR
cheese  # For USB Camera (install with: sudo apt install cheese)
```

#### Configure GPS

```bash
# Find your GPS device
ls /dev/ttyUSB* /dev/ttyACM*
# Usually /dev/ttyUSB0 or /dev/ttyACM0

# Test GPS
sudo cat /dev/ttyUSB0  # Replace with your device
# You should see NMEA data streaming

# Configure gpsd
sudo nano /etc/default/gpsd
```

Edit to match:
```
START_DAEMON="true"
GPSD_OPTIONS="-n"
DEVICES="/dev/ttyUSB0"  # Change to your device
USBAUTO="true"
```

Restart GPS:
```bash
sudo systemctl restart gpsd
cgps -s  # Test GPS (wait for fix)
```

#### Configure Bluetooth Audio

```bash
# Start Bluetooth
sudo systemctl start bluetooth

# Pair your headphones
bluetoothctl
```

In bluetoothctl:
```
power on
agent on
default-agent
scan on
# Wait for your device to appear as XX:XX:XX:XX:XX:XX

pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
exit
```

Test audio:
```bash
speaker-test -t wav -c 2
```

### 9. Test the System

Run the test script:
```bash
python3 test_system.py
```

Fix any issues reported.

### 10. Run the Application

```bash
python3 main.py
```

You should hear: "Hello! I am your navigation assistant..."

Test commands:
- "Where am I?"
- "What's ahead?"
- "Help"
- "Stop"

## Making it Portable

### 1. Power Setup

Use a USB power bank:
- **Minimum**: 10,000mAh, 2.4A output
- **Recommended**: 20,000mAh, 3A output
- Look for "always on" feature (doesn't turn off with low draw)

### 2. Mounting

Consider these mounting options:
- Chest harness with pockets
- Belt clip case
- Backpack mount
- Custom 3D-printed case

### 3. Auto-Start on Boot

If you set up the systemd service during installation:
```bash
sudo systemctl enable nav-assistant
sudo reboot
```

The assistant will start automatically when powered on.

### 4. Portable Assembly

1. **Case/Enclosure**: Use a case with access to ports
2. **Camera position**: Forward-facing, around chest height
3. **Microphone**: Near mouth, away from speakers
4. **GPS antenna**: Top of case, clear sky view
5. **Bluetooth range**: Keep within 10m of headphones

## Tips for Development

### Editing Code on Laptop

1. Edit files on your laptop in this folder
2. Test what you can locally (AI, navigation logic)
3. Transfer to Pi:

```bash
# From your laptop
scp main.py pi@raspberrypi.local:~/Dubhacks_25_T-Mobile/
# Or commit and pull via Git
```

### Using Git Workflow

```bash
# On laptop - make changes
git add .
git commit -m "Updated navigation logic"
git push

# On Pi - get updates
cd ~/Dubhacks_25_T-Mobile
git pull
```

### Remote Development

Use VS Code Remote SSH:
1. Install "Remote - SSH" extension in VS Code
2. Connect to Pi: `ssh pi@raspberrypi.local`
3. Edit files directly on Pi

## Troubleshooting

### Can't Connect to Pi
```bash
# Find Pi on network
ping raspberrypi.local
# Or scan network
nmap -sn 192.168.1.0/24
```

### No Internet on Pi
```bash
# Check WiFi
iwconfig
# Reconnect
sudo raspi-config
# Interface Options -> Wi-Fi
```

### Permission Errors
```bash
# Add user to necessary groups
sudo usermod -a -G audio,video,bluetooth,dialout $USER
# Log out and back in
```

### GPS Not Getting Fix
- Ensure GPS has clear view of sky
- Wait 2-5 minutes for initial fix
- Check antenna is connected properly

### Low Volume/Audio Issues
```bash
# Adjust volume
alsamixer
# Select Bluetooth device and increase volume
```

## Next Steps

Once everything is working:

1. **Optimize for battery**: Disable unused services
2. **Add physical buttons**: Emergency stop, repeat instruction
3. **Improve accuracy**: Better GPS antenna, differential GPS
4. **Add sensors**: Ultrasonic distance, IMU for orientation
5. **Offline mode**: Download maps, use local LLM

## Support

For issues specific to:
- **Raspberry Pi**: https://forums.raspberrypi.com/
- **GPS**: Check your GPS module documentation
- **Bluetooth**: https://wiki.archlinux.org/title/bluetooth

For project issues: Open an issue on GitHub

