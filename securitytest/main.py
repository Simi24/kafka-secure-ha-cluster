import os
import time
import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError

print("Consumer hacker script started")

class KafkaMessageConsumer:
    def __init__(self, topic):
        self.topic = topic
        self.consumer = self.create_consumer()

    def create_consumer(self):
        print(f"Attempting to connect to Kafka brokers")
        bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka1:19092,kafka2:19093,kafka3:19094').split(',')
        
        consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=bootstrap_servers,
            security_protocol="SASL_SSL",
            ssl_check_hostname=True,
            ssl_cafile="/etc/kafka/secrets/client.ca",
            ssl_certfile="/etc/kafka/secrets/client.crt",
            ssl_keyfile="/etc/kafka/secrets/client.key",
            sasl_mechanism="PLAIN",
            sasl_plain_username=os.environ.get('KAFKA_SASL_USERNAME'),
            sasl_plain_password=os.environ.get('KAFKA_SASL_PASSWORD'),
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

    def consume_message(self):
        try:
            message = next(self.consumer)
            print(f"Received message: {message.value}")
            return message.value
        except StopIteration:
            print("No messages available")
            return None
        except Exception as e:
            print(f"Error consuming message: {str(e)}")
            raise

    def close(self):
        if self.consumer:
            self.consumer.close()
            print("KafkaConsumer closed.")

def main():
    print("Entering main function")
    topic = 'test-topic'
    consumer = KafkaMessageConsumer(topic)

    try:
        while True:
            try:
                consumer.consume_message()
            except Exception as e:
                print(f"Error in message consumption loop: {str(e)}")
                # Wait before retrying
                time.sleep(5)
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()

if __name__ == "__main__":
    print("Starting main function")
    main()