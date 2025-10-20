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

### Interactive Mode

Simply run the program and enter your locations when prompted:

```bash
python text_maps.py
```

Example:
```
Starting location: Seattle, WA
Destination: Portland, OR
```

### Command Line Mode

Pass the starting location and destination as arguments:

```bash
python text_maps.py "Seattle, WA" "Portland, OR"
```

```bash
python text_maps.py "1600 Amphitheatre Parkway, Mountain View, CA" "1 Apple Park Way, Cupertino, CA"
```

### Using Current Location

You can use `current` (or `current location`, `my location`, `here`) to navigate from or to your current location:

```bash
# Navigate from current location to a destination
python text_maps.py "current" "Space Needle, Seattle"
```

```bash
# Navigate from an address to your current location
python text_maps.py "Pike Place Market, Seattle" "current"
```

```bash
# Interactive mode - just type "current" when prompted
python text_maps.py
Starting location: current
Destination: Starbucks Reserve Roastery, Seattle
```

**Note:** Current location detection uses IP-based geolocation, which provides city-level accuracy. For more precise location, you can enter your specific address.

### Changing Transportation Mode

By default, the program provides **walking directions**. You can change the mode using the `--mode` flag:

```bash
# Walking directions (default)
python text_maps.py "Pike Place Market" "Space Needle"

# Driving directions
python text_maps.py --mode driving "Seattle, WA" "Portland, OR"

# Cycling directions
python text_maps.py --mode cycling "University of Washington" "Downtown Seattle"
```

Available modes:
- `walking` (default) - Pedestrian routes, sidewalks, and footpaths
- `driving` - Car routes on roads and highways
- `cycling` - Bicycle-friendly routes

### Live Navigation Mode 🧭

The **live navigation mode** continuously tracks your location and provides real-time turn-by-turn directions as you move!

```bash
# Start live navigation to a destination
python text_maps.py --live "Space Needle, Seattle"

# Live navigation with custom update interval (default: 5 seconds)
python text_maps.py --live --interval 10 "Pike Place Market"

# Live navigation with driving mode
python text_maps.py --live --mode driving "Portland, OR"
```

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

