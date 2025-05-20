# Real-Time Logistics & Fleet Tracking Dashboard

A comprehensive real-time fleet tracking system that processes GPS data, performs geofence analysis, and provides real-time visualization through a multi-datastore architecture.

## Architecture

The system uses a modern microservices architecture with the following components:

- **Data Generation**: Python producer generates synthetic GPS data
- **Message Queue**: Apache Kafka for real-time data streaming
- **Stream Processing**: Custom Kafka consumer for real-time processing
- **Geospatial Database**: PostgreSQL with PostGIS for geofence queries
- **Time-Series Database**: InfluxDB for high-throughput event storage
- **Visualization**: Grafana for real-time dashboards
- **Containerization**: Docker Compose for easy deployment

## Tech Stack

- **Backend**: Python 3.x, Apache Kafka, PostgreSQL with PostGIS
- **Databases**: InfluxDB 2.7, PostgreSQL 14 with PostGIS 3.3
- **Stream Processing**: Custom Kafka consumer (alternative to Apache Flink)
- **Visualization**: Grafana 9.4.3
- **Infrastructure**: Docker, Docker Compose
- **Message Queue**: Apache Kafka 7.0.1, Apache Zookeeper

## Project Structure

```
Real-Time-Logistics-Fleet-Tracking-Dashboard/
├── docker-compose.yml              # Main orchestration file
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
├── ACCESS_GUIDE.md                 # System access and usage guide
├── TROUBLESHOOTING.md              # Common issues and solutions
├── run_producer.sh                 # Start GPS data producer
├── run_kafka_processor.sh          # Start data processing
├── check_services.sh               # System health check
├── test_system.sh                  # Comprehensive system test
├── producer/
│   └── producer.py                 # GPS data generator
├── kafka_processor.py              # Real-time data processor
├── postgres/
│   └── init-db.sql                # Database initialization
├── flink-job/
│   └── process_stream.py          # Flink job (alternative)
└── grafana/
    └── provisioning/              # Grafana auto-configuration
        ├── dashboards/
        │   ├── dashboard.yml
        │   └── fleet-tracking-dashboard.json
        └── datasources/
            ├── postgresql.yml
            └── influxdb.yml
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.x (for local development)
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Real-Time-Logistics-Fleet-Tracking-Dashboard
   ```

2. **Start all services**
   ```bash
   docker compose up -d
   ```

3. **Set up Python environment (optional)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Start data generation**
   ```bash
   ./run_producer.sh
   ```

5. **Start data processing**
   ```bash
   ./run_kafka_processor.sh
   ```

6. **Access the dashboard**
   - Grafana Dashboard: http://localhost:3000 (admin/admin)
   - InfluxDB: http://localhost:8086
   - Flink Web UI: http://localhost:8081

## System Components

### Data Flow

1. **GPS Producer** generates synthetic vehicle GPS data every second
2. **Kafka** receives and streams GPS messages in real-time
3. **Kafka Processor** consumes data, performs geofence analysis
4. **PostgreSQL** handles spatial queries for geofence lookups
5. **InfluxDB** stores processed events and alerts
6. **Grafana** provides real-time visualization

### Services

- **Grafana Dashboard**: Real-time fleet tracking visualization
- **InfluxDB**: Time-series data storage for events
- **Kafka**: Message streaming for GPS data
- **PostgreSQL**: Geospatial database with PostGIS
- **Flink Web UI**: Stream processing monitoring (optional)

## Dashboard Features

The Grafana dashboard includes:

- **Vehicle Locations Table**: Real-time positions and geofence status
- **Alert Events Over Time**: Geofence entry/exit events
- **Geofence Status**: Vehicle count per geofence
- **Vehicle Activity Timeline**: Historical movement patterns

## Data Processing

### GPS Data Format
```json
{
  "vehicle_id": "VEH001",
  "timestamp": "2024-01-15T10:30:00Z",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

### Processed Event Format
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

## Geofences

The system includes three predefined geofences:

- **Downtown**: Manhattan downtown area
- **Warehouse District**: Industrial warehouse zone
- **Industrial Zone**: Manufacturing district

## Management Commands

### System Health
```bash
# Check all services
./check_services.sh

# Comprehensive system test
./test_system.sh

# View logs
docker compose logs -f
```

### Data Processing
```bash
# Start GPS producer
./run_producer.sh

# Start Kafka processor
./run_kafka_processor.sh

# Stop processors
pkill -f "kafka_processor.py"
pkill -f "producer.py"
```

### Service Management
```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart specific service
docker compose restart kafka
```

## Configuration

### Environment Variables

Key configuration options in `docker-compose.yml`:

- **Kafka**: Topic `gps_data`, port 9092
- **PostgreSQL**: Database `fleet_tracking`, port 5432
- **InfluxDB**: Bucket `fleet-data`, org `fleet-org`
- **Grafana**: Port 3000, auto-provisioned dashboards

### Customization

- **Add Geofences**: Modify `postgres/init-db.sql`
- **Change GPS Range**: Update `producer/producer.py`
- **Custom Dashboards**: Add to `grafana/provisioning/dashboards/`

## Troubleshooting

Common issues and solutions are documented in `TROUBLESHOOTING.md`.

### Quick Fixes

- **Services not starting**: Check Docker is running
- **Database errors**: Restart PostgreSQL container
- **Processor issues**: Check Python dependencies
- **Dashboard not loading**: Verify Grafana container status

## Development

### Local Development

1. Create Python virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Start services: `docker compose up -d`
4. Run processors locally for debugging

### Adding Features

- **New Data Sources**: Add Kafka producers
- **Custom Processing**: Extend `kafka_processor.py`
- **Additional Visualizations**: Create new Grafana dashboards
- **Geofence Logic**: Modify PostgreSQL spatial queries

## Production Deployment

For production use:

1. **Security**: Add authentication to all services
2. **Monitoring**: Implement proper logging and metrics
3. **Scaling**: Use Kubernetes for container orchestration
4. **Backup**: Set up database backup strategies
5. **SSL**: Configure HTTPS for all web interfaces

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
- Check `TROUBLESHOOTING.md`
- Review system logs
- Verify service configurations 