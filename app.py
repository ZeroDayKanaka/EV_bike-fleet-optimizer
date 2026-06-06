import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Set up page configurations
st.set_page_config(page_title="E-Bike Fleet Optimizer", layout="wide", page_icon="⚡")

# --- 🎨 ENTERPRISE LIGHT BLUE THEME (FIXED TEXT VISIBILITY) ---
st.markdown("""
    <!-- Load FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
    /* 1. Professional Light Blue App Background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
        color: #0A192F !important; /* Force main text to be dark navy */
    }
    
    /* 2. Make top header bar blend in transparently */
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    /* Force ALL standard text, labels, and markdown outside cards to be dark navy */
    p, span, label, th, td, .stMarkdown {
        color: #0A192F !important;
    }
    
    /* Main Title Color */
    h1 {
        color: #023E8A !important; /* Deep Royal Blue */
        font-weight: 800 !important;
    }
    
    /* Subheaders and Section Titles */
    h2, h3, h4 {
        color: #023E8A !important; 
    }

    /* --- PROFESSIONAL KPI CARD STYLES (Stays Dark Blue with White/Cyan Text) --- */
    .kpi-card-custom {
        background-color: #172A45 !important; 
        border: 1px solid #233554 !important; 
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15) !important;
        margin-bottom: 20px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        height: 100% !important;
    }

    /* Keep text INSIDE the custom KPI cards white and light blue */
    .kpi-card-custom div, 
    .kpi-card-custom span, 
    .kpi-card-custom i,
    .kpi-card-custom .kpi-label-custom {
        color: #A8B2D1 !important; /* Soft grayish-blue for labels */
    }

    .kpi-label-custom {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-bottom: 10px !important;
        display: flex !important;
        align-items: center !important;
    }

    .kpi-label-custom i {
        color: #00B4D8 !important; /* Light Blue highlight for icons */
        margin-right: 12px !important;
        font-size: 1.4rem !important;
    }

    .kpi-card-custom .kpi-value-custom,
    .kpi-card-custom .highlight-value {
        color: #00B4D8 !important; /* Light blue numbers */
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    
    /* Fix slider label colors explicitly */
    div[data-testid="stSlider"] label p {
        color: #0A192F !important;
        font-weight: bold !important;
    }
    
    /* Colored Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #172A45 !important; 
        border-radius: 8px 8px 0px 0px !important;
        padding: 10px 20px !important;
        border: 1px solid #233554 !important;
    }
    
    /* Tab text states */
    .stTabs [data-baseweb="tab"] p {
        color: #FFFFFF !important; /* White text for non-selected tabs */
    }
    .stTabs [aria-selected="true"] {
        background-color: #00B4D8 !important; 
        border: 1px solid #00B4D8 !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #0A192F !important; /* Dark text for active tab */
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ EV Bike Fleet Command Center")
st.markdown("<h4 style='text-align: center;'>Welcome <b>Kanaka M</b>! Monitor your two-wheeler delivery fleet health and charging windows.</h4>", unsafe_allow_html=True)
st.markdown("---")

# --- 1. LOAD AND PROCESS FLEET DATA ---
@st.cache_data
def load_and_process_data():
    df = pd.read_csv('ev_battery_logs.csv')
    df['Thermal_Risk_Flag'] = np.where(df['Battery_Temperature_C'] > 45.0, 1, 0)
    
    def calculate_soh(row):
        health = 100.0 - (row['Cumulative_Charge_Cycles'] * 0.02)
        if row['Thermal_Risk_Flag'] == 1: health -= 2.0
        return max(0, round(health, 2))
    
    df['State_of_Health_Pct'] = df.apply(calculate_soh, axis=1)
    
    def check_degradation(soh):
        if soh >= 85: return "Healthy"
        elif soh >= 70: return "Moderate Degradation"
        else: return "Severely Degraded"
        
    df['Battery_Condition'] = df['State_of_Health_Pct'].apply(check_degradation)
    return df

try:
    df_fleet = load_and_process_data()
except FileNotFoundError:
    st.error("Missing 'ev_battery_logs.csv'. Please make sure your data generation script has run successfully first!")
    st.stop()

# --- 2. SMART CHARGING LOGIC FOR BIKES ---
def optimize_charging_inr(current_soc, departure_hour, battery_capacity_kwh=4, charging_speed_kw=1):
    target_soc = 100
    needed_soc = target_soc - current_soc
    if needed_soc <= 0: return 0, [], 0
        
    energy_needed_kwh = (needed_soc / 100) * battery_capacity_kwh
    hours_needed = int(np.ceil(energy_needed_kwh / charging_speed_kw))
    
    available_hours = []
    for h in range(0, 24):
        if h < departure_hour:
            price = 9.00 if 7 <= h <= 21 else 5.00
            available_hours.append({"hour": h, "price": price})
            
    cheapest_slots = sorted(available_hours, key=lambda x: x['price'])[:hours_needed]
    scheduled_hours = sorted([slot['hour'] for slot in cheapest_slots])
    total_cost = sum(slot['price'] * charging_speed_kw for slot in cheapest_slots)
    
    return hours_needed, scheduled_hours, round(total_cost, 2)

# --- 3. FRONTEND TABS ---
tab1, tab2 = st.tabs(["📊 Bike Health & Swap Ledger", "🔌 E-Bike Smart Charger"])

with tab1:
    st.header("Overall E-Bike Fleet Health Overview")
    
    # --- GET REAL-TIME METRICS ---
    df_latest_status = df_fleet.groupby('Vehicle_VIN').last().reset_index()
    total_vehicles = df_latest_status['Vehicle_VIN'].nunique()
    avg_soh = round(df_latest_status['State_of_Health_Pct'].mean(), 1)
    permanent_swap_count = df_latest_status[df_latest_status['Battery_Condition'] == "Severely Degraded"].shape[0]
    low_battery_swap_count = df_latest_status[df_latest_status['State_of_Charge_Pct'] < 20.0].shape[0]
    
    # --- CUSTOM PROFESSIONAL KPI CARDS ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="kpi-card-custom">
                <div class="kpi-label-custom"><i class="fa-solid fa-motorcycle"></i> Managed E-Bikes</div>
                <div class="kpi-value-custom">{total_vehicles}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="kpi-card-custom">
                <div class="kpi-label-custom"><i class="fa-solid fa-heart-pulse"></i> Average Fleet SoH</div>
                <div class="kpi-value-custom highlight-value">{avg_soh}%</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="kpi-card-custom">
                <div class="kpi-label-custom"><i class="fa-solid fa-battery-quarter"></i> Low-Battery Swap</div>
                <div class="kpi-value-custom highlight-value">{low_battery_swap_count}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="kpi-card-custom">
                <div class="kpi-label-custom"><i class="fa-solid fa-triangle-exclamation"></i> New Battery Pack</div>
                <div class="kpi-value-custom highlight-value">{permanent_swap_count}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Bottom Section Layout
    bot_col1, bot_col2 = st.columns([1, 1.5])
    
    with bot_col1:
        st.subheader("📈 Health Distribution")
        fig = px.pie(
            df_latest_status, 
            names='Battery_Condition', 
            hole=0.5,
            color_discrete_sequence=['#00B4D8', '#023E8A', '#48CAE4'] 
        )
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#0A192F'), margin=dict(t=20, b=20, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with bot_col2:
        st.subheader("📋 Raw Telemetry & Status Logs")
        st.dataframe(df_fleet[['Vehicle_VIN', 'State_of_Charge_Pct', 'Battery_Temperature_C', 'State_of_Health_Pct', 'Battery_Condition']], use_container_width=True)

with tab2:
    st.header("🔌 Smart Charging Optimizer Engine")
    st.markdown("Adjust parameters below to evaluate cost-savings for a delivery bike plugged in at the hub.")
    
    st.markdown("<div style='background-color: #172A45; padding: 20px; border-radius: 12px; border: 1px solid #233554; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    input_soc = c1.slider("Current State of Charge (SoC %)", min_value=10, max_value=95, value=30, step=5)
    input_departure = c2.slider("Required Departure Deadline (Hour of Day)", min_value=1, max_value=23, value=8, step=1)
    st.markdown("</div>", unsafe_allow_html=True)
    
    hrs_needed, opt_hours, cost_inr = optimize_charging_inr(input_soc, input_departure)
    
    st.markdown("---")
    
    # Custom styled output for the calculator
    res_html = f"""
    <div style="display: flex; gap: 20px; justify-content: space-between;">
        <div class="kpi-card-custom" style="width: 33%;">
            <div class="kpi-label-custom"><i class="fa-solid fa-clock"></i> Charging Required</div>
            <div class="kpi-value-custom highlight-value">{hrs_needed} Hrs</div>
        </div>
        <div class="kpi-card-custom" style="width: 33%;">
            <div class="kpi-label-custom"><i class="fa-solid fa-calendar-check"></i> Allocated Time Blocks</div>
            <div class="kpi-value-custom highlight-value" style="font-size: 1.8rem;">Hr: {opt_hours}</div>
        </div>
        <div class="kpi-card-custom" style="width: 33%;">
            <div class="kpi-label-custom"><i class="fa-solid fa-indian-rupee-sign"></i> Minimized Tariff Cost</div>
            <div class="kpi-value-custom highlight-value">₹{cost_inr}</div>
        </div>
    </div>
    """
    st.markdown(res_html, unsafe_allow_html=True)

st.markdown("---")
st.caption("Pragyan AI Hackathon Project - Constructed using Streamlit, Pandas, and Plotly.")