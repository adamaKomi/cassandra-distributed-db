"""
Gestion de la connexion à Cassandra
"""
from cassandra.cluster import Cluster, Session
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from config import settings

logger = logging.getLogger(__name__)


class CassandraDB:
    """Gestionnaire de connexion à Cassandra"""
    
    def __init__(self):
        self.cluster: Optional[Cluster] = None
        self.session: Optional[Session] = None
        
    def connect(self):
        """Établir la connexion au cluster Cassandra"""
        try:
            logger.info(f"Connexion au cluster Cassandra: {settings.cassandra_hosts}")
            
            # Connexion au cluster (sans authentification pour une démo)
            self.cluster = Cluster(
                contact_points=settings.cassandra_hosts,
                port=settings.cassandra_port,
                protocol_version=4
            )
            
            self.session = self.cluster.connect()
            
            # Utilisation du keyspace
            self.session.set_keyspace(settings.cassandra_keyspace)
            
            logger.info("Connexion à Cassandra réussie")
            
        except Exception as e:
            logger.error(f"Erreur de connexion à Cassandra: {e}")
            raise
    
    def disconnect(self):
        """Fermer la connexion"""
        if self.session:
            self.session.shutdown()
        if self.cluster:
            self.cluster.shutdown()
        logger.info("Connexion à Cassandra fermée")
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Obtenir le statut du cluster"""
        if not self.cluster:
            return {"connected": False, "nodes": []}
        
        metadata = self.cluster.metadata
        nodes = []
        
        for host in metadata.all_hosts():
            nodes.append({
                "address": str(host.address),
                "datacenter": host.datacenter,
                "rack": host.rack,
                "is_up": host.is_up
            })
        
        return {
            "connected": True,
            "nodes": nodes,
            "keyspace": settings.cassandra_keyspace
        }
    
    def get_all_sensors(self) -> List[str]:
        """Obtenir la liste de tous les capteurs"""
        query = "SELECT DISTINCT sensor_id FROM sensor_data"
        
        try:
            rows = self.session.execute(query)
            return [row.sensor_id for row in rows]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des capteurs: {e}")
            return []
    
    def get_latest_reading(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Obtenir la dernière lecture d'un capteur"""
        query = """
        SELECT sensor_id, timestamp, value 
        FROM sensor_data 
        WHERE sensor_id = %s 
        LIMIT 1
        """
        
        try:
            rows = self.session.execute(query, (sensor_id,))
            row = rows.one()
            
            if row:
                return {
                    "sensor_id": row.sensor_id,
                    "timestamp": row.timestamp,
                    "value": row.value
                }
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la dernière lecture: {e}")
            return None
    
    def get_sensor_history(
        self, 
        sensor_id: str, 
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Obtenir l'historique d'un capteur"""
        
        # Construction de la requête selon les paramètres
        if start_time and end_time:
            query = """
            SELECT sensor_id, timestamp, value 
            FROM sensor_data 
            WHERE sensor_id = %s 
            AND timestamp >= %s 
            AND timestamp <= %s 
            LIMIT %s
            """
            params = (sensor_id, start_time, end_time, limit)
        elif start_time:
            query = """
            SELECT sensor_id, timestamp, value 
            FROM sensor_data 
            WHERE sensor_id = %s 
            AND timestamp >= %s 
            LIMIT %s
            """
            params = (sensor_id, start_time, limit)
        else:
            query = """
            SELECT sensor_id, timestamp, value 
            FROM sensor_data 
            WHERE sensor_id = %s 
            LIMIT %s
            """
            params = (sensor_id, limit)
        
        try:
            rows = self.session.execute(query, params)
            
            return [
                {
                    "sensor_id": row.sensor_id,
                    "timestamp": row.timestamp,
                    "value": row.value
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique: {e}")
            return []


# Instance globale de la base de données
db = CassandraDB()
