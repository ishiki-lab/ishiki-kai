#!/usr/bin/env python

import pygame
import os
from time import sleep

DELAY = .75

os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
sleep(DELAY)

print("pygame.init")
pygame.init()
sleep(DELAY)

print("pygame.display")
lcd = pygame.display.set_mode((480, 320))
sleep(DELAY)
print("pygame.mouse")
pygame.mouse.set_visible(False)
sleep(DELAY)

print("lcd.fill red")
lcd.fill((255,0,0))
print("display.update")
pygame.display.update()
sleep(DELAY)

print("lcd.fill green")
lcd.fill((0,255,0))
print("display.update")
pygame.display.update()
sleep(DELAY)

print("lcd.fill blue")
lcd.fill((0,0,255))
print("display.update")
pygame.display.update()
sleep(DELAY)

print("lcd.fill yellow")
lcd.fill((255,255,0))
print("display.update")
pygame.display.update()
sleep(DELAY)

print("lcd.fill magenta")
lcd.fill((255,0,255))
print("display.update")
pygame.display.update()
sleep(DELAY)

print("lcd.fill cyan")
lcd.fill((0,255,255))
print("display.update")
pygame.display.update()
sleep(DELAY)

print("lcd.fill white")
lcd.fill((255,255,255))
print("display.update")
pygame.display.update()
sleep(DELAY*3)

print("lcd.fill black")
lcd.fill((0,0,0))
print("display.update")
pygame.display.update()
sleep(DELAY)
