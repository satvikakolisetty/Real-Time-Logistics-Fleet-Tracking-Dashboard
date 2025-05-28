#!/bin/bash

echo "Fleet Tracking System - Quick Status Check"
echo "========================================="

# Check Docker
echo "Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo "OK - Docker is running"
else
    echo "ERROR - Docker is not running"
    exit 1
fi

# Check Docker Compose
echo "Checking Docker Compose..."
if docker compose version > /dev/null 2>&1; then
    echo "OK - Docker Compose is available"
else
    echo "ERROR - Docker Compose not found"
    exit 1
fi

# Check running services
echo "Checking running services..."
if docker compose ps | grep -q "Up"; then
    echo "OK - Services are running"
    docker compose ps
else
    echo "WARNING - No services running"
    echo "Start services with: docker compose up -d"
fi

# Check Kafka topic
echo "Checking Kafka topic..."
if docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092 | grep -q "gps_data"; then
    echo "OK - Kafka topic 'gps_data' exists"
else
    echo "WARNING - Kafka topic 'gps_data' not found"
fi

echo ""
echo "System Access URLs:"
echo "- Grafana Dashboard: http://localhost:3000 (admin/admin)"
echo "- InfluxDB: http://localhost:8086"
echo "- Flink Web UI: http://localhost:8081"
echo ""
echo "To start data generation: ./run_producer.sh"
echo "To start data processing: ./run_kafka_processor.sh" 