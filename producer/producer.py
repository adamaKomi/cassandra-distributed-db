from kafka import KafkaProducer #1. Importation de la bibliothèque Kafka
import json                     #2. Importation de la bibliothèque JSON
import time                     #3. Importation de la bibliothèque time
from datetime import datetime   #4. Importation de la bibliothèque datetime
import random                   #5. Importation de la bibliothèque random

import os

# 1. Connexion à Kafka avec retry
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

producer = None
while producer is None:
    try:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Connecté à Kafka !")
    except Exception as e:
        print(f"En attente de Kafka... ({e})")
        time.sleep(2)

# 2. Topic Kafka
TOPIC = 'sensor-data' #Nom de mon topic Kafka

# 3. Capteurs simulés
sensors = [f"sensor_{i:03d}" for i in range(1, 51)]

print("Producer démarré...")

# 4. Boucle infinie d'envoi de données
while True:
    for sensor_id in sensors:
        data = {
            "sensor_id": sensor_id,
            "timestamp": datetime.now().isoformat(),
            "value": round(random.uniform(20, 30), 2)
        }

        producer.send(TOPIC, value=data)
        print("Message envoyé :", data)

    time.sleep(1)
