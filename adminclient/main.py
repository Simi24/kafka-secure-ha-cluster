import os
import time
import json
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError, TopicAlreadyExistsError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from circuitbreaker import circuit

print("Admin client script started")

class KafkaAdminManager:
    def __init__(self):
        self.admin_client = self.create_admin_client()

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def create_admin_client(self):
        print("Attempting to create KafkaAdminClient")
        bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka1:19092,kafka2:19093,kafka3:19094').split(',')
        
        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            security_protocol="SASL_SSL",
            ssl_cafile="/etc/kafka/secrets/client.ca",
            ssl_certfile="/etc/kafka/secrets/client.crt",
            ssl_keyfile="/etc/kafka/secrets/client.key",
            sasl_mechanism="PLAIN",
            sasl_plain_username=os.environ.get('KAFKA_SASL_USERNAME'),
            sasl_plain_password=os.environ.get('KAFKA_SASL_PASSWORD'),
        )
        print("Successfully created KafkaAdminClient")
        return admin_client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @circuit(failure_threshold=5, recovery_timeout=30)
    def create_topic(self, topic_name, num_partitions, replication_factor):
        print(f"Attempting to create topic '{topic_name}'")
        
        # Check number of available brokers
        cluster_metadata = self.admin_client.describe_cluster()
        broker_count = len(cluster_metadata.brokers)
        print(f"Number of available brokers: {broker_count}")

        if replication_factor > broker_count:
            print(f"Warning: Requested replication factor ({replication_factor}) is greater than the number of available brokers ({broker_count}). Setting replication factor to {broker_count}.")
            replication_factor = broker_count

        topic_list = [NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
        
        try:
            self.admin_client.create_topics(new_topics=topic_list, validate_only=False)
            print(f"Topic '{topic_name}' created successfully.")
        except TopicAlreadyExistsError:
            print(f"Topic '{topic_name}' already exists.")
        except Exception as e:
            print(f"Error creating topic '{topic_name}': {str(e)}")
            raise

    def close(self):
        if self.admin_client:
            self.admin_client.close()
            print("KafkaAdminClient closed.")

def main():
    print("Entering main function")

    topic = 'test-topic'
    num_partitions = 3
    replication_factor = 3

    admin_manager = KafkaAdminManager()

    try:
        admin_manager.create_topic(topic, num_partitions, replication_factor)
    except Exception as e:
        print(f"Failed to create topic. Error: {str(e)}")
    finally:
        admin_manager.close()

if __name__ == "__main__":
    print("Starting main function")
    main()