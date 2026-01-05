# API REST - IoT Sensor Monitoring

API FastAPI pour consulter les données des capteurs IoT stockées dans un cluster Cassandra distribué.

## Structure du projet

```
api/
├── main.py              # Application FastAPI principale
├── config.py            # Configuration de l'application
├── models.py            # Modèles Pydantic
├── database.py          # Connexion et requêtes Cassandra
├── requirements.txt     # Dépendances Python
├── .env.example         # Exemple de configuration
└── README.md           # Ce fichier
```

## Installation

1. Installer les dépendances :

```bash
pip install -r requirements.txt
```

2. Configurer l'application :

```bash
cp .env.example .env
# Éditer .env avec vos paramètres (IPs des nœuds Cassandra)
```

3. Vérifier que le cluster Cassandra est opérationnel sur les 3 PC

## Démarrage

Lancer l'API :

```bash
python main.py
```

Ou avec uvicorn directement :

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

L'API sera accessible sur : http://localhost:8000

## Endpoints disponibles

### Documentation interactive

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Endpoints principaux

#### `GET /`

Page d'accueil avec la liste des endpoints

#### `GET /health`

Vérifier l'état de santé de l'API et la connexion au cluster Cassandra

```json
{
  "status": "healthy",
  "cassandra_connected": true,
  "cassandra_nodes": ["192.168.1.10", "192.168.1.11", "192.168.1.12"],
  "message": "API opérationnelle"
}
```

#### `GET /sensors`

Obtenir la liste de tous les capteurs avec leur dernière lecture

```json
[
  {
    "sensor_id": "sensor_01",
    "last_reading": {
      "sensor_id": "sensor_01",
      "timestamp": "2026-01-05T10:00:01",
      "value": 22.7
    },
    "total_readings": 0
  }
]
```

#### `GET /sensors/{sensor_id}/latest`

Obtenir la dernière lecture d'un capteur spécifique

```json
{
  "sensor_id": "sensor_01",
  "timestamp": "2026-01-05T10:00:01",
  "value": 22.7
}
```

#### `GET /sensors/{sensor_id}/history?limit=100&hours=24`

Obtenir l'historique des lectures d'un capteur

Paramètres :

- `limit` : Nombre maximum de lectures (1-1000, défaut: 100)
- `hours` : Optionnel - Limiter aux N dernières heures

```json
{
  "sensor_id": "sensor_01",
  "count": 100,
  "readings": [
    {
      "sensor_id": "sensor_01",
      "timestamp": "2026-01-05T10:00:01",
      "value": 22.7
    }
  ]
}
```

#### `GET /cluster/status`

Obtenir le statut détaillé du cluster Cassandra

```json
{
  "connected": true,
  "nodes": [
    {
      "address": "192.168.1.10",
      "datacenter": "datacenter1",
      "rack": "rack1",
      "is_up": true
    }
  ],
  "keyspace": "iot_demo"
}
```

## Configuration

Les paramètres sont configurables via le fichier `.env` :

- `CASSANDRA_HOSTS` : Liste des IPs des nœuds Cassandra (format JSON)
- `CASSANDRA_PORT` : Port Cassandra (défaut: 9042)
- `CASSANDRA_KEYSPACE` : Nom du keyspace (défaut: iot_demo)
- `CORS_ORIGINS` : Liste des origines autorisées pour CORS

## Architecture

L'API suit une architecture en couches :

1. **main.py** : Endpoints FastAPI, gestion des requêtes HTTP
2. **models.py** : Validation des données avec Pydantic
3. **database.py** : Logique d'accès aux données Cassandra
4. **config.py** : Gestion de la configuration

## Points importants

- L'API se connecte aux **3 nœuds Cassandra** pour assurer la haute disponibilité
- La connexion est maintenue pendant toute la durée de vie de l'application
- CORS est activé pour permettre l'accès depuis le frontend
- Logs détaillés pour le débogage
- Documentation automatique via Swagger/OpenAPI

## Tests

Tester l'API avec curl :

```bash
# Health check
curl http://localhost:8000/health

# Liste des capteurs
curl http://localhost:8000/sensors

# Dernière lecture d'un capteur
curl http://localhost:8000/sensors/sensor_01/latest

# Historique (100 dernières lectures)
curl http://localhost:8000/sensors/sensor_01/history?limit=100

# Historique (dernières 24h)
curl http://localhost:8000/sensors/sensor_01/history?hours=24
```

## Démonstration

Pour la démo du projet :

1. Démarrer les 3 nœuds Cassandra
2. Lancer le producer Kafka (génération de données)
3. Lancer le consumer (ingestion dans Cassandra)
4. Lancer cette API
5. Ouvrir le frontend
6. Éteindre un nœud Cassandra → l'API continue de fonctionner !

## Dépannage

### Erreur de connexion à Cassandra

- Vérifier que les 3 PC Cassandra sont allumés et accessibles
- Vérifier les IPs dans le fichier `.env`
- Vérifier le firewall (ports 9042 et 7000)
- Tester la connectivité : `ping <ip_cassandra>`

### Pas de données

- Vérifier que le producer Kafka fonctionne
- Vérifier que le consumer insère bien les données
- Vérifier le keyspace : `cqlsh -e "SELECT * FROM iot_demo.sensor_data LIMIT 10;"`
