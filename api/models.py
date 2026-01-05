"""
Modèles de données pour l'API
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class SensorReading(BaseModel):
    """Lecture d'un capteur"""
    sensor_id: str
    timestamp: datetime
    value: float
    
    class Config: #Pour la documentation automatique
        json_schema_extra = {
            "example": {
                "sensor_id": "sensor_01",
                "timestamp": "2026-01-04T10:00:01",
                "value": 22.7
            }
        }


class SensorInfo(BaseModel):
    """Informations sur un capteur"""
    sensor_id: str
    last_reading: Optional[SensorReading] = None
    total_readings: int = 0


class SensorHistoryResponse(BaseModel):
    """Historique d'un capteur"""
    sensor_id: str
    readings: List[SensorReading]
    count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "sensor_id": "sensor_01",
                "count": 100,
                "readings": [
                    {
                        "sensor_id": "sensor_01",
                        "timestamp": "2026-01-04T10:00:01",
                        "value": 22.7
                    }
                ]
            }
        }


class HealthResponse(BaseModel):
    """Réponse de santé de l'API"""
    status: str
    cassandra_connected: bool
    cassandra_nodes: List[str]
    message: Optional[str] = None
