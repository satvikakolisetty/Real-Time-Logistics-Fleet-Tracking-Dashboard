#!/bin/bash

echo "Checking Fleet Tracking System Services"
echo "======================================"

# Check Grafana
echo "Checking Grafana Dashboard..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "OK - Grafana Dashboard: http://localhost:3000 (admin/admin)"
else
    echo "ERROR - Grafana Dashboard: Not accessible"
fi

# Check InfluxDB
echo "Checking InfluxDB..."
if curl -s http://localhost:8086 > /dev/null; then
    echo "OK - InfluxDB UI: http://localhost:8086"
else
    echo "ERROR - InfluxDB UI: Not accessible"
fi

# Check Flink Web UI
echo "Checking Flink Web UI..."
if curl -s http://localhost:8081 > /dev/null; then
    echo "OK - Flink Web UI: http://localhost:8081"
else
    echo "ERROR - Flink Web UI: Not accessible"
fi

# Check Kafka
echo "Checking Kafka..."
if docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092 > /dev/null 2>&1; then
    echo "OK - Kafka: localhost:9092 (gps_data topic available)"
else
    echo "ERROR - Kafka: Not accessible"
fi

# Check PostgreSQL
echo "Checking PostgreSQL..."
if docker compose exec postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "OK - PostgreSQL: localhost:5432 (fleet_tracking database)"
else
    echo "ERROR - PostgreSQL: Not accessible"
fi

# Check if producer is running
echo "Checking GPS Producer..."
if pgrep -f "producer.py" > /dev/null; then
    echo "OK - GPS Producer: Running (generating data)"
else
    echo "WARNING - GPS Producer: Not running (use ./run_producer.sh to start)"
fi

echo ""
echo "All services should now be accessible!"
echo "Main Dashboard: http://localhost:3000" 