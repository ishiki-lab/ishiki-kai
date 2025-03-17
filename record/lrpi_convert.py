#!/usr/bin/env python

# lrpi_convert.py
# traverse track folders, converting mlp files to .mp4 and creating empty .srt
# files if they don't exist

import os, commands
from os.path import abspath, join, isdir, splitext, exists
from os import system, chdir, walk, listdir
from shutil import copyfile

#MEDIA_DIR = "/media/usb/tracks"
MEDIA_DIR = "/Volumes/usbstick/tracks"
CONVERT_CMD = "ffmpeg -i %s %s"
SRT_TOUCH_CMD = "touch %s"

debug = True

def process_folder(target_dir):
    print("\nConverting .mlp files in folder %s." % target_dir)
    files = listdir(target_dir)
    for f in files:
        fn = join(MEDIA_DIR,target_dir,f)
        if not isdir(f):
            fp, fe = splitext(fn)
            if fe.lower() == ".mlp":
                mp4_fn = fp+".mp4"
                # print(mp4_fn)
                if not exists(mp4_fn):
                    #print(fp, fe)
                    cmd_mlp = CONVERT_CMD % (fn, mp4_fn)
                    print(cmd_mlp)
                    system(cmd_mlp)
                else:
                    print("The MP4 file %s already exists." % mp4_fn)
                srt_fn = fp+".srt"
                # print(srt_fn)
                if not exists(srt_fn):
                    cmd_srt = SRT_TOUCH_CMD % srt_fn
                    print(cmd_srt)
                    system(cmd_srt)
                else:
                    print("The SRT file %s already exists." % srt_fn)
    # #outfilename = join(abspath(target_dir),FILENAME)
    # outfilename = FILENAME
    # if debug: print(outfilename, json)
    # filename = open(outfilename,'w')
    # filename.write(json)
    # filename.close()
    # if target_dir == ".":
    #     cmd = RCLONE_COPY_CMD % (outfilename, "")
    # else:
    #     cmd = RCLONE_COPY_CMD % (outfilename, join(target_dir,""))
    #     copyfile(outfilename, join(target_dir,FILENAME))
    # print(cmd)
    # system(cmd)

def main():
    chdir(MEDIA_DIR)
    for root, dirs, files in walk(".", topdown = False):
        for name in dirs:
            process_folder(name)

if __name__ == "__main__":
    main()
