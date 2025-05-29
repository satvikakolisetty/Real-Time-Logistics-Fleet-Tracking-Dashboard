# Troubleshooting Guide

This guide covers common issues and their solutions for the Real-Time Logistics & Fleet Tracking Dashboard.

## Quick Diagnosis

### Check System Status
```bash
# View all running services
docker compose ps

# Check system health
./check_services.sh

# View recent logs
docker compose logs --tail=50
```

### Common Issues

1. **Services not starting**
2. **No data in dashboard**
3. **Database connection errors**
4. **Processor not working**
5. **Port conflicts**

## Detailed Solutions

### 1. Services Not Starting

**Symptoms**: Docker containers fail to start or exit immediately

**Causes**:
- Docker not running
- Port conflicts
- Insufficient system resources
- Configuration errors

**Solutions**:

```bash
# Check Docker status
docker info

# Check for port conflicts
lsof -i :3000
lsof -i :5432
lsof -i :8081
lsof -i :8086
lsof -i :9092

# Restart Docker (if needed)
# On Linux: sudo systemctl restart docker
# On Windows/Mac: Restart Docker Desktop

# Clean restart
docker compose down -v
docker compose up -d
```

**Prevention**:
- Ensure Docker has sufficient resources (4GB+ RAM)
- Close other applications using required ports
- Keep Docker updated

### 2. No Data in Dashboard

**Symptoms**: Grafana dashboard shows empty panels or "No data" messages

**Causes**:
- GPS producer not running
- Kafka not receiving data
- Database connection issues
- Data source configuration problems

**Solutions**:

```bash
# Check if producer is running
ps aux | grep producer

# Start producer if not running
./run_producer.sh

# Check Kafka topic
docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Check Kafka messages
docker compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic gps_data --from-beginning --max-messages 5

# Verify data sources in Grafana
# Go to http://localhost:3000 → Configuration → Data Sources
```

**Data Source Configuration**:

**PostgreSQL**:
- Host: postgres:5432
- Database: fleet_tracking
- User: postgres
- Password: postgres
- SSL Mode: disable

**InfluxDB**:
- URL: http://influxdb:8086
- Token: fleet-token-123
- Organization: fleet-org
- Bucket: fleet-data

### 3. Database Connection Errors

**Symptoms**: PostgreSQL or InfluxDB connection failures

**Causes**:
- Database not initialized
- Wrong credentials
- Network connectivity issues
- Container not ready

**Solutions**:

```bash
# Check PostgreSQL status
docker compose exec postgres pg_isready -U postgres

# Check database initialization
docker compose exec postgres psql -U postgres -d fleet_tracking -c "\dt"

# Reinitialize database
docker compose restart postgres

# Check InfluxDB
curl -s http://localhost:8086/health

# Verify database contents
docker compose exec postgres psql -U postgres -d fleet_tracking -c "SELECT * FROM geofences;"
```

**Database Reset**:
```bash
# Complete database reset
docker compose down -v
docker compose up -d postgres
sleep 10
docker compose exec postgres psql -U postgres -d fleet_tracking -c "SELECT * FROM geofences;"
```

### 4. Processor Not Working

**Symptoms**: Kafka processor not processing data or showing errors

**Causes**:
- Python dependencies missing
- Kafka connectivity issues
- PostgreSQL connection problems
- Virtual environment issues

**Solutions**:

```bash
# Check processor status
ps aux | grep kafka_processor

# Restart processor
pkill -f kafka_processor.py
./run_kafka_processor.sh

# Check Python dependencies
source venv/bin/activate
pip list | grep -E "(kafka|psycopg2|requests)"

# Install missing dependencies
pip install kafka-python psycopg2-binary requests

# Test connectivity
python3 -c "import kafka; print('Kafka OK')"
python3 -c "import psycopg2; print('PostgreSQL OK')"
```

**Virtual Environment Issues**:
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Port Conflicts

**Symptoms**: Services fail to start with "port already in use" errors

**Causes**:
- Other applications using required ports
- Previous containers not properly stopped
- System services using ports

**Solutions**:

```bash
# Find processes using ports
lsof -i :3000  # Grafana
lsof -i :5432  # PostgreSQL
lsof -i :8081  # Flink
lsof -i :8086  # InfluxDB
lsof -i :9092  # Kafka
lsof -i :2181  # Zookeeper

# Kill processes using ports
sudo kill -9 <PID>

# Alternative: Change ports in docker-compose.yml
# Edit ports section for each service
```

