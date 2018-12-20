#!/usr/bin/env python3

from phue import Bridge
from random import random
from time import sleep, time, perf_counter
from pysrt import SubRipFile, SubRipItem, SubRipTime
from pysrt import open as srtopen
from threading import Timer
from datetime import datetime, timedelta
from pynput import keyboard
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
import vlc
import argparse
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_dmx import BrickletDMX
from tf_device_ids import deviceIdentifiersList
from numpy import array, ones

HOST = "127.0.0.1"
PORT = 4223

DEBUG = False
VERBOSE = True

MAX_BRIGHTNESS = 200
SRT_FILENAME = "Surround_Test_Audio.srt"
AUDIO_FILENAME = "Surround_Test_Audio.m4a"
HUE_IP_ADDRESS = "10.0.0.2"
TICK_TIME = 0.1 # seconds
PLAY_HUE = True
PLAY_AUDIO = True
PLAY_DMX = True
# SLEEP_TIME = 0.1 # seconds
# TRANSITION_TIME = 10 # milliseconds

subs = []
player = None
bridge = None
dmx = None
scheduler = None
last_played = 0
tfIDs = []
tfConnect = True
ipcon = IPConnection()
deviceIDs = [i[0] for i in deviceIdentifiersList]

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

def find_subtitle(subtitle, from_t, to_t, lo=0):
    i = lo
    while (i < len(subtitle)):
        # print(subtitle[i])
        if (subtitle[i].start >= to_t):
            break
        if (subtitle[i].start <= from_t) & (to_t  <= subtitle[i].end):
            # print(subtitle[i].start, from_t, to_t)
            return subtitle[i].text, i
        i += 1
    return "", i

def end_callback(event):
    print('End of media stream (event %s)' % event.type)
    exit(0)

def trigger_light(subs):
    # print(perf_counter(), subs)
    commands = str(subs).split(";")
    global bridge, dmx, MAX_BRIGHTNESS, DEBUG
    for command in commands:
        try:
            # print(command)
            scope,items = command[0:len(command)-1].split("(")
            # print(scope,items)
            if scope[0:3] == "HUE":
                l = int(scope[3:])
                hue, sat, bri, TRANSITION_TIME = items.split(',')
                # print(perf_counter(), l, items, hue, sat, bri, TRANSITION_TIME)
                bri = int((float(bri)/255.0)*int(MAX_BRIGHTNESS))
                # print(bri)
                cmd =  {'transitiontime' : int(TRANSITION_TIME), 'on' : True, 'bri' : int(bri), 'sat' : int(sat), 'hue' : int(hue)}
                if DEBUG:
                    print("Trigger HUE",l,cmd)
                if PLAY_HUE:
                    bridge.set_light(l, cmd)
            if scope[0:3] == "DMX":
                l = int(scope[3:])
                channels = int(int(MAX_BRIGHTNESS)/255.0*(array(items.split(",")).astype(int)))
                # channels = array(map(lambda i: int(MAX_BRIGHTNESS)*i, channels))
                if DEBUG:
                    print("Trigger DMX:", l, channels)
                if PLAY_DMX:
                    dmx.write_frame(channels)
        except:
            pass
    print(30*'-')

def tick():
    global subs
    global player
    global last_played
    global TICK_TIME, DEBUG
    # print(subs[0])
    t = perf_counter()
    # ts = str(timedelta(seconds=t)).replace('.',',')
    # tsd = str(timedelta(seconds=t+10*TICK_TIME)).replace('.',',')
    ts = SubRipTime(seconds = t)
    tsd = SubRipTime(seconds = t+1*TICK_TIME)
    # print(dir(player))
    pp = player.get_position()
    ptms = player.get_time()/1000.0
    pt = SubRipTime(seconds=(player.get_time()/1000.0))
    ptd = SubRipTime(seconds=(player.get_time()/1000.0+1*TICK_TIME))
    if DEBUG:
        print('Time: %s | %s | %s - %s | %s - %s | %s | %s' % (datetime.now(),t,ts,tsd,pt,ptd,pp,ptms))
    # sub, i = find_subtitle(subs, ts, tsd)
    sub, i = find_subtitle(subs, pt, ptd)
    # hours, minutes, seconds, milliseconds = time_convert(sub.start)
    # t = seconds + minutes*60 + hours*60*60 + milliseconds/1000.0
    if sub!="" and i > last_played:
        print(i, "Light event:", sub)
        # print("Trigger light event %s" % i)
        trigger_light(sub)
        last_played=i

