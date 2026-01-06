# IoT Monitoring Project

## Frontend Application
This directory contains the React frontend for the IoT Monitoring Dashboard.

### Prerequisites
- Node.js (v18+)
- npm

### Installation & Run
```bash
cd frontend
npm install
npm run dev
```

---

## 📡 API Specification
The backend must expose the following RESTful endpoints to support the frontend dashboard.
Base URL: `http://localhost:8000` (example)

### 1. Get All Sensors
Retrieves the list of available sensors for the dropdown selection.

- **Endpoint**: `GET /api/sensors`
- **Response**: `200 OK`
```json
[
  {
    "id": "s1",
    "name": "Sensor 01",
    "location": "Manufacturing Unit"
  },
  {
    "id": "s2",
    "name": "Sensor 02",
    "location": "Assembly Line"
  }
]
```

### 2. Get Sensor Statistics
Retrieves key indicators for a specific sensor (Current Value, Daily Average, Trend).

- **Endpoint**: `GET /api/sensors/{id}/stats`
- **Response**: `200 OK`
```json
{
  "currentValue": 42.5,
  "averageValue": 40.1,
  "trendPercentage": 1.2,     // Positive or negative float
  "trendLabel": "vs last hour"
}
```

### 3. Get Sensor History (Chart Data)
Retrieves historical data points for the visualization chart.

- **Endpoint**: `GET /api/sensors/{id}/history`
- **Query Parameters**:
  - `range`: `live` | `1h` | `24h` | `7d` (optional, default: `live`)
- **Response**: `200 OK`
```json
[
  {
    "timestamp": "10:00",  // Format depends on range (HH:mm or DD/MM)
    "value": 41.2
  },
  {
    "timestamp": "10:05",
    "value": 42.0
  }
]
```

### 4. WebSocket (Optional / Future)
For real-time "Live" mode without polling.
- **Endpoint**: `ws://localhost:8000/ws/sensors/{id}`
- **Message Format**:
```json
{
  "timestamp": "10:30:01",
  "value": 42.8
}
```
