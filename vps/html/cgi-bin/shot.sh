#!/bin/bash
mosquitto_pub -h localhost -p 51062 -t 'webcam' -m "SHOT" -u webcam -P webcam
echo -e 'Content-Type: application/json\n\n{"RC" :'$?'}'
