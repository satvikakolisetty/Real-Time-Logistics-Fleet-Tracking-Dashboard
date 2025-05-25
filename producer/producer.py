#!/usr/bin/env python3
"""
Real-Time GPS Data Producer
Generates simulated vehicle GPS data and sends it to Kafka topic 'gps_data'
"""

import json
import time
import random
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer
from kafka.errors import KafkaError

class GPSDataProducer:
    def __init__(self, kafka_bootstrap_servers='localhost:9092'):
        """Initialize the GPS data producer"""
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.producer = None
        self.connect_to_kafka()
        
    def connect_to_kafka(self):
        """Connect to Kafka with retry logic"""
        max_retries = 10
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"Attempting to connect to Kafka at {self.kafka_bootstrap_servers} (attempt {retry_count + 1}/{max_retries})")
                self.producer = KafkaProducer(
                    bootstrap_servers=self.kafka_bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None,
                    request_timeout_ms=5000,
                    api_version_auto_timeout_ms=5000
                )
                print("✅ Successfully connected to Kafka!")
                break
            except Exception as e:
                retry_count += 1
                print(f"❌ Connection attempt {retry_count} failed: {e}")
                if retry_count < max_retries:
                    print(f"⏳ Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    print("❌ Failed to connect to Kafka after all attempts.")
                    print("💡 Make sure Docker services are running: docker-compose up -d")
                    raise
        self.fake = Faker()
        
        # Define 5 vehicle IDs
        self.vehicle_ids = ['VEH001', 'VEH002', 'VEH003', 'VEH004', 'VEH005']
        
        # Define base coordinates for realistic movement around NYC area
        self.base_coordinates = {
            'VEH001': {'lat': 40.7128, 'lon': -74.0060},  # Manhattan
            'VEH002': {'lat': 40.7505, 'lon': -73.9934},  # Midtown
            'VEH003': {'lat': 40.7589, 'lon': -73.9851},  # Times Square
            'VEH004': {'lat': 40.7484, 'lon': -73.9857},  # Penn Station
            'VEH005': {'lat': 40.7614, 'lon': -73.9776}   # Grand Central
        }
        
        # Current positions for each vehicle
        self.current_positions = self.base_coordinates.copy()

    def generate_gps_data(self, vehicle_id):
        """Generate realistic GPS data for a vehicle"""
        # Get current position
        current_pos = self.current_positions[vehicle_id]
        
        # Add small random movement (simulating vehicle movement)
        lat_offset = random.uniform(-0.001, 0.001)  # Small movement
        lon_offset = random.uniform(-0.001, 0.001)
        
        # Update current position
        new_lat = current_pos['lat'] + lat_offset
        new_lon = current_pos['lon'] + lon_offset
        
        # Ensure coordinates stay within reasonable bounds
        new_lat = max(40.6, min(40.8, new_lat))  # NYC latitude bounds
        new_lon = max(-74.1, min(-73.9, new_lon))  # NYC longitude bounds
        
        # Update current position
        self.current_positions[vehicle_id] = {'lat': new_lat, 'lon': new_lon}
        
        # Generate timestamp
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        return {
            'vehicle_id': vehicle_id,
            'timestamp': timestamp,
            'latitude': round(new_lat, 6),
            'longitude': round(new_lon, 6)
        }

    def send_to_kafka(self, data):
        """Send GPS data to Kafka topic"""
        try:
            future = self.producer.send('gps_data', key=data['vehicle_id'], value=data)
            record_metadata = future.get(timeout=10)
            print(f"Sent GPS data for {data['vehicle_id']}: {data['latitude']:.6f}, {data['longitude']:.6f}")
            return True
        except KafkaError as e:
            print(f"Failed to send data to Kafka: {e}")
            return False

    def run(self, interval=1):
        """Main loop to continuously generate and send GPS data"""
        print("Starting GPS data producer...")
        print(f"Generating data for vehicles: {', '.join(self.vehicle_ids)}")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Randomly select a vehicle to generate data for
                vehicle_id = random.choice(self.vehicle_ids)
                
                # Generate GPS data
                gps_data = self.generate_gps_data(vehicle_id)
                
                # Send to Kafka
                self.send_to_kafka(gps_data)
                
                # Wait for next interval
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nStopping GPS data producer...")
        finally:
            self.producer.close()
            print("Producer closed.")

if __name__ == "__main__":
    # Create and run the producer
    producer = GPSDataProducer()
    producer.run() 