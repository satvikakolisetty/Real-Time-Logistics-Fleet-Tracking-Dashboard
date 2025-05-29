# Fleet Tracking System - Access Guide

## System Status

Your Real-Time Logistics & Fleet Tracking Dashboard is now fully operational!

### Running Services
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **InfluxDB**: http://localhost:8086
- **Kafka**: localhost:9092
- **PostgreSQL**: localhost:5432
- **Zookeeper**: localhost:2181
- **Flink Web UI**: http://localhost:8081

### Data Flow
1. **GPS Producer** generates vehicle GPS data every second
2. **Kafka** receives and stores GPS messages
3. **PostgreSQL** stores geofence definitions with PostGIS
4. **InfluxDB** stores processed events and time-series data
5. **Grafana** visualizes real-time fleet data

## Access Your Dashboards

### 1. Grafana Dashboard (Main Interface)
**URL**: http://localhost:3000
- **Username**: admin
- **Password**: admin

**Features**:
- Auto-configured data sources (PostgreSQL & InfluxDB)
- Pre-built dashboard with 4 panels:
  - Vehicle Locations Table
  - Alert Events Over Time
  - Geofence Status
  - Vehicle Activity Timeline
- Real-time updates every 5 seconds
- Dark theme for better visibility

### 2. InfluxDB UI (Time-series Database)
**URL**: http://localhost:8086
- **Username**: admin
- **Password**: adminpassword
- **Organization**: fleet-org
- **Bucket**: fleet-data

### 3. Flink Web UI (Stream Processing)
**URL**: http://localhost:8081
- Monitor Flink jobs and processing status
- View cluster overview and task managers
- Submit and manage Flink jobs

## Dashboard Panels Explained

### 1. Vehicle Locations Table
- Shows current position of all vehicles
- Displays which geofence each vehicle is in
- Updates in real-time

### 2. Alert Events Over Time
- Counts geofence entry/exit events
- Shows alert frequency over time
- Helps identify unusual patterns

### 3. Geofence Status
- Shows how many vehicles are in each geofence
- Real-time geofence occupancy
- Quick status overview

### 4. Vehicle Activity Timeline
- Individual vehicle activity over time
- Helps track vehicle movement patterns
- Historical analysis

## System Commands

### Check System Status
```bash
# View all running services
docker compose ps

# Check system health
./test_system.sh

# View logs
docker compose logs -f
```

### Manage Data Generation
```bash
# Start GPS producer
./run_producer.sh

# Stop GPS producer
pkill -f producer.py

# Run simple processor (demo mode)
./run_processor.sh

# Run Kafka consumer (real-time processing)
./run_kafka_processor.sh
```

### System Management
```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart specific service
docker compose restart kafka

# View service logs
docker compose logs -f kafka
docker compose logs -f postgres
```

## Data Formats

### GPS Data (Kafka Topic: gps_data)
```json
{
  "vehicle_id": "VEH001",
  "timestamp": "2024-01-15T10:30:00Z",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

### Processed Events (InfluxDB)
```json
{
  "vehicle_id": "VEH001",
  "timestamp": "2024-01-15T10:30:00Z",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "current_geofence": "Downtown",
  "alert_status": true
}
```

### Geofences (PostgreSQL)
```sql
CREATE TABLE geofences (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    area GEOMETRY(POLYGON, 4326) NOT NULL
);
```

## Sample Queries

### PostgreSQL Queries

**Get all vehicles in Downtown geofence**:
```sql
SELECT vehicle_id, latitude, longitude, timestamp
FROM fleet_events
WHERE current_geofence = 'Downtown'
ORDER BY timestamp DESC;
```

**Count vehicles per geofence**:
```sql
SELECT current_geofence, COUNT(*) as vehicle_count
FROM (
    SELECT DISTINCT vehicle_id, current_geofence
    FROM fleet_events
    WHERE current_geofence IS NOT NULL
) geofence_status
GROUP BY current_geofence;
```

### InfluxDB Queries

**Alert events in last hour**:
```flux
from(bucket: "fleet-data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "fleet_events")
  |> filter(fn: (r) => r["alert_status"] == "true")
  |> aggregateWindow(every: 1m, fn: count, createEmpty: false)
```

**Vehicle activity timeline**:
```flux
from(bucket: "fleet-data")
  |> range(start: -30m)
  |> filter(fn: (r) => r["_measurement"] == "fleet_events")
  |> group(columns: ["vehicle_id"])
  |> aggregateWindow(every: 5m, fn: count, createEmpty: false)
```

## Troubleshooting

### Common Issues

1. **Services not starting**
   - Check Docker is running
   - Verify ports are available
   - Check system resources

2. **No data in dashboard**
   - Ensure producer is running
   - Check Kafka topic exists
   - Verify data sources are configured

3. **Database connection errors**
   - Restart PostgreSQL container
   - Check database initialization
   - Verify credentials

4. **Processor not working**
   - Check Python dependencies
   - Verify Kafka connectivity
   - Check PostgreSQL connection

### Quick Fixes

```bash
# Restart all services
docker compose down
docker compose up -d

# Check service status
docker compose ps

# View recent logs
docker compose logs --tail=50

# Restart specific service
docker compose restart postgres
```

### Performance Monitoring

```bash
# Check resource usage
docker stats

# Monitor Kafka topics
docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Check database connections
docker compose exec postgres psql -U postgres -d fleet_tracking -c "SELECT count(*) FROM pg_stat_activity;"
```

## Development Tips

### Adding New Geofences
1. Connect to PostgreSQL
2. Insert new geofence with spatial data
3. Restart processor to pick up changes

### Customizing GPS Data
1. Modify producer/producer.py
2. Adjust vehicle movement patterns
3. Restart producer

### Extending Processing Logic
1. Edit kafka_processor.py
2. Add new alert conditions
3. Restart processor

### Creating Custom Dashboards
1. Use Grafana UI or provisioning
2. Add new panels and queries
3. Configure alerts and notifications 