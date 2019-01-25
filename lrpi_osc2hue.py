#!/usr/bin/env python3

from phue import Bridge
import argparse
import math
import phue
from colorsys import rgb_to_hsv

from pythonosc import dispatcher
from pythonosc import osc_server

from typing import List, Any

import json
import time
from requests import post
from sys import exit

# TOD: add hue discovery using uPNP - https://www.meethue.com/api/nupnp

HUE_URL = "https://www.meethue.com/api/nupnp"
response = post(HUE_URL)
print(dir(response))
print(response.content)
#print(json.loads(response.json()))

# HUE_IP_ADDRESS = "192.168.1.129"
HUE_IP_ADDRESS = "10.0.0.2"
TRANSITION_TIME = 10
MAX_BRIGHTNESS = 255
INTERVAL = 1 # seconds
previous_time = 0
bridge = None

def set_filter(address: str, *args: List[Any]) -> None:
    global bridge
    global TRANSITION_TIME
    global previous_time
    #print(len(args))
    #if not len(args) == 4 or type(args[0]) is not float or type(args[1]) is not float:
    #    return

    #print(len(args), args)

    # Check that address starts with filter
    #if not address[:-1] == "/hue":  # Cut off the last character
    #    return

    r = args[1]
    g = args[2]
    b = args[3]

    h,s,v = rgb_to_hsv(r,g,b)

    h *= 65535.0
    s *= 254.0
    v *= 254.0

    h = int(h)
    s = int(s)
    v = int(v*MAX_BRIGHTNESS/254.0)

    hue_n = args[0][0][-1]

    print(hue_n,h,s,v)

    current_time = time.time()
    elapsed_time = current_time - previous_time
    #print(current_time, previous_time, elapsed_time)

    cmd =  {'transitiontime' : int(TRANSITION_TIME), 'on' : True, 'bri' : int(v), 'sat' : int(s), 'hue' : int(h)}
    if (elapsed_time > INTERVAL):
        print(hue_n,h,s,v)
        bridge.set_light(int(hue_n), cmd)
        previous_time = time.time()

    #filterno = address[-1]
    #print("RGB {filterno} values: {value1}, {value2}, {value3}")

def print_hue(unused_addr, args, hue_n):
    print("[{0}] ~ {1}".format(args[0], hue_n))
    #print("[{0}] ~ {1} {2} {3}".format(args[0], args[1], args[2]))
    #print(hue_n, len(args))

def print_dmx(unused_addr, args, dmx_n):
    #print("[{0}] ~ {1}".format(args[0], dmx_n))
    print(dmx_n, args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
        default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",
        type=int, default=8000, help="The port to listen on")
    args = parser.parse_args()

    bridge = Bridge(HUE_IP_ADDRESS)
    bridge.connect()
    bridge.get_api()
    lights = bridge.lights
    for l in lights:
        print(l.name)
    for l in lights:
        l.brightness = 1

    light_names = bridge.get_light_objects('name')
    print("Light names:", light_names)

    dispatcher = dispatcher.Dispatcher()
    print(dir(dispatcher))

    for h in range(512):
        dispatcher.map("/hue%s" % h, set_filter, "HUE%s" % h)

    for h in range(512):
        dispatcher.map("/dmx%s" % h, print_dmx, "DMX%s" % h)

    server = osc_server.ThreadingOSCUDPServer(
          (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
