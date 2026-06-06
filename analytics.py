import pandas as pd
import numpy as np

# 1. Load the EV telemetry data
df = pd.read_csv('ev_battery_logs.csv')

# 2. Thermal Risk Indexing: Flag if temperature is above 45°C
df['Thermal_Risk_Flag'] = np.where(df['Battery_Temperature_C'] > 45.0, 1, 0)

# 3. State of Health (SoH) Formula
def calculate_soh(row):
    health = 100.0 
    
    # Age penalty: lose 0.02% per charge cycle
    cycle_penalty = row['Cumulative_Charge_Cycles'] * 0.02
    health = health - cycle_penalty
    
    # Heat penalty: lose an extra 2% if currently overheating
    if row['Thermal_Risk_Flag'] == 1:
        health = health - 2.0
        
    return max(0, round(health, 2))

# Apply the SoH formula
df['State_of_Health_Pct'] = df.apply(calculate_soh, axis=1)

# 4. NEW CODE: Degradation Status Classification
def check_degradation_status(soh):
    if soh >= 85:
        return "Healthy"
    elif soh >= 70:
        return "Moderate Degradation"
    else:
        return "Severely Degraded"

# Apply the degradation classification
df['Battery_Condition'] = df['State_of_Health_Pct'].apply(check_degradation_status)

# 5. Let's look at the final results!
print("--- ANALYSIS COMPLETE ---")
print(df[['Vehicle_VIN', 'State_of_Health_Pct', 'Battery_Condition']].head(10))

print("\n--- FLEET HEALTH SUMMARY ---")
print(df['Battery_Condition'].value_counts())