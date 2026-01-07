from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class SensorReading:
    sensor_id: str
    timestamp: datetime
    value: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SensorReading":
        # Le producer envoie un ISO 8601 via datetime.now().isoformat()
        return cls(
            sensor_id=str(data["sensor_id"]),
            timestamp=datetime.fromisoformat(str(data["timestamp"])),
            value=float(data["value"]),
        )