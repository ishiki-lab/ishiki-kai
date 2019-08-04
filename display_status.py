#!/usr/bin/env python3

# this will catch exceptions and send them to sentry
import os
import json
import sentry_sdk
import socket
from sentry_sdk import capture_message, capture_exception

SENTRY_URL = os.environ.get("SENTRY_URL")

if SENTRY_URL is not None:
    print("Exceptions in Sentry")
    sentry_sdk.init(SENTRY_URL)

import time

from time import sleep, tzname, daylight, gmtime, strftime, localtime
from os.path import exists, join
from os import listdir, putenv, getenv, environ
from os import name as osname
from random import random
import socket
from socket import gethostname
from datetime import datetime as dt
from signal import alarm, signal, SIGALRM, SIGKILL
import netifaces
# from apscheduler.schedulers.background import BackgroundScheduler
import schedule
# import evdev
# from evdev import ecodes
from scipy.interpolate import interp1d
import pygame
from pygame.locals import *

import find_hue


from phue import Bridge, PhueRegistrationException, PhueRequestTimeout


HUE_BRIDGE = None
DELAY = 60 # delay for updating the screen information in seconds
FONT_SIZE = 45
IMAGES_PATH = '/media/usb/Images'

# DIM = None # screen framebuffer dimensions
# SCREEN_WIDTH = None
# SCREEN_HEIGHT = None

time.sleep(0.75)
pygame.display.init()
pygame.font.init()
time.sleep(0.75)
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h
DIM = (SCREEN_WIDTH, SCREEN_HEIGHT)

print(DIM)

putenv('SDL_VIDEODRIVER', 'fbcon')
putenv('SDL_FBDEV', '/dev/fb0')
putenv('SDL_MOUSEDRV', 'TSLIB')
putenv('SDL_MOUSEDEV', '/dev/input/event0')

WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
BLUE       = (  0,   0, 255)
GREEN      = (  0, 255,   0)
RED        = (255,   0,   0)
ORANGE     = (255, 165,   0)
GREY       = (128, 128, 128)
YELLOW     = (255, 255,   0)
PINK       = (255, 192, 203)
LBLUE      = (191, 238, 244)


lcd = None

def get_ipaddresses(adapters):
    addresses = []
    for adapter in adapters:
        if adapter in ('eth0','wlan0'):
            mac_addr = netifaces.ifaddresses(adapter)[netifaces.AF_LINK][0]['addr']
            try:
                ip_addr = netifaces.ifaddresses(adapter)[netifaces.AF_INET][0]['addr']
            except:
                ip_addr = 'disconnected'
            #print(mac_addr, ip_addr)
            addresses.append((adapter,mac_addr,ip_addr))
    return(addresses)


def print_ipaddresses():
    adapters = netifaces.interfaces()
    addresses = get_ipaddresses(adapters)
    print(addresses)


def get_imagenames(path):
    items = listdir(path)
    images_list = []
    for names in items:
       if names.endswith(".jpg") and not names.startswith("._"):
           images_list.append(names)
    return(images_list)


def draw_time():
    try:
        draw_time_wrapped()
    except Exception as e:
        # Alternatively the argument can be omitted
        if SENTRY_URL is not None:
            capture_exception(e)
        raise(e)


def draw_time_wrapped():
   global FONT_SIZE
   global lcd
   font_regular = pygame.font.Font(None, FONT_SIZE)
   #current_dt = dt.now()
   current_dt = strftime("%Y-%m-%d %H:%M:%S %Z", localtime())
   #print(current_dt)
   pygame.draw.rect(lcd, BLACK, pygame.Rect(0, SCREEN_HEIGHT -int(FONT_SIZE*1.2), SCREEN_WIDTH, SCREEN_HEIGHT))
   show_text(current_dt, font_regular, WHITE, [SCREEN_WIDTH/2, SCREEN_HEIGHT - FONT_SIZE/2])



def show_text(text, font, colour, coordinates):
    text_surface = font.render('%s' % text, True,BLACK)
    rect = text_surface.get_rect(center=(coordinates[0]+2,coordinates[1]+2))
    lcd.blit(text_surface, rect)
    text_surface = font.render('%s' % text, True, colour)
    rect = text_surface.get_rect(center=coordinates)
    lcd.blit(text_surface, rect)
    pygame.display.update()


def draw_hue():
    try:
        draw_hue_wrapped()
    except Exception as e:
        # Alternatively the argument can be omitted
        if SENTRY_URL is not None:
            capture_exception(e)
        raise(e)

def get_hue_address():
    return find_hue.hue_ip()


