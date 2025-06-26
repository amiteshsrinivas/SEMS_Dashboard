import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Sensor configuration
SENSOR_RANGES = {
    'TSL2561_Light': {'min': 0, 'max': 1000, 'noise': 50},
    'ACS712_Current': {'min': 0, 'max': 30, 'noise': 1},
    'INA219_Voltage': {'min': 10, 'max': 24, 'noise': 0.5},
    'DS18B20_Temp': {'min': 20, 'max': 40, 'noise': 2},
    'MQ8_H2_Level': {'min': 0, 'max': 1, 'noise': 0.1},
    'DHT22_Temp': {'min': 18, 'max': 35, 'noise': 3},
    'DHT22_Humidity': {'min': 30, 'max': 80, 'noise': 5},
    'YF_S201_Flow': {'min': 0, 'max': 10, 'noise': 0.5}
}


def generate_realistic_data(num_entries=50, time_interval_seconds=60):
    """
    Generate realistic sensor data with gradual changes and noise.
    
    Args:
        num_entries (int): Number of data points to generate
        time_interval_seconds (int): Time interval between data points in seconds
    
    Returns:
        pd.DataFrame: DataFrame containing generated sensor data
    """
    current_values = {
        sensor: (ranges['max'] + ranges['min']) / 2 
        for sensor, ranges in SENSOR_RANGES.items()
    }
    
    end_time = datetime.now()
    start_time = end_time - timedelta(seconds=time_interval_seconds * (num_entries - 1))
    timestamps = [start_time + timedelta(seconds=i * time_interval_seconds) for i in range(num_entries)]
    
    data = []
    for timestamp in timestamps:
        row = {'Timestamp': timestamp}
        for sensor, ranges in SENSOR_RANGES.items():
            drift = np.random.normal(0, ranges['noise'] * 0.1)
            current_values[sensor] += drift
            noise = np.random.normal(0, ranges['noise'] * 0.05)
            value = current_values[sensor] + noise
            value = max(ranges['min'], min(ranges['max'], value))
            current_values[sensor] = value
            row[sensor] = round(value, 2)
        data.append(row)
    return pd.DataFrame(data)

def save_data(df, filename='sensor_data.csv'):
    """
    Save sensor data to CSV file.
    
    Args:
        df (pd.DataFrame): DataFrame containing sensor data
        filename (str): Name of the CSV file to save
    """
    filepath = os.path.join(os.path.dirname(__file__), filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"Data saved to {filepath}")

if __name__ == '__main__':
    # Generate and save sample data when run directly
    df = generate_realistic_data()
    save_data(df) 