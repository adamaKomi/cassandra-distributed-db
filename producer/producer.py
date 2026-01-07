from kafka import KafkaProducer #1. Importation de la bibliothèque Kafka
import json                     #2. Importation de la bibliothèque JSON
import time                     #3. Importation de la bibliothèque time
from datetime import datetime   #4. Importation de la bibliothèque datetime
import random                   #5. Importation de la bibliothèque random

# 1. Connexion à Kafka
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',#Adresse de mon serveur Kafka
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

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
