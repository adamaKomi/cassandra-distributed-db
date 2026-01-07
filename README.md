# 🌡️ IoT Sensor Monitoring - Cluster Cassandra Distribué

Application de monitoring de capteurs IoT en temps réel, démontrant les concepts de **bases de données NoSQL distribuées** avec Apache Cassandra.

---

## 📋 Sommaire

- [Objectifs du Projet](#-objectifs-du-projet)
- [Architecture](#-architecture)
- [Technologies Utilisées](#-technologies-utilisées)
- [Structure du Projet](#-structure-du-projet)
- [Installation & Lancement](#-installation--lancement)
- [Démonstration de la Distribution](#-démonstration-de-la-distribution)
- [API REST](#-api-rest)
- [Documentation](#-documentation)

---

## 🎯 Objectifs du Projet

Ce projet a pour but de démontrer concrètement les avantages d'une base de données NoSQL distribuée :

| Concept | Démonstration |
|---------|---------------|
| **Réplication des données** | Les données écrites sur un nœud sont automatiquement copiées sur les autres |
| **Tolérance aux pannes** | Le système continue de fonctionner même si un nœud tombe |
| **Scalabilité horizontale** | Ajout facile de nouveaux nœuds pour augmenter la capacité |
| **Haute disponibilité** | Aucun point unique de défaillance (SPOF) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PIPELINE DE DONNÉES                            │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
  │   Producer   │ ───► │    Kafka     │ ───► │   Consumer   │
  │  (Capteurs)  │      │   (Queue)    │      │  (Ingestion) │
  └──────────────┘      └──────────────┘      └──────┬───────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLUSTER CASSANDRA DISTRIBUÉ                         │
│                                                                             │
│    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐             │
│    │   Nœud 1    │◄─────►│   Nœud 2    │◄─────►│   Nœud 3    │             │
│    │   (Seed)    │       │             │       │             │             │
│    │   PC 1      │       │   PC 2      │       │   PC 3      │             │
│    └─────────────┘       └─────────────┘       └─────────────┘             │
│          ▲                     ▲                     ▲                      │
│          └─────────────────────┴─────────────────────┘                      │
│                        Réplication Automatique                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
                            ┌──────────────┐
                            │   API REST   │
                            │  (FastAPI)   │
                            └──────┬───────┘
                                   │
                                   ▼
                            ┌──────────────┐
                            │   Frontend   │
                            │   (React)    │
                            └──────────────┘
```

### Flux de Données

1. **Producer** : Simule des capteurs IoT qui envoient des mesures (température, etc.)
2. **Kafka** : File de messages qui découple les producteurs des consommateurs
3. **Consumer** : Lit les messages Kafka et les insère dans Cassandra
4. **Cassandra** : Stocke les données de manière distribuée et répliquée
5. **API REST** : Expose les données via des endpoints HTTP
6. **Frontend** : Dashboard de visualisation en temps réel

---

## 🛠️ Technologies Utilisées

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| Base de données | Apache Cassandra | 4.1 | Stockage distribué NoSQL |
| Message Broker | Apache Kafka | 7.5.0 | File de messages temps réel |
| Backend API | FastAPI (Python) | 3.11 | API REST asynchrone |
| Frontend | React + TypeScript | 18.x | Interface utilisateur |
| Build Tool | Vite | 5.x | Bundler frontend |
| Styling | Tailwind CSS | 3.x | Framework CSS |
| Conteneurisation | Docker + Compose | - | Déploiement |

---

## 📁 Structure du Projet

```
noSqlProject/
├── docker-compose.yml              # Stack principale (Kafka, Cassandra, etc.)
├── docker-compose-cassandra-node.yml  # Config pour nœuds Cassandra additionnels
│
├── producer/                       # Simulateur de capteurs
│   ├── Dockerfile
│   ├── producer.py                 # Génère des données aléatoires
│   └── requirements.txt
│
├── consumer/                       # Service d'ingestion
│   ├── Dockerfile
│   ├── main.py                     # Point d'entrée
│   ├── kafka_consumer.py           # Lecture Kafka
│   ├── cassandra_client.py         # Écriture Cassandra
│   └── requirements.txt
│
├── api/                            # API REST FastAPI
│   ├── Dockerfile
│   ├── main.py                     # Endpoints REST
│   ├── database.py                 # Connexion Cassandra
│   ├── config.py                   # Configuration
│   └── requirements.txt
│
├── frontend/                       # Dashboard React
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── dashboard/          # Composants du tableau de bord
│   │   │   └── layout/             # Header, Layout
│   │   └── services/
│   │       └── SensorService.ts    # Appels API
│   ├── package.json
│   └── vite.config.ts
│
└── docs/                           # Documentation
    ├── guide_test_distribue.md     # Guide de test du cluster
    ├── specifications.md           # Spécifications techniques
    └── deployment_strategy.md      # Stratégie de déploiement
```

---

## 🚀 Installation & Lancement

### Prérequis

- **Docker Desktop** (v4.x+) - [Télécharger](https://www.docker.com/products/docker-desktop)
- **Node.js** (v18+) - Pour le frontend local
- **Git** - Pour cloner le projet

### Lancement Rapide (1 seul PC)

```powershell
# 1. Cloner le projet
git clone <url-du-repo>
cd noSqlProject

# 2. Lancer toute la stack
docker-compose up -d

# 3. Vérifier que tout tourne
docker ps

# 4. Lancer le frontend (optionnel, en local)
cd frontend
npm install
npm run dev
```

### Accès aux Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Dashboard de monitoring |
| API REST | http://localhost:8000 | Endpoints FastAPI |
| API Docs | http://localhost:8000/docs | Documentation Swagger |
| Kafka UI | http://localhost:8888 | Monitoring Kafka |

---

## 🔄 Démonstration de la Distribution

Le point fort de ce projet est la démonstration d'un **cluster Cassandra distribué sur plusieurs PCs physiques**.

### Configuration Multi-PC

```
PC 1 (Master)          PC 2 (Nœud)           PC 3 (Nœud)
192.168.1.6            192.168.1.42          192.168.1.x
┌─────────────┐        ┌─────────────┐       ┌─────────────┐
│ Kafka       │        │             │       │             │
│ Producer    │        │             │       │             │
│ Consumer    │        │             │       │             │
│ API         │        │             │       │             │
│ Cassandra ◄─┼────────┼─► Cassandra ◄───────┼─► Cassandra │
└─────────────┘        └─────────────┘       └─────────────┘
```

### Démarrage du Cluster

**PC 1 (Master)** :
```powershell
$env:HOST_IP="192.168.1.6"; docker-compose up -d
```

**PC 2, 3, ... (Nœuds)** :
```powershell
$env:HOST_IP="<IP_CE_PC>"; $env:SEED_IP="192.168.1.6"
docker-compose -f docker-compose-cassandra-node.yml up -d
```

### Vérification

```powershell
docker exec -it nosqlproject-cassandra-1 nodetool status
```

Résultat attendu :
```
UN  192.168.1.6   xxx KB  16  33.3%  ...
UN  192.168.1.42  xxx KB  16  33.3%  ...
UN  192.168.1.x   xxx KB  16  33.3%  ...
```

> 📖 **Guide complet** : Voir [docs/guide_test_distribue.md](docs/guide_test_distribue.md)

---

## 📡 API REST

L'API expose les données des capteurs via FastAPI.

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/` | Informations de l'API et liste des endpoints |
| `GET` | `/health` | État de santé de l'API et connexion Cassandra |
| `GET` | `/sensors` | Liste tous les capteurs avec dernières lectures |
| `GET` | `/sensors/{sensor_id}` | Informations détaillées d'un capteur spécifique |
| `GET` | `/sensors/{sensor_id}/latest` | Dernière lecture d'un capteur |
| `GET` | `/sensors/{sensor_id}/history` | Historique des lectures (paramètres: limit, hours) |
| `GET` | `/cluster/status` | Statut du cluster Cassandra |

### Exemple de Requêtes

```bash
# État de santé
curl http://localhost:8000/health

# Liste des capteurs
curl http://localhost:8000/sensors

# Dernière valeur du capteur sensor_001
curl http://localhost:8000/sensors/sensor_001/latest

# Historique du capteur sensor_001 (100 dernières lectures)
curl http://localhost:8000/sensors/sensor_001/history

# Historique limité aux 24 dernières heures
curl "http://localhost:8000/sensors/sensor_001/history?hours=24"

# Statut du cluster
curl http://localhost:8000/cluster/status
```

### Réponse Exemple

```json
// /health
{
  "status": "healthy",
  "cassandra_connected": true,
  "cassandra_nodes": ["192.168.1.6", "192.168.1.42"],
  "message": "API opérationnelle"
}

// /sensors/sensor_001/latest
{
  "sensor_id": "sensor_001",
  "timestamp": "2026-01-07T19:31:35.123000",
  "value": 22.69
}

// /cluster/status
{
  "connected": true,
  "nodes": [
    {"address": "192.168.1.6", "datacenter": "dc1", "rack": "rack1", "is_up": true},
    {"address": "192.168.1.42", "datacenter": "dc1", "rack": "rack1", "is_up": true}
  ],
  "keyspace": "iot_demo"
}
```

### Documentation Interactive

Accédez à la documentation Swagger : http://localhost:8000/docs

---

## � Gestion des Nœuds du Cluster

### Ajouter un nœud

**Sur le nouveau PC** (ex: PC3 avec IP 192.168.1.100) :
```powershell
# 1. Définir les variables
$env:HOST_IP="192.168.1.100"
$env:SEED_IP="192.168.1.6"

# 2. Lancer le nœud Cassandra
docker-compose -f docker-compose-cassandra-node.yml up -d
```

**Sur PC1 (Master)** - Après l'ajout :
```powershell
# 1. Vérifier que le nœud a rejoint
docker exec -it nosqlproject-cassandra-1 nodetool status

# 2. Augmenter le facteur de réplication
docker exec -it nosqlproject-cassandra-1 cqlsh -e "ALTER KEYSPACE iot_demo WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '2'};"

# 3. Mettre à jour docker-compose.yml → CASSANDRA_REPLICATION_FACTOR: 2

# 4. Redémarrer le consumer
docker-compose up -d --build consumer
```

### Retirer un nœud

**Cas 1 : Arrêt propre** (nœud accessible)
```powershell
# Sur le PC à retirer - Transférer les données avant arrêt
docker exec -it cassandra-node nodetool decommission

# Puis arrêter
docker-compose -f docker-compose-cassandra-node.yml down -v
```

**Cas 2 : Nœud en panne** (inaccessible)
```powershell
# Sur PC1 - Obtenir le Host ID du nœud mort
docker exec -it nosqlproject-cassandra-1 nodetool status

# Retirer le nœud (remplacer <HOST_ID>)
docker exec -it nosqlproject-cassandra-1 nodetool removenode <HOST_ID>
```

**Après retrait** - Ajuster la configuration :
```powershell
# Réduire le facteur de réplication si nécessaire
docker exec -it nosqlproject-cassandra-1 cqlsh -e "ALTER KEYSPACE iot_demo WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};"

# Mettre à jour docker-compose.yml → CASSANDRA_REPLICATION_FACTOR: 1

# Redémarrer le consumer
docker-compose up -d --build consumer
```

### Règles de Configuration

| Nœuds | RF recommandé | Consistance | Tolérance pannes |
|-------|---------------|-------------|------------------|
| 1 | 1 | ONE | 0 |
| 2 | 2 | ONE | 0 (lecture seule si 1 tombe) |
| 3 | 3 | LOCAL_QUORUM | 1 nœud |
| 5 | 3 | LOCAL_QUORUM | 1 nœud |

> ⚠️ **Important** : Le facteur de réplication (RF) ne peut jamais dépasser le nombre de nœuds actifs, sinon les écritures échouent !

> 📖 **Guide détaillé** : Voir [docs/guide_test_distribue.md](docs/guide_test_distribue.md#7-étendre-le-cluster-ajouter-des-nœuds)

---

## �📚 Documentation

| Document | Description |
|----------|-------------|
| [Guide de Test Distribué](docs/guide_test_distribue.md) | Configuration multi-PC, scénarios de test |
| [Spécifications](docs/specifications.md) | Cahier des charges technique |
| [Stratégie de Déploiement](docs/deployment_strategy.md) | Plan de déploiement |

---

## 🧪 Scénarios de Test

### Test 1 : Réplication
1. Écrire des données sur PC 1
2. Lire les mêmes données sur PC 2
3. ✅ Succès si les données sont identiques

### Test 2 : Tolérance aux Pannes
1. Arrêter Cassandra sur PC 1 : `docker stop nosqlproject-cassandra-1`
2. Lire les données sur PC 2
3. ✅ Succès si les données sont toujours accessibles

### Test 3 : Pipeline End-to-End
1. Vérifier que le Producer envoie des messages
2. Vérifier que Kafka reçoit les messages
3. Vérifier que le Consumer écrit dans Cassandra
4. Vérifier que l'API retourne les données
5. Vérifier que le Frontend affiche les graphiques

---

## 👥 Équipe

Projet réalisé dans le cadre du module **Bases de Données NoSQL** - ILISI 3

---

## 📄 Licence

Ce projet est à usage éducatif.
