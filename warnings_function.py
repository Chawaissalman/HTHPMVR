# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 12:19:14 2024

@author: me
"""
import warnings
import streamlit as st
import CoolProp.CoolProp as CP


# Custom format for warnings to hide the location (file and line number)
def custom_warning_format(message, category, filename, lineno, file=None, line=None):
    return f"{category.__name__}: {message}\n"

# Apply the custom format to warnings
warnings.formatwarning = custom_warning_format

def validate_and_warn(var_name, value, default=None, lower_limit=0, warning_msg=None, unit=""):
    if value < lower_limit:
        raise ValueError(f"{var_name} cannot be less than {lower_limit}. Value provided: {value}")
    if value == 0 and default is not None:
        # Add unit in the message
        warnings.warn(
            warning_msg if warning_msg else f"{var_name} was not provided. Using default value of {default} {unit}."
        )
        return default
    return value


# Helper function for user prompts
def user_prompt(message):
    user_input = input(message + " (yes/no): ").strip().lower()
    if user_input != 'yes':
        raise SystemExit("Operation aborted by the user.")
    return user_input

def check_negative_values(source_inlet_temp, source_outlet_temp, source_inlet_pressure, 
                          source_outlet_pressure, mass_flow_source, heat_source,
                          Sink_T_inlet, Sink_T_outlet, Sink_P_inlet, Sink_P_outlet,
                          heat_sink, mass_sink):
    """
    Check if any values are less than 0 and raise an error.
    
    Parameters:
    All required variables as function arguments.
    
    Raises:
    ValueError: If any value is less than 0, it raises an error with a message.
    """
    critical_values = {
        'source_inlet_temp': source_inlet_temp,
        'source_outlet_temp': source_outlet_temp,
        'source_inlet_pressure': source_inlet_pressure,
        'source_outlet_pressure': source_outlet_pressure,
        'mass_flow_source': mass_flow_source,
        'heat_source': heat_source,
        'Sink_T_inlet': Sink_T_inlet,
        'Sink_T_outlet': Sink_T_outlet,
        'Sink_P_inlet': Sink_P_inlet,
        'Sink_P_outlet': Sink_P_outlet,
        'heat_sink': heat_sink,
        'mass_sink': mass_sink
    }

    # Find all negative values
    negative_values = {name: val for name, val in critical_values.items() if val < 0}

    # Raise an error if any negative values are found
    if negative_values:
        raise ValueError(f"The following value(s) cannot be less than 0: {negative_values}")



def warn_for_combination(heat_sink, mass_sink, heat_source, mass_flow_source):
    """Warn user which variables are provided and ask for their choice for the calculation."""
    provided_vars = []
    
    if heat_sink > 0 or mass_sink > 0:
        provided_vars.append(f"heat_sink: {heat_sink}")
    # if mass_sink > 0:
    #     provided_vars.append(f"mass_sink: {mass_sink}")
    if heat_source > 0 or mass_flow_source>0:
        provided_vars.append(f"heat_source: {heat_source}")
    # if mass_flow_source > 0:
    #     provided_vars.append(f"mass_flow_source: {mass_flow_source}")
    
    if len(provided_vars) > 1:
        # Display the provided variables and their values
        st.warning(f"The following variables are provided: {', '.join(provided_vars)}")
        
        # Ask the user which calculation to base on
        choice = st.selectbox(
            "Choose which calculation to base on:",
            ("heat_sink/mass_sink", "heat_source/mass_flow_source")
        )
        
        if choice == 'heat_sink/mass_sink':
            # Reset heat_source and mass_flow_source to 0 if sink side is chosen
            heat_source = 0
            mass_flow_source = 0
            st.info("Calculations will be based on heat_sink/mass_sink.")
        elif choice == 'heat_source/mass_flow_source':
            # Reset heat_sink and mass_sink to 0 if source side is chosen
            heat_sink = 0
            mass_sink = 0
            st.info("Calculations will be based on heat_source/mass_flow_source.")
        else:
            st.error("Invalid choice.")
        
        return heat_sink, mass_sink, heat_source, mass_flow_source  # Return updated values

    return heat_sink, mass_sink, heat_source, mass_flow_source  # No change if no conflicts


'---------------------------------------------'

