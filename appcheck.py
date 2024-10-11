# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 22:05:26 2024

@author: me
"""

import streamlit as st
import numpy as np
import CoolProp.CoolProp as CP
import matplotlib.pyplot as plt
from tabulate import tabulate
from scipy.optimize import fsolve
import warnings
import pandas as pd


# These must be placed in the same directory as Streamlit app
from HTHP_Source import calculate_heat_pump_performance_source
from HTHP_Sink import calculate_heat_pump_performance_sink
from check_inputs import check_inputs_source, check_inputs_sink, calculate_heat_sink,validate_source_inlet_phase, validate_sink_vapor_phase, validate_sink_temperature_pressure, check_and_return_min_heat_sink, check_and_return_min_mass_flow
from check_inputs import validate_sink_t_outlet, validate_min_sink_t_outlet, check_coolprop_pressure_error
from warnings_function import validate_and_warn, check_negative_values, warn_for_combination
import constants
from MVR_function import MVR

from email.mime.text import MIMEText
import random
import smtplib


        
st.title("Heat Pump Performance Calculator")
# Default configuration settings
CONFIG = {
    "default_source_inlet_pressure": 6.0,
    "default_sink_T_inlet": 90.0,
    "min_sink_T_outlet":110,
    "default_sink_P_inlet": 8.0,
    "min_heat_sink": 15,
    "max_sink_P_outlet": 60,
    "max_sink_T_outlet": 330,
    "max_source_inlet_temp": 95,
    "warning_source_inlet_temp": 80,
    "min_source_outlet_temp": 25,
}
#     "default_source_inlet_pressure": 6.0,
#     "default_sink_T_inlet": 90.0,
#     "default_sink_P_inlet": 8.0,
#     "min_heat_sink": 15,
#     "max_sink_P_outlet": 60,
#     "max_sink_T_outlet": 330,
#     "max_source_inlet_temp": 95,
#     "warning_source_inlet_temp": 80,
#     "min_source_outlet_temp": 25,
# }

# File upload for Excel
uploaded_file = st.file_uploader("Upload an Excel file for inputs", type="xlsx")

# Extract data from Excel if uploaded
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name='HP Questionnaire_eng', header=None)
    st.write("Data from the Excel file:")
    # Filter the relevant rows (6 to 19) and the relevant columns (Symbol and Value)
    filtered_df = df.iloc[6:21, [3, 5, 6]]  # 6:20 selects rows, [3, 5, 6] selects "Symbol", "Value", and "Unit" columns

    # Rename the columns for better display
    filtered_df.columns = ["Symbol", "Value", "Unit"]

    # Display the filtered DataFrame in Streamlit
    st.write("Technical Parameters:")
    st.dataframe(filtered_df)
    #st.write(df.head(20))  # Display the first 20 rows for inspection

    # Extract the relevant inputs from the Excel sheet (adjust the cell locations as needed)
    try:
        # Extract sink parameters
        sink_inlet_temp = pd.to_numeric(df.iloc[6, 5], errors='coerce') if not pd.isna(df.iloc[6, 5]) else constants.default_values['sink_inlet_temp']
        sink_outlet_temp = pd.to_numeric(df.iloc[7, 5], errors='coerce') if not pd.isna(df.iloc[7, 5]) else constants.default_values['sink_outlet_temp']
        sink_outlet_pressure = pd.to_numeric(df.iloc[8, 5], errors='coerce') if not pd.isna(df.iloc[8, 5]) else constants.default_values['sink_outlet_pressure']
        q_sink = pd.to_numeric(df.iloc[10, 5], errors='coerce') if not pd.isna(df.iloc[10, 5]) else constants.default_values['q_sink']
        m_sink = pd.to_numeric(df.iloc[12, 5], errors='coerce') if not pd.isna(df.iloc[12, 5]) else constants.default_values['m_sink']
        # Extract source parameters
        source_inlet_temp = pd.to_numeric(df.iloc[16, 5], errors='coerce') if not pd.isna(df.iloc[16, 5]) else constants.default_values['source_inlet_temp']
        source_outlet_temp = pd.to_numeric(df.iloc[17, 5], errors='coerce') if not pd.isna(df.iloc[17, 5]) else constants.default_values['source_outlet_temp']
        q_source = pd.to_numeric(df.iloc[19, 5], errors='coerce') if not pd.isna(df.iloc[19, 5]) else constants.default_values['q_source']
        m_source = pd.to_numeric(df.iloc[21, 5], errors='coerce') if not pd.isna(df.iloc[21, 5]) else constants.default_values['m_source']
        
        # Handle missing or invalid data by converting to float
        sink_inlet_temp = float(sink_inlet_temp) if not pd.isna(sink_inlet_temp) else constants.default_values['sink_inlet_temp']
        sink_outlet_temp = float(sink_outlet_temp) if not pd.isna(sink_outlet_temp) else constants.default_values['sink_outlet_temp']
        sink_outlet_pressure = float(sink_outlet_pressure) if not pd.isna(sink_outlet_pressure) else constants.default_values['sink_outlet_pressure']
        q_sink = float(q_sink) if not pd.isna(q_sink) else constants.default_values['q_sink']
        m_sink = float(m_sink) if not pd.isna(m_sink) else constants.default_values['m_sink']
        source_inlet_temp = float(source_inlet_temp) if not pd.isna(source_inlet_temp) else constants.default_values['source_inlet_temp']
        source_outlet_temp = float(source_outlet_temp) if not pd.isna(source_outlet_temp) else constants.default_values['source_outlet_temp']
        q_source = float(q_source) if not pd.isna(q_source) else constants.default_values['q_source']
        m_source = float(m_source) if not pd.isna(m_source) else constants.default_values['m_source']

                
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
        sink_inlet_temp = constants.default_values['sink_inlet_temp']
        sink_outlet_temp = constants.default_values['sink_outlet_temp']
        sink_outlet_pressure = constants.default_values['sink_outlet_pressure']
        q_sink = constants.default_values['q_sink']
        m_sink = constants.default_values['m_sink']
        source_inlet_temp = constants.default_values['source_inlet_temp']
        source_outlet_temp = constants.default_values['source_outlet_temp']
        q_source = constants.default_values['q_source']
        m_source = constants.default_values['m_source']
else:
    # Use default values if no file is uploaded
    sink_inlet_temp = constants.default_values['sink_inlet_temp']
    sink_outlet_temp = constants.default_values['sink_outlet_temp']
    sink_outlet_pressure = constants.default_values['sink_outlet_pressure']
    q_sink = constants.default_values['q_sink']
    m_sink = constants.default_values['m_sink']
    source_inlet_temp = constants.default_values['source_inlet_temp']
    source_outlet_temp = constants.default_values['source_outlet_temp']
    q_source = constants.default_values['q_source']
    m_source = constants.default_values['m_source']
    
# Input fields (allow user to override Excel data or default values)
st.sidebar.header("Input Parameters")

col1, col2 = st.sidebar.columns(2)

with col1:
    source_inlet_temp = st.number_input("Source Inlet Temperature (°C)", value=source_inlet_temp,
                                        help="Source inlet can not be vapor! it should not be higher than 95 °C")
    source_outlet_temp = st.number_input("Source Outlet Temperature (°C)", value=source_outlet_temp,
                                        help="Solution is not feasible below 25 °C. If you leave it blank, the default value of 25 °C will be used.")
    source_inlet_pressure = st.number_input("Source Inlet Pressure (bar)", min_value = 1.0, value=6.0,
                                            help="Default value is 6 bar. You can change this value, but don't leave it blank or set it to 0.")
    #source_outlet_pressure = st.number_input("Source Outlet Pressure (bar)", min_value = 1.0, value=3.0)
    mass_flow_source = st.number_input("m source (kg/s)", value=m_source, help="Enter the value or leave as 0 to indicate the value is not provided.")
    heat_source = st.number_input("Q source (MWth)", value=q_source, help="Enter the value or leave as 0 to indicate the value is not provided.")  # Displaying extracted Q_sink as heat_source for user to override

with col2:
    Sink_T_inlet = st.number_input("Sink Inlet Temperature (°C)", value=sink_inlet_temp,
                                help="Default value is 90°C. You can change this value, but don't leave it blank or set it to 0.")
    #Sink_P_inlet = st.number_input("Sink Inlet Pressure (bar)", value=8.0, min_value = 1.0,
    #                            help="Default value is 8 bar. You can change this value, but don't leave it blank or set it to 0.")
    Sink_T_outlet = st.number_input("Sink Outlet Temperature (°C)", value=sink_outlet_temp,
                                    help="Currently, we don't support temperatures higher than 330°C.")
    Sink_P_outlet = st.number_input("Sink Outlet Pressure (bar)", value=sink_outlet_pressure,
                                    help="Currently we don't support pressure higher than 61 bar")
    
    heat_sink = st.number_input("Q sink (MWth)", value=q_sink,
                                help="Enter the value or leave as 0 to indicate the value is not provided.")
    mass_sink = st.number_input("m sink (kg/s)", value=m_sink, help="Enter the value or leave as 0 to indicate the value is not provided.")

# Advanced parameters
#st.sidebar.header("Advanced Parameters")
#evaporator_temp_diff = st.sidebar.number_input("Evaporator Temperature Difference", value=3)
#eff_isentropic = st.sidebar.number_input("Isentropic Efficiency", value=0.8)
#eff_isentropic_c2 = st.sidebar.number_input("Isentropic Efficiency C2", value=0.8)
#comp2_press_factor = st.sidebar.number_input("Comp2 Press Factor", value=0.995)
#eff_mech = st.sidebar.number_input("Mechanical Efficiency", value=0.95)

source_outlet_pressure = 4.5
Sink_P_inlet = 8

evaporator_temp_diff = 3
eff_isentropic = 0.8
eff_isentropic_c2 = 0.8
comp2_press_factor = 0.995
eff_mech = 0.95

# Warnings and validations

# check double inputs are provided
heat_sink, mass_sink, heat_source, mass_flow_source = warn_for_combination(heat_sink, mass_sink, heat_source, mass_flow_source)

# Check and return the minimum heat sink when both heat_sink and mass_sink are provided. The mass_sink will be set to zero for the calculation.
heat_sink, mass_sink = check_and_return_min_heat_sink(heat_sink, mass_sink, Sink_T_inlet, Sink_P_inlet, Sink_T_outlet, Sink_P_outlet)

# Check and return the minimum mass flow when both heat_source and mass_flow_source are provided. The heat_source will be set to zero for calculation.
mass_flow_source, heat_source = check_and_return_min_mass_flow(heat_source, mass_flow_source, source_inlet_temp, source_inlet_pressure, source_outlet_temp, source_outlet_pressure)

# Use min_mass_flow_source and heat_source in further calculations

# heat sink must not be lower than 15 MW, warning is issue, but calculations proceed
def check_heat_sink(heat_sink_value):
    if heat_sink_value < CONFIG["min_heat_sink"]:
        st.warning(f"Warning: The heat sink value ({heat_sink_value:.2f} MW) is less than {CONFIG['min_heat_sink']} MW. This is lower than our product range.")

def user_prompt(message):
    st.warning(message)
    return st.button("Continue")

if st.sidebar.button("Calculate"):
    # Input validation
    try:
        check_negative_values(source_inlet_temp, source_outlet_temp, source_inlet_pressure, 
                            source_outlet_pressure, mass_flow_source, heat_source,
                            Sink_T_inlet, Sink_T_outlet, Sink_P_inlet, Sink_P_outlet,
                            heat_sink, mass_sink)
    except ValueError as e:
        st.error(f"Input Error: {str(e)}")
        st.stop()
    
    # Check if source_outlet_temp is at least 5 degrees lower than source_inlet_temp
    if source_outlet_temp >= source_inlet_temp - 4:
        st.error(f"Error: Source outlet temperature ({source_outlet_temp}°C) must be at least 5°C lower than the source inlet temperature ({source_inlet_temp}°C).")
        st.stop()
        
    #check if either of source inlet is vapor or sink outlet is liquid water at MVR only conditions
    validate_source_inlet_phase(source_inlet_temp, source_inlet_pressure)
    validate_sink_vapor_phase(Sink_T_outlet, Sink_P_outlet)
    validate_sink_temperature_pressure(Sink_T_inlet, Sink_P_inlet, Sink_T_outlet, Sink_P_outlet)
    if check_coolprop_pressure_error('Water', source_inlet_pressure, source_inlet_temp):
        st.error('pressure is too high for source inlet')
        st.stop()  # Stop further execution if there's an error   
    
    if check_coolprop_pressure_error('Water', Sink_T_inlet, sink_inlet_temp):
        st.error('pressure is too high for sink inlet')
        st.stop()  # Stop further execution if there's an error

    if heat_sink == 0 and mass_sink == 0 and mass_flow_source == 0 and heat_source == 0:
        st.error("Please provide at least one non-zero value for mass_flow_source, heat_source, heat_sink, or mass_sink.")
        st.stop()

    # Determine superheat temperature difference
    diff = source_inlet_temp - source_outlet_temp
    SH_temp_diff = 8 if diff > 10 else 5 if diff > 5 else 2
    
    source_inlet_pressure = validate_and_warn('source_inlet_pressure', source_inlet_pressure, CONFIG["default_source_inlet_pressure"])
    #Sink_T_inlet = validate_and_warn('Sink_T_inlet', Sink_T_inlet, CONFIG["default_sink_T_inlet"])
    # Sink_P_inlet = validate_and_warn('Sink_P_inlet', Sink_P_inlet, CONFIG["default_sink_P_inlet"])
    
    
    if Sink_T_inlet == 0 or Sink_T_inlet is None:
        st.warning(f"Warning:Inlet temp for sink is missing, default value of {CONFIG['default_sink_T_inlet']}°C was used in calculations.")
        Sink_T_inlet = validate_and_warn('Sink_T_inlet', Sink_T_inlet, CONFIG["default_sink_T_inlet"])
    
    if Sink_P_inlet == 0:
        st.warning(f"Warning:Inlet pressure for sink is missing or zero, default value of {CONFIG['default_sink_P_inlet']} bar was used in calculations.")
        Sink_P_inlet = validate_and_warn('Sink_P_inlet', Sink_P_inlet, CONFIG["default_sink_P_inlet"])


    if source_inlet_temp > CONFIG['max_source_inlet_temp']:
        st.error(f"Error: source_inlet_temp ({source_inlet_temp}°C) exceeds {CONFIG['max_source_inlet_temp']}°C. Operation aborted.")
        st.stop()
    elif source_inlet_temp > CONFIG['warning_source_inlet_temp']:
        st.warning(f"Warning: source_inlet_temp is {source_inlet_temp}°C, which exceeds {CONFIG['warning_source_inlet_temp']}°C.")

    if source_outlet_temp < CONFIG['min_source_outlet_temp']:
            st.error(f"Error: source_outlet_temp is {source_outlet_temp}°C, which is less than {CONFIG['min_source_outlet_temp']}°C. ")
            st.stop()
    
    if Sink_P_outlet > CONFIG['max_sink_P_outlet']:
        st.error(f"Sink_P_outlet exceeds {CONFIG['max_sink_P_outlet']} bar. Operation aborted.")
        st.stop()
        
    # Check if Sink_T_outlet exceeds the config value (145 C for HTHP and 330°C)
    Sink_T_outlet = validate_sink_t_outlet(Sink_T_outlet, Sink_P_outlet, CONFIG['max_sink_T_outlet'])
    # Call the validation function with the values and config for min_sink_T_outlet
    Sink_T_outlet = validate_min_sink_t_outlet(Sink_T_outlet, Sink_P_outlet, CONFIG['min_sink_T_outlet'])

    # Saturation temperature check
    T_sat_liquid = CP.PropsSI('T', 'P', Sink_P_inlet * 100000, 'Q', 0, 'Water') - 273.15
    T_sat_vapor = CP.PropsSI('T', 'P', Sink_P_inlet * 100000, 'Q', 1, 'Water') - 273.15
    if T_sat_liquid <= Sink_T_inlet <= T_sat_vapor:
        st.warning(f"Sink_T_inlet ({Sink_T_inlet}°C) is in the saturated range at Sink_P_inlet {Sink_P_inlet} bar.")
    elif Sink_T_inlet > T_sat_vapor:
        st.error(f"Sink inlet temp is ({Sink_T_inlet}°C) that is superheated at inlet sink pressure of {Sink_P_inlet} bar. MVR only solution would be more feasible")
        st.stop()
    
    if heat_sink > 0:
        check_heat_sink(heat_sink)
    elif mass_sink > 0:
        calculated_heat_sink = calculate_heat_sink(mass_sink, Sink_T_inlet, Sink_P_inlet, Sink_T_outlet, Sink_P_outlet)
        check_heat_sink(calculated_heat_sink)
        #st.info(f"Calculated Heat Sink: {calculated_heat_sink:.2f} MW")
        st.success("inputs are checked")

    # Main calculation logic
    results = None
    sink_required_temp = Sink_T_outlet + 10

    if heat_sink == 0 and mass_sink == 0 and (heat_source > 0 or mass_flow_source > 0):
        validated_mass_flow, messages = check_inputs_source('water', source_inlet_temp, source_outlet_temp, source_inlet_pressure,
                                                            mass_flow_source, heat_source)
        
        for msg in messages:
            st.info(msg)

        #st.info(f"Validated mass_flow_source: {validated_mass_flow:.3f} kg/s")
        st.info("Inputs are validated, calculations will follow")

        if Sink_P_outlet <= 3.7:
            results = calculate_heat_pump_performance_source(
                fluid='R1233ZD', 
                source_inlet_temp=source_inlet_temp, 
                source_inlet_pressure=source_inlet_pressure, 
                mass_flow_source=validated_mass_flow, 
                source_outlet_temp=source_outlet_temp, 
                evaporator_temp_diff=evaporator_temp_diff, 
                SH_temp_diff=SH_temp_diff, 
                sink_required_temp=sink_required_temp, 
                eff_isentropic=eff_isentropic, 
                eff_isentropic_c2=eff_isentropic_c2, 
                comp2_press_factor=comp2_press_factor,
                eff_mech=eff_mech, 
                Sink_T_inlet=Sink_T_inlet, 
                Sink_P_inlet=Sink_P_inlet, 
                Sink_T_outlet=Sink_T_outlet, 
                Sink_P_outlet=Sink_P_outlet
            )
        elif Sink_P_outlet > 3.7:
            Tsat_sink_out = CP.PropsSI('T', 'P', Sink_P_outlet * 1e5*1.02, 'Q', 1, 'Water') - 273.15
            if Sink_T_outlet < Tsat_sink_out:
                st.error(f"Warning: Sink_T_outlet ({Sink_T_outlet}°C) is lower than the saturation temperature ({Tsat_sink_out:.2f}°C) at Sink_P_outlet ({Sink_P_outlet} bar).")
                st.stop()
            st.info("Sink_P_outlet is higher than 3.7 bar, HTHP + MVR solution will be applied.")

            results_HTHP = calculate_heat_pump_performance_source(
                fluid='R1233ZD', 
                source_inlet_temp=source_inlet_temp, 
                source_inlet_pressure=source_inlet_pressure, 
                mass_flow_source=validated_mass_flow, 
                source_outlet_temp=source_outlet_temp, 
                evaporator_temp_diff=evaporator_temp_diff, 
                SH_temp_diff=SH_temp_diff, 
                sink_required_temp=constants.fluid_out_temp_HTHP, #10 degrees difference
                eff_isentropic=eff_isentropic, 
                eff_isentropic_c2=eff_isentropic_c2, 
                comp2_press_factor=comp2_press_factor,
                eff_mech=eff_mech, 
                Sink_T_inlet=Sink_T_inlet, 
                Sink_P_inlet=Sink_P_inlet, 
                Sink_T_outlet=constants.T_steam_outlet_HTHP, 
                Sink_P_outlet=constants.P_steam_outlet_HTHP
            )

            if results_HTHP is None:
                st.error("Error: results_HTHP is None. Check the calculate_heat_pump_performance_source function.")
                st.stop()

            results_MVR = MVR(
                stages=constants.stages,
                initial_pressure=constants.P_steam_inlet_MVR,
                initial_temperature=constants.T_steam_outlet_HTHP, 
                initial_mass_flow=results_HTHP.get('Mass Flowrate of Steam (kg/s)'), 
                final_pressure=Sink_P_outlet*constants.press_increase_factor_MVR_out, 
                attemporation_temp=constants.attemporation_temp, 
                condensate_temp=Sink_T_inlet, 
                last_stage_superheat = Sink_T_outlet - Tsat_sink_out,
                isentropic_efficiency=eff_isentropic, 
                mech_efficiency=constants.eff_mech_MVR, 
                default_superheat=constants.default_superheat
            )

            if results_MVR is None:
                st.error("Error: results_MVR is None. Check the MVR function.")
                st.stop()
            
            if Sink_T_outlet > results_MVR['stage_temps'][-1]:
                st.warning(f"Warning: Sink_T_outlet ({Sink_T_outlet}°C) was not achieved with this pressure. The max achieved temperature is {results_MVR['stage_temps'][-1]:.2f}°C. Please increase the pressure.")
            heat_sink_hthp_mvr = (results_MVR.get('output_enthalpy_mw') - results_MVR.get('condensate_enthalpy_mw'))
            Total_power = results_HTHP.get('Total Electric Power (MW)') + results_MVR.get('total_power_mw')
            COP_gross = (results_MVR.get('output_enthalpy_mw') - results_MVR.get('condensate_enthalpy_mw')) / (results_HTHP.get('Total Electric Power (MW)') + results_MVR.get('total_power_mw'))
            
            if Sink_T_outlet > results_MVR['stage_temps'][-1]:
                st.warning(f"Warning: Sink_T_outlet ({Sink_T_outlet}°C) was not achieved with this pressure. The max achieved temperature is {results_MVR['stage_temps'][-1]:.2f}°C. Please increase the pressure.")

            results = {}
            results.update(results_HTHP)
            results.update(results_MVR)
            results['heat sink total'] = heat_sink_hthp_mvr
            results['COP_gross'] = COP_gross
            results['total power hthp plus MVR'] = Total_power
            st.success('calculations completed successfully')
            st.info(f"Final COP_gross: {COP_gross:.2f}")
    

    elif mass_flow_source == 0 and heat_source == 0 and (heat_sink > 0 or mass_sink > 0):
        
        if Sink_P_outlet < 3.7:
            mass_sink, messages = check_inputs_sink('water', Sink_T_inlet, Sink_T_outlet, Sink_P_inlet, Sink_P_outlet, 
                                mass_sink, heat_sink)
            
            st.info(f"Mass flow sink with given heat sink would be: {mass_sink:.1f} kg/s")
            st.info("Inputs checked successfully, calculations will follow")

            results = calculate_heat_pump_performance_sink(
                fluid='R1233ZD', 
                source_inlet_temp=source_inlet_temp, 
                source_inlet_pressure=source_inlet_pressure, 
                mass_flow_source=1, 
                source_outlet_temp=source_outlet_temp, 
                evaporator_temp_diff=evaporator_temp_diff, 
                SH_temp_diff=SH_temp_diff, 
                sink_required_temp=sink_required_temp, 
                eff_isentropic=eff_isentropic, 
                eff_isentropic_c2=eff_isentropic_c2, 
                comp2_press_factor=comp2_press_factor,
                eff_mech=eff_mech, 
                Sink_T_inlet=Sink_T_inlet, 
                Sink_P_inlet=Sink_P_inlet, 
                Sink_T_outlet=Sink_T_outlet, 
                Sink_P_outlet=Sink_P_outlet,
                mass_sink_given=mass_sink,
            )
        elif Sink_P_outlet > 3.7:
            st.info("Sink_P_outlet is higher than 3.7 bar, HTHP + MVR solution will be applied.")
            Tsat_sink_out = CP.PropsSI('T', 'P', Sink_P_outlet * 1e5*1.02, 'Q', 1, 'Water') - 273.15
            if Sink_T_outlet < Tsat_sink_out:
                st.error(f"Error: Sink is liquid as required outlet temp of ({Sink_T_outlet}°C) is lower than the saturation temperature ({Tsat_sink_out:.2f}°C) at Sink_P_outlet ({Sink_P_outlet} bar). Calculations will stopped")
                st.stop()

            def enthalpy_difference(heat_sink_hthp):
                heat_sink_hthp = heat_sink_hthp.item() if isinstance(heat_sink_hthp, np.ndarray) else heat_sink_hthp
                global results_MVR, results_HTHP
                mass_sink, _ = check_inputs_sink(
                    'water', 
                    Sink_T_inlet, 
                    constants.T_steam_outlet_HTHP, 
                    Sink_P_inlet, 
                    constants.P_steam_outlet_HTHP, 
                    100, 
                    heat_sink_hthp
                )

                results_HTHP = calculate_heat_pump_performance_sink(
                    fluid='R1233ZD', 
                    source_inlet_temp=source_inlet_temp, 
                    source_inlet_pressure=source_inlet_pressure, 
                    mass_flow_source=1, 
                    source_outlet_temp=source_outlet_temp, 
                    evaporator_temp_diff=evaporator_temp_diff, 
                    SH_temp_diff=SH_temp_diff,
                    sink_required_temp=constants.fluid_out_temp_HTHP, #10 degrees difference
                    eff_isentropic=eff_isentropic, 
                    eff_isentropic_c2=eff_isentropic_c2, 
                    comp2_press_factor=comp2_press_factor,
                    eff_mech=eff_mech, 
                    Sink_T_inlet=Sink_T_inlet, 
                    Sink_P_inlet=Sink_P_inlet, 
                    Sink_T_outlet=constants.T_steam_outlet_HTHP, 
                    Sink_P_outlet=constants.P_steam_outlet_HTHP, #1.4 bar for HTHP imported from constants
                    mass_sink_given=mass_sink,
                )

                results_MVR = MVR(
                    stages=constants.stages,
                    initial_pressure=constants.P_steam_inlet_MVR,
                    initial_temperature=constants.T_steam_outlet_HTHP, 
                    initial_mass_flow=results_HTHP.get('Mass Flowrate of Steam (kg/s)'), 
                    final_pressure=Sink_P_outlet * constants.press_increase_factor_MVR_out, 
                    attemporation_temp=Sink_T_inlet, 
                    condensate_temp=Sink_T_inlet, 
                    last_stage_superheat = Sink_T_outlet - Tsat_sink_out,
                    isentropic_efficiency=eff_isentropic, 
                    mech_efficiency=constants.eff_mech_MVR, 
                    default_superheat=constants.default_superheat
                    
                )

                output_enthalpy_mvr = results_MVR.get('output_enthalpy_mw') - results_MVR.get('condensate_enthalpy_mw')
                return output_enthalpy_mvr - heat_sink

            if mass_sink > 0:
                heat_sink = calculate_heat_sink(mass_sink, Sink_T_inlet, Sink_P_inlet, Sink_T_outlet, Sink_P_outlet)
            #st.info(f"Heat Sink: {heat_sink:.6f} MW")
                
            # Use fsolve to find the heat_sink_hthp value that minimizes the enthalpy difference
            initial_guess = heat_sink * 0.85
            optimal_heat_sink_hthp = fsolve(enthalpy_difference, initial_guess, xtol=1e-6)[0]

            #st.info(f"Optimal heat_sink_hthp found: {optimal_heat_sink_hthp:.6f} MW")

            heat_sink_hthp_mvr = (results_MVR.get('output_enthalpy_mw') - results_MVR.get('condensate_enthalpy_mw'))
            Total_power = results_HTHP.get('Total Electric Power (MW)') + results_MVR.get('total_power_mw')
            COP_gross = (results_MVR.get('output_enthalpy_mw') - results_MVR.get('condensate_enthalpy_mw')) / (results_HTHP.get('Total Electric Power (MW)') + results_MVR.get('total_power_mw'))
            if Sink_T_outlet > results_MVR['stage_temps'][-1]:
                st.warning(f"Warning: Sink_T_outlet ({Sink_T_outlet}°C) was not achieved with this pressure. The max achieved temperature is {results_MVR['stage_temps'][-1]:.2f}°C. Please increase the pressure.")

            results = {}
            results.update(results_HTHP)
            results.update(results_MVR)
            results['heat sink total'] = heat_sink_hthp_mvr
            results['COP_gross'] = COP_gross
            results['total power hthp plus MVR'] = Total_power
            st.success('calculations completed successfully')
            st.info(f"Final COP_gross: {COP_gross:.2f}")

    # Display results
    if results:
        st.header("Results")
        
        # Create two columns for displaying results
        col1, col2 = st.columns(2)
        
        # Separate the results into two groups
        group1 = {'Sink Power (MW)': results.get('Sink Power (MW)', 'N/A'),
                'Mass Flowrate of Steam (kg/s)': results.get('Mass Flowrate of Steam (kg/s)', 'N/A'),
                'Total Electric Power HTHP (MW)': results.get('Total Electric Power (MW)', 'N/A'),
                'COP HTHP only': results.get('COP', 'N/A'),
                
                }
        
        group2 = {'Sink Power MVR (MW)': results.get('heat sink total', 'N/A'),
                
                'Mass Flowrate of Steam after MVR (kg/s)': results.get('current_mass_flow', 'N/A'),

                
                'Total Electric Power HTHP + MVR (MW)': results.get('total power hthp plus MVR', 'N/A'),
                'COP HTHP + MVR': results.get('COP_gross', 'N/A')
        }
        
        # Display group1 results in the first column
        with col1:
            for key, value in group1.items():
                st.metric(label=key, value=f"{value:.2f}" if isinstance(value, (int, float)) else value)
        
        # Display group2 results in the second column
        with col2:
            for key, value in group2.items():
                st.metric(label=key, value=f"{value:.2f}" if isinstance(value, (int, float)) else value)
        
        # Display any additional results
        st.subheader("Additional Results")
        for key, value in results.items():
            if key not in group1 and key not in group2:
                if isinstance(value, (int, float)):
                    st.write(f"{key}: {value:.2f}")
            else:
                st.write(f"{key}: {value}")

                
    else:
        st.warning("No results were generated. Please check your inputs and try again.")

else:
    st.warning("Please verify your OTP to access the calculator.")