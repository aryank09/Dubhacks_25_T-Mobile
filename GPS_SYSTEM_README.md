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
