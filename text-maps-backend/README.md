# Text Maps Backend API

Flask-based backend API for the Text Maps navigation system.

## 🚀 Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the server:**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## 📡 API Endpoints

### Health Check
```
GET /api/health
```
Returns server status and available services.

### Geocoding
```
POST /api/geocode
Content-Type: application/json

{
  "address": "Seattle, WA"
}
```
Converts an address to GPS coordinates.

### Route Calculation
```
POST /api/route
Content-Type: application/json

{
  "start_lat": 47.6062,
  "start_lng": -122.3321,
  "end_lat": 45.5152,
  "end_lng": -122.6784,
  "mode": "walking"
}
```
Calculates route between two coordinates.

### Full Directions
```
POST /api/directions
Content-Type: application/json

{
  "start_address": "Seattle, WA",
  "end_address": "Portland, OR",
  "mode": "driving"
}
```
Gets complete directions from addresses.

## 🛠️ Technical Details

- **Framework**: Flask with CORS support
- **Geocoding**: OpenStreetMap Nominatim API
- **Routing**: OSRM (Open Source Routing Machine)
- **No API keys required**
- **Free to use** (within reasonable limits)

## 🔧 Configuration

The server runs on `0.0.0.0:5000` by default. To change the port:

```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

## 📊 Response Format

### Geocoding Response
```json
{
  "lat": 47.6062,
  "lng": -122.3321,
  "display_name": "Seattle, King County, Washington, USA",
  "address": {
    "city": "Seattle",
    "state": "Washington",
    "country": "USA"
  }
}
```

### Route Response
```json
{
  "distance": 278500,
  "duration": 10440,
  "steps": [
    {
      "step": 1,
      "instruction": "Start by heading south on 5th Avenue",
      "distance": 150,
      "duration": 18,
      "direction": "↓",
      "coordinates": [-122.3321, 47.6062]
    }
  ],
  "geometry": {
    "type": "LineString",
    "coordinates": [[-122.3321, 47.6062], [-122.6784, 45.5152]]
  }
}
```

## 🚨 Error Handling

All endpoints return appropriate HTTP status codes:
- `200` - Success
- `400` - Bad Request (missing parameters, invalid data)
- `500` - Server Error

Error responses include a descriptive message:
```json
{
  "error": "Address not found: Invalid Location"
}
```

## 🌐 External Services

- **Nominatim**: `https://nominatim.openstreetmap.org`
- **OSRM**: `https://router.project-osrm.org`

Both services are free and don't require API keys.
