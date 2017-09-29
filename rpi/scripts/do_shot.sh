#!/bin/bash

#wget http://localhost:8080/?action=snapshot -O snapshot.jpg

#timestamp=`stat -c %y snapshot.jpg`
#convert snapshot.jpg -fill white -pointsize 24 -draw "text 15,20 'S ${timestamp:0:19}'" /mnt/dav/outcam.jpg

raspistill -md 4 -n -hf -vf -ae 128 -a 4 -a "NOW %Y-%m-%d %X" -o snapshot_i.jpg
cp snapshot_i.jpg /mnt/dav/outcam.jpg

