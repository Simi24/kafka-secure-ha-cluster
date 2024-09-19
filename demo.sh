echo "Starting demo"

konsole --noclose -e bash -c "docker-compose up --build --remove-orphans" 2>/dev/null &

echo "Waiting for Kafka to be ready"
{
  for pc in $(seq 1 100); do
    echo -ne "$pc%\033[0K\r"
    sleep 0.6
  done
  echo
}

# Open a terminal to see logs for each service
konsole --noclose -e bash -c "docker-compose logs -f adminclient" 2>/dev/null &
konsole --noclose -e bash -c "docker-compose logs -f consumer" 2>/dev/null &
konsole --noclose -e bash -c "docker-compose logs -f producer" 2>/dev/null &

sleep 15

echo "Fault tolerance demo"
echo "Stopping Kafka broker 1"
docker-compose stop kafka1

echo "Waiting to see if Kafka is still working"
{
  for pc in $(seq 1 100); do
    echo -ne "$pc%\033[0K\r"
    sleep 0.3
  done
  echo
}

echo "Starting Kafka broker 1"
docker-compose start kafka1
echo "Waiting to see if Kafka is still working after broker 1 is back"

{
  for pc in $(seq 1 100); do
    echo -ne "$pc%\033[0K\r"
    sleep 0.3
  done
  echo
}

echo "Trying to connect a new malicius consumer with wrong password"
konsole --noclose -e bash -c "docker-compose -f docker-compose.security-test.yml up --build" 2>/dev/null &

echo "Waiting to see if Kafka is still working after the malicius consumer"
{
  for pc in $(seq 1 100); do
    echo -ne "$pc%\033[0K\r"
    sleep 0.3
  done
  echo
}

echo "Stopping the malicius consumer"
docker-compose -f docker-compose.security-test.yml down

sleep 5

echo "Demo finished!!!!"
docker-compose down