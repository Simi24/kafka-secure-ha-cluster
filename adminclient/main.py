import os
import time
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka.admin import KafkaAdminClient, NewTopic

print("Admin client script started")

def create_topic(topic_name, num_partitions, replication_factor, bootstrap_servers):
    admin_client = KafkaAdminClient(
        bootstrap_servers=bootstrap_servers,
        security_protocol="SSL",
        ssl_cafile="/etc/kafka/secrets/client.ca",
        ssl_certfile="/etc/kafka/secrets/client.crt",
        ssl_keyfile="/etc/kafka/secrets/client.key"
    )

    #TODO: Controllo del numero di broker disponibili
    #broker_count = len(admin_client.describe_cluster().brokers)

    topic_list = [NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
    
    try:
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"Topic '{topic_name}' creato con successo.")
    except Exception as e:
        print(f"Errore durante la creazione del topic '{topic_name}': {str(e)}")
    finally:
        admin_client.close()


def main():
    print("Entering main function")

    topic = 'test-topic'
    num_partitions = 3
    replication_factor = 3
    bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka1:19092,kafka2:19093,kafka3:19094').split(',')

    create_topic(topic, num_partitions, replication_factor, bootstrap_servers)

if __name__ == "__main__":
    print("Starting main function")
    main()