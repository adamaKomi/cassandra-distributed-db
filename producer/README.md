# Installation et configuration de Kafka

## ÉTAPE 1 — Télécharger Kafka
1. Rendez-vous sur le site officiel [Apache Kafka](https://kafka.apache.org/downloads).
2. Téléchargez la version binaire (ex : Scala 2.13).
3. Le fichier téléchargé aura un nom du type :
	 - `kafka_2.13-3.x.x.tgz`

## ÉTAPE 2 — Installer Kafka
### Sous Windows
- Décompressez le fichier `.tgz` (avec 7-Zip par exemple).
- Placez le dossier obtenu (ex : `kafka_2.13-3.x.x`) dans `C:\kafka\`.

### Sous Linux / macOS
```bash
tar -xzf kafka_2.13-3.x.x.tgz
cd kafka_2.13-3.x.x
```

## ÉTAPE 3 — Vérifier l'installation
Dans le dossier Kafka, vous devez voir :
- `bin/`
- `config/`
- `libs/`
Si le dossier `config/` est présent, Kafka est bien installé ✔️.

## ÉTAPE 4 — ZooKeeper
ZooKeeper est inclus dans Kafka, inutile de l’installer séparément.
Vous trouverez le fichier de configuration :
- `config/zookeeper.properties`

## ÉTAPE 5 — Démarrer ZooKeeper
### Windows
```bat
bin\windows\zookeeper-server-start.bat config\zookeeper.properties
```
### Linux / macOS
```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
```
Laissez ce terminal ouvert.

## ÉTAPE 6 — Démarrer Kafka
Ouvrez un autre terminal :
### Windows
```bat
bin\windows\kafka-server-start.bat config\server.properties
```
### Linux / macOS
```bash
bin/kafka-server-start.sh config/server.properties
```

## ÉTAPE 7 — Vérifier Kafka et créer le topic
### Vérifier que Kafka fonctionne
Ouvrez un nouveau terminal (Kafka doit être lancé) :
#### Windows
```bat
bin\windows\kafka-topics.bat --bootstrap-server localhost:9092 --list
```
#### Linux / macOS
```bash
bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```
Si la commande ne donne pas d’erreur, Kafka fonctionne ✔️ (la liste peut être vide).

### Créer le topic `sensor-data`
#### Windows
```bat
bin\windows\kafka-topics.bat --create 
	--topic sensor-data 
	--bootstrap-server localhost:9092 
	--partitions 1 
	--replication-factor 1
```
#### Linux / macOS
```bash
bin/kafka-topics.sh --create \
	--topic sensor-data \
	--bootstrap-server localhost:9092 \
	--partitions 1 \
	--replication-factor 1
```

### Vérifier que le topic existe
```bat
bin\windows\kafka-topics.bat --bootstrap-server localhost:9092 --list
```
Vous devez voir :
```
sensor-data
```
# Producer Kafka pour données de capteurs

Ce script Python simule l'envoi de données de capteurs vers un topic Kafka nommé `sensor-data`. Il génère des valeurs aléatoires pour 50 capteurs et publie les messages à intervalles réguliers.

## Fonctionnalités
- Génère des données simulées pour 50 capteurs
- Envoie les données au topic Kafka `sensor-data`
- Sérialise les messages au format JSON

## Prérequis
- Python 3.x
- Kafka en cours d'exécution sur `localhost:9092`
- Installation du package `kafka-python`

### Installation des dépendances
```bash
pip install kafka-python
```

## Utilisation
1. Assurez-vous que le serveur Kafka est démarré sur votre machine.
2. Lancez le script :
```bash
python producer.py
```

Le script enverra en continu des messages au topic Kafka. Pour arrêter le script, utilisez `Ctrl+C`.

## Configuration
- Le serveur Kafka est configuré par défaut sur `localhost:9092`. Modifiez la variable `bootstrap_servers` dans le script si besoin.
- Le topic utilisé est `sensor-data`.

## Exemple de message envoyé
```json
{
	"sensor_id": "sensor_001",
	"timestamp": "2026-01-07T12:34:56.789012",
	"value": 25.67
}
```

## Auteur
-  Binta TRAORE.

## Liens utiles
- [Documentation kafka-python](https://kafka-python.readthedocs.io/en/master/)
- [Apache Kafka](https://kafka.apache.org/)
producer