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

# HUE_IP_ADDRESS = "192.168.1.129"
# HUE_IP_ADDRESS = "10.0.0.4"
HUE_IP_ADDRESS = "10.251.140.208"
SRT_FILENAME = ""
TRANSITION_TIME = 10 # Unit is tenths of second (10 = 1 second)
MAX_BRIGHTNESS = 254
INTERVAL = 1    # Seconds
RECORD = True
DEBUG = True
VERBOSE = True
PLAY_HUE = True
PLAY_DMX = True
DMX_INTERVAL = 0.05 # 0.05 means 20 times per second

previous_time = 0
previous_dmx_time = 0
bridge = None
hue_list = [[]]
hue_cmds = []
prev_cmds_str = ""

srtFile = None

tfIDs = []
tfConnect = True

dmx_array = zeros(512)
prev_frame = zeros(512)
prev_time = 0

subs = []
sub_incr = 1

HOST = "127.0.0.1"
PORT = 4223
dmx = None
scheduler = None
last_played = 0
tfIDs = []
tfConnect = True
ipcon = IPConnection() # Tinkerforge IP connection
deviceIDs = [i[0] for i in deviceIdentifiersList]


if DEBUG:
    print(deviceIDs)
    for i in range(len(deviceIDs)):
        print(deviceIdentifiersList[i])

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
    global bridge, INTERVAL, TRANSITION_TIME, previous_time, hue_list, hue_cmds, RECORD, VERBOSE, MAX_BRIGHTNESS
    global prev_time, subs, srtFile, sub_incr, prev_cmds_str
    # print(hue_list)
    #print(len(args))
    #if not len(args) == 4 or type(args[0]) is not float or type(args[1]) is not float:
    #    return

    if DEBUG:
        print(len(args), args)

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

    on = True
    if v<=1:
        on = False

    cmd =  {'transitiontime' : int(TRANSITION_TIME), 'on' : on, 'bri' : int(v), 'sat' : int(s), 'hue' : int(h)}

    if len(hue_cmds) < hue_n:
        hue_cmds.append(cmd)
    else:
        hue_cmds[hue_n-1] = cmd

    if int(hue_n) < len(hue_list):

        # print(hue_n,hue_list[int(hue_n)],h,s,v)

        current_time = time.time()
        elapsed_time = current_time - previous_time
        if DEBUG:
            print("HUE time", current_time, previous_time, elapsed_time)

        # print(cmd, hue_list,hue_list[int(hue_n)])

        if (elapsed_time > INTERVAL):
        # if True:
            for hl in hue_list[int(hue_n)]:
                if DEBUG:
                    print("---",hue_n,hl,h,s,v)
                l = (h, s, v, int(TRANSITION_TIME))
                if PLAY_HUE:
                    bridge.set_light(hl, cmd)
            cmds_str = ""
            if DEBUG:
                print(hue_cmds)
            i = 0
            for c in hue_cmds:
                l = (hue_cmds[i]["hue"], hue_cmds[i]["sat"], hue_cmds[i]["bri"], hue_cmds[i]["transitiontime"])
                if cmds_str == "":
                    cmds_str += "HUE"+str(i+1)+str(l).replace(" ", "")
                else:
                    cmds_str += ";HUE"+str(i+1)+str(l).replace(" ", "")
                i += 1
            if cmds_str != prev_cmds_str:
                item = SubRipItem(sub_incr, text=cmds_str)
                item.shift(seconds=prev_time)
                item.end.shift(seconds=perf_counter()-prev_time)
                # item.end.shift(seconds=prev_time+int(TRANSITION_TIME)/10.0)
                if VERBOSE:
                    print("---",item)
                subs.append(item)
                if srtFile!=None:
                    srtFile.append(item)
                    encoding="utf_8"
                    srtFile.save(SRT_FILENAME, encoding=encoding)
                sub_incr += 1
                prev_cmds_str = cmds_str
            prev_time = perf_counter()

            # bridge.set_light(int(hue_n), cmd)
            previous_time = time.time()
            if DEBUG:
                print("Hue commands",hue_cmds)

        #filterno = address[-1]
        #print("RGB {filterno} values: {value1}, {value2}, {value3}")

# def print_hue(unused_addr, args, hue_n):
#     print("[{0}] ~ {1}".format(args[0], hue_n))
#     #print("[{0}] ~ {1} {2} {3}".format(args[0], args[1], args[2]))
#     #print(hue_n, len(args))

