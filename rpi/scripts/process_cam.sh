#!/bin/bash

#echo $1 > last.txt

cnt=0

cfile="$HOME/camera/.cnt"

if [ -e $cfile ] ; then
    cnt=$(cat $cfile)
fi

wget http://localhost:8080/?action=snapshot -O snapshot.jpg

timestamp=`stat -c %y snapshot.jpg`
convert snapshot.jpg -fill white -pointsize 24 -draw "text 15,20 '${timestamp:0:19}'" /mnt/dav/outcam.tmp

#every 30th run
if ! ((cnt % 30)); then
	cp /mnt/dav/outcam_2.jpg /mnt/dav/outcam_3.jpg
fi

#every 5th run
if ! ((cnt % 5)); then
	cp /mnt/dav/outcam_1.jpg /mnt/dav/outcam_2.jpg
fi

#every one run
cp /mnt/dav/outcam.jpg /mnt/dav/outcam_1.jpg

cp /mnt/dav/outcam.tmp /mnt/dav/outcam.jpg

# counter increase

((cnt++))

#save it output the file
echo $cnt > $cfile
 

