import streamlit as st
import io

# Set page configuration first
st.set_page_config(
    page_title="Smart Energy Management System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import numpy as np
import hashlib

# Configuration
DATA_FILE = 'data/sensor_data.csv'
BATTERY_CAPACITY = 100  # Battery capacity in Ah
BATTERY_VOLTAGE = 12    # Nominal battery voltage
MIN_BATTERY_SOC = 40    # Minimum battery SoC percentage
SOLAR_THRESHOLD = 100   # Minimum light intensity for solar power (lux)
LOAD_POWER = 200        # Estimated load power requirement (W)

# Power source information
POWER_SOURCES = {
    'solar': {
        'name': 'Solar Panel',
        'description': 'Power from solar panel',
        'color': '#FFD700',
        'icon': '☀️ '
    },
    'grid': {
        'name': 'Grid Power', 
        'description': 'Power directly from grid',
        'color': '#4169E1',
        'icon': '🔌 '
    },
    'battery': {
        'name': 'Battery',
        'description': 'Power from battery storage',
        'color': '#32CD32',
        'icon': '🔋 '
    },
    'auto': {
        'name': 'Automatic Mode',
        'description': 'Automatic power source selection based on availability and load',
        'color': '#FF4500',
        'icon': '⚡ '
    }
}

# Sensor information
SENSOR_INFO = {
    'TSL2561_Light': {
        'name': 'Light Intensity',
        'description': 'Measures light intensity in the system',
        'unit': 'lux',
        'icon': '💡'
    },
    'ACS712_Current': {
        'name': 'Current',
        'description': 'Measures electrical current in the system',
        'unit': 'A',
        'icon': '⚡'
    },
    'INA219_Voltage': {
        'name': 'Voltage',
        'description': 'Measures electrical voltage in the system',
        'unit': 'V',
        'icon': '🔌'
    },
    'DS18B20_Temp': {
        'name': 'Electrolyzer Temp',
        'description': 'Measures electrolyzer temperature in the system',
        'unit': '°C',
        'icon': '🌡️'
    },
    'MQ8_H2_Level': {
        'name': 'H2 Level',
        'description': 'Measures hydrogen level in the system',
        'unit': 'ppm',
        'icon': '💨'
    },
    'DHT22_Temp': {
        'name': 'Ambient Temperature',
        'description': 'Measures ambient temperature in the system',
        'unit': '°C',
        'icon': '🌡️'
    },
    'DHT22_Humidity': {
        'name': 'Humidity',
        'description': 'Measures humidity in the system',
        'unit': '%',
        'icon': '💧'
    },
    'YF_S201_Flow': {
        'name': 'Flow Rate',
        'description': 'Measures water flow rate in the system',
        'unit': 'L/min',
        'icon': '💦'
    }
}

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if 'show_graphs' not in st.session_state:
        st.session_state.show_graphs = {}
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'last_file_check' not in st.session_state:
        st.session_state.last_file_check = None

# Custom CSS (keeping your existing styles)
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
        padding: 2rem;
    }
    
    h1 {
        color: #1e3c72;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 2rem !important;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    h2 {
        color: #2c3e50;
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        margin: 1.5rem 0 !important;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
    }
    
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1.2rem;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .metric-description {
        font-size: 0.9rem;
        color: #6c757d;
        margin-bottom: 1rem;
        min-height: 40px;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3c72;
        margin: 0.5rem 0;
    }
    
    .metric-unit {
        font-size: 1rem;
        color: #6c757d;
        margin-left: 0.5rem;
    }
    
    .status-indicator {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 600;
        font-size: 1.2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        background: linear-gradient(135deg, #1e3c72, #2c3e50);
        color: white;
    }
    
    .plot-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem 1.25rem;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)  # Cache for 1 minute