**Port Mapping**:
```yaml
# Example port changes in docker-compose.yml
services:
  grafana:
    ports:
      - "3001:3000"  # Change from 3000 to 3001
  postgres:
    ports:
      - "5433:5432"  # Change from 5432 to 5433
```

## Performance Issues

### High Resource Usage

**Symptoms**: System becomes slow, containers crash

**Solutions**:

```bash
# Check resource usage
docker stats

# Monitor specific containers
docker stats grafana influxdb kafka postgres

# Adjust memory limits in docker-compose.yml
```

**Memory Optimization**:
```yaml
# Example memory limits
services:
  kafka:
    environment:
      KAFKA_HEAP_OPTS: "-Xmx1G -Xms1G"
  postgres:
    environment:
      POSTGRES_SHARED_BUFFERS: "256MB"
```

### Slow Dashboard Response

**Symptoms**: Grafana dashboard loads slowly or times out

**Solutions**:

```bash
# Check Grafana logs
docker compose logs grafana

# Restart Grafana
docker compose restart grafana

# Check data source performance
# Test queries directly in PostgreSQL/InfluxDB
```

## Network Issues

### Container Communication

**Symptoms**: Services can't communicate with each other

**Solutions**:

```bash
# Check network
docker network ls
docker network inspect real-time-logistics-fleet-tracking-dashboard_default

# Test inter-container communication
docker compose exec kafka ping postgres
docker compose exec postgres ping kafka

# Restart network
docker compose down
docker compose up -d
```

### External Access

**Symptoms**: Can't access services from host machine

**Solutions**:

```bash
# Check port bindings
docker compose ps

# Test local access
curl http://localhost:3000  # Grafana
curl http://localhost:8086  # InfluxDB

# Check firewall settings
# Ensure ports are not blocked
```

## Data Issues

### Missing Geofences

**Symptoms**: All vehicles show "None" for geofence

**Solutions**:

```bash
# Check geofences table
docker compose exec postgres psql -U postgres -d fleet_tracking -c "SELECT * FROM geofences;"

# Recreate geofences
docker compose exec postgres psql -U postgres -d fleet_tracking -c "
INSERT INTO geofences (name, area) VALUES 
('Downtown', ST_GeomFromText('POLYGON((-74.006 40.712, -74.006 40.722, -73.996 40.722, -73.996 40.712, -74.006 40.712))', 4326)),
('Warehouse District', ST_GeomFromText('POLYGON((-74.016 40.702, -74.016 40.712, -74.006 40.712, -74.006 40.702, -74.016 40.702))', 4326)),
('Industrial Zone', ST_GeomFromText('POLYGON((-73.986 40.692, -73.986 40.702, -73.976 40.702, -73.976 40.692, -73.986 40.692))', 4326));
"
```

### No Alert Events

**Symptoms**: No alerts showing in dashboard

**Solutions**:

```bash
# Check if processor is running
ps aux | grep kafka_processor

# Restart processor
./run_kafka_processor.sh

# Check alert logic in kafka_processor.py
# Verify geofence queries are working
```

## Recovery Procedures

### Complete System Reset

```bash
# Stop all services
docker compose down -v

# Remove all containers and volumes
docker system prune -a --volumes

# Restart fresh
docker compose up -d

# Wait for services to start
sleep 30

# Start data generation
./run_producer.sh
./run_kafka_processor.sh
```

### Data Backup and Restore

```bash
# Backup PostgreSQL data
docker compose exec postgres pg_dump -U postgres fleet_tracking > backup.sql

# Backup InfluxDB data
# Use InfluxDB CLI or API for data export

# Restore PostgreSQL data
docker compose exec -T postgres psql -U postgres -d fleet_tracking < backup.sql
```

## Getting Help

### Log Analysis

```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs kafka
docker compose logs postgres
docker compose logs grafana

# Follow logs in real-time
docker compose logs -f
```

### System Information

```bash
# Docker version
docker --version
docker compose version

# System resources
free -h
df -h

# Network information
ifconfig
netstat -tulpn
```

### Contact Information

For additional help:
- Check the main README.md
- Review ACCESS_GUIDE.md
- Search GitHub issues
- Check Docker and service documentation 