# Kafka → Cassandra Consumer

- Lit le topic Kafka `sensor-data` (aligné avec ton producer).
- Écrit dans Cassandra keyspace `iot_demo`, table `sensor_data`.

## Prérequis
- Python 3.10+
- Kafka reachable (`KAFKA_BOOTSTRAP`)
- Cassandra cluster (3 nœuds de préférence), keyspace/table existants :
```sql
CREATE KEYSPACE IF NOT EXISTS iot_demo
WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': 3 };

CREATE TABLE IF NOT EXISTS iot_demo.sensor_data (
  sensor_id text,
  timestamp timestamp,
  value double,
  PRIMARY KEY (sensor_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

## Variables d’environnement (`.env`)
```env
KAFKA_BOOTSTRAP=localhost:9092
KAFKA_TOPIC=sensor-data
KAFKA_GROUP_ID=cassandra-consumer
KAFKA_POLL_TIMEOUT_MS=1000

CASSANDRA_HOSTS=192.168.1.10,192.168.1.11,192.168.1.12
CASSANDRA_KEYSPACE=iot_demo
CASSANDRA_USERNAME=
CASSANDRA_PASSWORD=
CASSANDRA_BATCH_SIZE=100
```

## Installation
```bash
cd consumer
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement
```bash
python main.py
```

## Notes
- Consistency `LOCAL_QUORUM` pour tolérance aux pannes.
- Batch d’insert (`CASSANDRA_BATCH_SIZE`) pour augmenter le débit.
- Le consumer n’a pas besoin de l’API ni du frontend.