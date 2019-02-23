#!/usr/bin/env python3

# import xmltodict
# import untangle
# import xml.etree.ElementTree
# import xml.etree.ElementTree as ET

from xml.dom import minidom
from os.path import join

XML_FILENAME = '/Arup/Jobs/Lush_Spa/Media_Player/Vezer/01_Comforter_Intro_Loop.xml'
OUT_EXT = ".srt"
HUE_SAMPLING = 1.0 # Sampling rate of HUE frames in seconds
DMX_SAMPLING = 0.05 # Sampling rate of DMX frames in seconds

# parse the Vezér composition xml file
compositions_file = minidom.parse(XML_FILENAME)

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def handle_track(track, start, end):
    track_doms = track.getElementsByTagName('track')
    track_dict = {}
    track_name_list = []
    track_address_list = []
    track_events_list = []
    for track_dom in track_doms:
        track_name_doms = track_dom.getElementsByTagName('name')
        for track_name_dom in track_name_doms:
            track_name = getText(track_name_dom.childNodes)
            track_name_list.append(track_name)
        track_address_doms = track_dom.getElementsByTagName('address')
        for track_address_dom in track_address_doms:
            track_address = getText(track_address_dom.childNodes)
            track_address_list.append(track_address)
        for i in range (start,10,):
            frame_no = "f%s" % i
            track_event_doms = track_dom.getElementsByTagName(frame_no)
            # print(len(track_event_doms),)
            j = 0
            for track_event_dom in track_event_doms:
                track_event = getText(track_event_dom.childNodes)
                print(frame_no, len(track_events_list), j, track_event)
                if len(track_events_list)<=j:
                    track_events_list.append([track_event])
                else:
                    track_events_list[j].append(track_event)
                j += 1

    # print(track_name_list)
    # print(track_address_list)
    # print(track_events_list)
    return([track_name_list, track_address_list, track_events_list])

def handle_tracks(tracks, start, end):
    for track in tracks:
        track_list = handle_track(track, start, end)
        print(track_list)

def handle_compositions(compositions):
    for composition in compositions:
        composition_name_dom = composition.getElementsByTagName('name')[0]
        composition_name = getText(composition_name_dom.childNodes)
        srt_filename = composition_name+OUT_EXT
        print(srt_filename)
        fps    = int(getText(composition.getElementsByTagName('fps')[0].childNodes))
        bpm    = int(getText(composition.getElementsByTagName('bpm')[0].childNodes))
        length = int(getText(composition.getElementsByTagName('length')[0].childNodes))
        start  = int(getText(composition.getElementsByTagName('start')[0].childNodes))
        end    = int(getText(composition.getElementsByTagName('end')[0].childNodes))
        print(fps,bpm,length,start,end)
        tracks = composition.getElementsByTagName('tracks')
        handle_tracks(tracks, start, end)




def handle_compositions_file(compositions_file):
    compositions = compositions_file.getElementsByTagName('composition')
    handle_compositions(compositions)

def main():
    handle_compositions_file(compositions_file)

if __name__ == "__main__":
    main()

"""
# # print(help(xmltodict.parse))
# compositions = xmltodict.parse(open(XML_FILENAME).read())
#
# # print(compositions[''])
#
# for key1, value1 in compositions.items():
#     print(key1)
#     for key2, value2 in value1.items():
#         print(key2)
#         for item in value2[1]:
#             print(item)
#     # for c in compositions:
#         # print(c)

# obj = untangle.parse(XML_FILENAME)

# print(obj['compositions'])
# print(obj.compositions)

# for composition in obj.compositions:
#     print(composition['name'])
#     print("%s" % (composition.cdata))
    # for composition in compositions:
    #     print(dir(composition))


tree = ET.parse(XML_FILENAME)
root = tree.getroot()
#
# compositions = []

# print(dir(root))
# print('Tag',root.tag)
# print('Attrib',root.attrib)
# print('Text',root.text)
# print('Keys',root.keys)
# print('Items',root.items)

# for child in root:
#     print(child.tag, child.attrib)

# for composition in root.findall('composition'):
#     print(composition.tag)
#     print(dir(composition))
#     for track in composition.findall('tracks'):
#         print(track.tag)
#         print(dir(track))
#         #print(track.findall('name'))

def navigate(node, level):
    for child in node:
        if child.tag=='composition':
            print(level*'  ', child.text)
            print(dir(child.findall('name')))
            navigate(child, level+1)
        # if child.tag=='name':
            #compositions.append()
        # print(child, child.tag, child.attrib)
        # if child.tag=='name':
        #     print(level*'  ', child.text)


navigate(root, 0)

# e = xml.etree.ElementTree.parse(XML_FILENAME).getroot()
#
# print(dir(e))

# for atype in e.findall('compositions'):
#     print(atype, dir(atype))
#     # print(atype.get('foobar'))
"""
