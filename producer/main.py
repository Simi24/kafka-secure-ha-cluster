import os
import time
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from circuitbreaker import circuit

print("Producer script started")

class KafkaMessageProducer:
    def __init__(self):
        self.producer = self.create_producer()

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def create_producer(self):
        print("Attempting to connect to Kafka brokers")
        bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka1:19092,kafka2:19093,kafka3:19094').split(',')
        
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

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @circuit(failure_threshold=5, recovery_timeout=30)
    def send_message(self, topic, message):
        print(f"Attempting to send message: {message}")
        future = self.producer.send(topic, value=message)
        self.producer.flush()
        record_metadata = future.get(timeout=300)
        print(f"Successfully produced message to {record_metadata.topic} [{record_metadata.partition}] at offset {record_metadata.offset}")

def main():
    print("Entering main function")

    topic = 'test-topic'
    producer = KafkaMessageProducer()

    while True:
        message = {'timestamp': int(time.time())}
        try:
            producer.send_message(topic, message)
        except Exception as e:
            print(f"Failed to produce message. Error: {str(e)}")
        
        time.sleep(5)

if __name__ == "__main__":
    print("Starting main function")
    main()