def draw_hue_wrapped():

    global HUE_BRIDGE
    text_x_offset = int(SCREEN_HEIGHT / 4)
    row = 5
    font_regular = pygame.font.Font(None, FONT_SIZE)
    hue_address = get_hue_address()
    try:
        if HUE_BRIDGE is None:
            HUE_BRIDGE = Bridge(hue_address, config_file_path="/media/usb/python_hue")
        lights = HUE_BRIDGE.lights
        for l in lights:
            show_text("%s OK" % l.name, font_regular, WHITE, [SCREEN_WIDTH / 2, text_x_offset + FONT_SIZE * (row)])
            row += 1
    except PhueRegistrationException as e:
        print("PhueRegistrationException")
        HUE_BRIDGE = None
        msg = "Press Hue button to connect on %s" % hue_address
        show_text(msg, font_regular, WHITE, [SCREEN_WIDTH / 2, text_x_offset + FONT_SIZE * (row)])
    except PhueRequestTimeout as e:
        print("PhueRequestTimeout Ignore the extra connection trace")
        HUE_BRIDGE = None
        msg = "Press Hue button to connect on %s" % hue_address
        show_text(msg, font_regular, WHITE, [SCREEN_WIDTH / 2, text_x_offset + FONT_SIZE * (row)])
    except OSError as e:
        HUE_BRIDGE = None
        msg = "Failed to connect to Hue"
        show_text(msg, font_regular, WHITE, [SCREEN_WIDTH / 2, text_x_offset + FONT_SIZE * (row)])
        



def draw_screen():
    try:
        draw_screen_wrapped()
    except Exception as e:
        # Alternatively the argument can be omitted
        if SENTRY_URL is not None:
            capture_exception(e)
        raise(e)


def draw_screen_wrapped():

    global FONT_SIZE
    global lcd
    lcd.fill((0,0,0))
    pygame.display.update()
    images = get_imagenames(IMAGES_PATH)
    font_regular = pygame.font.Font(None, FONT_SIZE)
    font_big = pygame.font.Font(None, int(FONT_SIZE*1.5))
    #print(images)
    logo_name = join(IMAGES_PATH,'logo.png')

    if len(images)>0:
        image_number = int(random()*len(images))
        image_name = join(IMAGES_PATH,images[image_number])
        if exists(image_name):
            image = pygame.image.load(image_name)
            resized_image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            lcd.blit(resized_image, (0, 0))
    if exists(logo_name):
        image = pygame.image.load(logo_name)
        resized_image = pygame.transform.scale(image, (SCREEN_WIDTH, int(SCREEN_HEIGHT/5)))
        lcd.blit(resized_image, (0,0))
    row = 1
    text_x_offset = int(SCREEN_HEIGHT/4)
    # get and print hostname
    hostname = gethostname()
    show_text(hostname, font_big, WHITE, [SCREEN_WIDTH/2,text_x_offset + FONT_SIZE*(row)])
    row += 1
    # get timezone / location information
    timezone = 'time zone: %s' % tzname[0]
    show_text(timezone, font_regular, WHITE, [SCREEN_WIDTH/2,text_x_offset + FONT_SIZE*(row)])
    row += 1
    # get mac and ip addresses of network interfaces
    adapters = netifaces.interfaces()
    addresses = get_ipaddresses(adapters)
    #print(addresses)
    for i in range(len(addresses)):
        #print(addresses[i])
        address = '%s - %s - %s' % addresses[i]
        show_text(address, font_regular, WHITE, [SCREEN_WIDTH/2,text_x_offset + FONT_SIZE*(row)])
        row += 1
    draw_hue_wrapped()


class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm

    signal(SIGALRM, alarm_handler)
    alarm(3)
    try:
        print("alarm")
        pygame.init()
        DISPLAYSURFACE = pygame.display.set_mode((DISPLAYWIDTH, DISPLAYHEIGHT)) 
        alarm(0)
    except Alarm:
        raise KeyboardInterrupt

    pygame.display.set_caption('Drawing')


def main():
    global DELAY
    global lcd

    signal(SIGALRM, alarm_handler)
    alarm(3)

    try:
        lcd = pygame.display.set_mode(DIM)
        alarm(0)
    except Alarm:
        raise KeyboardInterrupt

    #pygame.init()
    pygame.mouse.set_visible(False)
    #lcd = pygame.display.set_mode(DIM)
    lcd.fill((0,0,0))
    pygame.display.flip()
    pygame.display.update()
 
    draw_screen()

    schedule.every(20).seconds.do(draw_screen)
    schedule.every(1).seconds.do(draw_time)
    # schedule.every(10).seconds.do(draw_hue)

    # swapped apscheduler for schedule as it was stuck in a lock - I think during db access
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(draw_screen, 'interval', seconds=DELAY)
    # scheduler.add_job(draw_time, 'interval', seconds=1)
    # scheduler.add_job(draw_hue, 'interval', seconds=10)
    # scheduler.start()
    # #
    # print("scheduler: %s" % scheduler.get_jobs())

    print('Press Ctrl+{0} to exit'.format('Break' if osname == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(0.5)
            schedule.run_pending()
    except (KeyboardInterrupt, SystemExit):
        print("goodbye")
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        # scheduler.shutdown()

if __name__ == '__main__': 
    main()
