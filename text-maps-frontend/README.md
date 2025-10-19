# Text Maps Frontend

React-based frontend for the Text Maps navigation system with a beautiful terminal-style interface.

## 🚀 Quick Start

1. **Install dependencies:**
```bash
npm install
```

2. **Start development server:**
```bash
npm run dev
```

The app will be available at `http://localhost:3001` (or the port shown in terminal)

## 🎨 Features

- **Terminal Interface** - Retro green-on-black terminal styling
- **Speech-to-Text Input** - Voice input for all address fields
- **Voice Guidance** - Complete text-to-speech navigation
- **Sequential Reading** - Step-by-step voice directions without interruption
- **Responsive Design** - Works on desktop and mobile
- **Live Navigation** - Real-time GPS tracking with voice
- **Multiple Modes** - Walking, driving, and cycling
- **Modern React** - Built with React 18 and hooks
- **Error Handling** - Comprehensive error boundaries and fallbacks

## 🛠️ Development

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Project Structure
```
src/
├── components/
│   ├── Header.jsx           # App header
│   ├── NavigationForm.jsx   # Voice input forms
│   ├── RouteDisplay.jsx    # Voice reading results
│   ├── LiveNavigation.jsx   # Live voice navigation
│   └── ErrorBoundary.jsx   # Error handling
├── hooks/
│   ├── useVoiceGuidance.js # Voice output system
│   └── useSpeechToText.js   # Voice input system
├── App.jsx                  # Main app component
├── main.jsx                 # Entry point
└── index.css                # Global styles
```

## 🎯 Components

### NavigationForm
- **Voice input fields** with microphone buttons
- Regular navigation input
- Live navigation input
- Mode selection (walking/driving/cycling)
- Error handling and validation

### RouteDisplay
- Route summary (distance, time, steps)
- Turn-by-turn directions
- Visual direction arrows
- Step-by-step navigation
- **Sequential voice reading** of all directions
- **Voice control buttons** (test, stop, read all)
- **Speech synthesis debugging**

### LiveNavigation
- Real-time GPS tracking
- Automatic step advancement
- Distance to destination/next turn
- Arrival detection
- **Live voice guidance** with announcements

## 🎨 Styling

Built with Tailwind CSS and custom terminal theme:

```css
.terminal {
  @apply bg-black text-green-400 p-4 rounded-lg font-mono;
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
}
```

### Key Classes
- `.terminal` - Main terminal container
- `.direction-arrow` - Direction indicators
- `.step-number` - Step numbering
- `.input-field` - Form inputs
- `.btn-primary` - Primary buttons

## 📱 Responsive Design

- Mobile-first approach
- Flexible grid layouts
- Touch-friendly buttons
- Optimized for all screen sizes

## 🔧 Configuration

### Vite Config
```javascript
export default defineConfig({
  plugins: [react()],
  server: { 
    port: 3000, 
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
});
```

### Tailwind Config
```javascript
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        'mono': ['JetBrains Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
```

## 🌐 API Integration

The frontend communicates with the Flask backend through these endpoints:

- `POST /api/geocode` - Address geocoding
- `POST /api/route` - Route calculation
- `POST /api/directions` - Full directions

### Example Usage
```javascript
const response = await fetch('/api/directions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    start_address: 'Seattle, WA',
    end_address: 'Portland, OR',
    mode: 'driving'
  })
});
```

## 📦 Dependencies

### Production
- `react` - UI framework
- `react-dom` - DOM rendering
- `axios` - HTTP client (optional, using fetch)

### Development
- `@vitejs/plugin-react` - Vite React plugin
- `tailwindcss` - CSS framework
- `autoprefixer` - CSS autoprefixer
- `postcss` - CSS processor

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Static Hosting
The built files in `dist/` can be deployed to any static hosting service:
- Vercel
- Netlify
- GitHub Pages
- AWS S3

### Environment Variables
No environment variables required - the app uses relative API paths.

## 🎯 Browser Support

- Modern browsers with ES6+ support
- Geolocation API support for live navigation
- HTTPS required for GPS in production

## 🔧 Customization

### Terminal Theme
Modify `src/index.css` to change the terminal appearance:

```css
.terminal {
  @apply bg-black text-green-400; /* Change colors */
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.3); /* Change glow */
}
```

### Font
Change the monospace font in `tailwind.config.js`:

```javascript
fontFamily: {
  'mono': ['Your Font', 'monospace'],
}
```
