#!/usr/bin/env python

# lushroom-rclone
# traverse track folders and update content.json file with folder content

import os, commands
from os.path import abspath, join
from os import system, chdir, walk
from shutil import copyfile

MEDIA_DIR = "/media/usb/tracks"
RCLONE_CMD = "rclone -v --config /media/usb/rclone_lushrooms.conf lsjson lushrooms:Tracks/%s"
RCLONE_COPY_CMD = "rclone -v --config /media/usb/rclone_lushrooms.conf copy %s lushrooms:Tracks/%s"
FILENAME = "content.json"

debug = True

def json_folder(target_dir):
    if target_dir == ".":
        cmd = RCLONE_CMD % ""
    else:
        cmd = RCLONE_CMD % target_dir
    print(cmd)
    json = commands.getoutput(cmd)
    #outfilename = join(abspath(target_dir),FILENAME)
    outfilename = FILENAME
    if debug: print(outfilename, json)
    filename = open(outfilename,'w')
    filename.write(json)
    filename.close()
    if target_dir == ".":
        cmd = RCLONE_COPY_CMD % (outfilename, "")
    else:
        cmd = RCLONE_COPY_CMD % (outfilename, join(target_dir,""))
        copyfile(outfilename, join(target_dir,FILENAME))
    print(cmd)
    system(cmd)

def main():
    chdir(MEDIA_DIR)
    for root, dirs, files in walk(".", topdown = False):
        for name in dirs:
            print(join(root[2:],name))
            json_folder(join(root[2:],name))
    json_folder(".")

if __name__ == "__main__":
    main()
