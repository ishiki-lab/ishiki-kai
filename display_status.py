#!/usr/bin/env python3

import netifaces
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import os, time
import evdev
from evdev import ecodes
from scipy.interpolate import interp1d
import pygame
from pygame.locals import *
import os
from time import sleep

DELAY = 5 # delay for updating the screen in seconds
FONT_SIZE = 30

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

os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/event0')

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

def draw_screen():
    global FONT_SIZE
    global lcd
    lcd.fill((0,0,0))
    pygame.display.update()
    font_big = pygame.font.Font(None, FONT_SIZE)
    adapters = netifaces.interfaces()
    addresses = get_ipaddresses(adapters)
    print(addresses)
    for i in range(len(addresses)):
        print(addresses[i])
        text_surface = font_big.render('%s - %s - %s' % addresses[i], True, WHITE)
        rect = text_surface.get_rect(center=[480/2,50+320/(len(addresses)+1)*i])
        lcd.blit(text_surface, rect)
        pygame.display.update()

def main():
    global DELAY
    global lcd

    pygame.init()
    pygame.mouse.set_visible(False)
    lcd = pygame.display.set_mode(DIM)
    lcd.fill((0,0,0))
    pygame.display.update()
 
    draw_screen()

    scheduler = BackgroundScheduler()
    #scheduler.add_job(print_ipaddresses, 'interval', seconds=DELAY)
    scheduler.add_job(draw_screen, 'interval', seconds=DELAY)
    scheduler.start()

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()

if __name__ == '__main__': 
    main()
