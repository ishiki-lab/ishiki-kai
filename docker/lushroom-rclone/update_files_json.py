#!/usr/bin/env python

import os, commands
from os.path import abspath, join
from os import system, chdir, walk

MEDIA_DIR = "/media/usb/tracks"
RCLONE_CMD = "rclone lsjson %s"
RCLONE_COPY_CMD = "rclone copy %s lushrooms:Tracks/%s"
FILENAME = "content.json"

debug = False

def json_folder(target_dir):
    cmd = RCLONE_CMD % abspath(target_dir)
    print(cmd)
    json = commands.getoutput(cmd)
    outfilename = join(abspath(target_dir),FILENAME)
    if debug: print(outfilename, json)
    filename = open(outfilename,'w')
    filename.write(json)
    filename.close()
    if target_dir == ".":
        cmd = RCLONE_COPY_CMD % (outfilename, "")
    else:
        cmd = RCLONE_COPY_CMD % (outfilename, join(target_dir,""))
    print(cmd)
    system(cmd)

def main():
    chdir(MEDIA_DIR)
    json_folder(".")
    for root, dirs, files in walk(".", topdown = False):
        for name in dirs:
            json_folder(name)

if __name__ == "__main__":
    main()
