#!/usr/bin/env python

import pygame
import os
import pygameui as ui
import logging

log_format = '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s'
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/event0')

MARGIN = 20

class PiTft(ui.Scene):
    def __init__(self):
        ui.Scene.__init__(self)

        self.one_button = ui.Button(ui.Rect(MARGIN, MARGIN, 130, 90), '1')
        self.one_button.on_clicked.connect(self.print_button)
        self.add_child(self.one_button)

        self.two_button = ui.Button(ui.Rect(170, MARGIN, 130, 90), '2')
        self.two_button.on_clicked.connect(self.print_button)
        self.add_child(self.two_button)

        self.three_button = ui.Button(ui.Rect(MARGIN, 130, 130, 90), '3')
        self.three_button.on_clicked.connect(self.print_button)
        self.add_child(self.three_button)

        self.four_button = ui.Button(ui.Rect(170, 130, 130, 90), '4')
        self.four_button.on_clicked.connect(self.print_button)
        self.add_child(self.four_button)

    def print_button(self, btn, mbtn):
        logger.info(btn.text)
        
        if btn.text == '1':
            print('Button 1')
        elif btn.text == '2':
            print('Button 2')
        elif btn.text == '3':
            print('Button 3')
        elif btn.text == '4':
            print('Button 4')

ui.init('Raspberry Pi UI', (480, 320))
pygame.mouse.set_visible(False)
ui.scene.push(PiTft())
ui.run()


