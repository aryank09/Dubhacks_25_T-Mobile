# Text Maps - Text-Based Navigation System

A command-line navigation tool that works like Google Maps but provides directions through text instead of showing maps. Get turn-by-turn walking directions for any route!

## Features

- 🚶 **Walking-focused** - Optimized for pedestrian navigation (default mode)
- 🧭 **Live Navigation** - Real-time turn-by-turn directions based on your current location
- 🗺️ **Turn-by-turn directions** - Clear, step-by-step navigation instructions
- 📍 **Address geocoding** - Enter any address or place name
- 📍 **Current location tracking** - Automatically detects and updates your position
- 📊 **Route summary** - Total distance and estimated travel time
- 🎯 **Smart step detection** - Automatically advances to the next instruction as you move
- 🧭 **Direction indicators** - Visual arrows and icons for each turn
- 🌍 **Global coverage** - Works anywhere in the world using OpenStreetMap data
- 🚴 **Multiple modes** - Supports walking (default), driving, and cycling

## Installation

1. Make sure you have Python 3.7+ installed
2. Install dependencies:

# Installation notes:
#for raspberry pi: because its externally manager and debian you need virtual env for python
# For macOS: brew install portaudio (required for pyaudio)
# Then: pip install -r requirements.txt
# Installation notes:
#for raspberry pi: because its externally manager and debian you need virtual env for python
# For macOS: brew install portaudio (required for pyaudio)
# Then: pip install -r requirements.txt
#ON LINUX:
#ollama linux: curl -fsSL https://ollama.com/install.sh | sh
#ollama pull gemma:2b
#in the env add pip3 install ollama
#brew install eSpeak (not needed for linux)
#sudo apt-get update
#sudo apt-get install flac espeak-ng espeak 

```bash
pip install -r requirements.txt
```

## Usage
# GPS System for Computer-to-Raspberry Pi Navigation

This system allows a computer to send GPS coordinates to a Raspberry Pi running the voice navigation system.

## System Architecture

```
Computer (GPS Sender) → Raspberry Pi (GPS Server) → Navigation System
```

1. **Computer**: Runs `gps_sender.py` to send GPS coordinates
2. **Raspberry Pi**: Runs `gps_server.py` to receive coordinates
3. **Raspberry Pi**: Runs `main.py --server-gps` for navigation

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Helper

Run the setup script to get guided instructions:

```bash
python setup_gps_system.py
```

### 3. Manual Setup

#### On Raspberry Pi (GPS Server):

Terminal 1 - Start GPS server:
```bash
python gps_server.py
```
**Note**: The server will display its IP address when it starts (e.g., `http://192.168.1.100:5000`)

Terminal 2 - Start navigation with server GPS:
```bash
# Use default server
python main.py --server-gps

# Use custom server URL
python main.py --server-gps --server-url http://192.168.1.100:5000
```

#### On Computer (GPS Sender):

```bash
# Send GPS to Raspberry Pi server
python gps_sender.py http://RASPBERRY_PI_IP:5000

# Example:
python gps_sender.py http://192.168.1.100:5000
```

**Important**: Replace `RASPBERRY_PI_IP` with the actual IP address shown when you start the GPS server.

## Files Overview

- **`gps_sender.py`**: Computer script that sends GPS coordinates to server
- **`gps_server.py`**: Raspberry Pi server that receives and stores GPS coordinates
- **`main.py`**: Modified navigation system with server GPS support
- **`text_maps.py`**: Updated with server GPS functionality
- **`setup_gps_system.py`**: Helper script for system setup

## Usage Examples

### Basic Usage

1. **Start GPS server on Raspberry Pi:**
   ```bash
   python gps_server.py
   ```
   Note the IP address displayed (e.g., `http://192.168.1.100:5000`)

2. **Start GPS sender on computer:**
   ```bash
   python gps_sender.py http://192.168.1.100:5000
   ```
   (Replace with the actual Raspberry Pi IP)

3. **Start navigation on Raspberry Pi:**
   ```bash
   python main.py --server-gps "123 Main Street, City"
   ```

### Advanced Usage

#### Custom Server URL
If the Raspberry Pi has a different IP address:

```bash
# On computer (use the IP shown by the server)
python gps_sender.py http://192.168.1.100:5000

# On Raspberry Pi
python main.py --server-gps --server-url http://192.168.1.100:5000 "123 Main Street"
```

#### Network Discovery
If you don't know the Raspberry Pi's IP address:

1. Run `python gps_server.py` on Raspberry Pi - it will show the IP
2. Or run `python setup_gps_system.py` on each device to see IP addresses