def load_data():
    """Load data from CSV file with validation and caching"""
    try:
        if not os.path.exists(DATA_FILE):
            st.error(f"❌ Data file not found: `{DATA_FILE}`")
            st.info("💡 Make sure the CSV file exists in the data directory")
            return pd.DataFrame()
            
        # Check file modification time for auto-refresh
        file_mtime = os.path.getmtime(DATA_FILE)
        
        df = pd.read_csv(DATA_FILE)
        
        if df.empty:
            st.error("❌ Data file is empty")
            return df
        
        # Validate required columns
        required_columns = list(SENSOR_INFO.keys()) + ['Timestamp']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Missing required columns: {missing_columns}")
            st.info(f"📋 Available columns: {list(df.columns)}")
            return pd.DataFrame()
            
        # Convert and validate timestamp
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        invalid_timestamps = df['Timestamp'].isna().sum()
        
        if invalid_timestamps > 0:
            st.warning(f"⚠️ Found {invalid_timestamps} invalid timestamps - removing these rows")
            df = df.dropna(subset=['Timestamp'])
        
        # Convert sensor columns to numeric
        for col in SENSOR_INFO.keys():
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with all NaN sensor values
        sensor_cols = list(SENSOR_INFO.keys())
        df = df.dropna(subset=sensor_cols, how='all')
        
        if not df.empty:
            st.success(f"✅ Successfully loaded {len(df)} records (Last update: {df['Timestamp'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S')})")
        
        return df.sort_values('Timestamp').reset_index(drop=True)
        
    except FileNotFoundError:
        st.error(f"❌ File not found: `{DATA_FILE}`")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        st.error("❌ CSV file is empty")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.info("💡 Check if your CSV file format is correct")
        return pd.DataFrame()

@st.cache_data
def calculate_battery_soc(df_hash, df_json):
    """Calculate battery state of charge with caching"""
    try:
        df = pd.read_json(io.StringIO(df_json))
        if df.empty:
            return None
            
        soc = np.zeros(len(df))
        soc[0] = 80  # Start with 80% charge
        
        for i in range(1, len(df)):
            # Calculate solar power based on light intensity
            light = df['TSL2561_Light'].iloc[i]
            voltage = df['INA219_Voltage'].iloc[i] 
            current = df['ACS712_Current'].iloc[i]
            
            solar_power = voltage * current
            if light > SOLAR_THRESHOLD:
                # Solar efficiency factor based on light intensity
                solar_efficiency = min(light / 1000 * 0.2, 1.0)
                solar_power *= solar_efficiency
            else:
                solar_power = 0
                
            # Calculate power deficit/surplus
            power_deficit = LOAD_POWER - solar_power
            
            # Update battery SoC based on power flow
            if power_deficit <= 0:  # Excess solar power - charge battery
                charge_power = abs(power_deficit)
                charge_rate = (charge_power * 0.01) / (BATTERY_CAPACITY * BATTERY_VOLTAGE) * 100
                soc[i] = min(100, soc[i-1] + charge_rate)
            else:  # Power deficit - discharge battery
                discharge_rate = (power_deficit * 0.01) / (BATTERY_CAPACITY * BATTERY_VOLTAGE) * 100
                soc[i] = max(0, soc[i-1] - discharge_rate)
                
        return soc
    except Exception as e:
        st.error(f"Error calculating battery SoC: {str(e)}")
        return None

def determine_power_source(df, current_index):
    """Determine optimal power source based on conditions"""
    if df.empty or current_index < 0 or current_index >= len(df):
        return 'grid'
        
    try:
        # Get current sensor readings
        light = df['TSL2561_Light'].iloc[current_index]
        voltage = df['INA219_Voltage'].iloc[current_index]
        current = df['ACS712_Current'].iloc[current_index]
        
        # Calculate available solar power
        solar_power = voltage * current
        if light > SOLAR_THRESHOLD:
            solar_efficiency = min(light / 1000 * 0.2, 1.0)
            solar_power *= solar_efficiency
        else:
            solar_power = 0
        
        # Get battery SoC
        df_hash = hashlib.md5(str(df.values.tobytes()).encode()).hexdigest()
        df_json = df.to_json()
        battery_soc = calculate_battery_soc(df_hash, df_json)
        
        if battery_soc is not None:
            current_soc = battery_soc[current_index]
        else:
            current_soc = 50  # Default assumption
        
        # Decision logic
        if solar_power >= LOAD_POWER * 0.8:  # Solar can handle 80% of load
            return 'solar'
        elif current_soc > MIN_BATTERY_SOC:
            return 'battery'
        else:
            return 'grid'
            
    except Exception as e:
        st.error(f"Error determining power source: {str(e)}")
        return 'grid'

