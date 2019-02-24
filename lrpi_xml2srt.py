#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Lushrooms

lrpi_xml2srt.py

This program converts Vezér lighting event files rendered in XML to SRT files that can be played
on the Lushroom Pi open source light and sound player.

Tracks should be encoded as follows:

For Philips Hue tracks, the address should be in the form of
/hue#
where # is an incremental integer, for instance /hue1, /hue2, /hue3, etc.
Philips Hue lamps should be named with incremental integer numbers, for instance
1, 2, 3, etc.
The OSC type should be "OSCColor/floatarray" enconding the RGB values without alpha channel.

For DMX tracks, the address should be in the form of
/dmx#
where # is an incremental integer between 1 and 512, for instance /dmx1, /dmx2, /dmx3, etc.
The OSC type should be "OSCColor/floatarray" for RGB (3 values) and RGBW (4 values, including alpha as white channel),
or "OSCValue/float" for a single light intensity channel (single DMX address).
'''

from xml.dom import minidom
from os.path import join
from sys import stdout
from colorsys import rgb_to_hsv
from numpy import array, zeros, array_equal, append, trim_zeros
from pysrt import SubRipFile, SubRipItem, SubRipTime
import argparse

__author__ = "Francesco Anselmo"
__copyright__ = "Copyright 2019, Francesco Anselmo"
__credits__ = ["Francesco Anselmo"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Francesco Anselmo"
__email__ = "francesco.anselmo@arup.com"
__status__ = "Dev"

# XML_FILENAME = '/Arup/Jobs/Lush_Spa/Media_Player/Vezer/01_Comforter.xml'
XML_FILENAME = 'ChID-BLITS-EBU.xml'
OUT_EXT = ".srt"
HUE_SAMPLING = 1.0 # Sampling rate of HUE frames in seconds
DMX_SAMPLING = 0.05 # Sampling rate of DMX frames in seconds
SAMPLING = 0.05 # Sampling rate in seconds. For instance 0.05 means 20 frames per second
TRANSITION_TIME = 10
START = None
END = None
DEBUG = False
VERBOSE = False

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def handle_track(track, start, end, fps):
    global SAMPLING
    track_doms = track.getElementsByTagName('track')
    track_dict = {}
    track_name_list = []
    track_type_list = []
    track_address_list = []
    track_events_list = []
    track_frames_list = []
    # Iterate through tracks - i is the track number
    i = 0
    for track_dom in track_doms:
        track_type_doms = track_dom.getElementsByTagName('type')
        for track_type_dom in track_type_doms:
            track_type = getText(track_type_dom.childNodes)
            print("Track type:", track_type)
            # if track_type != "audio":
            track_type_list.append(track_type)
        track_name_doms = track_dom.getElementsByTagName('name')
        # print("%s tracks have been found" % len(track_name_doms))
        for track_name_dom in track_name_doms:
            track_name = getText(track_name_dom.childNodes)
            print("Track name:", track_name)
            # if track_type != "audio":
            track_name_list.append(track_name)
        track_address_doms = track_dom.getElementsByTagName('address')
        # print("%s OSC addresses have been found" % len(track_address_doms))
        if track_type != "audio":
            for track_address_dom in track_address_doms:
                track_address = getText(track_address_dom.childNodes)
                print("Track address:", track_address)
                track_address_list.append(track_address)
            # if track_address[1:4] == "hue":
            #     SAMPLING = HUE_SAMPLING
            #     print("Choosing Hue Sampling:", SAMPLING)
            # elif track_address[1:4] == "dmx":
            #     SAMPLING = DMX_SAMPLING
            #     print("Choosing DMX Sampling:", SAMPLING)
        else:
            track_address_list.append("audio")

        print("Sampling:", SAMPLING)
        # Iterate through frames - i is the frame number
        prev_track_event = ""
        # if track_type != "audio":
        # if True:
        # print(int(fps*SAMPLING))
        for frame_no in range (start,end,int(fps*SAMPLING)):
            # Take all events for each track
                # for j in range(len(track_name_doms)+1):
                track_frames_list.append(frame_no)
                frame_id = "f%s" % frame_no
                track_event_doms = track_dom.getElementsByTagName(frame_id)
                # print("Number of track event doms", len(track_event_doms))
                # j = 0
                if len(track_event_doms)>0:
                    for track_event_dom in track_event_doms:
                        track_event = getText(track_event_dom.childNodes)
                        if DEBUG:
                            print(frame_id, len(track_events_list), frame_no, track_event)
                        else:
                            if frame_no % 100 == 0:
                                print(".", end = "")
                                stdout.flush()
                        if len(track_events_list)<=i:
                            track_events_list.append([track_event])
                        else:
                            track_events_list[i].append(track_event)
                        # j += 1
                        prev_track_event = track_event
                else:
                    if len(track_events_list)<=i:
                        track_events_list.append([prev_track_event])
                    else:
                        track_events_list[i].append(prev_track_event)
                    if DEBUG:
                        print(frame_id, len(track_events_list), frame_no, prev_track_event)
                    else:
                        if frame_no % 100 == 0:
                            print(".", end = "")
                            stdout.flush()
        i += 1
        print()

    # print(track_name_list)
    # print(track_address_list)
    # print(track_events_list)
    return([track_name_list, track_type_list, track_address_list, track_events_list, track_frames_list])

def handle_tracks(tracks, start, end, fps, srt_filename):
    global XML_FILENAME, HUE_SAMPLING, DMX_SAMPLING, TRANSITION_TIME
    track_list = []
    for track in tracks:
        track_list = handle_track(track, start, end, fps)
        # print(track_list)
        print("Number of lighting events: ",len(track_list[3][0]))
    # srt_file = open(srt_filename,"w")

    dmx_frame = zeros(512)
    prev_dmx_frame = zeros(512)

    subrip_file = SubRipFile(path=srt_filename)

    for i in range(len(track_list[3][0])):
        frame_no = track_list[4][i]
        print(30*"-")
        t = frame_no*(1.0/float(fps))
        print("Frame %s / time %s seconds" % (frame_no, t))
        print(30*"-")
        hue_cmd = ""
        dmx_cmd = ""
        for j in range(len(track_list[0])):
            if track_list[1][j] != "audio":
                name = track_list[0][j]
                type = track_list[1][j]
                addr = track_list[2][j]
                payload = track_list[3][j][i]
                # print(name, type, addr, payload)
                # Convert Hue payload to hue command
                if payload!="":
                    if addr[1:4].lower() == "hue" and type =="OSCColor/floatarray":
                        print("hue", addr, payload)
                        r,g,b,a = 0,0,0,0
                        payload_list = payload.split(",")
                        # print(payload_list)
                        if len(payload_list) == 3:
                            r,g,b = payload_list
                        elif len(payload_list) == 4:
                            r,g,b,a = payload_list

                        h,s,v = rgb_to_hsv(float(r),float(g),float(b))

                        h *= 65535.0
                        s *= 254.0
                        v *= 254.0

                        h = int(h)
                        s = int(s)
                        v = int(v)
                        # print("hue", addr, payload, h,s,v)
                        n = int(addr[4:])
                        # print("hue", n, h,s,v)
                        if len(hue_cmd) == 0:
                            hue_cmd += "HUE%s(%s,%s,%s,%s)" % (n,h,s,v,TRANSITION_TIME)
                        else:
                            hue_cmd += ";HUE%s(%s,%s,%s,%s)" % (n,h,s,v,TRANSITION_TIME)
                    # Convert single DMX channel to command
                    elif addr[1:4].lower() == "dmx" and type =="OSCValue/float":
                        print("dmx value", addr, payload)
                        n = int(addr[4:])
                        if payload!="":
                            dmx_frame[int(n)] = int(float(payload)*255)
                    # Convert multiple DMX channels to command
                    elif addr[1:4].lower() == "dmx" and (type =="OSCColor/floatarray" or type =="OSCValue/standard"):
                        print("dmx colour", addr, payload)
                        n = int(addr[4:])
                        if payload!="":
                            payload_list = payload.split(",")
                            for channel in payload_list:
                                dmx_frame[int(n)] = int(float(channel)*255)
                                n += 1

        # Output HUE commands
        # hue_t = frame_no * (1.0/HUE_SAMPLING)
        if frame_no % fps == 0 and hue_cmd!="":
            item = SubRipItem(frame_no, text=hue_cmd)
            item.shift(seconds=t)
            item.end.shift(seconds=1)
            if VERBOSE:
                print(item)
            subrip_file.append(item)
        # Output DMX command
        dmx_frame_trimmed = trim_zeros(dmx_frame,'b').astype('uint8')
        dmx_cmd = "DMX1"+str(tuple(dmx_frame_trimmed)[1:]).replace(" ", "")
        # cmd = hue_cmd + ";" + dmx_cmd
        if not array_equal(dmx_frame_trimmed,prev_dmx_frame):
            item = SubRipItem(frame_no, text=dmx_cmd)
            item.shift(seconds=t)
            item.end.shift(seconds=1.0/fps)
            if VERBOSE:
                print(item)
            subrip_file.append(item)
        prev_dmx_frame = dmx_frame_trimmed
        # print(cmd)
        print(30*"-")
                # print(track_list[0][j], track_list[1][j], track_list[2][j], track_list[3][j][i])
            # print(frame)
            # j = 1
            # for frame in track:
            #     print(track_list[0][i] + " " +frame, end = " ")
            #     j += 1
            # print()
    encoding="utf_8"
    subrip_file.save(srt_filename, encoding=encoding)
    # srt_file.close()

def handle_compositions(compositions):
    global START, END
    for composition in compositions:
        composition_name_dom = composition.getElementsByTagName('name')[0]
        composition_name = getText(composition_name_dom.childNodes)
        srt_filename = composition_name+OUT_EXT
        # print("SRT output filename: %s" % srt_filename)
        print("Processing composition %s" % composition_name)
        fps    = int(getText(composition.getElementsByTagName('fps')[0].childNodes))
        bpm    = int(getText(composition.getElementsByTagName('bpm')[0].childNodes))
        length = int(getText(composition.getElementsByTagName('length')[0].childNodes))
        start  = int(getText(composition.getElementsByTagName('start')[0].childNodes))
        end    = int(getText(composition.getElementsByTagName('end')[0].childNodes))
        print("Frames per second (lighting): ", fps)
        print("Beats per minute (audio):     ", bpm)
        print("Number of frames:             ", length)
        print("Start frame:                  ", start)
        print("End frame:                    ", end)
        tracks = composition.getElementsByTagName('tracks')
        if START != None:
            start = START
        if END != None:
            end = END
        handle_tracks(tracks, start, end, fps, srt_filename)
        print(30*"-")

def handle_compositions_file(compositions_file):
    compositions = compositions_file.getElementsByTagName('composition')
    handle_compositions(compositions)

def main():
    global XML_FILENAME, HUE_SAMPLING, DMX_SAMPLING, TRANSITION_TIME, START, END, VERBOSE, DEBUG

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("-x","--xml", default=XML_FILENAME, help=".xml file name for lighting events")
    parser.add_argument("-s","--start", default=START, help="starting frame")
    parser.add_argument("-e","--end", default=END, help="ending frame")
    parser.add_argument("-i","--hue_sampling", default=HUE_SAMPLING, help="sampling interval for Philips Hue events")
    parser.add_argument("-d","--dmx_sampling", default=DMX_SAMPLING, help="sampling interval for DMX events")
    parser.add_argument("-t","--transition_time", default=TRANSITION_TIME, help="transition time between Philips Hue events in tenths of seconds")

    args = parser.parse_args()

    print(args)

    VERBOSE = args.verbose
    DEBUG = args.debug
    XML_FILENAME = args.xml
    HUE_SAMPLING = float(args.hue_sampling)
    DMX_SAMPLING = float(args.dmx_sampling)
    TRANSITION_TIME = float(args.transition_time)
    if args.start!=None:
        START = int(args.start)
    if args.end!=None:
        END = int(args.end)

    # parse the Vezér composition XML file
    compositions_file = minidom.parse(XML_FILENAME)
    handle_compositions_file(compositions_file)

if __name__ == "__main__":
    main()
