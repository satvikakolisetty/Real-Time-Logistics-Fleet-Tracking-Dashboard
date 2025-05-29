# Project Structure

## Overview

This is a real-time fleet tracking system that processes GPS data, performs geofence analysis, and provides real-time visualization through a multi-datastore architecture.

## File Organization

```
Real-Time-Logistics-Fleet-Tracking-Dashboard/
├── README.md                       # Main project documentation
├── ACCESS_GUIDE.md                 # System access and usage guide
├── TROUBLESHOOTING.md              # Common issues and solutions
├── PROJECT_STRUCTURE.md            # This file
├── docker-compose.yml              # Main orchestration file
├── requirements.txt                 # Python dependencies
├── .gitignore                      # Git ignore rules
├── run_producer.sh                 # Start GPS data producer
├── run_kafka_processor.sh          # Start data processing
├── check_services.sh               # System health check
├── test_system.sh                  # Comprehensive system test
├── run_processor.sh                # Alternative processor (legacy)
├── kafka_processor.py              # Real-time data processor
├── producer/
│   └── producer.py                 # GPS data generator
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

## Core Components

### Documentation
- **README.md**: Main project documentation with setup instructions
- **ACCESS_GUIDE.md**: Detailed system access and usage guide
- **TROUBLESHOOTING.md**: Comprehensive troubleshooting guide
- **PROJECT_STRUCTURE.md**: This file explaining the organization

### Configuration
- **docker-compose.yml**: Orchestrates all services (Kafka, PostgreSQL, InfluxDB, Grafana, Flink)
- **requirements.txt**: Python dependencies for data generation and processing
- **.gitignore**: Excludes temporary files and virtual environments

### Scripts
- **run_producer.sh**: Starts GPS data generation
- **run_kafka_processor.sh**: Starts real-time data processing
- **check_services.sh**: Quick system health check
- **test_system.sh**: Comprehensive system testing
- **run_processor.sh**: Alternative processor (legacy)

### Application Code
- **kafka_processor.py**: Main data processing application
- **producer/producer.py**: GPS data generation
- **flink-job/process_stream.py**: Alternative Flink-based processing

### Database
- **postgres/init-db.sql**: PostgreSQL initialization with geofences

### Visualization
- **grafana/provisioning/**: Auto-configuration for Grafana dashboards and data sources

## Service Architecture

### Data Flow
1. **Producer** generates GPS data → **Kafka** receives messages
2. **Kafka Processor** consumes data → **PostgreSQL** for geofence queries
3. **Processed events** → **InfluxDB** for time-series storage
4. **Grafana** visualizes real-time data

### Services
- **Kafka**: Message streaming (port 9092)
- **PostgreSQL**: Geospatial database with PostGIS (port 5432)
- **InfluxDB**: Time-series database (port 8086)
- **Grafana**: Visualization dashboard (port 3000)
- **Flink**: Stream processing (port 8081, optional)

## Key Features

### Real-time Processing
- GPS data generation every second
- Geofence detection and alerting
- Time-series data storage
- Real-time dashboard updates

### Geofence Management
- Three predefined geofences (Downtown, Warehouse District, Industrial Zone)
- Spatial queries using PostGIS
- Alert generation on geofence entry/exit

### Data Visualization
- Vehicle location tracking
- Alert event monitoring
- Geofence status overview
- Historical activity analysis

## Development Workflow

### Setup
1. Clone repository
2. Run `docker compose up -d`
3. Create virtual environment: `python3 -m venv venv`
4. Install dependencies: `pip install -r requirements.txt`

### Running
1. Start services: `docker compose up -d`
2. Start producer: `./run_producer.sh`
3. Start processor: `./run_kafka_processor.sh`
4. Access dashboard: http://localhost:3000

### Monitoring
- Check system health: `./check_services.sh`
- View logs: `docker compose logs -f`
- Test system: `./test_system.sh`

## Customization

### Adding Geofences
Edit `postgres/init-db.sql` to add new geofence areas

### Modifying GPS Data
Update `producer/producer.py` to change vehicle behavior

### Custom Processing
Extend `kafka_processor.py` for additional logic

### Dashboard Customization
Add new panels to `grafana/provisioning/dashboards/`

## Production Considerations

### Security
- Add authentication to all services
- Use SSL/TLS for external access
- Implement proper access controls

### Scaling
- Use Kubernetes for container orchestration
- Implement horizontal scaling for processors
- Add load balancing for web interfaces

### Monitoring
- Implement proper logging and metrics
- Add health checks and alerting
- Set up backup and recovery procedures

### Performance
- Optimize database queries
- Configure appropriate memory limits
- Implement caching strategies 