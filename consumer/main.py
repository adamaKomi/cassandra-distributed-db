import asyncio
import contextlib

from kafka_consumer import KafkaToCassandraConsumer
from settings import settings


async def main():
    consumer = KafkaToCassandraConsumer(
        kafka_bootstrap=settings.KAFKA_BOOTSTRAP,
        topic=settings.KAFKA_TOPIC,
        group_id=settings.KAFKA_GROUP_ID,
        cassandra_hosts=settings.CASSANDRA_HOSTS,
        cassandra_keyspace=settings.CASSANDRA_KEYSPACE,
        cassandra_username=settings.CASSANDRA_USERNAME,
        cassandra_password=settings.CASSANDRA_PASSWORD,
        batch_size=settings.CASSANDRA_BATCH_SIZE,
        poll_timeout_ms=settings.KAFKA_POLL_TIMEOUT_MS,
        cassandra_port=settings.CASSANDRA_PORT,
    )

    await consumer.start()
    print("Kafka → Cassandra consumer started (Ctrl+C pour arrêter).")

    task = asyncio.create_task(consumer.run_forever())
    try:
        await task
    except KeyboardInterrupt:
        print("Interruption demandée, arrêt en cours...")
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
        await consumer.stop()
        print("Consumer stopped.")


if __name__ == "__main__":
    asyncio.run(main())