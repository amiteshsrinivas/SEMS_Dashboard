# SEMS & Hydrogen Generation Dashboard

A modern, interactive dashboard for visualizing sensor data from a Smart Energy Management System (SEMS) integrated with hydrogen generation. This project uses Streamlit for the frontend dashboard and includes a data generator for simulating sensor readings.

## Features

- 🌟 Real-time sensor data visualization
- 📊 Interactive charts and graphs
- 🛡️ Data validation and error handling
- 📱 Responsive design
- 📝 Easy data simulation for testing

## Project Structure

```
SEMS_Dashboard/
├── dashboard/            # Streamlit dashboard app
│   ├── dashboard.py      # Main dashboard application
│   └── __init__.py       # Package marker
├── data/                 # Data storage and generator
│   ├── sensor_data.csv   # Sensor readings (CSV)
│   ├── generate_data.py  # Data generator script
│   └── __init__.py       # Package marker
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Sensor Specifications

| Sensor           | Description                | Range         |
|------------------|---------------------------|---------------|
| TSL2561_Light    | Light intensity sensor     | 0-1000 lux    |
| ACS712_Current   | Current sensor             | 0-30A         |
| INA219_Voltage   | Voltage sensor             | 10-24V        |
| DS18B20_Temp     | Electrolyzer temperature   | 20-40°C       |
| MQ8_H2_Level     | Hydrogen level sensor      | 0-1           |
| DHT22_Temp       | Ambient temperature sensor | 18-35°C       |
| DHT22_Humidity   | Humidity sensor            | 30-80%        |
| YF_S201_Flow     | Water flow sensor          | 0-10 L/min    |

## Setup Instructions

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .\.venv\Scripts\activate
   # On Linux/Mac:
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Generate sample data:**
   ```bash
   python data/generate_data.py
   ```
   This will create or update `data/sensor_data.csv` with simulated sensor readings.

4. **Run the dashboard:**
   ```bash
   streamlit run dashboard/dashboard.py
   ```
   The dashboard will open in your browser (usually at http://localhost:8501).

## Usage

- The dashboard visualizes sensor data from `data/sensor_data.csv`.
- Click metric buttons to view interactive graphs for each sensor.
- Use the sidebar to select power source and view quick stats.

## Screenshots

### Main Dashboard
![Main Dashboard](SEMS_DASHBOARD/screenshots/1.png)

### System Metrics
![System Metrics](SEMS_DASHBOARD/screenshots/5.png)

### System Control
![System Control](SEMS_DASHBOARD/screenshots/2.png)

### Power Management
![Power Management](SEMS_DASHBOARD/screenshots/3.png)

### Sensor Graph Example
![Sensor Graph](SEMS_DASHBOARD/screenshots/4.png)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