def play_record_dmx(unused_addr, args, value):
    global INTERVAL, TRANSITION_TIME, previous_time, dmxCounter, VERBOSE
    global prev_frame, prev_time, subs, srtFile, previous_dmx_time, DMX_INTERVAL, sub_incr
    global dmx

    dmx_array[int(args[0])] = int(value*255)

    current_dmx_time = time.time()
    elapsed_dmx_time = current_dmx_time - previous_dmx_time

    if DEBUG:
        print("DMX time", current_dmx_time, previous_dmx_time, elapsed_dmx_time)

    if (elapsed_dmx_time > DMX_INTERVAL):
        frameArray = trim_zeros(dmx_array,'b').astype('uint8')
        # frameArray = array(frameArray)
        print(array_equal(prev_frame,frameArray), tuple(prev_frame), tuple(frameArray))
        if not array_equal(prev_frame,frameArray):
            if frameArray.any() != None:
                item = SubRipItem(sub_incr, text="DMX1"+str(tuple(frameArray)[1:]).replace(" ", ""))
                item.shift(seconds=prev_time)
                item.end.shift(seconds=perf_counter()-prev_time)
                if VERBOSE:
                    print(item)
                subs.append(item)
                if srtFile!=None:
                    srtFile.append(item)
                    # encoding="utf_8"
                    # srtFile.save(SRT_FILENAME, encoding=encoding)
                sub_incr += 1
                prev_time = perf_counter()
                if PLAY_DMX:
                    if DEBUG:
                        print("DMX tuple",tuple(frameArray)[1:])
                    dmx.write_frame(tuple(frameArray)[1:])
                if not array_equal(prev_frame,frameArray):
                    prev_frame = frameArray

        previous_dmx_time = time.time()
        print(previous_dmx_time)

    # if prev_frame. == 0:
    #     prev_frame = array(frame)

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
    global DMX_INTERVAL, INTERVAL, TRANSITION_TIME, HUE_IP_ADDRESS, DEBUG, VERBOSE
    global subs, srtFile
    global ipcon, tfIDs, dmx

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
        default="127.0.0.1", help="OSC ip address to listen to")
    parser.add_argument("--port",
        type=int, default=8000, help="OSC port to listen to")
    parser.add_argument("-s","--srt", default=SRT_FILENAME, help=".srt file name for lighting events")
    parser.add_argument("-b","--brightness", default=MAX_BRIGHTNESS, help="maximum brightness")
    parser.add_argument("-i","--interval", default=INTERVAL, help="sampling interval for Philips Hue events")
    parser.add_argument("-d","--dmx_interval", default=DMX_INTERVAL, help="sampling interval for DMX events")
    parser.add_argument("-t","--transition_time", default=TRANSITION_TIME, help="transition time between Philips Hue events")
    parser.add_argument("--hue", default=HUE_IP_ADDRESS, help="Philips Hue bridge IP address")

    args = parser.parse_args()

    print(args)

    MAX_BRIGHTNESS = int(args.brightness)
    SRT_FILENAME = args.srt
    INTERVAL = float(args.interval)
    DMX_INTERVAL = float(args.dmx_interval)
    TRANSITION_TIME = float(args.transition_time)
    HUE_IP_ADDRESS = args.hue
    # VERBOSE = args.verbose
    # DEBUG = args.debug

    if SRT_FILENAME!="":
        print("Start recording the %s subtitles track for light events." % SRT_FILENAME)
        srtFile = SubRipFile(path=SRT_FILENAME)

    if PLAY_HUE:
        bridge = Bridge(HUE_IP_ADDRESS)
        bridge.connect()
        bridge.get_api()
        lights = bridge.lights
        for l in lights:
            print(l.name)
        for l in lights:
            l.on = True
            l.brightness = MAX_BRIGHTNESS

        light_names = bridge.get_light_objects('name')
        print("Light names:", light_names)

        hue_list = hue_build_lookup_table(lights)
        print(hue_list)

    if PLAY_DMX:

        ipcon.connect(HOST, PORT)

        # Register Enumerate Callback
        ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, cb_enumerate)

        # Trigger Enumerate
        ipcon.enumerate()

        sleep(2)

        if DEBUG:
            print(tfIDs)

        dmxcount = 0
        for tf in tfIDs:
            # try:
            if True:
                # print(len(tf[0]))

                if len(tf[0])<=3: # if the device UID is 3 characters it is a bricklet
                    if tf[1] in deviceIDs:
                        if VERBOSE:
                            print(tf[0],tf[1], getIdentifier(tf))
                    if tf[1] == 285: # DMX Bricklet
                        if dmxcount == 0:
                            print("Registering %s as slave DMX device for capturing DMX frames" % tf[0])
                            dmx = BrickletDMX(tf[0], ipcon)
                            dmx.set_dmx_mode(dmx.DMX_MODE_MASTER)
                            # channels = int((int(MAX_BRIGHTNESS)/255.0)*ones(512,)*255)
                            # dmx.write_frame([255,255])
                            sleep(1)
                            # channels = int((int(MAX_BRIGHTNESS)/255.0)*zeros(512,)*255)
                            # dmx.write_frame(channels)
                        dmxcount += 1

    disp = dispatcher.Dispatcher()
    # print(dir(dispatcher))

    for h in range(512):
        disp.map("/hue%s" % h, play_record_hue, "%s" % h)

    for h in range(512):
        disp.map("/dmx%s" % h, play_record_dmx, "%s" % h)

    server = osc_server.ThreadingOSCUDPServer(
          (args.ip, args.port), disp)
    print("Serving OSC on {}".format(server.server_address))
    signal.signal(signal.SIGINT, signal_handler)
    server.serve_forever()

if __name__ == "__main__":
    main()
