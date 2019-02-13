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
from time import sleep, perf_counter

from requests import get
import sys
from sys import exit
from os.path import join, splitext
from os import listdir

import math, time, datetime
from numpy import array, zeros, array_equal, append, trim_zeros
import signal

from pysrt import SubRipFile, SubRipItem, SubRipTime

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_dmx import BrickletDMX
from tf_device_ids import deviceIdentifiersList

# TODO: add hue discovery using uPNP - https://www.meethue.com/api/nupnp

HUE_URL = "https://www.meethue.com/api/nupnp"
response = get(HUE_URL)
# print(dir(response))
print(response.content)
#print(json.loads(response.json()))

HUE_IP_ADDRESS = "192.168.1.129"
# HUE_IP_ADDRESS = "10.0.0.4"
SRT_FILENAME = ""
TRANSITION_TIME = 10
MAX_BRIGHTNESS = 255
INTERVAL = 1 # seconds
RECORD = True
DEBUG = True
VERBOSE = True
PLAY_HUE = True
PLAY_DMX = True
DMX_INTERVAL = .05

previous_time = 0
previous_dmx_time = 0
bridge = None
hue_list = [[]]

srtFile = None

tfIDs = []
tfConnect = True

dmxArray = zeros(512)
prevFrame = zeros(512)
prevTime = 0
subs = []
sub_incr = 1

ipcon = IPConnection()

deviceIDs = [i[0] for i in deviceIdentifiersList]

# if DEBUG:
#     print(deviceIDs)
#     for i in range(len(deviceIDs)):
#         print(deviceIdentifiersList[i])

def getIdentifier(ID):
    deviceType = ""

    for t in range(len(deviceIDs)):
        if ID[1]==deviceIdentifiersList[t][0]:
            deviceType = deviceIdentifiersList[t][1]
    return(deviceType)

# Tinkerforge bricklets enumeration
def cb_enumerate(uid, connected_uid, position, hardware_version, firmware_version,
                 device_identifier, enumeration_type):
    tfIDs.append([uid, device_identifier])

def hue_build_lookup_table(lights):
    #print(lights)
    hue_l = [[]]
    i = 1
    for j in range(len(lights)+1):
        for l in lights:
            #print(dir(l))
            #lname = "lamp   "+l.name+"   "
            lname = str(l.name)
            #print(lname)
            #print("testing", str(j), lname.find(str(i)), len(hue), l.name.find(str(i)), l.light_id, l.name, l.bridge.ip, l.bridge.name, str(i+1))
            if lname.find(str(j))>=0:
                #if str(i) in lname:
                print(j, lname.find(str(j)), l.light_id, l.name, l.bridge.ip, l.bridge.name)
                if len(hue_l)<=j:
                   hue_l.append([l.light_id])
                else:
                   hue_l[j].append(l.light_id)
        i += 1
    return(hue_l)

def play_record_hue(address: str, *args: List[Any]) -> None:
    global bridge, INTERVAL, TRANSITION_TIME, previous_time, hue_list, RECORD, VERBOSE
    global prevTime, subs, srtFile, sub_incr
    # print(hue_list)
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

    # hue_n = args[0][0][-1]
    hue_n = int(args[0][0])
    # print(hue_n,len(hue_list),hue_list)

    if int(hue_n) < len(hue_list):

        # print(hue_n,hue_list[int(hue_n)],h,s,v)

        current_time = time.time()
        elapsed_time = current_time - previous_time
        #print(current_time, previous_time, elapsed_time)

        on = True
        if v<=10:
            on = False

        cmd =  {'transitiontime' : int(TRANSITION_TIME), 'on' : on, 'bri' : int(v), 'sat' : int(s), 'hue' : int(h)}
        # print(cmd, hue_list,hue_list[int(hue_n)])
        if (elapsed_time > INTERVAL):
            for hl in hue_list[int(hue_n)]:
                print("---",hue_n,hl,h,s,v)
                l = (h, s, v, int(TRANSITION_TIME))
                item = SubRipItem(sub_incr, text="HUE"+str(hue_n)+str(l).replace(" ", ""))
                item.shift(seconds=prevTime)
                item.end.shift(seconds=perf_counter()-prevTime)
                if VERBOSE:
                    print("---",item)
                subs.append(item)
                if srtFile!=None:
                    srtFile.append(item)
                    sub_incr += 1
                prevTime = perf_counter()
                if PLAY_HUE:
                    bridge.set_light(hl, cmd)
            # bridge.set_light(int(hue_n), cmd)
            previous_time = time.time()

        #filterno = address[-1]
        #print("RGB {filterno} values: {value1}, {value2}, {value3}")

