Projet Démo – Base de Données NoSQL Distribuée (Cassandra)
Objectif du projet
Mettre en place une application de monitoring de capteurs dont la base de données Cassandra est distribuée sur 3 PC différents, et démontrer :
•	la réplication des données
•	la tolérance aux pannes
•	la continuité du service quand un nœud tombe
________________________________________
Architecture globale
PC 1 ─ Cassandra Node 1 (Seed)
PC 2 ─ Cassandra Node 2
PC 3 ─ Cassandra Node 3

PC 4 ─ Kafka
       ─ Simulateur de capteurs (Producer)
       ─ Service d’ingestion (Consumer)
       ─ API REST
       ─ Interface Web
Seule la base de données est distribuée.
________________________________________
Ce que NOUS devons développer (concret)
________________________________________
1 Base de données Cassandra 
À mettre en place
•	1 nœud Cassandra par PC (PC 1, PC 2, PC 3)
•	Les 3 nœuds forment un seul cluster
À configurer
•	Même cluster_name
•	Même seed node (PC 1)
•	Réplication sur 3 nœuds
Schéma de base (CQL)
CREATE KEYSPACE iot_demo
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 3
};

CREATE TABLE iot_demo.sensor_data (
  sensor_id text,
  timestamp timestamp,
  value double,
  PRIMARY KEY (sensor_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
Démonstration prévue
•	nodetool status
•	Arrêt d’un PC Cassandra → les données restent accessibles
________________________________________
2️ Simulateur de capteurs (Producer Kafka)
Rôle
Générer des données comme si des capteurs réels envoyaient des mesures.
À développer
•	Script Python
•	Envoi d’un message par seconde
•	Plusieurs capteurs simulés
Format des données
{
  "sensor_id": "sensor_01",
  "timestamp": "2026-01-04T10:00:01",
  "value": 22.7
}
Technologie
•	Kafka (1 broker suffit)
•	Producer Kafka en Python
________________________________________
3️  Service d’ingestion (Consumer Kafka → Cassandra)
Rôle
Recevoir les données depuis Kafka et les stocker dans Cassandra.
À développer
•	Service indépendant
•	Kafka Consumer
•	Connexion au cluster Cassandra (3 IP)
Fonctionnement
1.	Écoute le topic Kafka
2.	Parse le message JSON
3.	Insère dans Cassandra
👉 Ce service ne parle pas à l’API ni au frontend
________________________________________
4️  API REST (Lecture des données)
Rôle
Permettre à l’interface de consulter les données stockées.
À développer
•	API simple (FastAPI recommandé)
Endpoints minimum
GET /sensors
GET /sensors/{id}/latest
GET /sensors/{id}/history
Important
•	L’API lit uniquement Cassandra
•	Elle ne dépend pas de Kafka
________________________________________
5️	Interface Web (Visualisation)
Rôle
Rendre la démonstration compréhensible visuellement.
À développer
•	Interface simple (React ou HTML + JS)
•	Graphique des valeurs de capteurs
Fonctionnalités
•	Sélection d’un capteur
•	Courbe des valeurs (Chart.js)
•	Rafraîchissement automatique
 
________________________________________
Scénario de démonstration (le jour J)
1.	Les capteurs envoient des données
2.	Les graphiques se mettent à jour
3.	On éteint un PC Cassandra
4.	Le graphique continue
5.	nodetool status montre un nœud DOWN
________________________________________
 Répartition du travail conseillée
Rôle	Responsabilités
Infra	Cassandra cluster (3 PC)
Data	Producer Kafka
Backend	Consumer + API
Frontend	Interface graphique
________________________________________
⚠️ Points de vigilance
•	Tous les PC sur le même réseau
•	Firewall désactivé
•	IP fixes connues
•	Réplication = 3 (obligatoire)
________________________________________
🏁 Résultat attendu
•	Base NoSQL réellement distribuée
•	Démo claire et convaincante
•	Projet compréhensible même par un non-expert