@st.cache_data
def calculate_power(df_hash, df_json, power_source):
    """Calculate power with caching"""
    try:
        df = pd.read_json(io.StringIO(df_json))
        if df.empty:
            return None
            
        # Base power calculation
        base_power = df['INA219_Voltage'] * df['ACS712_Current']
        
        if power_source == 'solar':
            # Solar power depends on light intensity
            efficiency = np.minimum(df['TSL2561_Light'] / 1000 * 0.2, 1.0)
            return base_power * efficiency
            
        elif power_source == 'battery':
            # Battery has ~90% efficiency
            return base_power * 0.9
            
        elif power_source == 'grid':
            # Grid power is base power
            return base_power
            
        elif power_source == 'auto':
            # Calculate optimal power for each timestamp
            power = np.zeros(len(df))
            for i in range(len(df)):
                source = determine_power_source(df, i)
                if source == 'solar':
                    efficiency = min(df['TSL2561_Light'].iloc[i] / 1000 * 0.2, 1.0)
                    power[i] = base_power.iloc[i] * efficiency
                elif source == 'battery':
                    power[i] = base_power.iloc[i] * 0.9
                else:  # grid
                    power[i] = base_power.iloc[i]
            return power
            
        return base_power
    except Exception as e:
        st.error(f"Error calculating power: {str(e)}")
        return None

