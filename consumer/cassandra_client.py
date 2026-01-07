import sys
import types

# Patch asyncore manquant en Python 3.12+ (3.13 inclus)
# Le module asyncore a été supprimé, on crée un mock complet
if sys.version_info >= (3, 12):
    mock_asyncore = types.ModuleType("asyncore")
    
    class MockDispatcher:
        """Mock de asyncore.dispatcher pour Python 3.12+"""
        def __init__(self, sock=None, map=None):
            pass
        def create_socket(self, family=None, type=None):
            pass
        def set_socket(self, sock, map=None):
            pass
        def add_channel(self, map=None):
            pass
        def del_channel(self, map=None):
            pass
        def handle_read(self):
            pass
        def handle_write(self):
            pass
        def handle_error(self):
            pass
        def handle_close(self):
            pass
        def close(self):
            pass
    
    mock_asyncore.dispatcher = MockDispatcher
    mock_asyncore.loop = lambda *args, **kwargs: None
    mock_asyncore.socket_map = {}
    sys.modules["asyncore"] = mock_asyncore

from typing import List

from cassandra.cluster import Cluster, Session
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import PreparedStatement, BatchStatement, ConsistencyLevel
# Note: On n'utilise pas AsyncioConnection car il a des problèmes de compatibilité
# Le driver fonctionne de manière synchrone mais c'est OK pour notre use case
import time
import logging

logger = logging.getLogger(__name__)

from models import SensorReading


class CassandraWriter:
    def __init__(
        self,
        hosts: List[str],
        keyspace: str,
        port: int = 9042,
        username: str | None = None,
        password: str | None = None,
    ):
        self.hosts = hosts
        self.port = port
        self.keyspace = keyspace
        self.username = username
        self.password = password

        self.cluster: Cluster | None = None
        self.session: Session | None = None
        self.insert_stmt: PreparedStatement | None = None

    async def connect(self):
        auth_provider = None
        if self.username and self.password:
            auth_provider = PlainTextAuthProvider(username=self.username, password=self.password)

        # Retry loop for initial connection
        connected = False
        while not connected:
            try:
                # Création du cluster à chaque tentative pour éviter "Cluster is already shut down"
                self.cluster = Cluster(
                    contact_points=self.hosts,
                    port=self.port,
                    auth_provider=auth_provider,
                    # Pas de connection_class spécifique, utilise le défaut synchrone
                    connect_timeout=10.0,
                )
                
                # On se connecte d'abord sans keyspace pour créer le schéma si besoin
                self.session = self.cluster.connect()
                self._init_schema()
                # On bascule sur le keyspace cible
                self.session.set_keyspace(self.keyspace)
                connected = True
                print(f"Connecté à Cassandra (Keyspace: {self.keyspace})")
                
            except Exception as e:
                print(f"En attente de Cassandra... ({e})")
                try:
                    if self.cluster:
                        self.cluster.shutdown()
                except:
                    pass
                time.sleep(2)

        self.insert_stmt = self.session.prepare(
            """
            INSERT INTO sensor_data (sensor_id, timestamp, value)
            VALUES (?, ?, ?)
            """
        )
        self.insert_stmt.consistency_level = ConsistencyLevel.LOCAL_QUORUM

    def _init_schema(self):
        """Initialise le Keyspace et la Table si inexistants."""
        if not self.session:
            return

        # CORRECTION : Récupération dynamique du facteur de réplication
        # On lit la variable d'env ici pour éviter de modifier toute la chaîne d'appels (main -> consumer -> writer)
        import os
        replication_factor = int(os.getenv("CASSANDRA_REPLICATION_FACTOR", "1"))

        print(f"Initialisation Schema -> Keyspace: {self.keyspace}, RF: {replication_factor}")

        # Création du Keyspace adaptée au nombre de nœuds réels
        self.session.execute(
            f"""
            CREATE KEYSPACE IF NOT EXISTS {self.keyspace}
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': {replication_factor}}}
            """
        )

        # Création de la Table (Pas de changement ici)
        self.session.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.keyspace}.sensor_data (
                sensor_id text,
                timestamp timestamp,
                value double,
                PRIMARY KEY (sensor_id, timestamp)
            ) WITH CLUSTERING ORDER BY (timestamp DESC)
            """
        )

    async def write_batch(self, readings: List[SensorReading]):
        if not self.session or not self.insert_stmt:
            raise RuntimeError("Cassandra session not initialized")

        batch = BatchStatement(consistency_level=ConsistencyLevel.LOCAL_QUORUM)
        for reading in readings:
            batch.add(self.insert_stmt, (reading.sensor_id, reading.timestamp, reading.value))

        self.session.execute(batch)

    async def close(self):
        if self.cluster:
            self.cluster.shutdown()