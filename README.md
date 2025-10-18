# Navigation Assistant for the Blind

An AI-powered navigation system designed for blind users, running on Raspberry Pi with Bluetooth audio, GPS navigation, and camera-based obstacle detection.

## Features

- 🎤 **Voice Control**: Hands-free interaction using speech recognition
- 🔊 **Text-to-Speech**: Clear audio feedback via Bluetooth headphones/speakers
- 🤖 **AI Assistant**: Conversational AI powered by OpenAI GPT or Anthropic Claude
- 🗺️ **GPS Navigation**: Real-time location tracking and turn-by-turn directions
- 📷 **Obstacle Detection**: Camera-based detection of obstacles and scene description
- 📡 **Bluetooth Audio**: Wireless audio output support

## Hardware Requirements

- **Raspberry Pi 4** (recommended) or Raspberry Pi 3B+
- **Raspberry Pi Camera Module** or USB webcam
- **USB GPS Module** (e.g., VK-172, BU-353S4)
- **Bluetooth Headphones** or Bluetooth speaker
- **USB Microphone** or USB audio adapter with microphone
- **Power bank** (for portable use)
- **SD Card** (16GB minimum, 32GB recommended)

## Software Requirements

- **Raspberry Pi OS** (Bullseye or newer)
- **Python 3.7+**
- Internet connection (for initial setup and AI features)

## Installation

### On Your Laptop (Development)

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Dubhacks_25_T-Mobile
```

2. Install dependencies (for testing):
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### On Raspberry Pi

1. **Transfer files to Raspberry Pi:**

   Option A - Using SD Card:
   ```bash
   # On your laptop, copy entire project folder to SD card
   # Then insert SD card into Raspberry Pi
   ```

   Option B - Using SSH:
   ```bash
   # From your laptop
   scp -r /Users/aryankhanna/Documents/GitHub/Dubhacks_25_T-Mobile pi@raspberrypi.local:~/
   ```

   Option C - Using Git:
   ```bash
   # On Raspberry Pi
   cd ~
   git clone <your-repo-url>
   cd Dubhacks_25_T-Mobile
   ```

2. **Run installation script:**
```bash
cd ~/Dubhacks_25_T-Mobile
chmod +x install.sh
./install.sh
```

3. **Configure API Keys:**
```bash
nano .env
# Add your OpenAI or Anthropic API key
```

4. **Pair Bluetooth Audio Device:**
```bash
bluetoothctl
# In bluetoothctl:
scan on
# Wait for your device to appear
pair [DEVICE_MAC_ADDRESS]
trust [DEVICE_MAC_ADDRESS]
connect [DEVICE_MAC_ADDRESS]
exit
```

## Usage

### Basic Usage

Start the navigation assistant:
```bash
python3 main.py
```

### Command Examples

Once running, you can say:

- **"Where am I?"** - Get current location
- **"Navigate to Starbucks"** - Start navigation to a destination
- **"What's ahead?"** - Describe obstacles and scene
- **"Find the nearest bus stop"** - Search for nearby places
- **"Continue navigation"** - Get next turn-by-turn instruction
- **"Help"** - Learn what the assistant can do
- **"Stop"** or **"Goodbye"** - Exit the application

### Run Options

```bash
# Run without Bluetooth (use built-in audio)
python3 main.py --no-bluetooth

# Run without camera (disable obstacle detection)
python3 main.py --no-camera

# Run with both disabled
python3 main.py --no-bluetooth --no-camera
```

### Auto-Start at Boot

If you configured the systemd service during installation:
```bash
sudo systemctl start nav-assistant    # Start now
sudo systemctl stop nav-assistant     # Stop
sudo systemctl restart nav-assistant  # Restart
sudo systemctl status nav-assistant   # Check status
```

## Project Structure

```
Dubhacks_25_T-Mobile/
├── main.py                 # Main application entry point
├── voice_assistant.py      # Speech recognition and TTS
├── ai_brain.py            # AI conversation handler
├── navigation_system.py   # GPS and routing logic
├── obstacle_detection.py  # Camera-based obstacle detection
├── bluetooth_handler.py   # Bluetooth device management
├── requirements.txt       # Python dependencies
├── install.sh            # Raspberry Pi installation script
├── .env.example          # Environment variables template
└── README.md             # This file
```

## API Keys

This project supports two AI providers:

### OpenAI (GPT)
1. Sign up at https://platform.openai.com/
2. Create an API key
3. Add to `.env`: `OPENAI_API_KEY=your_key_here`
4. Set `AI_SERVICE=openai` in `.env`

### Anthropic (Claude)
1. Sign up at https://www.anthropic.com/
2. Create an API key
3. Add to `.env`: `ANTHROPIC_API_KEY=your_key_here`
4. Set `AI_SERVICE=anthropic` in `.env`

## Troubleshooting

### No Audio Output
- Check Bluetooth connection: `bluetoothctl devices Connected`
- Test speaker: `speaker-test -t wav -c 2`
- Restart PulseAudio: `pulseaudio --kill && pulseaudio --start`

### Microphone Not Working
- List audio devices: `arecord -l`
- Test recording: `arecord -d 5 test.wav && aplay test.wav`
- Check permissions: `sudo usermod -a -G audio $USER`

### GPS Not Working
- Check GPS status: `cgps -s`
- View raw GPS data: `cat /dev/ttyUSB0` or `cat /dev/ttyACM0`
- Restart GPS daemon: `sudo systemctl restart gpsd`

### Camera Not Working
- Test Pi Camera: `libcamera-hello --list-cameras`
- Test USB camera: `ls /dev/video*`
- Check camera permissions: `sudo usermod -a -G video $USER`

### AI Not Responding
- Check internet connection: `ping google.com`
- Verify API key in `.env` file
- Check API quota/balance on provider website

## Development

### Testing Individual Components

Test Bluetooth:
```bash
python3 bluetooth_handler.py
```

Test Voice Assistant:
```bash
python3 voice_assistant.py
```

Test Navigation:
```bash
python3 navigation_system.py
```

Test Obstacle Detection:
```bash
python3 obstacle_detection.py
```

Test AI Brain:
```bash
python3 ai_brain.py
```

## Future Enhancements

- [ ] Advanced object detection using YOLO or similar models
- [ ] Offline AI using local LLMs (Llama, Mistral)
- [ ] Multi-language support
- [ ] Indoor navigation using Bluetooth beacons
- [ ] Emergency SOS feature
- [ ] Route history and favorites
- [ ] Integration with public transit APIs
- [ ] Haptic feedback support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for any purpose.

## Acknowledgments

Built for DubHacks 2025 with ❤️ for the visually impaired community.

## Support

For issues or questions, please open an issue on GitHub or contact the development team.

---

**Safety Notice**: This navigation assistant is designed to aid navigation but should not replace traditional mobility aids like white canes or guide dogs. Always prioritize safety and use multiple navigation tools.

