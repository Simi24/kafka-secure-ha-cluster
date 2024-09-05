import os
import time
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka.admin import KafkaAdminClient, NewTopic

print("Producer script started")

def create_topic(topic_name, num_partitions, replication_factor, bootstrap_servers):
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)

    topic_list = [NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
    
    try:
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"Topic '{topic_name}' creato con successo.")
    except Exception as e:
        print(f"Errore durante la creazione del topic '{topic_name}': {str(e)}")
    finally:
        admin_client.close()

def create_producer():
    retries = 10
    delay = 5
    bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka1:19092,kafka2:19093,kafka3:19094').split(',')
    
    for i in range(retries):
        try:
            print(f"Attempting to connect to Kafka brokers: {bootstrap_servers}")
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                security_protocol="SSL",
                ssl_check_hostname=True,
                ssl_cafile="pem/ca-root.pem",
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                key_serializer=lambda v: json.dumps(v, default=self.serialize).encode("utf-8"),
                api_version=(0, 10, 1),
                request_timeout_ms=300000,
                metadata_max_age_ms=300000,
                max_block_ms=300000
            )
            print("Successfully connected to Kafka")
            return producer
        except Exception as e:
            print(f"Failed to connect to Kafka. Retrying in {delay} seconds... Error: {str(e)}")
            time.sleep(delay)
    
    print("Failed to connect to Kafka after all retries")
    return None

def main():
    print("Entering main function")

    topic = 'test-topic'

    producer = create_producer()
    
    if producer is None:
        print("Failed to create producer. Exiting.")
        return
    
    while True:
        message = {'timestamp': int(time.time())}
        try:
            print(f"Attempting to send message: {message}")
            future = producer.send(topic, value=message)
            producer.flush()
            record_metadata = future.get(timeout=300)
            print(f"Successfully produced message to {record_metadata.topic} [{record_metadata.partition}] at offset {record_metadata.offset}")
        except Exception as e:
            print(f"Failed to produce message. Error: {str(e)}")
        
        time.sleep(5)

if __name__ == "__main__":
    print("Starting main function")
    main()