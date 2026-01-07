import json
from typing import List
import asyncio
from aiokafka import AIOKafkaConsumer

from cassandra_client import CassandraWriter
from models import SensorReading


class KafkaToCassandraConsumer:
    def __init__(
        self,
        kafka_bootstrap: str,
        topic: str,
        group_id: str,
        cassandra_hosts: List[str],
        cassandra_keyspace: str,
        cassandra_username: str | None,
        cassandra_password: str | None,
        batch_size: int,
        poll_timeout_ms: int,
        cassandra_port: int = 9042,
    ):
        self.kafka_bootstrap = kafka_bootstrap
        self.topic = topic
        self.group_id = group_id
        self.batch_size = batch_size
        self.poll_timeout_ms = poll_timeout_ms

        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.kafka_bootstrap,
            group_id=self.group_id,
            value_deserializer=lambda v: v.decode("utf-8"),
            enable_auto_commit=False,
            auto_offset_reset="latest",
        )
        self.writer = CassandraWriter(
            hosts=cassandra_hosts,
            keyspace=cassandra_keyspace,
            port=cassandra_port,
            username=cassandra_username,
            password=cassandra_password,
        )

    async def start(self):
        await self.writer.connect()
        await self.consumer.start()

    async def stop(self):
        try:
            await self.consumer.stop()
        finally:
            await self.writer.close()

    async def run_once(self):
        msgs = await self.consumer.getmany(timeout_ms=self.poll_timeout_ms, max_records=self.batch_size)
        records: list[SensorReading] = []

        for tp, batch in msgs.items():
            for msg in batch:
                try:
                    payload = json.loads(msg.value)
                    records.append(SensorReading.from_dict(payload))
                except Exception as exc:
                    print(f"[WARN] Skipping bad message: {exc} | raw={msg.value}")

        if records:
            await self.writer.write_batch(records)
            await self.consumer.commit()

    async def run_forever(self):
        while True:
            await self.run_once()
            await asyncio.sleep(0)