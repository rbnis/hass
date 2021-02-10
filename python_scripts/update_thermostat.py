temperature = data.get("temperature")
thermostat = data.get("thermostat")
temperature_target = data.get("temperature_target", 21.0)

if thermostat is not None and temperature is not None:
  if not temperature.startswith('sensor.'):
    logger.error("themperature needs to be an entity from the sensor domain.")
    exit()
  if not thermostat.startswith('climate.'):
    logger.error("thermostat needs to be an entity from the climate domain.")
    exit()

  thermostat_state = hass.states.get(thermostat)
  thermostat_target = 0

  if thermostat_state.state == 'off':
    logger.debug("Set min temperature, because state=off")
    thermostat_target = float(thermostat_state.attributes['min_temp'])
  else:
    temperature_state=hass.states.get(temperature)
    temperature_delta = temperature_target - float(temperature_state.state)

    # logger.debug("temperature_delta=%s", temperature_delta)

    thermostat_target = float(thermostat_state.attributes['current_temperature']) + float(temperature_delta)
    if thermostat_target > float(thermostat_state.attributes['max_temp']):
      thermostat_target = float(thermostat_state.attributes['max_temp'])

  thermostat_target = round(thermostat_target * 2) / 2
  if thermostat_target != float(thermostat_state.attributes['temperature']):
    logger.debug("Set target to %s", thermostat_target)
    hass.services.call('climate', 'set_temperature', {
      'entity_id': thermostat,
      'temperature': thermostat_target
    })
