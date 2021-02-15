temperature = data.get("temperature")
thermostat = data.get("thermostat")
temperature_target = data.get("temperature_target", 21.0)
enable_heating = data.get("enable_heating", 'on')

if thermostat is not None and temperature is not None:
  if not temperature.startswith('sensor.'):
    logger.error("themperature needs to be an entity from the sensor domain.")
    exit()
  if not thermostat.startswith('climate.'):
    logger.error("thermostat needs to be an entity from the climate domain.")
    exit()

  thermostat_state = hass.states.get(thermostat)
  thermostat_target = 0

  # if thermostat_state.state == 'off':
  if enable_heating == 'off':
    if thermostat_state.state == 'off':
      exit()
    else:
      logger.info("Setting target %s to min temperature, because enable_heating==off", thermostat)
      thermostat_target = float(thermostat_state.attributes['min_temp'])
  else:
    temperature_state=hass.states.get(temperature)
    temperature_delta = temperature_target - float(temperature_state.state)

    logger.debug("temperature_target=%s", temperature_target)
    logger.debug("temperature_state=%s", float(temperature_state.state))
    logger.debug("temperature_delta=%s (%s - %s)", temperature_delta, temperature_target, float(temperature_state.state))

    thermostat_target = float(thermostat_state.attributes['current_temperature']) + float(temperature_delta)

    logger.debug("thermostat_state=%s", float(thermostat_state.attributes['current_temperature']))
    logger.debug("thermostat_target=%s (%s + %s)", thermostat_target, float(thermostat_state.attributes['current_temperature']), temperature_delta)

    if thermostat_target > float(thermostat_state.attributes['max_temp']):
      thermostat_target = float(thermostat_state.attributes['max_temp'])

    logger.debug("thermostat_target_sanitized=%s", thermostat_target)

    thermostat_target = round(thermostat_target * 2) / 2
    logger.debug("thermostat_target_rounded=%s", thermostat_target)

  if thermostat_target != float(thermostat_state.attributes['temperature']):
    logger.info("Setting target %s to %s", thermostat, thermostat_target)
    hass.services.call('climate', 'set_temperature', {
      'entity_id': thermostat,
      'temperature': thermostat_target
    })

    hvac_mode = 'auto'
    if thermostat_target == float(thermostat_state.attributes['min_temp']):
      hvac_mode = 'off'

    if thermostat_state.state != hvac_mode:
      hass.services.call('climate', 'set_hvac_mode', {
        'entity_id': thermostat,
        'temperature': 'off'
      })
