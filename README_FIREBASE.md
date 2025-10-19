# Firebase Integration for HINT Gateway System

This document explains how to set up and use the Firebase Realtime Database integration for the HINT Gateway system, where the Raspberry Pi acts as a router/gateway and the laptop acts as a client.

## System Architecture

```
┌─────────────────┐    Firebase Realtime Database    ┌─────────────────┐
│   Raspberry Pi  │◄──────────────────────────────►│   Laptop Client │
│   (Router)      │                                 │                 │
│                 │                                 │                 │
│ • Pulls location│                                 │ • Sends location│
│   every 5 sec   │                                 │   every 5 sec   │
│ • Sends commands│                                 │ • Listens for   │
│ • Navigation    │                                 │   commands      │
│ • Voice output  │                                 │ • Voice output  │
└─────────────────┘                                 └─────────────────┘
```

## Firebase Database Structure

```
/user/
├── location/          # Location data from laptop
│   ├── type: "location_update"
│   ├── timestamp: 1234567890
│   └── location: {
│       ├── latitude: 47.6062
│       ├── longitude: -122.3321
│       └── accuracy: 5.0
│   }
└── command/           # Commands from Pi to laptop
    ├── type: "voice_command"
    ├── timestamp: 1234567890
    └── data: {
        └── text: "Turn left in 100 meters"
    }

/system/
├── router/            # Pi router status
└── client/            # Laptop client status
```

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Firebase

Run the setup script:

```bash
python setup_firebase.py
```

This will:
- Guide you through Firebase project creation
- Help you configure the database rules
- Test the connection
- Save configuration to `firebase_config.json`

### 3. Manual Configuration (Alternative)

If you prefer to configure manually, edit `firebase_config.json`:

```json
{
  "apiKey": "your-api-key",
  "authDomain": "your-project-id.firebaseapp.com",
  "databaseURL": "https://your-project-id-default-rtdb.firebaseio.com/",
  "projectId": "your-project-id",
  "storageBucket": "your-project-id.appspot.com",
  "messagingSenderId": "123456789",
  "appId": "your-app-id"
}
```

## Usage

### Running the System

#### On Raspberry Pi (Router):
```bash
python pi_router.py
```

The Pi will:
- Pull location data from Firebase every 5 seconds
- Process navigation if a destination is set
- Send voice commands to the laptop
- Send navigation instructions

#### On Laptop (Client):
```bash
python laptop_client.py
```

The laptop will:
- Send current GPS location to Firebase every 5 seconds
- Listen for commands from the Pi
- Speak voice commands received from the Pi

### Testing the System

1. **Start the Pi Router first:**
   ```bash
   python pi_router.py
   ```

2. **Start the Laptop Client:**
   ```bash
   python laptop_client.py
   ```

3. **Test location sharing:**
   - The laptop will automatically send location updates
   - The Pi will receive and process them

4. **Test navigation:**
   - On the Pi, you can manually start navigation by calling:
     ```python
     router.start_navigation("1600 Amphitheatre Parkway, Mountain View, CA")
     ```

## Message Types

### Location Messages (Laptop → Pi)
- `location_update`: Current GPS coordinates
- `location_request`: Request for location data

### Command Messages (Pi → Laptop)
- `navigation_start`: Start navigation to destination
- `navigation_stop`: Stop current navigation
- `voice_command`: Text to be spoken by laptop
- `system_command`: System-level commands

### Status Messages
- `status_update`: Device status updates
- `connection_alive`: Keep-alive messages

## Firebase Database Rules

For development/testing, use these permissive rules:

```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

For production, implement proper authentication and security rules.

## Troubleshooting

### Common Issues

1. **Firebase connection failed:**
   - Check your `firebase_config.json` file
   - Verify your Firebase project has Realtime Database enabled
   - Ensure database rules allow read/write access

2. **No location data received:**
   - Check if laptop client is running
   - Verify GPS permissions on laptop
   - Check Firebase console for data

3. **Commands not received:**
   - Check if Pi router is running
   - Verify Firebase connection on both devices
   - Check network connectivity

### Debug Mode

Enable debug output by setting environment variable:
```bash
export FIREBASE_DEBUG=1
python pi_router.py
```

## File Structure

```
├── firebase_config.py      # Firebase configuration management
├── firebase_client.py      # Firebase Realtime Database client
├── pi_router.py           # Raspberry Pi router implementation
├── laptop_client.py       # Laptop client implementation
├── setup_firebase.py      # Firebase setup helper
├── firebase_config.json   # Firebase configuration (created by setup)
└── README_FIREBASE.md     # This documentation
```

## Security Considerations

1. **API Keys:** Never commit API keys to version control
2. **Database Rules:** Implement proper authentication for production
3. **Network Security:** Use HTTPS and secure connections
4. **Data Privacy:** Consider data retention policies

## Performance Notes

- Location updates are sent every 5 seconds by default
- Firebase has rate limits for free tier
- Consider implementing exponential backoff for errors
- Monitor Firebase usage in the console

## Next Steps

1. Implement user authentication
2. Add data encryption for sensitive information
3. Implement proper error handling and reconnection logic
4. Add data persistence and offline capabilities
5. Implement proper security rules for production use