#### Network Setup
For different network configurations, update the server URL in both scripts.

## API Endpoints

The GPS server provides these endpoints:

- `POST /location` - Receive GPS coordinates
- `GET /location` - Get current GPS coordinates  
- `GET /status` - Get server status

## Troubleshooting

### Common Issues

1. **"Could not connect to server"**
   - Make sure the GPS server is running on Raspberry Pi
   - Check the server URL is correct
   - Ensure both devices are on the same network

2. **"No location available"**
   - Make sure the computer GPS sender is running
   - Check that location permissions are granted
   - Verify the computer can reach the server

3. **"Location is too old"**
   - The GPS coordinates are stale (>30 seconds)
   - Restart the GPS sender on computer
   - Check network connectivity

### Testing Connection

Test if the server is working:

```bash
# Check server status
curl http://localhost:5000/status

# Get current location
curl http://localhost:5000/location
```

## System Requirements

- **Computer**: Python 3.7+, GPS capability, network access
- **Raspberry Pi**: Python 3.7+, network access, audio output
- **Network**: Both devices on same network or accessible IPs

## Security Notes

- The GPS server accepts connections from any IP (0.0.0.0)
- For production use, consider adding authentication
- GPS coordinates are transmitted in plain text
- Use HTTPS for production deployments


**How it works:**
1. 📍 Detects your current location automatically
2. 🗺️ Calculates the route to your destination
3. 🧭 Shows you the current instruction based on where you are
4. ⏭️ Automatically advances to the next instruction as you move
5. 📏 Displays distance to next turn and to destination
6. 🎯 Alerts you when you've arrived (within 20 meters)

**Live Navigation Display:**
```
📍 Current Position: 47.6094, -122.3414
📏 Distance to destination: 1.5 km
📏 Distance to next turn: 150 meters

🧭 CURRENT INSTRUCTION:
2. → Turn right onto Virginia Street (389 meters)

⏭️  NEXT:
3. ← Turn left onto 4th Avenue (854 meters)
```

Press `Ctrl+C` to stop navigation at any time.

**Note:** Location updates every 5 seconds by default (adjustable with `--interval`).

### GPS Location Accuracy

The program now uses **browser-based GPS** for precise location tracking:

1. **First run**: Opens your browser to request GPS permission
2. **High accuracy**: Uses HTML5 Geolocation API (same as Google Maps)
3. **Automatic fallback**: If GPS unavailable, uses IP-based location (city-level accuracy)

When you start live navigation, a browser window will open asking for location permission. Allow it for precise GPS tracking!

## Example Output

```
============================================================
🗺️  TEXT MAPS - Text-Based Navigation System
============================================================

============================================================
Getting directions from:
  📍 Seattle, WA
to:
  📍 Portland, OR
============================================================

🔍 Finding locations...
✓ Start: 47.6062, -122.3321
✓ End: 45.5152, -122.6784

🗺️  Calculating route...

============================================================
📊 ROUTE SUMMARY
============================================================
Total Distance: 278.5 km
Estimated Time: 2 hours 54 min
============================================================

============================================================
🧭 TURN-BY-TURN DIRECTIONS
============================================================

1. 🚗 Start by heading south on 5th Avenue (150 meters)

2. → Turn right onto James Street (800 meters)

3. ⤴ Merge onto I-5 South (275.3 km)

4. → Turn right onto Broadway Street (1.2 km)

5. 🏁 Arrive at your destination (0 meters)

============================================================
✅ You have arrived at your destination!
============================================================
```

## How It Works

1. **Geocoding**: Converts your address/place name to GPS coordinates using OpenStreetMap's Nominatim service
2. **Routing**: Calculates the optimal route using OSRM (Open Source Routing Machine)
3. **Formatting**: Presents the route as clear, numbered turn-by-turn instructions with distance and time information

## Technical Details

- Uses **OpenStreetMap** for geocoding (free, no API key required)
- Uses **OSRM** for routing calculations (free, no API key required)
- No rate limits for reasonable personal use
- Works offline if you set up your own OSRM server

## Limitations

- Requires internet connection (uses public APIs)
- Currently optimized for driving directions
- May have rate limits if used excessively

## Future Enhancements

Potential features to add:
- Walking, cycling, and public transit directions
- Alternative routes
- Real-time traffic information
- Save favorite locations
- Export directions to text file
- Voice output for hands-free navigation

## License

Open source - feel free to use and modify!

## Credits

- OpenStreetMap for map data
- OSRM for routing engine
- Nominatim for geocoding service

