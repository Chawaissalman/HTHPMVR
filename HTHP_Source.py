# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 22:27:17 2024

@author: me
"""

import numpy as np
import CoolProp.CoolProp as CP
import math
import matplotlib.pyplot as plt
from tabulate import tabulate
from helper_functions import calculate_properties, adjust_subcooler_temp
import constants

def calculate_heat_pump_performance_source(fluid, source_inlet_temp, source_inlet_pressure, mass_flow_source,
                                    source_outlet_temp, evaporator_temp_diff, SH_temp_diff, 
                                    sink_required_temp, eff_isentropic, 
                                    eff_isentropic_c2, comp2_press_factor,eff_mech, Sink_T_inlet, Sink_P_inlet, 
                                    Sink_T_outlet, Sink_P_outlet):
    """
    Calculate the performance of a heat pump.

    Parameters:
    fluid (str): Refrigerant used in the heat pump.
    source_inlet_temp (float): Source water inlet temperature in °C.
    source_inlet_pressure (float): Source water inlet pressure in bar.
    mass_flow (float): Mass flow rate in kg/s.
    source_outlet_temp (float): Source water outlet temperature in °C.
    evaporator_temp_diff (float): Evaporator temperature difference in °C.
    SH_temp_diff (float): Temperature difference between source inlet and SH outlet in °C.
    sink_required_temp (float): Required temperature in the sink in °C.
    subcooler_temp_diff (float): Temperature difference between subcooler exit and feed water in °C.
    eff_isentropic (float): Isentropic efficiency of compressor 1.
    eff_isentropic_c2 (float): Isentropic efficiency of compressor 2.
    eff_mech (float): Mechanical efficiency.
    Sink_T_inlet (float): Feed water inlet temperature in °C.
    Sink_P_inlet (float): Feed water inlet pressure in bar.
    Sink_T_outlet (float): Desired temperature of the feed water outlet in °C.
    Sink_P_outlet (float): Desired pressure of the feed water outlet in bar.

    Returns:
    A dictionary containing various performance metrics of the heat pump or an error message.
    """
    # Initialize variables
    success = True
    results = {}
    
    

    
    # Water source calculations
    hin = CP.PropsSI('H', 'T', source_inlet_temp + 273.15, 'P', source_inlet_pressure * 100000, 'water')
    hout = CP.PropsSI('H', 'T', source_outlet_temp + 273.15, 'P', source_inlet_pressure * 100000, 'water')
    heat_source = mass_flow_source * (hin - hout) / 1000  # kW

    
    # Other calculations and iterations as per your existing logic
   
    T1 = (source_outlet_temp - evaporator_temp_diff) + 273.15
    # Initialize the success flag
    success = True

   # Define a tolerance for diff
    tolerance = constants.tolerance

   # Define a maximum number of iterations
    max_iterations = constants.max_iterations
    iteration = 0
    X_assume = constants.X_assume

    # comp 2 out part 1, point 5
    T5 = sink_required_temp + 273.15  # Temperature at point 5 (K)
    if 1.0 <= Sink_P_outlet <= 1.4:
        P5 = CP.PropsSI('P','Q',1,'T',T5, fluid)  # No adjustment
    else:
        P5 = CP.PropsSI('P','Q',1,'T',T5, fluid) * 0.97  # Adjust when pressure is higher than 1.4

    T1 = (source_outlet_temp - evaporator_temp_diff) + 273.15
    
    
        # Implement a try-except block to catch the ValueError
    try:
            while iteration < max_iterations:
                #Evaporator In, point 1
                P1, h1, s1 = calculate_properties(fluid, temperature=T1, quality=X_assume)
                
                #Evaporator out, point 2
                P2 = P1 * constants.PD_evap * constants.PD_SH
                                
                #Evaporator out, point 2 (temperature at saturated vapor Q=1)
                T2_evap, _, _ = calculate_properties(fluid, pressure=P2, quality=1)
                T2 = T2_evap + SH_temp_diff
                _, h2, s2 = calculate_properties(fluid, temperature=T2, pressure=P2)  
                rho2 = CP.PropsSI('D', 'H', h2, 'P', P2, fluid)
                
                PR = math.sqrt(P5/P2) #pressure ratio
                
                # comp 1 out, point 3
                P3 = PR * P2
                s3_is= s2
                T3_is, h3_is, _ = calculate_properties(fluid, pressure=P3, entropy=s3_is)

                h3 = (h3_is - h2)/eff_isentropic + h2
                T3, _, s3 = calculate_properties(fluid, enthalpy=h3, pressure=P3)

                #condenser out point 6
                P6 = P5* constants.PD_cond
                T6, h6, _ = calculate_properties(fluid, pressure=P6, quality=0)
                                
                #subcooler out, point 7
                P7 = P6 * constants.PD_SC
                
                #adjust via helper function
                T7 = adjust_subcooler_temp(Sink_T_inlet, P6, fluid)

                _, h7, s7 = calculate_properties(fluid, temperature=T7, pressure=P7)

                #expansion 1 out, point 8 liquid
                P8 = P3 * constants.Press_multiplier_exp_1 #pressure litle bit higher than comp 1 inlet
                h8 = h7
                Q8 = CP.PropsSI('Q','H',h8,'P',P8, fluid)
                              
                T8, _, s8 = calculate_properties(fluid, enthalpy=h8, pressure=P8)

    
                #point 10, vapor out flash
                T10 = T8
                P10 = P8
                _, h10, s10 = calculate_properties(fluid, pressure=P10, quality=1)

                # point 4 vapor from flash + comp 1 outlet
                P4 = P3 #pressure drop from point P8 to P3 equal to outlet of compressor
                h4 = (h3*(1-Q8)+h10*Q8)
                T4, _, s4 = calculate_properties(fluid, enthalpy=h4, pressure=P4)

                #point 11, liquid out flash
                T11 = T10
                P11 = P8
                _, h11, s11 = calculate_properties(fluid, pressure=P10, quality=0)


                #expansion 2 out, point 9
                P9 = P1
                s9_is = s8
                T9, _, _ = calculate_properties(fluid, enthalpy=h8, pressure=P9)
                h9 = h11
                Q9 = CP.PropsSI('Q','H',h9,'P',P9, fluid)
                
                #comp 2 out part 2
                s5_is = s4
                T5_is, h5_is, _ = calculate_properties(fluid, pressure=P5, entropy=s5_is)

                h5 = (h5_is - h4)/eff_isentropic_c2 + h4
                
                T5_b, _, s5 = calculate_properties(fluid, enthalpy=h5, pressure=P5)

                              
                diff_T = abs(T5-T5_b)
                diff = abs(Q9-X_assume)
                X_assume = Q9
                iteration += 1
                
                if diff < tolerance:
                     break
                
                else:
                    if Q9 < X_assume:
                        X_assume -= 0.001
                        
                    else:
                        X_assume += 0.001
                    
                iteration += 1

            # End of the while loop

            
            # If the calculation was successful, continue to process and return the results
            h1 = CP.PropsSI('H','Q',X_assume,'T',T1, fluid)
            mass_fluid = heat_source*1000/(h2-h1)
    
            mass_comp1 = mass_fluid
            vol = mass_comp1/rho2
            mass_comp2 = mass_fluid / (1-Q8)
            Power_comp1 = mass_comp1 * (h3-h2)/1000
            Power_comp2 = mass_comp2 * (h5-h4)/1000
            Power = (Power_comp1+Power_comp2)/eff_mech
    
            heat_sink = mass_comp2 * ((h5-h7))/1000
    
    
            # Sink side
            Q = heat_sink*1e3*constants.heat_sink_losses  #  kW to Watts # 0.98 as a factor for heat transfer losses
            
            COP = Q / Power /1000 # 1000 to convert power to watts back

            #inlet enthalpy 
            hin = CP.PropsSI('H','P',Sink_P_inlet*100000,'T',Sink_T_inlet+273.15, 'Water')
            # Get specific heat capacity of water at the average temperature and atmospheric pressure
            hout = CP.PropsSI('H','P',Sink_P_outlet*100000,'T',Sink_T_outlet+273.15, 'Water')
    
            # Calculate temperature difference
            delta_h = hout - hin
    
            # Calculate mass flowrate using the formula
            m_dot = Q / delta_h
    
            # Prepare the results in a dictionary 'source in T': source_inlet_temp,
            T = [T1, T2, T3, T4,T5_is, T5, T6, T7, T8, T9, T10]
            P = [P1, P2, P3, P4, P5, P6, P7, P8, P9, P10]
            T2 = [T5, T5_b]
            H = [h2, h3_is, h3, h4,h5_is, h5]
            
            results = {
                #'P': P,
                #'T': T,
                #"H": H,
                'source in T': source_inlet_temp,
                'source out T': source_outlet_temp,
                'heat source': heat_source/1000,
                'mass flow source': mass_flow_source,
                'suc vol comp 1': vol * 3600,
                "Power Comp 1 (MW)": Power_comp1 / 1000,
                "Power Comp 2 (MW)": Power_comp2 / 1000,
                "Total Electric Power (MW)": Power / 1000,
                "Sink Power (MW)": Q/1e6,
                "subcooler temp": T7-273.15,
                'sink in T': Sink_T_inlet ,
                'sink out T': Sink_T_outlet,
                'mass sink steam/water': m_dot,
                'sink inlet P': Sink_P_inlet ,
                'sink outlet P': Sink_P_outlet ,
                "COP": COP,
                "Mass Flowrate of Steam (kg/s)": m_dot
            }
            
    except Exception as e:
        # Log the error
        print(f"An error occurred: {e}")

        # Set success to False and prepare a results dictionary with error information
        success = False
        results = {
            "Error": str(e),
            "Heat Source (MW)": 0,
            "Power Comp 1 (MW)": 0,
            "Power Comp 2 (MW)": 0,
            "Total Electric Power (MW)": 0,
            "Sink Power (MW)": 0,
            "COP": 0,
            "Mass Flowrate of Steam (kg/s)": 0
        }
    

    return results