@st.cache_data
def create_sensor_plot(df_hash, df_json, sensor):
    """Create sensor plot with caching"""
    try:
        df = pd.read_json(io.StringIO(df_json))
        info = SENSOR_INFO[sensor]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Timestamp'],
            y=df[sensor],
            mode='lines+markers',
            name=info['name'],
            line=dict(width=2),
            marker=dict(size=4)
        ))
        
        fig.update_layout(
            title=f"{info['name']} Over Time",
            xaxis_title="Time",
            yaxis_title=f"{info['name']} ({info['unit']})",
            showlegend=True,
            height=400,
            hovermode='x unified'
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating plot for {sensor}: {str(e)}")
        return None

def create_power_plot(df, power_source):
    """Create power plot"""
    try:
        df_hash = hashlib.md5(str(df.values.tobytes()).encode()).hexdigest()
        df_json = df.to_json()
        power = calculate_power(df_hash, df_json, power_source)
        
        if power is None:
            return None
            
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Timestamp'],
            y=power,
            mode='lines+markers',
            name=f"{POWER_SOURCES[power_source]['name']} Power",
            line=dict(color=POWER_SOURCES[power_source]['color'], width=2),
            marker=dict(size=4)
        ))
        
        # Add load power reference line
        fig.add_hline(y=LOAD_POWER, line_dash="dash", line_color="red",
                     annotation_text=f"Load Requirement ({LOAD_POWER}W)")
        
        fig.update_layout(
            title=f"{POWER_SOURCES[power_source]['name']} Power Output",
            xaxis_title="Time",
            yaxis_title="Power (W)",
            showlegend=True,
            height=400,
            hovermode='x unified'
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating power plot: {str(e)}")
        return None

def create_battery_plot(df):
    """Create battery SoC plot"""
    try:
        df_hash = hashlib.md5(str(df.values.tobytes()).encode()).hexdigest()
        df_json = df.to_json()
        soc = calculate_battery_soc(df_hash, df_json)
        
        if soc is None:
            return None
            
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Timestamp'],
            y=soc,
            mode='lines+markers',
            name='Battery SoC',
            line=dict(color=POWER_SOURCES['battery']['color'], width=2),
            marker=dict(size=4),
            fill='tonexty'
        ))
        
        # Add minimum SoC threshold
        fig.add_hline(y=MIN_BATTERY_SOC, line_dash="dash", line_color="red",
                     annotation_text=f"Minimum SoC ({MIN_BATTERY_SOC}%)")
        
        fig.update_layout(
            title="Battery State of Charge",
            xaxis_title="Time",
            yaxis_title="State of Charge (%)",
            yaxis=dict(range=[0, 100]),
            showlegend=True,
            height=400,
            hovermode='x unified'
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating battery plot: {str(e)}")
        return None

def main():
    # Initialize session state
    initialize_session_state()
    
    st.title("Smart Energy Management System")
    
    # Auto-refresh toggle
    col1, col2 = st.columns([3, 1])
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=False)
        if auto_refresh:
            st.rerun()
    
    # Load data
    df = load_data()
    
    # Early exit if no data
    if df.empty:
        st.warning("📊 **No data available**")
        st.markdown("""
        **Please check:**
        - File exists at: `data/sensor_data.csv`
        - File contains valid data with proper column headers
        - Timestamps are in valid format
        """)
        
        # Show expected format
        with st.expander("📋 Expected CSV Format"):
            st.code("""
Timestamp,TSL2561_Light,ACS712_Current,INA219_Voltage,DS18B20_Temp,MQ8_H2_Level,DHT22_Temp,DHT22_Humidity,YF_S201_Flow
2025-06-12 11:23:46.699197,505.81,15.23,17.04,30.63,0.5,26.71,54.56,5.09
            """, language="csv")
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ System Control")
        st.markdown("---")
        
        # Power source selection
        st.markdown("#### 🔌 Power Source")
        power_source = st.radio(
            "Select Power Source",
            options=list(POWER_SOURCES.keys()),
            format_func=lambda x: f"{POWER_SOURCES[x]['icon']} {POWER_SOURCES[x]['name']}",
            help="Choose how to power your system"
        )
        
        st.markdown("---")
        st.markdown("#### 📊 Quick Stats")
        
        # Quick stats
        latest_time = df['Timestamp'].iloc[-1].strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"**📅 Last Update:** {latest_time}")
        st.markdown(f"**📈 Total Records:** {len(df)}")
        
        # Current power source in auto mode
        if power_source == 'auto':
            current_source = determine_power_source(df, -1)
            st.markdown(f"**⚡ Current Source:** {POWER_SOURCES[current_source]['icon']} {POWER_SOURCES[current_source]['name']}")
        
        # Data quality indicator
        data_quality = (1 - df.isnull().sum().sum() / (len(df) * len(SENSOR_INFO))) * 100
        st.markdown(f"**✅ Data Quality:** {data_quality:.1f}%")
    
    # Main content
    st.header("📊 System Metrics")
    
    # Create sensor metric cards
    cols = st.columns(4)
    for i, (sensor, info) in enumerate(SENSOR_INFO.items()):
        with cols[i % 4]:
            try:
                latest_value = df[sensor].iloc[-1]
                
                # Create metric card
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-icon">{info['icon']}</div>
                        <div class="metric-label">{info['name']}</div>
                        <div class="metric-description">{info['description']}</div>
                        <div class="metric-value">{latest_value:.2f}<span class="metric-unit">{info['unit']}</span></div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Toggle button for graphs
                if st.button(f"📈 View Graph", key=f"btn_{sensor}"):
                    st.session_state.show_graphs[sensor] = not st.session_state.show_graphs.get(sensor, False)
                
                # Show graph if toggled
                if st.session_state.show_graphs.get(sensor, False):
                    df_hash = hashlib.md5(str(df.values.tobytes()).encode()).hexdigest()
                    df_json = df.to_json()
                    fig = create_sensor_plot(df_hash, df_json, sensor)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
            except Exception as e:
                st.error(f"Error displaying {sensor}: {str(e)}")
    
    # Power Management Section
    st.header("⚡ Power Management")
    
    power_col, battery_col = st.columns(2)
    
    with power_col:
        try:
            df_hash = hashlib.md5(str(df.values.tobytes()).encode()).hexdigest()
            df_json = df.to_json()
            power_data = calculate_power(df_hash, df_json, power_source)
            
            if power_data is not None:
                latest_power = power_data.iloc[-1] if hasattr(power_data, 'iloc') else power_data[-1]
                
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-icon">{POWER_SOURCES[power_source]['icon']}</div>
                        <div class="metric-label">{POWER_SOURCES[power_source]['name']} Power</div>
                        <div class="metric-description">{POWER_SOURCES[power_source]['description']}</div>
                        <div class="metric-value">{latest_power:.2f}<span class="metric-unit">W</span></div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("📈 View Power Graph", key="btn_power"):
                    st.session_state.show_graphs['power'] = not st.session_state.show_graphs.get('power', False)
                
                if st.session_state.show_graphs.get('power', False):
                    fig = create_power_plot(df, power_source)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
        except Exception as e:
            st.error(f"Error displaying power data: {str(e)}")
    
    with battery_col:
        try:
            df_hash = hashlib.md5(str(df.values.tobytes()).encode()).hexdigest()
            df_json = df.to_json()
            soc_data = calculate_battery_soc(df_hash, df_json)
            
            if soc_data is not None:
                latest_soc = soc_data[-1]
                
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-icon">🔋</div>
                        <div class="metric-label">Battery State of Charge</div>
                        <div class="metric-description">Current battery charge level</div>
                        <div class="metric-value">{latest_soc:.1f}<span class="metric-unit">%</span></div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("📈 View Battery Graph", key="btn_battery"):
                    st.session_state.show_graphs['battery'] = not st.session_state.show_graphs.get('battery', False)
                
                if st.session_state.show_graphs.get('battery', False):
                    fig = create_battery_plot(df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
        except Exception as e:
            st.error(f"Error displaying battery data: {str(e)}")
    
    # Current status in auto mode
    if power_source == 'auto':
        current_source = determine_power_source(df, -1)
        st.markdown(f"""
            <div class="status-indicator">
                🔄 Auto Mode Active - Currently Using: {POWER_SOURCES[current_source]['icon']} {POWER_SOURCES[current_source]['name']}
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()