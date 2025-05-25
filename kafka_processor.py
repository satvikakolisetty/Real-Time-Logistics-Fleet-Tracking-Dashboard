#!/usr/bin/env python3
"""
Kafka Consumer for Fleet Tracking
Consumes GPS data from Kafka, performs geofence analysis, and writes to InfluxDB
"""

import json
import time
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from datetime import datetime
from kafka import KafkaConsumer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KafkaFleetProcessor:
    def __init__(self):
        """Initialize the Kafka fleet processor"""
        self.postgres_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'fleet_tracking',
            'user': 'postgres',
            'password': 'postgres'
        }
        self.influxdb_config = {
            'url': 'http://localhost:8086',
            'token': 'fleet-token-123',
            'org': 'fleet-org',
            'bucket': 'fleet-data'
        }
        self.vehicle_states = {}
        
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            'gps_data',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='fleet-processor-group'
        )

    def get_geofence(self, latitude, longitude):
        """Query PostgreSQL to find which geofence contains the given coordinates"""
        try:
            conn = psycopg2.connect(**self.postgres_config)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Spatial query to find which geofence contains the point
            query = """
                SELECT name 
                FROM geofences 
                WHERE ST_Contains(area, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                LIMIT 1
            """
            cursor.execute(query, (longitude, latitude))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return result['name'] if result else None
            
        except Exception as e:
            logger.error(f"Error querying geofence: {e}")
            return None

    def check_alert(self, vehicle_id, current_geofence):
        """Check if there's an alert condition (geofence status change)"""
        previous_geofence = self.vehicle_states.get(vehicle_id)
        
        # Update state
        self.vehicle_states[vehicle_id] = current_geofence
        
        # Alert if geofence status changed
        if previous_geofence != current_geofence:
            return True
        
        return False

    def write_to_influxdb(self, data):
        """Write processed event to InfluxDB"""
        try:
            headers = {
                'Authorization': f'Token {self.influxdb_config["token"]}',
                'Content-Type': 'application/json'
            }
            
            # Create InfluxDB line protocol format
            timestamp = int(datetime.now().timestamp() * 1e9)  # nanoseconds
            line_protocol = f"fleet_events,vehicle_id={data['vehicle_id']} latitude={data['latitude']},longitude={data['longitude']},current_geofence=\"{data['current_geofence']}\",alert_status={str(data['alert_status']).lower()} {timestamp}"
            
            url = f"{self.influxdb_config['url']}/api/v2/write?org={self.influxdb_config['org']}&bucket={self.influxdb_config['bucket']}"
            
            response = requests.post(url, headers=headers, data=line_protocol)
            
            if response.status_code == 204:
                logger.info(f"✅ Processed: {data['vehicle_id']} at ({data['latitude']:.6f}, {data['longitude']:.6f}) - Geofence: {data['current_geofence']} - Alert: {data['alert_status']}")
            else:
                logger.error(f"❌ Failed to write to InfluxDB: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error writing to InfluxDB: {e}")

    def process_gps_event(self, gps_data):
        """Process a single GPS event"""
        try:
            # Extract data
            vehicle_id = gps_data['vehicle_id']
            latitude = gps_data['latitude']
            longitude = gps_data['longitude']
            timestamp = gps_data['timestamp']
            
            # Get geofence
            current_geofence = self.get_geofence(latitude, longitude)
            
            # Check for alert
            alert_status = self.check_alert(vehicle_id, current_geofence)
            
            # Create processed event
            processed_event = {
                'vehicle_id': vehicle_id,
                'timestamp': timestamp,
                'latitude': latitude,
                'longitude': longitude,
                'current_geofence': current_geofence,
                'alert_status': alert_status
            }
            
            # Write to InfluxDB
            self.write_to_influxdb(processed_event)
            
        except Exception as e:
            logger.error(f"Error processing GPS event: {e}")

    def run(self):
        """Main processing loop"""
        logger.info("🚀 Starting Kafka Fleet Processor...")
        logger.info("📡 Consuming GPS data from Kafka topic: gps_data")
        logger.info("💡 Make sure the producer is running: ./run_producer.sh")
        logger.info("📊 Check Grafana Dashboard: http://localhost:3000")
        logger.info("")
        
        try:
            for message in self.consumer:
                gps_data = message.value
                logger.info(f"📨 Received GPS data: {gps_data}")
                self.process_gps_event(gps_data)
                
        except KeyboardInterrupt:
            logger.info("🛑 Stopping processor...")
        except Exception as e:
            logger.error(f"Error in processing loop: {e}")
        finally:
            self.consumer.close()

if __name__ == "__main__":
    processor = KafkaFleetProcessor()
    processor.run() 