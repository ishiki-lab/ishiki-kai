#!/usr/bin/env python3
# -*- coding: utf-8 -*-

HOST = "127.0.0.1"
PORT = 4223

debug = False
verbose = False
# reading_interval = 1.0

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_dmx import BrickletDMX

from time import sleep, perf_counter
from os.path import join, splitext
from os import listdir
import math, time, datetime
from numpy import array, zeros, array_equal
# import pysrt
import signal
import sys
from pysrt import SubRipFile, SubRipItem, SubRipTime

from tf_device_ids import deviceIdentifiersList

import argparse

SRT_FILENAME = "output_dmx.srt"
srtFile = SubRipFile()

tfIDs = []

tfConnect = True

prevFrame = zeros(512)
prevTime = 0
subs = []

ipcon = IPConnection()

# if tfConnect:
#     tfIDs = []

deviceIDs = [i[0] for i in deviceIdentifiersList]

if debug:
    print(deviceIDs)
    for i in range(len(deviceIDs)):
        print(deviceIdentifiersList[i])

def getIdentifier(ID):
    deviceType = ""

    for t in range(len(deviceIDs)):
        if ID[1]==deviceIdentifiersList[t][0]:
            deviceType = deviceIdentifiersList[t][1]
    return(deviceType)

# Tinkerforge sensors enumeration
def cb_enumerate(uid, connected_uid, position, hardware_version, firmware_version,
                 device_identifier, enumeration_type):
    tfIDs.append([uid, device_identifier])


def dmxread_callback(frame, frame_no):
    global prevFrame, prevTime, subs, srtFile
    # if prevFrame. == 0:
    #     prevFrame = array(frame)
    frameArray = array(frame)
    if not array_equal(prevFrame,frameArray):
        if frame != None:
            item = SubRipItem(1, text="DMX1"+str(frame))
            item.shift(seconds=prevTime)
            item.end.shift(seconds=perf_counter()-prevTime)
            if verbose:
                print(item)
            subs.append(item)
            srtFile.append(item)
            prevTime = perf_counter()
    prevFrame = array(frame)
    # if prevframe-frame:
    #     print(frame, frame_no)
    # prev
    # print("callback called")

def signal_handler(sig, frame):
    global subs, tfConnect, ipcon, srtFile, SRT_FILENAME
    if verbose:
        print(subs, len(subs))
    encoding="utf_8"

    srtFile.save(SRT_FILENAME, encoding=encoding)

    if tfConnect:
        ipcon.disconnect()
    sys.exit(0)

def main():

    parser = argparse.ArgumentParser(description="LushRoom sound and light command-line player")
    group = parser.add_mutually_exclusive_group()
    # group.add_argument("-v", "--verbose", action="store_true")
    # group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-s","--srt", default=SRT_FILENAME, help=".srt file name for lighting events")
    parser.add_argument("-a","--audio", default=AUDIO_FILENAME, help="audio file for sound stream")
    parser.add_argument("-b","--brightness", default=MAX_BRIGHTNESS, help="maximum brightness")
    parser.add_argument("-t","--time", default=TICK_TIME, help="time between events")
    parser.add_argument("--hue", default=HUE_IP_ADDRESS, help="Philips Hue bridge IP address")

    args = parser.parse_args()

    print(args)

    # global ipcon

    ipcon.connect(HOST, PORT)

    # Register Enumerate Callback
    ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, cb_enumerate)

    # Trigger Enumerate
    ipcon.enumerate()

    sleep(2)

    if verbose:
        print(tfIDs)

    dmxcount = 0
    for tf in tfIDs:
        # try:
        if True:
            # print(len(tf[0]))

            if len(tf[0])<=3: # if the device UID is 3 characters it is a bricklet
                if tf[1] in deviceIDs:
                    print(tf[0],tf[1], getIdentifier(tf))
                if tf[1] == 285: # DMX Bricklet
                    if dmxcount == 0:
                        print("Registering %s as slave DMX device for capturing DMX frames" % tf[0])
                        dmx = BrickletDMX(tf[0], ipcon)
                        dmx.set_dmx_mode(BrickletDMX.DMX_MODE_SLAVE)
                        dmx.register_callback(BrickletDMX.CALLBACK_FRAME, dmxread_callback)
                        dmx.set_frame_callback_config(False, False, True, False)
                        signal.signal(signal.SIGINT, signal_handler)

                    dmxcount += 1

    while True:
        pass

if __name__ == "__main__":
    main()
