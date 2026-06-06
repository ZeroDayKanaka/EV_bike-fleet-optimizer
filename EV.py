import pandas as pd
import numpy as np
import random

# Set a random seed so the data is consistent every time you run it
np.random.seed(42)
random.seed(42)

# Fleet Simulation Parameters
NUM_VEHICLES = 20
RECORDS_PER_VEHICLE = 50

# Pre-generate VINs
vins = [f"VIN_{str(i).zfill(3)}" for i in range(1, NUM_VEHICLES + 1)]

data = []

for vin in vins:
    # Assign a starting base for cumulative cycles so some cars look older than others
    base_cycles = np.random.randint(10, 1200)
    
    for _ in range(RECORDS_PER_VEHICLE):
        # Simulate state of charge between 10% and 100%
        soc = np.random.uniform(10.0, 100.0)
        
        # Determine if fast charging is active (20% probability)
        fast_charge = np.random.choice([0, 1], p=[0.8, 0.2])
        
        # Simulate battery temperature
        # We force a 10% chance of the temperature crossing the 45°C threshold
        if random.random() < 0.10 or (fast_charge == 1 and random.random() < 0.40):
            temp_c = np.random.uniform(45.1, 58.0) # Thermal Risk Zone
        else:
            temp_c = np.random.uniform(20.0, 44.9) # Safe Zone
            
        # Simulate voltage (typically around 350-400V)
        voltage = np.random.uniform(350.0, 380.0) + (soc * 0.2)
        
        # Simulate current (Amps) - positive for charging/driving, negative for regen braking
        current = np.random.uniform(-50.0, 200.0)
        
        # Increment charge cycles slightly per record
        base_cycles += np.random.uniform(0.01, 0.5)
        
        # Append the simulated row
        data.append({
            "Vehicle_VIN": vin,
            "State_of_Charge_Pct": round(soc, 2),
            "Battery_Temperature_C": round(temp_c, 2),
            "Voltage_V": round(voltage, 2),
            "Current_A": round(current, 2),
            "Cumulative_Charge_Cycles": int(base_cycles),
            "Fast_Charging_Flag": fast_charge
        })

# Create the DataFrame
df = pd.DataFrame(data)

# Export to CSV
csv_filename = "ev_battery_logs.csv"
df.to_csv(csv_filename, index=False)

print(f"Success! Generated {len(df)} telemetry records for {NUM_VEHICLES} vehicles.")
print(f"Data saved to: {csv_filename}")