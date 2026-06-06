import pandas as pd

# 1. Define a simple 24-hour electricity tariff in INR (Price per kWh)
# Cheap at night (10 PM to 6 AM), Expensive during the day (7 AM to 9 PM)
def get_electricity_price_inr(hour):
    if 7 <= hour <= 21:
        return 9.00  # Peak commercial price: ₹9.00 per kWh
    else:
        return 5.00  # Off-Peak price: ₹5.00 per kWh

# 2. Smart Charging Optimization Engine
def optimize_charging_inr(current_soc, departure_hour, battery_capacity_kwh=60):
    target_soc = 100
    needed_soc = target_soc - current_soc
    
    if needed_soc <= 0:
        return "Battery is already full. No charging needed."
    
    # Calculate energy needed in kWh
    energy_needed_kwh = (needed_soc / 100) * battery_capacity_kwh
    
    # Standard slow charger speed = 7 kW per hour
    charging_speed_kw = 7 
    hours_needed = int(round(energy_needed_kwh / charging_speed_kw))
    
    # Look at the available hours before departure to find the cheapest slots
    available_hours = []
    for h in range(0, 24):
        if h < departure_hour:
            available_hours.append({
                "hour": h,
                "price": get_electricity_price_inr(h)
            })
            
    # Sort slots by price (cheapest first)
    cheapest_slots = sorted(available_hours, key=lambda x: x['price'])
    
    # Select the number of slots we need
    scheduled_slots = cheapest_slots[:hours_needed]
    scheduled_hours = [slot['hour'] for slot in scheduled_slots]
    scheduled_hours.sort() 
    
    # Calculate total cost in Rupees
    total_cost = sum(slot['price'] * charging_speed_kw for slot in scheduled_slots)
    
    return {
        "Hours_Needed": hours_needed,
        "Optimal_Charging_Hours": scheduled_hours,
        "Estimated_Cost_INR": round(total_cost, 2)
    }

# 3. Test the optimizer
test_schedule = optimize_charging_inr(current_soc=30, departure_hour=8)

print("--- SMART CHARGING SCHEDULE ---")
print(f"Hours of charging required: {test_schedule['Hours_Needed']} hours")
print(f"Recommended hours to turn on chargers: {test_schedule['Optimal_Charging_Hours']}")
print(f"Minimized Charging Cost: ₹{test_schedule['Estimated_Cost_INR']}")