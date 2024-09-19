# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 14:06:07 2024

@author: me
"""

#while loop HTHP function
tolerance = 0.02
# Define a maximum number of iterations
max_iterations = 100
X_assume = 0.2

# Pressure drop ratios
PD_evap = 0.95  # Evaporator outlet
PD_SH = 0.98  # Evaporator outlet
PD_cond = 0.98  # Condenser outlet
PD_SC = 0.96  # Subcooler outlet
Press_multiplier_exp_1 = 1.06  # Expansion valve

# heat sink losses
heat_sink_losses = 0.98
'----------------------------------------------------'
# For HTHP + MVR these are output values for HTHP kept constants 
P_steam_outlet_HTHP = 1.4  #for MVR it is kept at 1.4 bar
P_steam_inlet_MVR = 1.34 # 2% press drop
T_steam_outlet_HTHP = 112.3 
stages = 2  #kept at 2 for HTHP+MVR
fluid_out_temp_HTHP = T_steam_outlet_HTHP + 10
press_increase_factor_MVR_out = 1.02

attemporation_temp = 105
default_superheat = 10
last_stage_superheat = 10
eff_mech_MVR = 0.95
'----------------------------'
default_values = {
    "sink_inlet_temp": 90.0,
    "sink_outlet_temp": 120.0,
    "sink_outlet_pressure": 1.5,
    "q_sink": 15.0,
    "m_sink": 0.0,
    "source_inlet_temp": 65.0,
    "source_outlet_temp": 35.0,
    "q_source":0.0,
    "m_source":0.0
}

