from flask import Flask
app = Flask(__name__)

import tempcontrol.views
import tempcontrol.tempcontrol_mqtt_client

