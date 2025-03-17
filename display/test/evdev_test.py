#!/usr/bin/env python

import evdev
from evdev import ecodes
from scipy.interpolate import interp1d
import pygame
from pygame.locals import *
import os
from time import sleep

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
#os.putenv('SDL_MOUSEDEV', '/devices/virtual/input/input0')

pygame.init()
pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode(DIM)
lcd.fill((0,0,0))
pygame.display.update()

font_big = pygame.font.Font(None, 50)

touch_buttons = {'1':(DIM[0]/3,DIM[1]/3), '2':(DIM[0]/3*2,DIM[1]/3), '3':(DIM[0]/3,DIM[1]/3*2), '4':(DIM[0]/3*2,DIM[1]/3*2)}

def draw_background():
    lcd.fill((0,0,0))
    pygame.display.update()
    for k,v in touch_buttons.items():
        text_surface = font_big.render('%s'%k, True, WHITE)
        rect = text_surface.get_rect(center=v)
        lcd.blit(text_surface, rect)
        pygame.display.update()

draw_background()


x = 0
y = 0

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
#print(devices)

for device in devices:
   print(device.path, device.name, device.phys)

device = evdev.InputDevice('/dev/input/event0')
print(device)
capabilities = device.capabilities(verbose=True, absinfo=True)
#print(capabilities[('EV_ABS', 3L)][0][1][1])

'''
{('EV_KEY', 1L): [('BTN_TOUCH', 330L)],
 ('EV_ABS', 3L): [(('ABS_X', 0L), AbsInfo(value=3401, min=110, max=3930, fuzz=0, flat=0, resolution=0)),
                  (('ABS_Y', 1L), AbsInfo(value=1894, min=170, max=3917, fuzz=0, flat=0, resolution=0)),
                  (('ABS_PRESSURE', 24L), AbsInfo(value=1, min=0, max=1, fuzz=0, flat=0, resolution=0))],
 ('EV_SYN', 0L): [('SYN_REPORT', 0L),
                  ('SYN_CONFIG', 1L),
                  ('SYN_DROPPED', 3L)]}
'''

fbX = 480
fbY = 320

#minX = 110
#minY = 170
#maxX = 3930
#maxY = 3917

minX = capabilities[('EV_ABS', 3L)][0][1][1]
minY = capabilities[('EV_ABS', 3L)][1][1][1]
maxX = capabilities[('EV_ABS', 3L)][0][1][2]
maxY = capabilities[('EV_ABS', 3L)][1][1][2]

print(minX,maxX,minY,maxY)

X = interp1d([minX,maxX],[0,fbX])
Y = interp1d([minY,maxY],[0,fbY])

for event in device.read_loop():
    if event.type == ecodes.EV_ABS:
        #print(evdev.categorize(event))
        #print(dir(event))
        #print(event.type, ecodes.ABS_X, event.value, event.code, event.sec, event.timestamp, event.usec )
        if event.code == ecodes.ABS_X:
            try:
                x = int(X(event.value))
            except:
                pass
        if event.code == ecodes.ABS_Y:
            try:
                y = int(Y(event.value))
            except:
                pass
        #print(x,y)
        draw_background()
        pygame.draw.circle(lcd, RED, (x,y), 40)
        pygame.display.update()

'''
ABS_X
ABS_Y
BTN_TOUCH
ABS_PRESSURE
SYN_REPORT
'''
