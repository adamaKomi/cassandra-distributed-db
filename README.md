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
| `GET` | `/health` | État de santé de l'API |
| `GET` | `/sensors` | Liste tous les capteurs |
| `GET` | `/sensors/last` | Dernière valeur d'un capteur |
| `GET` | `/sensors/{id}/stats` | Statistiques d'un capteur |
| `GET` | `/sensors/{id}/history` | Historique pour graphiques |

### Exemple de Requête

```bash
# Dernière valeur du capteur sensor_001
curl http://localhost:8000/sensors/last?sensor_id=sensor_001
```

```json
{
  "sensor_id": "sensor_001",
  "timestamp": "2026-01-07T19:31:35",
  "value": 22.69
}
```

### Documentation Interactive

Accédez à la documentation Swagger : http://localhost:8000/docs

---

## 📚 Documentation

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
