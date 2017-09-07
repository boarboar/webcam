#!/bin/bash
COPY_TO_FN=outcam.$(date +"%Y%m%d%H%M%S").jpg
cp /var/www/html/camera/outcam.jpg /var/www/html/camera/$COPY_TO_FN
echo -e 'Content-Type: application/json\n\n{"RC" :'$?',\n"FN" :"'$COPY_TO_FN'"}'