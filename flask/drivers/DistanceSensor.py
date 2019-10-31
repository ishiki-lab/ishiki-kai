# Presuming it's the IR bricklet, sample code here:
# https://www.tinkerforge.com/en/doc/Software/Bricklets/DistanceIR_Bricklet_Python.html
# There's a nice callback structure and all sorts
# See the "Threshold" example

from Relay import Relay
import urllib.request
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib import parse
import requests

class DistanceSensor:
    def __init__(self, dist):
        self.threshold_distance = dist
        self.relay = Relay()
        self.poll()

    def poll(self):
        print("Polling the TF distance sensor for distance measurement... but not really")

    def triggerRelay(self, path, start_position=0):
        postFields = { \
                    'upload_path': str(path), \
                    'start_position': str(start_position), \
                }
        playerRes = requests.post('http://192.168.0.56' + '/scentroom-trigger', json=postFields)