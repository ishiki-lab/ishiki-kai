#!/usr/bin/env python
import pygame
from pygame.locals import *
import os
from time import sleep

print(dir(pygame))

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

os.putenv('SDL_DIRECTFB_LINUX_INPUT', '1')
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/event0')
#os.putenv('SDL_MOUSEDEV', '/devices/virtual/input/input0')

#os.environ["SDL_FBDEV"] = "/dev/fb0"
#os.environ["SDL_MOUSEDRV"] = "TSLIB"
#os.environ["SDL_MOUSEDEV"] = "/dev/input/event0"

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

while True:
    # Scan touchscreen events
    for event in pygame.event.get():
        print(dir(event))
        print('type:', event.type)
        if(event.type == MOUSEBUTTONDOWN or event.type == MOUSEMOTION):
        #if(event.type == MOUSEMOTION):
            pass
            draw_background()
            pos = pygame.mouse.get_pos()
            print pos
            pygame.draw.circle(lcd, RED, (pos[0],pos[1]), 50)
            pygame.display.update()
        elif(event.type is MOUSEBUTTONUP):
            pass
            #pos = pygame.mouse.get_pos()
            #print pos
            #Find which quarter of the screen we're in
            #x,y = pos
            #if y < 120:
            #    if x < 160:
            #        GPIO.output(17, False)
            #    else:
            #        GPIO.output(4, False)
            #else:
            #    if x < 160:
            #        GPIO.output(17, True)
            #    else:
            #        GPIO.output(4, True)
    sleep(0.1)    
