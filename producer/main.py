import os
import time
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka.admin import KafkaAdminClient, NewTopic

print("Producer script started")

def create_producer():
    retries = 10
    delay = 5
    bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka1:19092,kafka2:19093,kafka3:19094').split(',')
    
    for i in range(retries):
        try:
            print(f"Attempting to connect to Kafka brokers: {bootstrap_servers}")
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                security_protocol="SASL_SSL",
                ssl_check_hostname=True,
                ssl_cafile="/etc/kafka/secrets/client.ca",
                ssl_certfile="/etc/kafka/secrets/client.crt",
                ssl_keyfile="/etc/kafka/secrets/client.key",
                sasl_mechanism="PLAIN",
                sasl_plain_username=os.environ.get('KAFKA_SASL_USERNAME'),
                sasl_plain_password=os.environ.get('KAFKA_SASL_PASSWORD'),
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                key_serializer=lambda v: json.dumps(v).encode('utf-8'),
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