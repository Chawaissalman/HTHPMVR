# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 22:29:03 2024

@author: me
"""
import numpy as np
import CoolProp.CoolProp as CP
import math
import streamlit as st

def check_inputs_source(fluid, source_inlet_temp, source_outlet_temp, source_inlet_pressure,
                 mass_flow_source, heat_source):
    """
    Check the inputs mass_flow_source and heat_source based on the given conditions.
    
    Parameters:
    fluid (str): Fluid name.
    source_inlet_temp (float): Source inlet temperature in °C.
    source_outlet_temp (float): Source outlet temperature in °C.
    source_inlet_pressure (float): Source inlet pressure in bar.
    mass_flow_source (float): Mass flow rate of the source in kg/s (can be zero).
    heat_source (float): Heat source in MW (can be zero).
    
    Returns:
    Tuple: A tuple containing the validated mass_flow_source and any messages.
    """
    # Initialize messages and status
    messages = []
    
    # Enthalpy at the source inlet and outlet (J/kg)
    hin = CP.PropsSI('H', 'T', source_inlet_temp + 273.15, 'P', source_inlet_pressure * 100000, fluid)
    hout = CP.PropsSI('H', 'T', source_outlet_temp + 273.15, 'P', source_inlet_pressure * 100000, fluid)
    
    # Enthalpy difference (J/kg)
    delta_h = (hin - hout) / 1000  # Convert to kJ/kg
    
    # Condition 1: Both mass_flow_source and heat_source are zero
    if mass_flow_source == 0 and heat_source == 0:
        raise ValueError("Please provide either mass_flow_source or heat_source.")
    
    # Condition 2: mass_flow_source and heat_source are given
    if mass_flow_source > 0 and heat_source > 0:
        # Convert heat_source from MW to kW (1 MW = 1000 kW)
        heat_source_kw = heat_source * 1000
        
        # Calculate mass flow from heat_source (kW)
        calculated_mass_flow = heat_source_kw / delta_h
        
        # Check if mass_flow_source is +/- 98% of calculated mass flow
        if not (0.98 * calculated_mass_flow <= mass_flow_source <= 1.02 * calculated_mass_flow):
            messages.append("Warning: mass_flow_source and heat_source are not aligned.")
            messages.append(f"Provided mass_flow_source: {mass_flow_source:.3f} kg/s")
            messages.append(f"Calculated from heat_source: {calculated_mass_flow:.3f} kg/s")
            messages.append("Using the smaller of the two values.")
            
            # Use the smaller value
            mass_flow_source = min(mass_flow_source, calculated_mass_flow)
    
    # Condition 3: heat_source is given, mass_flow_source is zero
    elif heat_source > 0 and mass_flow_source == 0:
        # Convert heat_source from MW to kW (1 MW = 1000 kW)
        heat_source_kw = heat_source * 1000
        
        # Calculate mass_flow_source from heat_source (kW)
        mass_flow_source = heat_source_kw / delta_h
        messages.append(f"Calculated mass flow of source from provided heat source is: {mass_flow_source:.1f} kg/s")
    
       
    # Return the validated mass_flow_source and messages
    return mass_flow_source, messages

'------------------------------------------------------------------------------'

def check_inputs_sink(fluid, Sink_T_inlet, Sink_T_outlet, Sink_P_inlet, Sink_P_outlet, 
                      mass_sink, heat_sink):
    """
    Check the inputs mass_sink and heat_sink based on the given conditions.
    
    Parameters:
    fluid (str): Fluid name.
    Sink_T_inlet (float): Sink inlet temperature in °C.
    Sink_T_outlet (float): Sink outlet temperature in °C.
    Sink_P_inlet (float): Sink inlet pressure in bar.
    Sink_P_outlet (float): Sink outlet pressure in bar.
    mass_sink (float): Mass flow rate of the sink in kg/s (can be zero).
    heat_sink (float): Heat sink in MW (can be zero).
    
    Returns:
    Tuple: A tuple containing the validated mass_sink and any messages.
    """
    # Initialize messages
    messages = []
    
    # Enthalpy at the sink inlet and outlet (J/kg)
    hin = CP.PropsSI('H', 'T', Sink_T_inlet + 273.15, 'P', Sink_P_inlet * 100000, fluid)
    hout = CP.PropsSI('H', 'T', Sink_T_outlet + 273.15, 'P', Sink_P_outlet * 100000, fluid)
    
    # Enthalpy difference (J/kg)
    delta_h = (hout - hin) / 1000  # Convert to kJ/kg
    
    # Condition 1: Both mass_sink and heat_sink are zero
    if mass_sink == 0 and heat_sink == 0:
        raise ValueError("Please provide either mass_sink or heat_sink.")
    
    # Condition 2: mass_sink and heat_sink are both given
    if mass_sink > 0 and heat_sink > 0:
        # Convert heat_sink from MW to kW (1 MW = 1000 kW)
        heat_sink_kw = heat_sink * 1000
        
        # Calculate mass flow from heat_sink (kW)
        calculated_mass_sink = heat_sink_kw / delta_h
        
        # Check if mass_sink is +/- 98% of calculated mass flow
        if not (0.98 * calculated_mass_sink <= mass_sink <= 1.02 * calculated_mass_sink):
            #messages.append("Warning: mass_sink and heat_sink are not aligned.")
            messages.append(f"Provided mass_sink: {mass_sink:.3f} kg/s" 
                            f"Calculated mass flow of sink from provided heat sink is: {calculated_mass_sink:.3f} kg/s")
            messages.append("Use one of these values in their respective block and put 0 in other (this wont affect the COP.")
            
            # Use the smaller value
            mass_sink = min(mass_sink, calculated_mass_sink)
    
    # Condition 3: heat_sink is given, mass_sink is zero
    elif heat_sink > 0 and mass_sink == 0:
        # Convert heat_sink from MW to kW (1 MW = 1000 kW)
        heat_sink_kw = heat_sink * 1000
        
        # Calculate mass_sink from heat_sink (kW)
        mass_sink = heat_sink_kw / delta_h
        messages.append(f"Calculated mass flow of sink from provided heat sink is: {mass_sink:.3f} kg/s")
    
    elif mass_sink>0 and heat_sink == 0:
        mass_sink = mass_sink
        messages.append(f"mass_sink is given already: {mass_sink:.3f} kg/s")

    
    # Return the validated mass_sink and messages
    return mass_sink, messages
'-----------------------------------------------------'


'------------------------------------------------------------------------------'

def calculate_heat_sink(mass_sink, Sink_T_inlet, Sink_P_inlet, Sink_T_outlet, Sink_P_outlet):
    """
    Calculate heat_sink based on mass_sink and temperature/pressure conditions.
    
    Parameters:
    - mass_sink (float): Mass sink in kg/s.
    - Sink_T_inlet (float): Sink inlet temperature in °C.
    - Sink_P_inlet (float): Sink inlet pressure in bar.
    - Sink_T_outlet (float): Sink outlet temperature in °C.
    - Sink_P_outlet (float): Sink outlet pressure in bar.
    
    Returns:
    - heat_sink (float): Heat sink in MW.
    """
    # Convert pressures to Pa for CoolProp (CoolProp expects Pa, not bar)
    Sink_P_inlet_Pa = Sink_P_inlet * 100000
    Sink_P_outlet_Pa = Sink_P_outlet * 100000
    
    # Get enthalpy in J/kg at Sink inlet and outlet conditions
    heat_in = CP.PropsSI('H', 'T', Sink_T_inlet + 273.15, 'P', Sink_P_inlet_Pa, 'Water')  # J/kg
    heat_out = CP.PropsSI('H', 'T', Sink_T_outlet + 273.15, 'P', Sink_P_outlet_Pa, 'Water')  # J/kg
    
    # Calculate heat_sink using mass_sink (kg/s)
    heat_sink = mass_sink * (heat_out - heat_in) / 1e6  # Convert to MW
    
    return heat_sink


'------------------------------------------------------------------------------------------'
def check_steam_condition(temp, pressure, label):
    """
    Check if the temperature and pressure correspond to steam (saturated or superheated).
    
    Parameters:
    temp (float): Temperature in °C.
    pressure (float): Pressure in bar.
    label (str): A label indicating if it's 'source inlet' or 'source outlet'.
    
    Raises:
    ValueError: If the condition corresponds to steam.
    """
    # Convert pressure to Pa for CoolProp (1 bar = 100,000 Pa)
    pressure_pa = pressure * 100000
    
    # Get the saturation temperature for the given pressure
    T_sat_liquid = CP.PropsSI('T', 'P', pressure_pa, 'Q', 0, 'Water') - 273.15  # °C
    T_sat_vapor = CP.PropsSI('T', 'P', pressure_pa, 'Q', 1, 'Water') - 273.15  # °C

    # Check if the temperature is above the saturation temperature
    if temp >= T_sat_liquid:
        raise ValueError(f"{label} temperature ({temp}°C) and pressure ({pressure} bar) indicate steam. Steam cannot be used as a heat source.")
    
    # Return saturated conditions for reference
    return T_sat_liquid, T_sat_vapor

'---------------------------------------------------------------------------------'

'--------------------------------------------------------------------------'



def validate_source_inlet_phase(source_inlet_temp, source_inlet_pressure):
    """
    Validates if the source inlet conditions (temperature and pressure) correspond to water in liquid phase.
    If the source is in vapor phase, it raises an error and stops the app.

    Parameters:
    - source_inlet_temp (float): Source inlet temperature in °C.
    - source_inlet_pressure (float): Source inlet pressure in bar.

    Returns:
    - None, stops the app if the phase is vapor.
    """
    # Convert pressure from bar to Pa (CoolProp expects Pa)
    source_inlet_pressure_pa = source_inlet_pressure * 1e5  # Convert from bar to Pa

    # Check the saturation temperature at the given pressure
    T_sat_vapor = CP.PropsSI('T', 'P', source_inlet_pressure_pa, 'Q', 1, 'Water') - 273.15  # Convert to °C

    # If the source inlet temperature is higher than or equal to the saturation temperature, it's vapor
    if source_inlet_temp >= T_sat_vapor:
        st.error(f"Error: Source inlet temperature ({source_inlet_temp}°C) at pressure ({source_inlet_pressure} bar) corresponds to vapor, not liquid.")
        st.stop()

'--------------------------------------------------------------------------'

def validate_sink_vapor_phase(Sink_T_outlet, Sink_P_outlet):
    """
    Validates if the sink outlet conditions (temperature and pressure) correspond to vapor phase if temperature is > 150°C.
    If the temperature is higher than 150°C and it's not vapor at the given pressure, an error is raised.

    Parameters:
    - Sink_T_outlet (float): Sink outlet temperature in °C.
    - Sink_P_outlet (float): Sink outlet pressure in bar.

    Returns:
    - None, stops the app if the phase is not vapor for temperatures above 150°C.
    """
    # Only check if the temperature is higher than 150°C
    if Sink_T_outlet > 150:
        # Convert pressure from bar to Pa (CoolProp expects Pa)
        Sink_P_outlet_pa = Sink_P_outlet * 1e5  # Convert from bar to Pa

        # Get the saturation temperature at the given pressure
        T_sat_vapor = CP.PropsSI('T', 'P', Sink_P_outlet_pa, 'Q', 1, 'Water') - 273.15  # Convert to °C

        # If the temperature is lower than the saturation temperature, it's not vapor
        if Sink_T_outlet < T_sat_vapor:
            st.error(f"Error: Sink outlet temperature ({Sink_T_outlet}°C) at pressure ({Sink_P_outlet} bar) does not correspond to vapor. Vapor phase is expected at temperatures above 150°C.")
            st.stop()
            
'-----------------------------------------------------------------------'
def validate_sink_temperature_pressure(Sink_T_inlet, Sink_P_inlet, Sink_T_outlet, Sink_P_outlet):
    """
    Validate sink temperatures and pressures, issue warnings for vapor phase, and stop calculation 
    if the enthalpy at Sink_T_inlet and Sink_P_inlet is greater than at Sink_T_outlet and Sink_P_outlet.
    
    Parameters:
    - Sink_T_inlet (float): Sink inlet temperature in °C.
    - Sink_P_inlet (float): Sink inlet pressure in bar.
    - Sink_T_outlet (float): Sink outlet temperature in °C.
    - Sink_P_outlet (float): Sink outlet pressure in bar.

    Returns:
    - None, but stops the app if the enthalpy condition is violated.
    """
    # General warning if Sink_T_inlet > Sink_T_outlet
    if Sink_T_inlet > Sink_T_outlet:
        st.warning(f"Warning: Sink inlet temperature ({Sink_T_inlet}°C) is greater than Sink outlet temperature ({Sink_T_outlet}°C).")

    # Convert pressures from bar to Pa (CoolProp expects Pa)
    Sink_P_inlet_pa = Sink_P_inlet * 1e5
    Sink_P_outlet_pa = Sink_P_outlet * 1e5

    # Check the phase of water at the sink inlet conditions
    T_sat_inlet_vapor = CP.PropsSI('T', 'P', Sink_P_inlet_pa, 'Q', 1, 'Water') - 273.15  # Convert to °C
    T_sat_inlet_liquid = CP.PropsSI('T', 'P', Sink_P_inlet_pa, 'Q', 0, 'Water') - 273.15  # Convert to °C

    # If the inlet temperature is higher than the saturation temperature for vapor, it's vapor
    if Sink_T_inlet >= T_sat_inlet_vapor:
        st.warning(f"Warning: Sink inlet temperature ({Sink_T_inlet}°C) at pressure ({Sink_P_inlet} bar) corresponds to vapor.")

    # Get the enthalpy at Sink inlet and outlet (J/kg)
    enthalpy_inlet = CP.PropsSI('H', 'T', Sink_T_inlet + 273.15, 'P', Sink_P_inlet_pa, 'Water')  # J/kg
    enthalpy_outlet = CP.PropsSI('H', 'T', Sink_T_outlet + 273.15, 'P', Sink_P_outlet_pa, 'Water')  # J/kg

    # If enthalpy at Sink inlet is higher than Sink outlet, raise an error and stop
    if enthalpy_inlet > enthalpy_outlet:
        st.error(f"Error: Enthalpy at Sink inlet ({enthalpy_inlet / 1000:.2f} kJ/kg) is higher than at Sink outlet ({enthalpy_outlet / 1000:.2f} kJ/kg). Calculation stopped.")
        st.stop()
'------------------------------------------------------------------------------------'

def check_and_return_min_heat_sink(heat_sink, mass_sink, Sink_T_inlet, Sink_P_inlet, Sink_T_outlet, Sink_P_outlet):
    
    """
    Check and return the minimum heat sink when both heat_sink and mass_sink are provided.
    The mass_sink will be set to zero for the calculation.
    
    Parameters:
    - heat_sink (float): Provided heat sink in MW.
    - mass_sink (float): Provided mass sink in kg/s.
    - Sink_T_inlet (float): Sink inlet temperature in °C.
    - Sink_P_inlet (float): Sink inlet pressure in bar.
    - Sink_T_outlet (float): Sink outlet temperature in °C.
    - Sink_P_outlet (float): Sink outlet pressure in bar.
    
    Returns:
    - min_heat_sink (float): The smaller heat sink value for further calculations.
    - mass_sink (float): The mass sink, set to 0 for calculation.
    """
    if heat_sink > 0 and mass_sink > 0:
        st.warning("Both heat_sink and mass_sink are provided. Checking if they are aligned...")

        # Calculate heat_sink based on mass_sink and the given temperatures/pressures
        calculated_heat_sink = calculate_heat_sink(mass_sink, Sink_T_inlet, Sink_P_inlet, Sink_T_outlet, Sink_P_outlet)
        
        # Check for discrepancies and select the smaller value
        if abs(calculated_heat_sink - heat_sink) > 0.01:  # Allow small numerical discrepancies
            st.warning(f"Discrepancy detected! The provided heat_sink is {heat_sink:.2f} MW, "
                       f"but the calculated heat_sink based on mass_sink is {calculated_heat_sink:.2f} MW.")
        
        # Use the smaller of the provided heat_sink or the calculated_heat_sink
        min_heat_sink = min(heat_sink, calculated_heat_sink)
        st.info(f"Using the smaller heat sink value: {min_heat_sink:.2f} MW for further calculations.")

        # Set mass_sink to 0 since we are now using heat_sink for calculation
        mass_sink = 0

        # Optional: you can validate the inputs here using check_inputs_sink if necessary
        mass_sink, messages = check_inputs_sink('water', Sink_T_inlet, Sink_T_outlet, Sink_P_inlet, Sink_P_outlet, 
                                                mass_sink, min_heat_sink)
        for msg in messages:
            st.info(msg)
            
        return min_heat_sink, mass_sink

    return heat_sink, mass_sink  # If one of the values is 0, return the provided heat_sink and mass_sink

'------------------------------------------------------------------------------------------------------'

def check_and_return_min_mass_flow(heat_source, mass_flow_source, source_inlet_temp, source_inlet_pressure, source_outlet_temp, source_outlet_pressure):
    """
    Check and return the minimum mass flow when both heat_source and mass_flow_source are provided.
    The heat_source will be set to zero for calculation.

    Parameters:
    - heat_source (float): Provided heat source in MW.
    - mass_flow_source (float): Provided mass flow source in kg/s.
    - source_inlet_temp (float): Source inlet temperature in °C.
    - source_inlet_pressure (float): Source inlet pressure in bar.
    - source_outlet_temp (float): Source outlet temperature in °C.
    - source_outlet_pressure (float): Source outlet pressure in bar.

    Returns:
    - min_mass_flow_source (float): The smaller mass flow value for further calculations.
    - heat_source (float): The heat source, set to 0 for calculation.
    """
    if heat_source > 0 and mass_flow_source > 0:
        st.warning("Both heat_source and mass_flow_source are provided. Checking if they are aligned...")

        
        # Convert pressures to Pa for CoolProp (CoolProp expects Pa, not bar)
        source_P_inlet_Pa = source_inlet_pressure * 100000
        source_P_outlet_Pa = source_outlet_pressure * 100000
        
        # Get enthalpy in J/kg at Source inlet and outlet conditions
        enthalpy_in = CP.PropsSI('H', 'T', source_inlet_temp + 273.15, 'P', source_P_inlet_Pa, 'Water')  # J/kg
        enthalpy_out = CP.PropsSI('H', 'T', source_outlet_temp + 273.15, 'P', source_P_outlet_Pa, 'Water')  # J/kg
        
        # Calculate heat_source using mass_flow_source (kg/s)
        calculated_heat_source = mass_flow_source * (enthalpy_in - enthalpy_out) / 1e6  # Convert to MW
        
        # Check for discrepancies and select the smaller mass flow
        if abs(calculated_heat_source - heat_source) > 0.01:  # Allow small numerical discrepancies
            st.warning(f"Discrepancy detected! The provided heat_source is {heat_source:.2f} MW, "
                       f"but the calculated heat_source based on mass_flow_source is {calculated_heat_source:.2f} MW.")
        
        
        # Use the smaller of the provided heat_source or the calculated_heat_source
        min_mass_flow_source = min(mass_flow_source, heat_source * 1e6 / (enthalpy_in -  enthalpy_out))  # Calculate corresponding mass flow
        st.info(f"Using the smaller mass flow value: {min_mass_flow_source:.2f} kg/s for further calculations.")

        # Set heat_source to 0 since we are now using mass_flow_source for calculation
        heat_source = 0

        # Optional: validate the inputs here using check_inputs_source if necessary
        mass_flow_source, messages = check_inputs_source('water', source_inlet_temp, source_outlet_temp, source_inlet_pressure, 
                                                         min_mass_flow_source, heat_source)
        for msg in messages:
            st.info(msg)
        
        return min_mass_flow_source, heat_source

    return mass_flow_source, heat_source  # If one of the values is 0, return the provided mass_flow_source and heat_source

'...................................................................................'

# Function to validate and suggest the correct Sink_T_outlet based on Sink_P_outlet
def validate_sink_t_outlet(Sink_T_outlet, Sink_P_outlet, config_value):
    # Check if Sink_T_outlet exceeds the config value (330°C)
    if Sink_P_outlet > 3.7:
        if Sink_T_outlet > config_value:
            # Calculate saturation temperature at Sink_P_outlet
            T_sat_vapor = CP.PropsSI('T', 'P', Sink_P_outlet * 100000, 'Q', 1, 'Water') - 273.15
            
            # Determine the superheat based on Sink_P_outlet
            superheat_temp = T_sat_vapor + 10
    
            # Suggest to the user the correct superheated temperature
            st.warning(f"Sink outlet temperature is too high! Please enter a lower value.")
            st.write(f"The saturation temperature at Sink_P_outlet ({Sink_P_outlet} bar) is {T_sat_vapor:.2f}°C.")
            st.write(f"You can proceed with a superheated temperature of {superheat_temp:.2f}°C ({'3°C' if Sink_P_outlet <= 3.7 else '10°C'} superheating at {Sink_P_outlet} bar).")
            
            st.stop()  # Stop the app until the user provides the valid input
    elif Sink_P_outlet <= 3.7:
        
        if Sink_T_outlet > 145:
            T_sat_vapor = CP.PropsSI('T', 'P', Sink_P_outlet * 100000, 'Q', 1, 'Water') - 273.15
            superheat_temp = T_sat_vapor + 3
        # Suggest to the user the correct superheated temperature
            st.warning(f"As it is a HTHP only solution, Sink outlet temperature high than 150 oC! Please enter a lower value or sugessted value below.")
            st.write(f"The saturation temperature at Sink_P_outlet ({Sink_P_outlet} bar) is {T_sat_vapor:.2f}°C.")
            st.write(f"You can proceed with a superheated temperature of {superheat_temp:.2f}°C ({'3°C' if Sink_P_outlet <= 3.7 else '10°C'} superheating at {Sink_P_outlet} bar).")
            
            st.stop()  # Stop the app until the user provides the valid input

    return Sink_T_outlet

'-------------------------------------------------------------------------------------'

# Function to validate and suggest the correct Sink_T_outlet based on Sink_P_outlet and config values
def validate_min_sink_t_outlet(Sink_T_outlet, Sink_P_outlet, config_value):
    """Validate that the Sink_T_outlet meets minimum temperature requirements based on Sink_P_outlet."""
    
    # Check if Sink_T_outlet is below the minimum threshold from config_value
    if Sink_T_outlet < config_value:
        if Sink_P_outlet <= 3.7:
            # Issue warning if Sink_P_outlet is less than or equal to 3.7 bar
            st.warning(f"The Sink_T_outlet is too low (below {config_value}°C). The model considers that the outlet is water, not steam.")
            st.info("Proceeding with calculations as water outlet.")
        elif Sink_P_outlet > 3.7:
            # Issue error if Sink_P_outlet is higher than 3.7 bar
            st.error("The Sink_T_outlet is too low for a pressure higher than 3.7 bar.")
            st.warning("The model treats Sink_P_outlet > 3.7 bar as HTHP + MVR. Reduce the pressure to proceed with the calculations.")
            st.stop()  # Stop the app until valid input is provided
    
    # Return validated or unchanged values for further use
    return Sink_T_outlet

'----------------------------------------------------------------------------------'

def check_coolprop_pressure_error(fluid, pressure, temperature):
    try:
        # Attempt to calculate a property using CoolProp at the given pressure and temperature
        # Here, we use density as an example, but you can use other properties if needed
        density = CP.PropsSI('D', 'P', pressure * 1e5, 'T', temperature + 273.15, fluid)
        return False  # No error occurred
    except Exception as e:
        st.error(f"CoolProp Error: Failed to calculate properties at {pressure} bar and {temperature}°C. {str(e)}")
        return True  # An error occurred