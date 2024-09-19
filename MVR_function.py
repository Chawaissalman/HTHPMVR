from CoolProp.CoolProp import PropsSI

from CoolProp.CoolProp import PropsSI

def MVR(stages, initial_pressure, initial_temperature, initial_mass_flow, final_pressure, attemporation_temp, condensate_temp, last_stage_superheat, isentropic_efficiency, mech_efficiency, default_superheat):
    initial_pressure *= 1e5 
    final_pressure *= 1e5
    
    current_pressure = initial_pressure
    current_temperature = initial_temperature + 273.15  # Convert to Kelvin
    current_mass_flow = initial_mass_flow
    total_power = 0
    stage_temps = []
    
    superheat_temps = [default_superheat] * (stages - 1) + [last_stage_superheat]
    
    h1 = PropsSI('H', 'T', current_temperature, 'P', current_pressure, 'Water')
    
    stage_data = []

    for stage in range(stages):
        pressure_ratio = (final_pressure / initial_pressure) ** (1 / stages)
        next_pressure = current_pressure * pressure_ratio
        
        s1 = PropsSI('S', 'T', current_temperature, 'P', current_pressure, 'Water')
        h2s = PropsSI('H', 'S', s1, 'P', next_pressure, 'Water')
        h2a = h1 + (h2s - h1) / isentropic_efficiency
        
        power = current_mass_flow * (h2a - h1)
        total_power += power
        
        current_pressure = next_pressure
        current_temperature = PropsSI('T', 'H', h2a, 'P', current_pressure, 'Water')
        
        stage_temps.append(round(current_temperature - 273.15, 1))  # Convert to Celsius
        
        Tsat = PropsSI('T', 'Q', 0, 'P', current_pressure, 'Water')
        target_temp = Tsat + superheat_temps[stage]
        
        if current_temperature > target_temp:
            h_water = PropsSI('H', 'T', attemporation_temp + 273.15, 'P', current_pressure, 'Water')
            h_steam = PropsSI('H', 'T', target_temp, 'P', current_pressure, 'Water')
            Q_excess = current_mass_flow * (PropsSI('H', 'T', current_temperature, 'P', current_pressure, 'Water') - h_steam)
            water_needed = Q_excess / (h_steam - h_water)
            current_mass_flow += water_needed
            current_temperature = target_temp
        
        stage_temps.append(round(current_temperature - 273.15, 1))  # Convert to Celsius
        h1 = PropsSI('H', 'T', current_temperature, 'P', current_pressure, 'Water')
        
        stage_data.append({
            'stage': stage + 1,
            'pressure': current_pressure / 1e5,
            'enthalpy': h1,
            'temperature': current_temperature - 273.15,  # Convert to Celsius
            'power': power,
            'entropy': PropsSI('S', 'T', current_temperature, 'P', current_pressure, 'Water')
        })

    h_out = PropsSI('H', 'T', current_temperature, 'P', current_pressure, 'Water')
    h_in = PropsSI('H', 'T', initial_temperature + 273.15, 'P', initial_pressure, 'Water')
    h_condensate = PropsSI('H', 'T', condensate_temp + 273.15, 'P', current_pressure, 'Water')
    
    energy_added = current_mass_flow * h_out - initial_mass_flow * h_in - (current_mass_flow-initial_mass_flow)*h_condensate
    cop_1 = energy_added / (total_power / mech_efficiency)
    cop_2 = (current_mass_flow * (h_out - h_condensate)) / (total_power / mech_efficiency)
    
    total_power_mw = total_power / 1e6  # Convert to MW
    output_enthalpy_mw = current_mass_flow * h_out / 1e6  # Convert to MW
    input_enthalpy_mw = initial_mass_flow * h_in / 1e6  # Convert to MW
    condensate_enthalpy_mw = current_mass_flow * h_condensate / 1e6  # Convert to MW

    # Return a dictionary
    return {
        'total_power_mw': total_power_mw / mech_efficiency,
        'current_mass_flow': current_mass_flow,
        'cop_MVR_1': cop_1,
        'cop_MVR_only': cop_2,
        'stage_temps': stage_temps,
        'output_enthalpy_mw': output_enthalpy_mw,
        'input_enthalpy_mw': input_enthalpy_mw,
        'condensate_enthalpy_mw': condensate_enthalpy_mw,
        #'stage_data': stage_data
    }
