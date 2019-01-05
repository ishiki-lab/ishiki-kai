#!/usr/bin/env python

import pygame
import os
from time import sleep

button_map = {"red":(255,0,0), "green":(0,255,0), "blue":(0,0,255), "black":(0,0,0)}

DIM = [480,320]
WHITE = (255,255,255)
DELAY = .5

os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')

pygame.init()
pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode(DIM)
lcd.fill((0,0,0))
pygame.display.update()

font_big = pygame.font.Font(None, 100)

while True:
    # Scan the buttons
    for (k,v) in button_map.items():
        lcd.fill(v)
        text_surface = font_big.render('%s'%k, True, WHITE)
        rect = text_surface.get_rect(center=(DIM[0]/2,DIM[1]/2))
        lcd.blit(text_surface, rect)
        pygame.display.update()
        sleep(DELAY)
    sleep(0.1)
