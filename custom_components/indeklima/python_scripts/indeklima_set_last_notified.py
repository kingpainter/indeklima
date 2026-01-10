"""Python script to update last_notified timestamp on Indeklima room sensors.

Place this file in: config/python_scripts/indeklima_set_last_notified.py

Requirements:
- python_script integration must be enabled in configuration.yaml

Usage:
  service: python_script.indeklima_set_last_notified
  data:
    entity_id: sensor.indeklima_stue_status
"""

entity_id = data.get('entity_id')

if not entity_id:
    logger.error("indeklima_set_last_notified: No entity_id provided")
else:
    # Get the entity
    entity = hass.states.get(entity_id)
    
    if not entity:
        logger.error(f"indeklima_set_last_notified: Entity {entity_id} not found")
    else:
        # Get current attributes
        attributes = dict(entity.attributes)
        
        # Update last_notified
        attributes['last_notified'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Update state with new attributes
        hass.states.set(entity_id, entity.state, attributes)
        
        logger.info(f"indeklima_set_last_notified: Updated {entity_id}")