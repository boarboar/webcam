#!/bin/bash
echo $1 > last.txt

timestamp=`stat -c %y $1`
convert $1 -fill white -pointsize 24 -draw "text 15,20 '${timestamp:0:19}'" /mnt/dav/outcam.tmp

cp /mnt/dav/outcam_2.jpg /mnt/dav/outcam_3.jpg
cp /mnt/dav/outcam_1.jpg /mnt/dav/outcam_2.jpg
cp /mnt/dav/outcam.jpg /mnt/dav/outcam_1.jpg
cp /mnt/dav/outcam.tmp /mnt/dav/outcam.jpg
 

