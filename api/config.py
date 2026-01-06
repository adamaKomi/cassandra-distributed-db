"""
Configuration de l'API REST pour le projet Cassandra IoT
"""
from pydantic_settings import BaseSettings
from typing import List


# Configuration des paramètres de l'application par defaut 
# ou lecture depuis des variables d'environnement
class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Configuration de l'API
    app_name: str = "IoT Sensor Monitoring API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Configuration Cassandra
    cassandra_hosts: List[str] = ["192.168.1.10", "192.168.1.11", "192.168.1.12"]
    cassandra_port: int = 9042
    cassandra_keyspace: str = "iot_demo"
    
    # CORS (pour permettre au frontend d'accéder à l'API)
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instance globale des settings
settings = Settings()
