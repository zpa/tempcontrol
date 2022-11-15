# tempcontrol config file
from datetime import timedelta

# temperature sensitivity control parameters of hysteresis
TEMP_DELTA_MINUS = 0.5
TEMP_DELTA_PLUS = 1.0

# gammu files backend sms outbox directory with a trailing slash
SMS_OUTBOX = "/Users/zsolt/src/tempcontrol/sms/outbox/"

# MQTT topics used for communication
# temperature sensor
SHELLY_HT_TOPIC = "shellies/shellyht.local/sensor/temperature"
# tempcontrol MQTT client command channel
TEMPCONTROL_TOPIC = "tempcontrol/command"
# relay control channels
SHELLY_RELAY_TOPICS = ["shellies/shelly1-livingroom/relay/0/command",
                       "shellies/shelly1-bathroom/relay/0/command",
                       "shellies/shelly1-bedroom1/relay/0/command",
                       "shellies/shelly1-bedroom2/relay/0/command"]

# cell phone number of system admin
ADMIN = '+36203732951'

# minimum time between healthchecks
HEALTHCHECK_DELAY = timedelta(hours = 6)
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

