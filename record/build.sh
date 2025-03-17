#!/bin/sh

pyinstaller --add-data "/Users/francesco.anselmo/Documents/Code/Python/venv/py39/lib/python3.9/site-packages/pyfiglet/fonts:./pyfiglet/fonts" --clean -c -F -n lrpi_vezer2srt_macos lrpi_vezer2srt.py