# def print_hue(unused_addr, args, hue_n):
#     print("[{0}] ~ {1}".format(args[0], hue_n))
#     #print("[{0}] ~ {1} {2} {3}".format(args[0], args[1], args[2]))
#     #print(hue_n, len(args))

def play_record_dmx(unused_addr, args, value):
    global INTERVAL, TRANSITION_TIME, previous_time, dmxCounter, VERBOSE
    global prevFrame, prevTime, subs, srtFile, previous_dmx_time, DMX_INTERVAL, sub_incr

    dmxArray[int(args[0])] = int(value*255)

    current_dmx_time = time.time()
    elapsed_dmx_time = current_dmx_time - previous_dmx_time

    print(current_dmx_time, previous_dmx_time, elapsed_dmx_time)

    if (elapsed_dmx_time > DMX_INTERVAL):
        frameArray = trim_zeros(dmxArray,'b').astype('uint8')
        # frameArray = array(frameArray)
        print(array_equal(prevFrame,frameArray), tuple(prevFrame), tuple(frameArray))
        if not array_equal(prevFrame,frameArray):
            if frameArray.any() != None:
                print("DMX",frameArray)
                item = SubRipItem(sub_incr, text="DMX1"+str(tuple(frameArray)).replace(" ", ""))
                item.shift(seconds=prevTime)
                item.end.shift(seconds=perf_counter()-prevTime)
                if VERBOSE:
                    print(item)
                subs.append(item)
                if srtFile!=None:
                    srtFile.append(item)
                    sub_incr += 1
                prevTime = perf_counter()
                if PLAY_DMX:
                    pass
                if not array_equal(prevFrame,frameArray):
                    prevFrame = frameArray

        previous_dmx_time = time.time()
        print(previous_dmx_time)

    # if prevFrame. == 0:
    #     prevFrame = array(frame)

    # print("[{0}] ~ {1}".format(args[0], value))
    # print(args[0], value)
    #print(dmx_n,hue_list[int(hue_n)],h,s,v)

def signal_handler(sig, frame):
    global subs, tfConnect, ipcon, srtFile, SRT_FILENAME

    if VERBOSE:
        #print(subs, len(subs))
        print("Number of subtitles", len(subs))
    encoding="utf_8"

    if srtFile!=None:
        print("Saving the %s subtitle file" % SRT_FILENAME)
        srtFile.save(SRT_FILENAME, encoding=encoding)

    # if tfConnect:
    #     ipcon.disconnect()
    sys.exit(0)

def main():
    global hue_list, bridge, SRT_FILENAME, HUE_IP_ADDRESS, MAX_BRIGHTNESS
    global INTERVAL, TRANSITION_TIME, HUE_IP_ADDRESS, DEBUG, VERBOSE
    global subs, srtFile
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
        default="127.0.0.1", help="OSC ip address to listen to")
    parser.add_argument("--port",
        type=int, default=8000, help="OSC port to listen to")
    parser.add_argument("-s","--srt", default=SRT_FILENAME, help=".srt file name for lighting events")
    parser.add_argument("-b","--brightness", default=MAX_BRIGHTNESS, help="maximum brightness")
    parser.add_argument("-i","--interval", default=INTERVAL, help="maximum brightness")
    parser.add_argument("-t","--transition", default=TRANSITION_TIME, help="time between events")
    parser.add_argument("--hue", default=HUE_IP_ADDRESS, help="Philips Hue bridge IP address")

    args = parser.parse_args()

    print(args)

    MAX_BRIGHTNESS = int(args.brightness)
    SRT_FILENAME = args.srt
    INTERVAL = float(args.interval)
    TRANSITION_TIME = float(args.transition)
    HUE_IP_ADDRESS = args.hue
    # VERBOSE = args.verbose
    # DEBUG = args.debug

    if SRT_FILENAME!="":
        print("Start recording the %s subtitles track for light events." % SRT_FILENAME)
        srtFile = SubRipFile()

    if PLAY_HUE:
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

        hue_list = hue_build_lookup_table(lights)
        print(hue_list)

    disp = dispatcher.Dispatcher()
    # print(dir(dispatcher))

    for h in range(512):
        disp.map("/hue%s" % h, play_record_hue, "%s" % h)

    for h in range(512):
        disp.map("/dmx%s" % h, play_record_dmx, "%s" % h)

    server = osc_server.ThreadingOSCUDPServer(
          (args.ip, args.port), disp)
    print("Serving on {}".format(server.server_address))
    signal.signal(signal.SIGINT, signal_handler)
    server.serve_forever()

if __name__ == "__main__":
    main()
