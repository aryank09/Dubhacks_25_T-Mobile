# HINT Gateway System - Complete Setup

This is the complete HINT Gateway system where the Raspberry Pi runs the full navigation program with voice interaction, and the laptop only sends GPS coordinates.

## 🏗️ **System Architecture**

```
┌─────────────────────────────────┐    Firebase Realtime Database    ┌─────────────────────────┐
│        Raspberry Pi             │◄──────────────────────────────►│      Laptop Client      │
│   (Navigation Router)           │                                 │   (GPS Only)            │
│                                 │                                 │                         │
│ • Full navigation program       │                                 │ • Sends GPS coordinates │
│ • Voice interaction             │                                 │ • No voice interaction  │
│ • Pulls GPS from Firebase       │                                 │ • Background operation  │
│ • Speaks navigation instructions│                                 │                         │
│ • Human talks to Pi directly    │                                 │                         │
└─────────────────────────────────┘                                 └─────────────────────────┘
```

## 🚀 **Quick Start**

### **On Raspberry Pi:**
```bash
python3 pi_navigation_router.py
```

### **On Laptop:**
```bash
python3 gps_laptop_client.py
```

### **Or use the launcher:**
```bash
python3 run_hint_system.py
```

## 📁 **Key Files**

### **Pi Navigation Router** (`pi_navigation_router.py`)
- Runs the complete navigation program
- Voice interaction for destination input
- Pulls GPS coordinates from Firebase
- Speaks navigation instructions
- Interactive mode for navigation control

### **GPS Laptop Client** (`gps_laptop_client.py`)
- Only sends GPS coordinates to Firebase
- No voice interaction
- Background operation
- Smart location caching (only sends when moved >10m)

### **System Launcher** (`run_hint_system.py`)
- Easy way to start either component
- Firebase testing and cleanup tools

## 🎯 **How It Works**

1. **Laptop** automatically sends GPS coordinates to Firebase every 5 seconds
2. **Pi Router** pulls GPS data from Firebase every 5 seconds
3. **Human** talks to the Pi directly for navigation:
   - "Start navigation to [destination]"
   - Voice confirmation of destination
   - Real-time navigation instructions
4. **Pi** processes navigation and speaks instructions

## 🎤 **Voice Interaction Features**

The Pi router includes all voice features from the original `main.py`:

- **Voice destination input** - Speak your destination
- **Voice confirmation** - Confirm destination with "yes" or "no"
- **Real-time navigation** - Speaks turn-by-turn instructions
- **Interactive mode** - Menu-driven navigation control

## 🔧 **Setup Instructions**

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Configure Firebase**
Your Firebase is already configured in `firebase_config.json`

### 3. **Run the System**

**Option A: Use the launcher**
```bash
python3 run_hint_system.py
```

**Option B: Run components directly**

On Pi:
```bash
python3 pi_navigation_router.py
```

On Laptop:
```bash
python3 gps_laptop_client.py
```

## 🎮 **Usage Examples**

### **Starting Navigation on Pi:**
1. Run `python3 pi_navigation_router.py`
2. Choose "y" for interactive mode
3. Select "1. Start navigation by voice"
4. Speak your destination: "Space Needle"
5. Confirm: "Yes"
6. Navigation starts automatically!

### **Pi Navigation Commands:**
- **Interactive Mode Options:**
  - `1` - Start navigation by voice
  - `2` - Stop current navigation
  - `3` - Check current location
  - `4` - Exit interactive mode

### **Laptop GPS Client:**
- Runs automatically in background
- Sends GPS every 5 seconds
- Only sends when you move >10 meters
- No user interaction needed

## 📊 **System Status**

### **Pi Router Status:**
- ✅ Connected to Firebase
- ✅ Monitoring GPS from laptop
- ✅ Voice interaction ready
- ✅ Navigation processing active

### **Laptop Client Status:**
- ✅ Connected to Firebase
- ✅ Sending GPS coordinates
- ✅ Background operation
- ✅ Smart location caching

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **"No location data available"**
   - Make sure laptop client is running
   - Check Firebase connection
   - Verify GPS permissions on laptop

2. **"Could not find destination"**
   - Try a more specific address
   - Check internet connection
   - Verify geocoding service

3. **Voice recognition issues**
   - Speak clearly and slowly
   - Reduce background noise
   - Try again if first attempt fails

### **Debug Commands:**
```bash
# Test Firebase connection
python3 test_firebase.py

# Clean up Firebase data
python3 cleanup_firebase.py

# Check system status
python3 run_hint_system.py
```

## 🎯 **Key Benefits**

- **Pi handles everything** - Full navigation program runs on Pi
- **Laptop is simple** - Just sends GPS, no complex interaction
- **Voice interaction** - Human talks directly to Pi
- **Real-time updates** - GPS updates every 5 seconds
- **Smart caching** - Only sends GPS when you actually move
- **Easy setup** - One command to start each component

## 📱 **File Structure**

```
├── pi_navigation_router.py    # Main Pi program (navigation + voice)
├── gps_laptop_client.py       # Simple laptop GPS sender
├── run_hint_system.py         # System launcher
├── firebase_client.py         # Firebase communication
├── firebase_config.py         # Firebase configuration
├── text_maps.py              # Navigation logic
├── TTS.py                    # Text-to-speech
├── test_firebase.py          # Firebase testing
├── cleanup_firebase.py       # Firebase cleanup
└── README_HINT_SYSTEM.md     # This documentation
```

## 🎉 **Ready to Use!**

The system is now configured exactly as you wanted:
- **Raspberry Pi** runs the full navigation program with voice interaction
- **Laptop** only sends GPS coordinates to Firebase
- **Human** talks directly to the Pi for navigation

Just run the components and start navigating!
