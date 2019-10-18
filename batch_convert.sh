# e.g. path: /Volumes/GoogleDrive/Shared\ drives/LushRooms/Documents/Vezer/2019-10-11/190816\ master/xml/

find /Volumes/GoogleDrive/Shared\ drives/LushRooms/Documents/Vezer/2019-10-11/190816\ master/xml -name "*.xml" > files.txt

while IFS="" read -r f || [ -n "$f" ]
do
  printf 'Processing: %s\n' "$f"
  python3 lrpi_vezer2srt.py -x "$f"
done < files.txt

rm -f files.txt