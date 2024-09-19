# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 17:00:35 2023

@author: me
"""

from calculate_heat_pump_performance_opti import calculate_heat_pump_performance
from ppt_func_HTHP import update_text_while_preserving_formatting
from ppt_func_HTHP import replace_specific_text
from MVR import MVR_function
import CoolProp.CoolProp as CP



# Case inputs:
results = calculate_heat_pump_performance(
    fluid='R1233ZDE', 
    source_inlet_temp=75.0, 
    source_inlet_pressure=6, 
    mass_flow=200.0, 
    source_outlet_temp=25.0, 
    evaporator_temp_diff=3.0, 
    SH_temp_diff=2.0, 
    sink_required_temp=122.10, 
    subcooler_temp_diff=2.460, 
    eff_isentropic=0.8, 
    eff_isentropic_c2=0.8, 
    eff_mech=0.95, 
    Sink_T_inlet=90, 
    Sink_P_inlet=8, 
    Sink_T_outlet=112.30, 
    Sink_P_outlet=1.4
)

results_MVR, _ = MVR_function(
    m_steam= results["mass sink water"]-6.95,  # kg/s
    P1 = results["sink outlet P"] * 0.95,  # in bar (1.4 bar converted to Pa), also add pressure drop e.g., 1.4 means use 1.34 inlet
    T1=results["sink out T"]  + 273.15,  # K (85°C converted to Kelvin)
    isentropic_efficiency=0.8,
    P_final= 15 ,  # in bar a factor is added to incorporate pressure drop
    pres_drop_factor = 1.0277,  # Pa a factor is added to incorporate pressure drop
    mech_eff=0.9,
    temp_adjust_after_C1=10,  # delta T
    attemporation_water_temp=90,  # °C
    temp_adjust_after_C2=2  # delta T
)

for key, value in results.items():
    print(f"{key}: {value}")

for key, value in results_MVR.items():
    print(f"{key}: {value:.1f}")
    
Total_power = round(results['Total Electric Power (MW)'] + results_MVR['Total Power, MW'],1)
Final_heat = round(results_MVR['total_steam'] * (CP.PropsSI('H','P',results_MVR['Final pressure, bar'],'T',results_MVR['Temperature after second compressor + intercooling:, oC']+273.15, 'Water') - CP.PropsSI('H','P',results['sink inlet P']*100000,'T',results['sink in T']+273.15, 'Water'))/1e6,1)

# heatout = round(results_MVR['total_steam'] * (CP.PropsSI('H','P',results_MVR['Final pressure, bar'],'T',results_MVR['Temperature after second compressor + intercooling:, oC']+273.15, 'Water'))/1e6,1)
 
# heatin =  (results['mass sink water']-6.95)* (CP.PropsSI('H','P',results['sink outlet P']*100000,'T',results['sink out T']+273.15, 'Water'))/1e6
# Final_heat = heatout - heatin
COP_gross = round(Final_heat/Total_power,1)

print('Total power required, MW',Total_power )
print('Total heat after MVR',Final_heat )
print('COP gross', COP_gross)

'''
ppt HP only
'''
#Here add values for source
HT_in_source = round(results['heat source']/1000,0)
T_in_source = int(round(results['source in T'],0))
T_out_source = int(round(results['source out T'],0))
m_in_source = round(results['mass flow source'],0)

#Here add values for sink
HT_out_sink = round(results['Sink Power (MW)'],0)
T_in_sink = int(round(results['sink in T'],0))
T_out_sink = int(round(results['sink out T'],0))
m_in_sink = int(round(results['mass sink water'],0))

#COP values
COP = round(results['COP'],2)
Req_power = round(results['Total Electric Power (MW)'],1)


# Define the updates to be made
updates = [
    {'slide_number': 0, 'shape_number': 5, 'new_text': f'Heat input: {HT_in_source} MWth\nCooling from {T_in_source} ˚C → {T_out_source} ˚C\nMass flow ~ {m_in_source} kg/s'},
    {'slide_number': 0, 'shape_number': 7, 'new_text': f'Heat output: {HT_out_sink} MWth hot water\nWater {T_in_sink} °C → {T_out_sink} °C\nMass flow ~ {m_in_sink} kg/s'},
    {'slide_number': 0, 'shape_number': 10, 'new_text': f'COP: {COP} (overall system)\nRequired electric power: ~ {Req_power} MWel (incl. HP auxiliaries)\nRefrigerant: R1233ZD(E) '},
    {'slide_number': 0, 'shape_number': 18, 'new_text': f'{T_out_source} °C, Water'},
    {'slide_number': 0, 'shape_number': 31, 'new_text': f'{T_in_sink} °C, Water'},
    {'slide_number': 0, 'shape_number': 32, 'new_text': f'{T_out_sink} °C, Water'},
    {'slide_number': 0, 'shape_number': 33, 'new_text': f'{T_in_source} °C, Water'}
     # ... add more updates as needed for other text boxes
]

# Path to the PowerPoint file
ppt_path = r'C:\Users\me\OneDrive\001 siemens\models\pyhton\HTHP\HTHP_HP_only.pptx'

# Update the text boxes in the PowerPoint file while preserving formatting
updated_ppt_path = update_text_while_preserving_formatting(ppt_path, updates)

# Print the path of the updated file
print(f"Updated PowerPoint file saved at: {updated_ppt_path}")

'''
ppt HP + MVR
'''

    


steam_P = int(round(results_MVR['Final pressure, bar'],0))
steam_T = round(results_MVR['Temperature after second compressor + intercooling:, oC'],0)
msource = int(round(m_in_source * 3.6, 0))# tph

msink = int(round(results_MVR['total_steam'] * 3.6, 0))# tph


updates_MVR = [
    {'slide_number': 0, 'shape_number': 39, 'new_text': f'{steam_T}'},
    {'slide_number': 0, 'shape_number': 40, 'new_text': f'{T_in_sink}'},
    {'slide_number': 0, 'shape_number': 41, 'new_text': f'{Total_power}'},

    {'slide_number': 0, 'shape_number': 42, 'new_text': f'{T_out_source}'},

    {'slide_number': 0, 'shape_number': 46, 'new_text': f'{T_in_source}'},

    {'slide_number': 0, 'shape_number': 47, 'new_text': f'{HT_in_source}'},
    {'slide_number': 0, 'shape_number': 49, 'new_text': f'Source: water at {T_in_source} °C'},
    {'slide_number': 0, 'shape_number': 50, 'new_text': f'Sink: steam at {steam_P} bar and {steam_T} °C'},
    {'slide_number': 0, 'shape_number': 51, 'new_text': f'{steam_P}'},
    {'slide_number': 0, 'shape_number': 52, 'new_text': f'{Final_heat}'},
    {'slide_number': 0, 'shape_number': 53, 'new_text': f'{msink}'},
    {'slide_number': 0, 'shape_number': 54, 'new_text': f'{msource}'},
    {'slide_number': 0, 'shape_number': 55, 'new_text': f'{COP_gross}'},
    {'slide_number': 0, 'shape_number': 56, 'new_text': f'{steam_P}'},


    # {'slide_number': 0, 'shape_number': 18, 'new_text': f'{T_out_source} °C, Water'},
    # {'slide_number': 0, 'shape_number': 31, 'new_text': f'{T_in_sink} °C, Water'},
    # {'slide_number': 0, 'shape_number': 32, 'new_text': f'{T_out_sink} °C, Water'},
    # {'slide_number': 0, 'shape_number': 33, 'new_text': f'{T_in_source} °C, Water'}
      # ... add more updates as needed for other text boxes
]


# Path to the PowerPoint file
ppt_path_MVR= r'C:\Users\me\OneDrive\001 siemens\models\pyhton\HTHP\HTHP_HP+MMVR.pptx'

# Update the text boxes in the PowerPoint file while preserving formatting
updated_ppt_path = replace_specific_text(ppt_path_MVR, updates_MVR)

# Print the path of the updated file
print(f"Updated PowerPoint file saved at: {updated_ppt_path}")

