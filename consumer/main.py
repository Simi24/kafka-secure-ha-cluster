import os
import time
import json
from kafka import KafkaConsumer

print("Consumer script started")

def create_consumer():
    retries = 10
    delay = 5
    bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(',')
    
    for i in range(retries):
        try:
            print(f"Attempting to connect to Kafka brokers: {bootstrap_servers}")
            consumer = KafkaConsumer(
                'test-topic',
                bootstrap_servers=bootstrap_servers,
                security_protocol="SSL",
                ssl_check_hostname=True,
                ssl_cafile="/etc/kafka/secrets/client.ca",
                ssl_certfile="/etc/kafka/secrets/client.crt",
                ssl_keyfile="/etc/kafka/secrets/client.key",
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='my-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                api_version=(0, 10, 1),
                request_timeout_ms=300000,
                metadata_max_age_ms=300000,
                max_poll_records=10
            )
            print("Successfully connected to Kafka")
            return consumer
        except Exception as e:
            print(f"Failed to connect to Kafka. Retrying in {delay} seconds... Error: {str(e)}")
            time.sleep(delay)
    
    print("Failed to connect to Kafka after all retries")
    return None

def main():
    print("Entering main function")
    consumer = create_consumer()
    
    if consumer is None:
        print("Failed to create consumer. Exiting.")
        return
    
    for message in consumer:
        print(f"Received message: {message.value}")

if __name__ == "__main__":
    print("Starting main function")
    main()