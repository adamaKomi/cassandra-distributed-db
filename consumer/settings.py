import os
from typing import List
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()


def _get_list(env_name: str, default: str = "") -> List[str]:
    raw = os.getenv(env_name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


class Settings:
    KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
    KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "sensor-data")
    KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "cassandra-consumer")
    KAFKA_POLL_TIMEOUT_MS = int(os.getenv("KAFKA_POLL_TIMEOUT_MS", "1000"))

    # CORRECTION 1 : Utiliser "cassandra" (nom du service docker) ou "localhost" comme défaut
    # au lieu d'une IP fixe spécifique qui risque de ne pas exister.
    CASSANDRA_HOSTS = _get_list("CASSANDRA_HOSTS", "cassandra")
    
    CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", "9042"))
    CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "iot_demo")
    CASSANDRA_USERNAME = os.getenv("CASSANDRA_USERNAME", "")
    CASSANDRA_PASSWORD = os.getenv("CASSANDRA_PASSWORD", "")
    CASSANDRA_BATCH_SIZE = int(os.getenv("CASSANDRA_BATCH_SIZE", "100"))
    
    # CORRECTION 2 : Ajout du paramètre Replication Factor (Défaut à 1 pour le dév)
    CASSANDRA_REPLICATION_FACTOR = int(os.getenv("CASSANDRA_REPLICATION_FACTOR", "1"))


settings = Settings()