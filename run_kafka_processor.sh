#!/bin/bash

echo "Starting Kafka Fleet Processor"
echo "============================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python3 -c "import psycopg2, requests, kafka" 2>/dev/null; then
    echo "Dependencies not installed. Installing now..."
    pip3 install psycopg2-binary requests kafka-python
fi

# Check if Docker services are running
if ! docker ps | grep -q "kafka"; then
    echo "Docker services not running. Please start services first:"
    echo "   docker compose up -d"
    exit 1
fi

echo "All checks passed. Starting Kafka processor..."
echo "This processor will consume GPS data from Kafka and process geofence events"
echo "Check Grafana Dashboard: http://localhost:3000"
echo "Make sure the producer is running: ./run_producer.sh"
echo ""

# Run the Kafka processor
python3 kafka_processor.py 