def time_convert(t):
    block, milliseconds = str(t).split(",")
    hours, minutes, seconds = block.split(":")
    return(int(hours),int(minutes),int(seconds), int(milliseconds))

class ExitException(Exception):
    def __init__(self, key):
        global scheduler, player, ipcon
        scheduler.shutdown()
        player.stop()
        if tfConnect:
            ipcon.disconnect()
        exit(0)

def on_release(key):
    # print(key.char)
    global scheduler, player
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        raise ExitException(key)
    elif key == keyboard.KeyCode.from_char('p'):
        print("Pausing ...")
        scheduler.pause()
        player.pause()
    elif key == keyboard.KeyCode.from_char('r'):
        print("Resuming ...")
        scheduler.resume()
        player.play()

def main():
    global subs, player, bridge, scheduler, ipcon, dmx
    global SRT_FILENAME, AUDIO_FILENAME, MAX_BRIGHTNESS, TICK_TIME, HUE_IP_ADDRESS, DEBUG, VERBOSE
    parser = argparse.ArgumentParser(description="LushRoom sound and light command-line player. \
        Press Esc to exit, P to pause and R to resume.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-s","--srt", default=SRT_FILENAME, help=".srt file name for lighting events")
    parser.add_argument("-a","--audio", default=AUDIO_FILENAME, help="audio file for sound stream")
    parser.add_argument("-b","--brightness", default=MAX_BRIGHTNESS, help="maximum brightness")
    parser.add_argument("-t","--time", default=TICK_TIME, help="time between events")
    parser.add_argument("--hue", default=HUE_IP_ADDRESS, help="Philips Hue bridge IP address")

    args = parser.parse_args()

    MAX_BRIGHTNESS = int(args.brightness)
    SRT_FILENAME = args.srt
    AUDIO_FILENAME = args.audio
    TICK_TIME = float(args.time)
    HUE_IP_ADDRESS = args.hue
    VERBOSE = args.verbose
    DEBUG = args.debug

    if DEBUG:
        print(args)

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
                        dmx.write_frame([255,255])
                        sleep(1)
                        channels = int((int(MAX_BRIGHTNESS)/255.0)*ones(512)*255)
                        dmx.write_frame(channels)
                    dmxcount += 1

    if PLAY_AUDIO:
        player = vlc.MediaPlayer(AUDIO_FILENAME)
        event_manager = player.event_manager()
        event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, end_callback)

    if PLAY_HUE:
        # b = Bridge('lushroom-hue.local')
        bridge = Bridge(HUE_IP_ADDRESS)
        # If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single time)
        bridge.connect()
        # Get the bridge state (This returns the full dictionary that you can explore)
        bridge.get_api()
        lights = bridge.lights
        # Print light names
        for l in lights:
            print(l.name)
            #print(dir(l))
        # Set brightness of each light to 10
        for l in lights:
            l.brightness = 1

        # Get a dictionary with the light name as the key
        light_names = bridge.get_light_objects('name')
        print("Light names:", light_names)

    subs = srtopen(SRT_FILENAME)

    print("Number of lighting events",len(subs))


    scheduler = BackgroundScheduler()
    scheduler.add_job(tick, 'interval', seconds=TICK_TIME)
    if PLAY_AUDIO:
        player.play()
    scheduler.start(paused=False)

    with keyboard.Listener(
        # on_press=on_press,
        on_release=on_release, suppress=False) as listener:
        try:
            listener.join()
        except ExitException as e:
            print("Exiting ...")

if __name__ == "__main__":
    main()
