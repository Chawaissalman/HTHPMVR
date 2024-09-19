import numpy as np
import CoolProp.CoolProp as CP
import math
import matplotlib.pyplot as plt
from tabulate import tabulate
from HTHP_Source import calculate_heat_pump_performance_source
from helper_functions import calculate_properties, adjust_subcooler_temp
import constants
from scipy.optimize import fsolve


# Function to calculate the difference between mass_sink_given and mass_sink_calculated
def mass_sink_difference(mass_flow_source, fluid, source_inlet_temp, source_inlet_pressure, 
                         source_outlet_temp, evaporator_temp_diff, SH_temp_diff, sink_required_temp, 
                         eff_isentropic, eff_isentropic_c2, comp2_press_factor, eff_mech, 
                         Sink_T_inlet, Sink_P_inlet, Sink_T_outlet, Sink_P_outlet, mass_sink_given):
    
    # Perform the HTHP calculation
    results = calculate_heat_pump_performance_source(
        fluid, 
        source_inlet_temp, 
        source_inlet_pressure, 
        mass_flow_source, 
        source_outlet_temp, 
        evaporator_temp_diff, 
        SH_temp_diff, 
        sink_required_temp, 
        eff_isentropic, 
        eff_isentropic_c2, 
        comp2_press_factor, 
        eff_mech, 
        Sink_T_inlet, 
        Sink_P_inlet, 
        Sink_T_outlet, 
        Sink_P_outlet
    )
    
    mass_sink_calculated = results['mass sink steam/water']
    
    # Return the difference between mass_sink_given and mass_sink_calculated
    return mass_sink_given - mass_sink_calculated

# Function to calculate heat pump performance using fsolve to solve for mass_flow_source
def calculate_heat_pump_performance_sink(fluid, source_inlet_temp, source_inlet_pressure, mass_flow_source, 
                                         source_outlet_temp, evaporator_temp_diff, SH_temp_diff, 
                                         sink_required_temp, eff_isentropic, eff_isentropic_c2, 
                                         comp2_press_factor, eff_mech, Sink_T_inlet, Sink_P_inlet, 
                                         Sink_T_outlet, Sink_P_outlet, mass_sink_given):
    
    # Perform the initial HTHP calculation
    results_initial = calculate_heat_pump_performance_source(
        fluid, 
        source_inlet_temp, 
        source_inlet_pressure, 
        mass_flow_source, 
        source_outlet_temp, 
        evaporator_temp_diff, 
        SH_temp_diff, 
        sink_required_temp, 
        eff_isentropic, 
        eff_isentropic_c2, 
        comp2_press_factor, 
        eff_mech, 
        Sink_T_inlet, 
        Sink_P_inlet, 
        Sink_T_outlet, 
        Sink_P_outlet
    )

    hin_sink = CP.PropsSI('H', 'T', Sink_T_inlet + 273.15, 'P', Sink_P_inlet * 100000, 'water')
    hout_sink = CP.PropsSI('H', 'T', Sink_T_outlet + 273.15, 'P', Sink_P_outlet * 100000, 'water')
    heat_sink = mass_sink_given * (hout_sink-hin_sink)/1e6
    
    COP = results_initial['COP']
    heat_source = heat_sink - heat_sink / COP
    hin = CP.PropsSI('H', 'T', source_inlet_temp + 273.15, 'P', source_inlet_pressure * 100000, 'water')
    hout = CP.PropsSI('H', 'T', source_outlet_temp + 273.15, 'P', source_inlet_pressure * 100000, 'water')
    mass_flow_source_initial = heat_source * 1e6 / (hin - hout)  # kW

    # Use fsolve to find the mass_flow_source that balances the mass sink
    optimal_mass_flow_source = fsolve(
        mass_sink_difference, 
        mass_flow_source_initial, 
        args=(
            fluid, 
            source_inlet_temp, 
            source_inlet_pressure, 
            source_outlet_temp, 
            evaporator_temp_diff, 
            SH_temp_diff, 
            sink_required_temp, 
            eff_isentropic, 
            eff_isentropic_c2, 
            comp2_press_factor, 
            eff_mech, 
            Sink_T_inlet, 
            Sink_P_inlet, 
            Sink_T_outlet, 
            Sink_P_outlet, 
            mass_sink_given
        )
    )[0]  # Extract the optimal value from the array

    print(f"Optimal mass_flow_source found: {optimal_mass_flow_source:.6f} kg/s")

    # Recalculate the final results with the optimal mass_flow_source
    results = calculate_heat_pump_performance_source(
        fluid, 
        source_inlet_temp, 
        source_inlet_pressure, 
        optimal_mass_flow_source, 
        source_outlet_temp, 
        evaporator_temp_diff, 
        SH_temp_diff, 
        sink_required_temp, 
        eff_isentropic, 
        eff_isentropic_c2, 
        comp2_press_factor, 
        eff_mech, 
        Sink_T_inlet, 
        Sink_P_inlet, 
        Sink_T_outlet, 
        Sink_P_outlet
    )
    
    return results

# Inputs for source
source_inlet_temp = 70.0  # °C
source_inlet_pressure = 6.0  # bar
mass_flow_source = 1.0  # kg/s
heat_source = 0  # MW
source_outlet_temp = 50.20  # °C

# Inputs for sink
Sink_T_inlet = 90  # °C
Sink_P_inlet = 8.0  # bar
Sink_P_outlet = 1.4  # bar
Sink_T_outlet = 120.3  # °C
heat_sink = 0
mass_sink = 8.79

sink_required_temp = Sink_T_outlet + 10

  # Based on source in and out temp diff is selected
diff = source_inlet_temp - source_outlet_temp
if diff > 10:
      SH_temp_diff = 8
elif 5 < diff <= 10:
      SH_temp_diff = 5
elif diff <= 5:
      SH_temp_diff = 2

# Example usage of the rest of your function
results = calculate_heat_pump_performance_sink(
        fluid='R1233ZD', 
        source_inlet_temp=source_inlet_temp, 
        source_inlet_pressure=source_inlet_pressure, 
        mass_flow_source=1, 
        source_outlet_temp=source_outlet_temp, 
        evaporator_temp_diff=3.0, 
        SH_temp_diff=SH_temp_diff, 
        sink_required_temp=sink_required_temp, 
        eff_isentropic=0.8, 
        eff_isentropic_c2=0.8, 
        comp2_press_factor=0.995,
        eff_mech=0.98, 
        Sink_T_inlet=Sink_T_inlet, 
        Sink_P_inlet=Sink_P_inlet, 
        Sink_T_outlet=Sink_T_outlet, 
        Sink_P_outlet=Sink_P_outlet,
        mass_sink_given = mass_sink
    )

# Printing the results
table_data = []
for key, value in results.items():
    row = [key, f"{value}"]

    # Check for specific keys to colorize
    if key in ["Power Comp 1 (MW)", "Power Comp 2 (MW)", "Total Electric Power (MW)"]:
        row = [f"\033[94m{key}\033[0m", f"\033[94m{value}\033[0m"]  # Blue text
    elif key == "COP":
        row = [f"\033[92m{key}\033[0m", f"\033[92m{value}\033[0m"]  # Green text
    elif key == "Sink Power (MW)":
        row = [f"\033[91m{key}\033[0m", f"\033[91m{value}\033[0m"]  # Red text

    table_data.append(row)

    # Print the table
print(tabulate(table_data, headers=["Parameter", "Value"], tablefmt="grid"))


