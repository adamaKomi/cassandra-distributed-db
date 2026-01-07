import sys
import types

# Patch asyncore manquant en Python 3.12+ (3.13 inclus)
if sys.version_info >= (3, 12):
    mock_asyncore = types.ModuleType("asyncore")
    mock_asyncore.dispatcher = object
    mock_asyncore.loop = lambda *args, **kwargs: None
    sys.modules["asyncore"] = mock_asyncore

from typing import List

from cassandra.cluster import Cluster, Session
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import PreparedStatement, BatchStatement, ConsistencyLevel
from cassandra.io.asyncioreactor import AsyncioConnection

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

        self.cluster = Cluster(
            contact_points=self.hosts,
            port=self.port,
            auth_provider=auth_provider,
            connection_class=AsyncioConnection,  # reactor asyncio
            connect_timeout=10.0,
        )
        self.session = self.cluster.connect(self.keyspace)
        self.insert_stmt = self.session.prepare(
            """
            INSERT INTO sensor_data (sensor_id, timestamp, value)
            VALUES (?, ?, ?)
            """
        )
        self.insert_stmt.consistency_level = ConsistencyLevel.LOCAL_QUORUM

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