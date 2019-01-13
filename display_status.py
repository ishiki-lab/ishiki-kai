#!/usr/bin/env python3

import netifaces
from apscheduler.schedulers.background import BackgroundScheduler
import os, time
import evdev
from evdev import ecodes
from scipy.interpolate import interp1d
import pygame
from pygame.locals import *
from time import sleep, tzname, daylight, gmtime, strftime
from os.path import exists, join
from os import listdir, putenv, getenv, environ
from os import name as osname
from random import random
from socket import gethostname
from datetime import datetime as dt
from signal import alarm, signal, SIGALRM, SIGKILL

DELAY = 60 # delay for updating the screen information in seconds
FONT_SIZE = 30
IMAGES_PATH = '/media/usb/Images'

DIM = [480,320] # screen framebuffer dimensions
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

putenv('SDL_VIDEODRIVER', 'fbcon')
putenv('SDL_FBDEV', '/dev/fb0')
putenv('SDL_MOUSEDRV', 'TSLIB')
putenv('SDL_MOUSEDEV', '/dev/input/event0')

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
       if names.endswith(".jpg"):
           images_list.append(names)
    return(images_list)

def draw_time():
   global FONT_SIZE
   global lcd
   font_regular = pygame.font.Font(None, FONT_SIZE)
   #current_dt = dt.now()
   current_dt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
   #print(current_dt)
   pygame.draw.rect(lcd, BLACK, pygame.Rect(0,320-int(FONT_SIZE*1.2),480,320))
   show_text(current_dt, font_regular, WHITE, [480/2,320 - FONT_SIZE/2])

def show_text(text, font, colour, coordinates):
    text_surface = font.render('%s' % text, True,BLACK)
    rect = text_surface.get_rect(center=(coordinates[0]+2,coordinates[1]+2))
    lcd.blit(text_surface, rect)
    text_surface = font.render('%s' % text, True, colour)
    rect = text_surface.get_rect(center=coordinates)
    lcd.blit(text_surface, rect)
    pygame.display.update()

def draw_screen():
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
            lcd.blit(image, (0,0))
    if exists(logo_name):
        image = pygame.image.load(logo_name)
        lcd.blit(image, (0,0))
    row = 1
    # get and print hostname
    hostname = gethostname()
    show_text(hostname, font_big,WHITE, [480/2,80+FONT_SIZE*(row)])
    row += 1
    # get timezone / location information
    timezone = 'time zone: %s' % tzname[0]
    show_text(timezone, font_regular, WHITE, [480/2,80+FONT_SIZE*(row)])
    row += 1
    # get mac and ip addresses of network interfaces
    adapters = netifaces.interfaces()
    addresses = get_ipaddresses(adapters)
    #print(addresses)
    for i in range(len(addresses)):
        #print(addresses[i])
        address = '%s - %s - %s' % addresses[i]
        show_text(address, font_regular, WHITE, [480/2,80+FONT_SIZE*(row+i)])


class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm

    signal(SIGALRM, alarm_handler)
    alarm(3)
    try:
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
        pygame.init()
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

    scheduler = BackgroundScheduler()
    #scheduler.add_job(print_ipaddresses, 'interval', seconds=DELAY)
    scheduler.add_job(draw_screen, 'interval', seconds=DELAY)
    scheduler.add_job(draw_time, 'interval', seconds=1)
    scheduler.start()

    print('Press Ctrl+{0} to exit'.format('Break' if osname == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()

if __name__ == '__main__': 
    main()
