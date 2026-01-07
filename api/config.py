"""
Configuration de l'API REST pour le projet Cassandra IoT
"""

# Configuration en dur pour éviter les problèmes de parsing Pydantic
class Settings:
    """Configuration de l'application"""
    
    # Configuration de l'API
    app_name: str = "IoT Sensor Monitoring API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Configuration Cassandra - IPs en dur
    cassandra_hosts = ["cassandra", "192.168.1.42"]
    cassandra_port: int = 9042
    cassandra_keyspace: str = "iot_demo"
    
    # CORS
    cors_origins = ["http://localhost:5173", "http://localhost:3000", "*"]


# Instance globale des settings
settings = Settings()
