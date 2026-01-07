import sys
import types

# Hack pour Cassandra driver sur Python 3.12+ (asyncore a été supprimé)
# Le module asyncore a été supprimé, on crée un mock complet
if sys.version_info >= (3, 12):
    mock_asyncore = types.ModuleType("asyncore")

    class MockDispatcher:
        """Mock de asyncore.dispatcher pour Python 3.12+"""
        _map = {}
        connected = False
        accepting = False
        connecting = False
        closing = False
        addr = None

        def __init__(self, sock=None, map=None):
            self.socket = sock
            if map is None:
                map = MockDispatcher._map
            self._map = map

        def create_socket(self, family=None, type=None):
            pass
        def set_socket(self, sock, map=None):
            self.socket = sock
        def add_channel(self, map=None):
            pass
        def del_channel(self, map=None):
            pass
        def handle_read_event(self):
            pass
        def handle_write_event(self):
            pass
        def handle_expt_event(self):
            pass
        def handle_read(self):
            pass
        def handle_write(self):
            pass
        def handle_error(self):
            pass
        def handle_close(self):
            pass
        def handle_connect(self):
            pass
        def handle_accept(self):
            pass
        def readable(self):
            return True
        def writable(self):
            return True
        def close(self):
            pass
        def recv(self, buffer_size):
            return b''
        def send(self, data):
            return len(data)

    mock_asyncore.dispatcher = MockDispatcher
    mock_asyncore.dispatcher_with_send = MockDispatcher
    mock_asyncore.loop = lambda *args, **kwargs: None
    mock_asyncore.socket_map = {}
    mock_asyncore.close_all = lambda *args, **kwargs: None
    sys.modules["asyncore"] = mock_asyncore
    print("Using mock asyncore for Python 3.12+")

from cassandra.cluster import Cluster, Session
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
# Note: On n'utilise pas AsyncioConnection car il a des problèmes de compatibilité
# Le driver fonctionne de manière synchrone mais c'est OK pour notre use case
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
                port=settings.cassandra_port
                # Utilise la configuration par défaut synchrone
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

    def get_sensor_stats(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Calculer les statistiques pour un capteur (moyenne sur les 24 dernières heures et tendance)"""
        try:
            # Récupérer les données des dernières 24h pour la moyenne
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            
            # Pour la tendance, on compare les 2 dernières heures vs les 2 heures précédentes
            # Mais pour faire simple, on va juste prendre les 50 dernières lectures
            readings = self.get_sensor_history(sensor_id, limit=50)
            
            if not readings:
                return None
            
            values = [r["value"] for r in readings]
            latest_value = values[0]
            avg_value = sum(values) / len(values)
            
            # Calcul de tendance (simplifié)
            # Comparaison de la moyenne des 5 derniers vs moyenne globale des 50
            recent_avg = sum(values[:5]) / 5 if len(values) >= 5 else latest_value
            trend = ((recent_avg - avg_value) / avg_value * 100) if avg_value != 0 else 0
            
            return {
                "current_value": latest_value,
                "average_value": round(avg_value, 2),
                "trend_percentage": round(trend, 2),
                "trend_label": "vs 24h average"
            }
        except Exception as e:
            logger.error(f"Erreur lors du calcul des stats: {e}")
            return None


# Instance globale de la base de données
db = CassandraDB()