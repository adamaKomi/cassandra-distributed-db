# Guide Complet de Test du Cluster Cassandra Distribué

Ce guide détaille la mise en place et les tests d'un cluster Cassandra distribué sur **2 PCs physiques**, démontrant la réplication des données et la tolérance aux pannes.

---

## 📋 Table des Matières

1. [Prérequis](#1-prérequis)
2. [Architecture du Système](#2-architecture-du-système)
3. [Configuration Réseau](#3-configuration-réseau)
4. [Mise en Place du Cluster](#4-mise-en-place-du-cluster)
5. [Vérification du Cluster](#5-vérification-du-cluster)
6. [Scénarios de Test](#6-scénarios-de-test)
7. [Étendre le Cluster (Ajouter des Nœuds)](#7-étendre-le-cluster-ajouter-des-nœuds)
8. [Dépannage](#8-dépannage)

---

## 1. Prérequis

### Matériel
| Élément | PC 1 (Master/Seed) | PC 2 (Nœud) |
|---------|-------------------|-------------|
| RAM minimum | 8 Go | 4 Go |
| Espace disque | 10 Go libres | 5 Go libres |
| Réseau | Même réseau local (WiFi ou Ethernet) | Même réseau local |

### Logiciels (à installer sur les 2 PCs)
- **Docker Desktop** (version 4.x ou supérieure)
  - Téléchargement : https://www.docker.com/products/docker-desktop
- **Git** (optionnel, pour cloner le projet)

### Fichiers nécessaires
- **PC 1** : Tout le projet (dossier `noSqlProject/`)
- **PC 2** : Uniquement le fichier `docker-compose-cassandra-node.yml`

---

## 2. Architecture du Système

```
┌─────────────────────────────────────────────────────────────────┐
│                        RÉSEAU LOCAL                             │
│                      (192.168.1.0/24)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────┐    ┌─────────────────────────┐    │
│  │      PC 1 (Master)      │    │      PC 2 (Nœud)        │    │
│  │     192.168.1.6         │    │     192.168.1.42        │    │
│  │                         │    │                         │    │
│  │  ┌─────────────────┐    │    │  ┌─────────────────┐    │    │
│  │  │   Cassandra     │◄───┼────┼──►   Cassandra     │    │    │
│  │  │   (Seed)        │    │    │  │   (Node)        │    │    │
│  │  │   Port 9042     │    │    │  │   Port 9042     │    │    │
│  │  └─────────────────┘    │    │  └─────────────────┘    │    │
│  │           ▲             │    │                         │    │
│  │  ┌────────┴────────┐    │    └─────────────────────────┘    │
│  │  │     Kafka       │    │                                   │
│  │  │   Port 9092     │    │                                   │
│  │  └────────┬────────┘    │                                   │
│  │  ┌────────┴────────┐    │                                   │
│  │  │    Producer     │    │                                   │
│  │  │  (Génère data)  │    │                                   │
│  │  └────────┬────────┘    │                                   │
│  │  ┌────────┴────────┐    │                                   │
│  │  │    Consumer     │    │                                   │
│  │  │ (Écrit Cassandra│    │                                   │
│  │  └─────────────────┘    │                                   │
│  │  ┌─────────────────┐    │                                   │
│  │  │      API        │    │                                   │
│  │  │   Port 8000     │    │                                   │
│  │  └─────────────────┘    │                                   │
│  │  ┌─────────────────┐    │                                   │
│  │  │    Frontend     │    │                                   │
│  │  │   Port 5173     │    │                                   │
│  │  └─────────────────┘    │                                   │
│  └─────────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Ports utilisés

| Service | Port | Protocole | Description |
|---------|------|-----------|-------------|
| Cassandra CQL | 9042 | TCP | Requêtes client (API, Consumer) |
| Cassandra Gossip | 7000 | TCP | Communication inter-nœuds |
| Kafka | 9092 | TCP | Messages du Producer |
| API REST | 8000 | TCP | Endpoints FastAPI |
| Frontend | 5173 | TCP | Interface React/Vite |
| Kafka UI | 8888 | TCP | Interface de monitoring Kafka |

---

## 3. Configuration Réseau

### 3.1 Identifier les adresses IP

**Sur chaque PC**, ouvrez PowerShell et tapez :
```powershell
ipconfig | Select-String "IPv4"
```

Notez l'adresse IPv4 (ex: `192.168.1.6` pour PC1, `192.168.1.42` pour PC2).

### 3.2 Vérifier la connectivité

**Depuis le PC 2**, testez la connexion vers le PC 1 :
```powershell
Test-NetConnection -ComputerName 192.168.1.6 -Port 7000
```

> ⚠️ Si `TcpTestSucceeded: False`, désactivez temporairement le pare-feu Windows sur le PC 1.

### 3.3 Désactiver le pare-feu (si nécessaire)

Sur le PC concerné, ouvrez PowerShell **en administrateur** :
```powershell
# Désactiver temporairement
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Réactiver après les tests
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

---

## 4. Mise en Place du Cluster

### 4.1 PC 1 - Démarrage du Master (Seed)

1. **Ouvrez PowerShell** dans le dossier du projet :
   ```powershell
   cd C:\chemin\vers\noSqlProject
   ```

2. **Nettoyez l'environnement** (si relance) :
   ```powershell
   docker-compose down -v
   ```

3. **Lancez la stack complète** :
   ```powershell
   $env:HOST_IP="192.168.1.6"; docker-compose up -d
   ```
   > Remplacez `192.168.1.6` par l'IP réelle du PC 1.

4. **Attendez ~2 minutes** que Cassandra démarre complètement.

5. **Vérifiez que Cassandra est prêt** :
   ```powershell
   docker exec -it nosqlproject-cassandra-1 nodetool status
   ```
   
   Résultat attendu :
   ```
   UN  192.168.1.6  xxx KB  16  100.0%  ...
   ```

### 4.2 PC 2 - Rejoindre le Cluster

1. **Créez un dossier** et placez-y le fichier `docker-compose-cassandra-node.yml` :
   ```powershell
   mkdir C:\Cassandra
   cd C:\Cassandra
   ```

2. **Contenu du fichier** `docker-compose-cassandra-node.yml` :
   ```yaml
   services:
     cassandra-node:
       image: cassandra:4.1
       container_name: cassandra-node
       ports:
         - "9042:9042"
         - "7000:7000"
       environment:
         - CASSANDRA_CLUSTER_NAME=IoTCluster
         - CASSANDRA_LISTEN_ADDRESS=cassandra-node
         - CASSANDRA_BROADCAST_ADDRESS=${HOST_IP}
         - CASSANDRA_SEEDS=${SEED_IP}
         - CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch
         - HEAP_NEWSIZE=128M
         - MAX_HEAP_SIZE=1024M
   ```

3. **Nettoyez** (si relance) :
   ```powershell
   docker-compose -f docker-compose-cassandra-node.yml down -v
   ```

4. **Lancez le nœud** :
   ```powershell
   $env:HOST_IP="192.168.1.42"; $env:SEED_IP="192.168.1.6"; docker-compose -f docker-compose-cassandra-node.yml up -d
   ```
   > Remplacez les IPs par vos valeurs réelles.

5. **Surveillez les logs** :
   ```powershell
   docker logs -f cassandra-node
   ```
   
   Attendez le message : `Node /192.168.1.42 state jump to NORMAL`

---

## 5. Vérification du Cluster

### 5.1 Vérifier l'état du cluster

**Sur n'importe quel PC** :
```powershell
# Sur PC 1
docker exec -it nosqlproject-cassandra-1 nodetool status

# Sur PC 2
docker exec -it cassandra-node nodetool status
```

**Résultat attendu** (2 nœuds UP/Normal) :
```
Datacenter: dc1
===============
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address       Load       Tokens  Owns   Host ID                               Rack
UN  192.168.1.6   109 KiB    16      50.0%  07f5cf66-114c-4845-ae86-949b8a6577fc  rack1
UN  192.168.1.42  75 KiB     16      50.0%  3d86a714-25d6-440a-a522-df72a41d6093  rack1
```

### 5.2 Vérifier la réplication des données

**Sur PC 1**, vérifiez les données du pipeline IoT :
```powershell
docker exec -it nosqlproject-cassandra-1 cqlsh -e "SELECT * FROM iot_demo.sensor_data LIMIT 5;"
```

**Sur PC 2**, vérifiez que les mêmes données existent :
```powershell
docker exec -it cassandra-node cqlsh -e "SELECT * FROM iot_demo.sensor_data LIMIT 5;"
```

> ✅ Si les données sont identiques, la réplication fonctionne !

---

## 6. Scénarios de Test

### 6.1 Test de Réplication (Création de données)

**Objectif** : Prouver que les données écrites sur un nœud sont automatiquement copiées sur l'autre.

1. **Sur PC 1**, créez un keyspace de test avec réplication :
   ```powershell
   docker exec -it nosqlproject-cassandra-1 cqlsh
   ```
   
   ```sql
   CREATE KEYSPACE test_replication 
   WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 2};
   
   USE test_replication;
   
   CREATE TABLE messages (
       id int PRIMARY KEY,
       contenu text,
       source text
   );
   
   INSERT INTO messages (id, contenu, source) VALUES (1, 'Message créé sur PC1', 'PC1');
   ```

2. **Sur PC 2**, vérifiez que la donnée est arrivée :
   ```powershell
   docker exec -it cassandra-node cqlsh -e "SELECT * FROM test_replication.messages;"
   ```
   
   **Résultat attendu** :
   ```
    id | contenu              | source
   ----+----------------------+--------
     1 | Message créé sur PC1 | PC1
   ```

3. **Sur PC 2**, ajoutez une donnée :
   ```powershell
   docker exec -it cassandra-node cqlsh -e "INSERT INTO test_replication.messages (id, contenu, source) VALUES (2, 'Message créé sur PC2', 'PC2');"
   ```

4. **Sur PC 1**, vérifiez la synchro inverse :
   ```powershell
   docker exec -it nosqlproject-cassandra-1 cqlsh -e "SELECT * FROM test_replication.messages;"
   ```
   
   **Résultat attendu** : Les deux messages apparaissent.

---

### 6.2 Test de Tolérance aux Pannes (Failover)

**Objectif** : Prouver que le système continue de fonctionner si un nœud tombe.

#### Scénario A : Panne du Master (PC 1)

1. **Sur PC 1**, arrêtez Cassandra brutalement :
   ```powershell
   docker stop nosqlproject-cassandra-1
   ```

2. **Sur PC 2**, vérifiez que les données sont toujours accessibles :
   ```powershell
   docker exec -it cassandra-node cqlsh -e "SELECT * FROM test_replication.messages;"
   ```
   
   > ✅ Les données doivent s'afficher normalement.

3. **Sur PC 2**, essayez d'écrire une nouvelle donnée :
   ```powershell
   docker exec -it cassandra-node cqlsh -e "INSERT INTO test_replication.messages (id, contenu, source) VALUES (3, 'Écrit pendant la panne du PC1', 'PC2');"
   ```
   
   > ⚠️ Avec un `replication_factor=2` et un seul nœud actif, l'écriture peut échouer (quorum non atteint). C'est le comportement normal de Cassandra.

4. **Rallumez PC 1** :
   ```powershell
   docker start nosqlproject-cassandra-1
   ```

5. **Vérifiez la resynchronisation** (après ~30 secondes) :
   ```powershell
   docker exec -it nosqlproject-cassandra-1 nodetool status
   ```

#### Scénario B : Panne du Nœud Esclave (PC 2)

1. **Sur PC 2**, arrêtez Cassandra :
   ```powershell
   docker stop cassandra-node
   ```

2. **Sur PC 1**, les données restent accessibles :
   ```powershell
   docker exec -it nosqlproject-cassandra-1 cqlsh -e "SELECT * FROM test_replication.messages;"
   ```

3. **Rallumez PC 2** :
   ```powershell
   docker start cassandra-node
   ```

---

### 6.3 Test du Pipeline Complet (End-to-End)

**Objectif** : Valider que les données circulent de bout en bout.

```
Producer → Kafka → Consumer → Cassandra (PC1) → Réplication → Cassandra (PC2) → API → Frontend
```

1. **Vérifiez que le Producer envoie des messages** :
   ```powershell
   docker logs nosqlproject-producer-1 --tail 10
   ```

2. **Vérifiez que Kafka reçoit les messages** :
   - Ouvrez http://localhost:8888 (Kafka UI)
   - Naviguez vers Topics → `sensor-data`

3. **Vérifiez que le Consumer écrit dans Cassandra** :
   ```powershell
   docker logs nosqlproject-consumer-1 --tail 10
   ```

4. **Vérifiez les données dans Cassandra (PC 1)** :
   ```powershell
   docker exec -it nosqlproject-cassandra-1 cqlsh -e "SELECT COUNT(*) FROM iot_demo.sensor_data;"
   ```

5. **Vérifiez la réplication (PC 2)** :
   ```powershell
   docker exec -it cassandra-node cqlsh -e "SELECT COUNT(*) FROM iot_demo.sensor_data;"
   ```
   
   > Les deux compteurs doivent être identiques (ou très proches).

6. **Testez l'API** :
   - Ouvrez http://localhost:8000/docs
   - Essayez l'endpoint `/sensors/last?sensor_id=sensor_001`

7. **Testez le Frontend** :
   - Ouvrez http://localhost:5173
   - Les données des capteurs doivent s'afficher

---

## 7. Étendre le Cluster (Ajouter des Nœuds)

Cette section explique comment ajouter un **3ème, 4ème PC** (ou plus) au cluster existant.

### 7.1 Principe de l'Extension

Cassandra est conçu pour l'extension horizontale (scale-out). Ajouter un nœud est simple :
1. Le nouveau PC démarre Cassandra avec l'IP d'un nœud existant comme "Seed"
2. Il contacte le Seed via le protocole Gossip (port 7000)
3. Le Seed lui transmet la topologie du cluster
4. Le nouveau nœud s'annonce et reçoit une partie des données (rééquilibrage automatique)

```
AVANT (2 nœuds)                    APRÈS (3 nœuds)
┌─────────┐    ┌─────────┐         ┌─────────┐    ┌─────────┐    ┌─────────┐
│  PC 1   │◄──►│  PC 2   │    →    │  PC 1   │◄──►│  PC 2   │◄──►│  PC 3   │
│  Seed   │    │  Node   │         │  Seed   │    │  Node   │    │  Node   │
│  50%    │    │  50%    │         │  33%    │    │  33%    │    │  33%    │
└─────────┘    └─────────┘         └─────────┘    └─────────┘    └─────────┘
```

### 7.2 Prérequis pour le Nouveau PC

| Élément | Valeur |
|---------|--------|
| RAM minimum | 4 Go |
| Docker Desktop | Installé et fonctionnel |
| Réseau | Même réseau local que PC 1 et PC 2 |
| Fichier requis | `docker-compose-cassandra-node.yml` |

### 7.3 Procédure d'Ajout (PC 3, PC 4, etc.)

#### Étape 1 : Identifier l'IP du nouveau PC

Sur le **nouveau PC**, ouvrez PowerShell :
```powershell
ipconfig | Select-String "IPv4"
```
> Exemple : `192.168.1.100`

#### Étape 2 : Vérifier la connectivité vers le Seed

```powershell
Test-NetConnection -ComputerName 192.168.1.6 -Port 7000
```
> Doit afficher `TcpTestSucceeded: True`

#### Étape 3 : Créer le dossier et le fichier de configuration

```powershell
mkdir C:\Cassandra
cd C:\Cassandra
```

Créez le fichier `docker-compose-cassandra-node.yml` avec ce contenu :

```yaml
services:
  cassandra-node:
    image: cassandra:4.1
    container_name: cassandra-node
    ports:
      - "9042:9042"
      - "7000:7000"
    environment:
      - CASSANDRA_CLUSTER_NAME=IoTCluster
      - CASSANDRA_LISTEN_ADDRESS=cassandra-node
      - CASSANDRA_BROADCAST_ADDRESS=${HOST_IP}
      - CASSANDRA_SEEDS=${SEED_IP}
      - CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch
      - HEAP_NEWSIZE=128M
      - MAX_HEAP_SIZE=1024M
```

#### Étape 4 : Lancer le nouveau nœud

```powershell
# Remplacez par vos vraies IPs :
# - HOST_IP = IP de CE nouveau PC
# - SEED_IP = IP du PC 1 (Master)

$env:HOST_IP="192.168.1.100"; $env:SEED_IP="192.168.1.6"; docker-compose -f docker-compose-cassandra-node.yml up -d
```

#### Étape 5 : Vérifier l'intégration

Attendez 2-3 minutes, puis vérifiez sur n'importe quel PC :
```powershell
docker exec -it nosqlproject-cassandra-1 nodetool status
```

**Résultat attendu** (3 nœuds UP/Normal) :
```
Datacenter: dc1
===============
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address        Load       Tokens  Owns   Host ID   Rack
UN  192.168.1.6    109 KiB    16      33.3%  ...       rack1
UN  192.168.1.42   75 KiB     16      33.3%  ...       rack1
UN  192.168.1.100  50 KiB     16      33.3%  ...       rack1
```

### 7.4 Ajuster le Facteur de Réplication

Après avoir ajouté des nœuds, vous pouvez augmenter le facteur de réplication pour plus de redondance.

**Exemple** : Passer de `replication_factor: 2` à `replication_factor: 3`

```sql
-- Sur n'importe quel nœud, via cqlsh
ALTER KEYSPACE iot_demo 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3};
```

Puis lancez une réparation pour redistribuer les données :
```powershell
docker exec -it nosqlproject-cassandra-1 nodetool repair iot_demo
```

### 7.5 Tableau des Configurations Recommandées

| Nombre de Nœuds | Replication Factor | Tolérance aux Pannes |
|-----------------|-------------------|----------------------|
| 2 | 2 | 0 nœud (lecture seule si 1 tombe) |
| 3 | 3 | 1 nœud peut tomber |
| 4 | 3 | 1 nœud peut tomber |
| 5 | 3 | 1 nœud peut tomber |
| 5 | 5 | 2 nœuds peuvent tomber |

> **Règle d'or** : Pour tolérer N pannes, il faut au minimum `2N + 1` nœuds avec un `replication_factor` de `N + 1` ou plus.

### 7.6 Retirer un Nœud du Cluster

Si vous voulez retirer proprement un PC du cluster :

#### Option A : Retrait planifié (le nœud est accessible)

Sur le nœud à retirer :
```powershell
docker exec -it cassandra-node nodetool decommission
```
Attendez que la commande se termine (peut prendre plusieurs minutes).
Puis arrêtez le conteneur :
```powershell
docker-compose -f docker-compose-cassandra-node.yml down -v
```

#### Option B : Retrait forcé (le nœud est mort/inaccessible)

Sur un nœud **actif** du cluster :
```powershell
# Remplacez par l'IP du nœud mort
docker exec -it nosqlproject-cassandra-1 nodetool removenode <Host_ID>
```

Pour trouver le `Host_ID` :
```powershell
docker exec -it nosqlproject-cassandra-1 nodetool status
```
C'est la longue chaîne UUID dans la colonne "Host ID".

### 7.7 Architecture Multi-Datacenter (Avancé)

Pour une architecture plus robuste (production), vous pouvez configurer plusieurs datacenters logiques :

```yaml
environment:
  - CASSANDRA_DC=datacenter1           # ou datacenter2
  - CASSANDRA_RACK=rack1
  - CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch
```

Et créer un keyspace avec réplication par datacenter :
```sql
CREATE KEYSPACE production 
WITH replication = {
  'class': 'NetworkTopologyStrategy', 
  'datacenter1': 2, 
  'datacenter2': 2
};
```

---

## 8. Dépannage

### Erreur : "Connection refused" sur le port 7000

**Cause** : Le pare-feu bloque la communication inter-nœuds.

**Solution** :
```powershell
# Sur le PC qui bloque
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
```

---

### Erreur : "A node with address X already exists"

**Cause** : Le cluster garde en mémoire l'ancien nœud.

**Solution** : Ajouter l'option de remplacement sur le PC 2 :
```powershell
$env:JVM_EXTRA_OPTS="-Dcassandra.replace_address=192.168.1.42"
docker-compose -f docker-compose-cassandra-node.yml up -d
```
> Retirez cette option après le premier démarrage réussi.

---

### Erreur : "No nodes present in the cluster"

**Cause** : Cassandra n'a pas fini de démarrer.

**Solution** : Attendez 1-2 minutes et réessayez.

---

### Le conteneur s'arrête immédiatement

**Cause possible 1** : Données corrompues d'une tentative précédente.
```powershell
docker-compose -f docker-compose-cassandra-node.yml down -v
```

**Cause possible 2** : Pas assez de RAM.
Ajoutez dans le docker-compose :
```yaml
environment:
  - MAX_HEAP_SIZE=512M
  - HEAP_NEWSIZE=128M
```

---

### Les données ne se répliquent pas

**Cause** : Le keyspace a été créé avec `replication_factor: 1`.

**Solution** : Modifiez le keyspace :
```sql
ALTER KEYSPACE iot_demo 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 2};
```

Puis forcez la réparation :
```powershell
docker exec -it nosqlproject-cassandra-1 nodetool repair iot_demo
```

---

## 📊 Résumé des Commandes Essentielles

| Action | Commande |
|--------|----------|
| Démarrer PC 1 | `$env:HOST_IP="192.168.1.6"; docker-compose up -d` |
| Démarrer PC 2 | `$env:HOST_IP="192.168.1.42"; $env:SEED_IP="192.168.1.6"; docker-compose -f docker-compose-cassandra-node.yml up -d` |
| Voir l'état du cluster | `docker exec -it <container> nodetool status` |
| Voir les données | `docker exec -it <container> cqlsh -e "SELECT * FROM iot_demo.sensor_data LIMIT 5;"` |
| Voir les logs | `docker logs -f <container>` |
| Arrêter proprement | `docker-compose down` |
| Tout effacer (reset) | `docker-compose down -v` |

---

## ✅ Checklist de Validation

- [ ] Les 2 PCs se pingent mutuellement
- [ ] `nodetool status` affiche 2 lignes `UN`
- [ ] Les données de `iot_demo.sensor_data` sont identiques sur les 2 PCs
- [ ] L'arrêt de PC 1 n'empêche pas la lecture sur PC 2
- [ ] L'API répond sur http://localhost:8000/docs
- [ ] Le Frontend affiche les données des capteurs

---

*Guide créé le 7 janvier 2026 - Projet NoSQL IoT Monitoring*
