# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 13:28:59 2024

@author: me
"""
import CoolProp.CoolProp as CP

from tabulate import tabulate

def calculate_properties(fluid, temperature=None, pressure=None, quality=None, enthalpy=None, entropy=None):
    """
    General helper function to calculate common thermodynamic properties.
    
    Parameters:
    - fluid: Refrigerant or fluid type.
    - temperature (T): Temperature in Kelvin.
    - pressure (P): Pressure in Pascal.
    - quality (Q): Quality (vapor fraction) as a decimal (0 to 1).
    - enthalpy (H): Enthalpy (J/kg).
    - entropy (S): Entropy (J/kg-K).
    
    Returns:
    - Tuple: (Pressure, Enthalpy, Entropy, Temperature) based on input parameters.
    """
    try:
        if quality is not None and pressure:
            # Calculate temperature, enthalpy, and entropy from quality and pressure
            temperature = CP.PropsSI('T', 'Q', quality, 'P', pressure, fluid)
            enthalpy = CP.PropsSI('H', 'Q', quality, 'P', pressure, fluid)
            entropy = CP.PropsSI('S', 'Q', quality, 'P', pressure, fluid)
            return temperature, enthalpy, entropy

        elif temperature and quality is not None:
            # Calculate pressure, enthalpy, and entropy from temperature and quality
            pressure = CP.PropsSI('P', 'Q', quality, 'T', temperature, fluid)
            enthalpy = CP.PropsSI('H', 'Q', quality, 'T', temperature, fluid)
            entropy = CP.PropsSI('S', 'Q', quality, 'T', temperature, fluid)
            return pressure, enthalpy, entropy

        elif temperature and pressure:
            # Calculate enthalpy and entropy from temperature and pressure
            enthalpy = CP.PropsSI('H', 'T', temperature, 'P', pressure, fluid)
            entropy = CP.PropsSI('S', 'T', temperature, 'P', pressure, fluid)
            return pressure, enthalpy, entropy

        elif enthalpy and pressure:
            # Calculate temperature and entropy from enthalpy and pressure
            temperature = CP.PropsSI('T', 'H', enthalpy, 'P', pressure, fluid)
            entropy = CP.PropsSI('S', 'H', enthalpy, 'P', pressure, fluid)
            return temperature, enthalpy, entropy

        elif entropy and pressure:
            # Calculate temperature and enthalpy from entropy and pressure
            temperature = CP.PropsSI('T', 'S', entropy, 'P', pressure, fluid)
            enthalpy = CP.PropsSI('H', 'S', entropy, 'T', temperature, fluid)
            return temperature, enthalpy, entropy

        else:
            raise ValueError("Invalid input combination. You must provide (T, P), (T, Q), (H, P), or (S, P).")

    except Exception as e:
        print(f"Error calculating properties: {e}")
        return None, None, None  # Return empty values in case of an error

"""
Adjust subcool temp
"""

def adjust_subcooler_temp(Sink_T_inlet, P6, fluid):
    """
    Adjust the subcooler temperature based on the sink inlet temperature.
    """
    if Sink_T_inlet <= 50:
        return round(CP.PropsSI('T', 'P', P6, 'Q', 0, fluid), 1) - 15
    elif 50 < Sink_T_inlet <= 70:
        return round(CP.PropsSI('T', 'P', P6, 'Q', 0, fluid), 1) - 10
    elif 70 < Sink_T_inlet <= 90:
        return round(CP.PropsSI('T', 'P', P6, 'Q', 0, fluid), 1) - 6
    elif 90 < Sink_T_inlet <= 100:
        return round(CP.PropsSI('T', 'P', P6, 'Q', 0, fluid), 1) - 4
    else:
        return round(CP.PropsSI('T', 'P', P6, 'Q', 0, fluid), 1) - 3

"""
display results
"""

# Function to display results in a more structured format
def display_results(results):
    table_data = []

    # Define custom formatting based on keys
    for key, value in results.items():
        if isinstance(value, float):  # If the value is a float, format it with two decimals
            formatted_value = f"{value:.2f}"
        else:  # For non-float values, just convert to string
            formatted_value = str(value)

        # Colorize based on specific keys
        if key in ["Power Comp 1 (MW)", "Power Comp 2 (MW)", "Total Electric Power (MW)"]:
            row = [f"\033[94m{key}\033[0m", f"\033[94m{formatted_value}\033[0m"]  # Blue text for power
        elif key == "COP":
            row = [f"\033[92m{key}\033[0m", f"\033[92m{formatted_value}\033[0m"]  # Green text for COP
        elif key == "Sink Power (MW)":
            row = [f"\033[91m{key}\033[0m", f"\033[91m{formatted_value}\033[0m"]  # Red text for sink power
        else:
            row = [key, formatted_value]  # Default display for other keys

        table_data.append(row)

    # Use the tabulate function to display the results in a structured table
    print(tabulate(table_data, headers=["Parameter", "Value"], tablefmt="grid"))

