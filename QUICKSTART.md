# Quick Start Guide

## What You Can Do Now (On Your Laptop)

While you're waiting to set up the Raspberry Pi, you can:

### 1. Test the Code Structure
```bash
cd /Users/aryankhanna/Documents/GitHub/Dubhacks_25_T-Mobile
python3 -m py_compile *.py
```

### 2. Review and Customize
- Edit voice prompts in `voice_assistant.py`
- Customize AI personality in `ai_brain.py` (system_prompt)
- Adjust navigation settings in `navigation_system.py`

### 3. Get API Keys

**OpenAI (Recommended for simplicity)**
1. Go to: https://platform.openai.com/signup
2. Create account
3. Go to: https://platform.openai.com/api-keys
4. Create new secret key
5. Copy and save it (you won't see it again)

**Anthropic Claude (Alternative)**
1. Go to: https://www.anthropic.com/
2. Sign up for Claude API access
3. Get your API key from console

### 4. Create .env File
```bash
cp .env.example .env
nano .env  # or open in any text editor
```

Add your key:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxx
AI_SERVICE=openai
```

## Transferring to Raspberry Pi

### Option 1: SD Card (Simplest)

1. **Prepare SD Card with Pi OS**
   - Use Raspberry Pi Imager
   - Flash Raspberry Pi OS to SD card

2. **Copy Project Files**
   ```bash
   # After SD card is written, mount it
   # Navigate to /Volumes/boot (or your SD mount point)
   # Create a file to enable SSH:
   touch /Volumes/boot/ssh
   
   # Copy entire project to SD card home directory
   cp -r /Users/aryankhanna/Documents/GitHub/Dubhacks_25_T-Mobile /Volumes/rootfs/home/pi/
   ```

3. **Eject SD card and insert into Pi**

### Option 2: Network Transfer (After Pi is Running)

```bash
# Find your Pi's IP address (after connecting to same WiFi)
ping raspberrypi.local

# Transfer files via SCP
scp -r /Users/aryankhanna/Documents/GitHub/Dubhacks_25_T-Mobile pi@raspberrypi.local:~/
```

### Option 3: Git (Most Flexible)

```bash
# On your laptop - push to GitHub
cd /Users/aryankhanna/Documents/GitHub/Dubhacks_25_T-Mobile
git init
git add .
git commit -m "Initial navigation assistant"
git branch -M main
git remote add origin https://github.com/yourusername/nav-assistant.git
git push -u origin main

# On Raspberry Pi - clone
ssh pi@raspberrypi.local
cd ~
git clone https://github.com/yourusername/nav-assistant.git
cd nav-assistant
```

## On the Raspberry Pi

### 1. Run Installation (One Command!)
```bash
cd ~/Dubhacks_25_T-Mobile
chmod +x install.sh
./install.sh
```

This installs everything automatically. Grab a coffee ☕ (takes ~15 minutes).

### 2. Configure Bluetooth Headphones
```bash
bluetoothctl
power on
scan on
# Look for your device: XX:XX:XX:XX:XX:XX
pair XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
exit
```

### 3. Run!
```bash
python3 main.py
```

## Basic Commands to Test

Once running, try saying:

1. **"Where am I?"**
   - Tests: GPS, reverse geocoding, speech

2. **"What's ahead?"**
   - Tests: Camera, obstacle detection

3. **"Navigate to Starbucks"**
   - Tests: Geocoding, routing, AI

4. **"Help"**
   - Tests: AI conversation

5. **"Stop"**
   - Exits program

## Common Issues & Quick Fixes

### "No module named 'X'"
```bash
pip3 install -r requirements.txt
```

### "Permission denied" for audio
```bash
sudo usermod -a -G audio,video $USER
# Log out and back in
```

### GPS not working
```bash
# Check device
ls /dev/ttyUSB* /dev/ttyACM*

# Test
sudo cat /dev/ttyUSB0  # Replace with your device
# Should see NMEA data: $GPGGA,...
```

### Bluetooth won't connect
```bash
# Restart Bluetooth
sudo systemctl restart bluetooth
pulseaudio --kill
pulseaudio --start
```

### Camera not found
```bash
# For Pi Camera
sudo raspi-config
# Interface Options -> Camera -> Enable

# For USB Camera
ls /dev/video*
# Should show /dev/video0
```

## File Overview

**Core Files (what you'll edit most):**
- `main.py` - Main application loop
- `ai_brain.py` - AI responses and conversation
- `voice_assistant.py` - Voice commands and speech
- `.env` - Your API keys and settings

**Support Files:**
- `navigation_system.py` - GPS and routing
- `obstacle_detection.py` - Camera vision
- `bluetooth_handler.py` - Audio device management

**Setup Files:**
- `install.sh` - Automated installation
- `requirements.txt` - Python packages
- `test_system.py` - Test all components

**Documentation:**
- `README.md` - Full project documentation
- `SETUP_GUIDE.md` - Detailed setup instructions
- `QUICKSTART.md` - This file

## Development Workflow

### Making Changes

1. **Edit on laptop** (better IDE)
2. **Test syntax**:
   ```bash
   python3 -m py_compile yourfile.py
   ```
3. **Transfer to Pi**:
   ```bash
   scp yourfile.py pi@raspberrypi.local:~/Dubhacks_25_T-Mobile/
   ```
4. **Test on Pi**:
   ```bash
   ssh pi@raspberrypi.local
   cd ~/Dubhacks_25_T-Mobile
   python3 main.py
   ```

### Using Git (Better)

```bash
# Laptop: make changes, commit, push
git add .
git commit -m "Improved navigation instructions"
git push

# Pi: pull changes
git pull
python3 main.py
```

## Next Steps

1. ✅ Get API keys
2. ✅ Copy project to SD card
3. ✅ Install on Pi (run install.sh)
4. ✅ Pair Bluetooth headphones
5. ✅ Test with `python3 main.py`
6. 🚀 Start building and customizing!

## Resources

- **Pi Documentation**: https://www.raspberrypi.com/documentation/
- **Python Speech Recognition**: https://github.com/Uberi/speech_recognition
- **OpenCV**: https://docs.opencv.org/
- **OpenAI API**: https://platform.openai.com/docs

## Need Help?

1. Run test script: `python3 test_system.py`
2. Check logs: Look for error messages
3. See `SETUP_GUIDE.md` for detailed troubleshooting
4. See `README.md` for full documentation

---

**Pro Tip**: Start simple! Test each component individually before running the full system. Use `--no-camera` or `--no-bluetooth` flags to disable features while testing.

```bash
# Test without hardware
python3 main.py --no-camera --no-bluetooth
```

