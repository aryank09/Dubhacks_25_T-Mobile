# 🗺️ Text Maps - Accessible Navigation System

A modern web-based navigation system designed specifically for accessibility and voice interaction. Get turn-by-turn walking, driving, and cycling directions with comprehensive voice guidance, speech-to-text input, and screen reader support!

## ✨ Key Features

- 🎤 **Speech-to-Text Input** - Talk to enter addresses instead of typing
- 🔊 **Voice Guidance** - Complete text-to-speech navigation instructions
- ♿ **Screen Reader Support** - Full compatibility with assistive technologies
- 🧭 **Live Navigation** - Real-time GPS tracking with voice announcements
- 📍 **Smart Geocoding** - Voice-friendly address input with fallbacks
- 📊 **Audio Route Summary** - Spoken distance, time, and step information
- 🎯 **Sequential Voice Reading** - Step-by-step directions without interruption
- 🌍 **Global Coverage** - Works anywhere using OpenStreetMap data
- 💻 **Accessible Interface** - High contrast terminal theme, keyboard navigation
- 📱 **Mobile Optimized** - Touch-friendly with voice input support

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.7+
- Git

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd text-maps-fullstack
```

2. **Start the backend:**
```bash
cd text-maps-backend
pip install -r requirements.txt
python app.py
```

3. **Start the frontend (in a new terminal):**
```bash
cd text-maps-frontend
npm install
npm run dev
```

4. **Open your browser:**
Navigate to `http://localhost:3001` (or the port shown in terminal)

## 🎯 Usage

### Voice Input Navigation
1. **Click the microphone button** next to any address field
2. **Speak your address** clearly (e.g., "Seattle Washington" or "123 Main Street")
3. **The app will automatically fill** the field with your spoken text
4. **Select transportation mode** (walking, driving, cycling)
5. **Click "Get Directions"** for turn-by-turn directions

### Regular Navigation
1. Enter your starting location (or "current" for current location)
2. Enter your destination
3. Select transportation mode (walking, driving, cycling)
4. Click "Get Directions"

### Live Navigation
1. Enter your destination (use voice input for hands-free operation)
2. Select transportation mode
3. Click "Start Live Navigation"
4. Allow location access when prompted
5. Follow the real-time voice instructions!

### Voice Features
- **🎤 Speech-to-Text**: Click microphone buttons to speak addresses
- **🔊 Voice Reading**: Directions are automatically read aloud
- **🛑 Stop Voice**: Use the stop button to cancel speech
- **🧪 Test Voice**: Test speech synthesis functionality

## 🛠️ Technical Details

### Backend (Flask)
- **Geocoding**: OpenStreetMap Nominatim API
- **Routing**: OSRM (Open Source Routing Machine)
- **CORS**: Enabled for frontend communication
- **Error Handling**: Comprehensive error responses

### Frontend (React + Vite)
- **UI Framework**: React 18 with hooks
- **Styling**: Tailwind CSS with custom terminal theme
- **Location**: HTML5 Geolocation API
- **Voice Input**: Web Speech Recognition API
- **Voice Output**: Web Speech Synthesis API
- **State Management**: React useState and useEffect
- **HTTP Client**: Fetch API

### APIs Used
- **Nominatim**: Free geocoding service (no API key required)
- **OSRM**: Free routing service (no API key required)
- **No rate limits** for reasonable personal use

## 📁 Project Structure

```
text-maps-fullstack/
├── text-maps-backend/          # Flask API server
│   ├── app.py                  # Main Flask application
│   └── requirements.txt        # Python dependencies
├── text-maps-frontend/         # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── NavigationForm.jsx    # Voice input forms
│   │   │   ├── RouteDisplay.jsx     # Voice reading results
│   │   │   ├── LiveNavigation.jsx    # Live voice guidance
│   │   │   └── ErrorBoundary.jsx    # Error handling
│   │   ├── hooks/
│   │   │   ├── useVoiceGuidance.js  # Voice output
│   │   │   └── useSpeechToText.js    # Voice input
│   │   ├── App.jsx            # Main app component
│   │   └── main.jsx           # Entry point
│   ├── package.json           # Node dependencies
│   └── vite.config.js         # Vite configuration
└── README.md                  # This file
```

## 🎨 Features in Detail

### Terminal Interface
- Retro terminal styling with green text on black background
- Terminal window controls (red, yellow, green dots)
- Monospace font for authentic terminal feel
- Responsive design that works on all devices

### Live Navigation
- Real-time GPS tracking
- Automatic step advancement as you move
- Distance to destination and next turn
- Arrival detection (within 20 meters)
- Location permission handling

### Route Display
- Turn-by-turn directions with visual arrows
- Distance and duration for each step
- Route summary with total distance and time
- Step-by-step navigation with icons
- **Sequential voice reading** of all directions
- **Voice control buttons** for manual reading
- **Speech synthesis testing** and debugging tools

## 🔧 Development

### Backend Development
```bash
cd text-maps-backend
pip install -r requirements.txt
python app.py
```

### Frontend Development
```bash
cd text-maps-frontend
npm install
npm run dev
```

### Building for Production
```bash
# Frontend
cd text-maps-frontend
npm run build

# Backend
cd text-maps-backend
# Deploy app.py to your preferred hosting service
```

## 🌐 API Endpoints

### Backend API
- `POST /api/geocode` - Convert address to coordinates
- `POST /api/route` - Get route between coordinates
- `POST /api/directions` - Get full directions from addresses
- `GET /api/health` - Health check

### Example API Usage
```javascript
// Geocode an address
const response = await fetch('/api/geocode', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ address: 'Seattle, WA' })
});
const data = await response.json();
```

## 🚧 Limitations

- Requires internet connection (uses public APIs)
- GPS accuracy depends on device and location
- No offline functionality
- Rate limits may apply with excessive use

## 🔮 Future Enhancements

- **Offline map support** for areas without internet
- **Alternative routes** with voice selection
- **Traffic information** integration
- **Save favorite locations** with voice shortcuts
- **Export directions** to audio files
- **Public transit directions** with voice guidance
- **Real-time traffic updates** with voice alerts
- **Multi-language support** for international users
- **Voice command shortcuts** for common actions

## 📄 License

Open source - feel free to use and modify!

## 🙏 Credits

- **OpenStreetMap** for map data
- **OSRM** for routing engine
- **Nominatim** for geocoding service
- **React** and **Flask** for the framework
- **Tailwind CSS** for styling

---

**🗺️ Text Maps - Navigate the world through text!**
