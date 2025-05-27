#!/usr/bin/env python3
"""
Real-Time Fleet Tracking Flink Job
Processes GPS data from Kafka, performs geofence lookups, and writes to InfluxDB
"""

import os
import json
import time
from datetime import datetime
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.table.udf import udf
from pyflink.common import Types
from pyflink.table.expressions import col, lit
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

class GeofenceProcessor:
    def __init__(self, postgres_host='postgres', postgres_port=5432, 
                 postgres_db='fleet_tracking', postgres_user='postgres', 
                 postgres_password='postgres'):
        """Initialize the geofence processor with PostgreSQL connection"""
        self.postgres_config = {
            'host': postgres_host,
            'port': postgres_port,
            'database': postgres_db,
            'user': postgres_user,
            'password': postgres_password
        }
        self.vehicle_states = {}  # Track previous geofence state for each vehicle

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
            print(f"Error querying geofence: {e}")
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

def create_flink_job():
    """Create and configure the Flink job"""
    
    # Set up Flink environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    
    # Create table environment
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, settings)
    
    # Create Kafka source table
    kafka_source_ddl = """
        CREATE TABLE gps_data (
            vehicle_id STRING,
            timestamp STRING,
            latitude DOUBLE,
            longitude DOUBLE,
            proc_time AS PROCTIME()
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'gps_data',
            'properties.bootstrap.servers' = 'kafka:9092',
            'properties.group.id' = 'flink-fleet-tracking',
            'format' = 'json',
            'json.fail-on-missing-field' = 'false',
            'json.ignore-parse-errors' = 'true'
        )
    """
    t_env.execute_sql(kafka_source_ddl)
    
    # Create InfluxDB sink table
    influxdb_sink_ddl = """
        CREATE TABLE fleet_events (
            vehicle_id STRING,
            timestamp STRING,
            latitude DOUBLE,
            longitude DOUBLE,
            current_geofence STRING,
            alert_status BOOLEAN
        ) WITH (
            'connector' = 'influxdb',
            'url' = 'http://influxdb:8086',
            'token' = 'fleet-token-123',
            'org' = 'fleet-org',
            'bucket' = 'fleet-data',
            'measurement' = 'fleet_events'
        )
    """
    t_env.execute_sql(influxdb_sink_ddl)
    
    # Create UDF for geofence processing
    @udf(result_type=Types.STRING())
    def get_geofence_udf(latitude, longitude):
        """UDF to get geofence for coordinates"""
        processor = GeofenceProcessor()
        return processor.get_geofence(latitude, longitude)
    
    @udf(result_type=Types.BOOLEAN())
    def check_alert_udf(vehicle_id, current_geofence):
        """UDF to check for alert conditions"""
        processor = GeofenceProcessor()
        return processor.check_alert(vehicle_id, current_geofence)
    
    # Register UDFs
    t_env.create_temporary_function("get_geofence", get_geofence_udf)
    t_env.create_temporary_function("check_alert", check_alert_udf)
    
    # Process the stream
    result_table = t_env.sql_query("""
        SELECT 
            vehicle_id,
            timestamp,
            latitude,
            longitude,
            get_geofence(latitude, longitude) as current_geofence,
            check_alert(vehicle_id, get_geofence(latitude, longitude)) as alert_status
        FROM gps_data
    """)
    
    # Insert into InfluxDB
    result_table.execute_insert('fleet_events')
    
    # Execute the job
    job_name = "Fleet Tracking Stream Processing"
    print(f"Starting Flink job: {job_name}")
    env.execute(job_name)

def main():
    """Main function to run the Flink job"""
    print("Initializing Fleet Tracking Flink Job...")
    
    # Wait for services to be ready
    print("Waiting for services to be ready...")
    time.sleep(30)  # Give time for Kafka and PostgreSQL to start
    
    try:
        create_flink_job()
    except Exception as e:
        print(f"Error running Flink job: {e}")
        raise

if __name__ == "__main__":
    main() 