#!/bin/bash
##########################
# MQTT Shell Listen & Exec
host=$2;port=$3;user=$4;pwd=$5;
topic_in="webcam"
topic_out="webcam_resp"
#clean="output input cmds";p="backpipe";pid=$(cat pidfile)
p="backpipe";pid=$(cat pidfile)

ctrl_c() {
  echo "Cleaning up..."
  #rm -f $p;rm "$clean";kill $pid 2>/dev/null
  rm -f $p;kill $pid 2>/dev/null
  if [[ "$?" -eq "0" ]];
  then
     echo "Exit success";exit 0
  else
     exit 1
  fi
}

listen(){
([ ! -p "$p" ]) && mkfifo $p
(mosquitto_sub -h $host -p $port -u $user -P $pwd -t $topic_in >$p 2>/dev/null) &
echo "$!" > pidfile
while read line <$p
do
#  echo $line > cmds
#  if grep -q "quit" cmds; then
#    (rm -f $p;rm $clean;kill $pid) 2>/dev/null
#    break
#  else
#    (bash cmds | tee out) && mosquitto_pub -h $host -t output -f out;>out
#  fi
  echo CMD: $line 
  if [[ "$line" -eq "SHOT" ]]; then
    #echo "DO SHOT"
	source ./process_cam.sh 2>&1
	mosquitto_pub -h $host -p $port -t $topic_out -m "SUCC" -u $user -P $pwd
  fi
done
}

usage(){
echo "    Mqtt-Exec Listener Via Bash"
echo "  Usage: -l <server> <port> <user> <pwd> <topic>" 
echo "  Subscripe to topic \"output\", publish to topic \"input\""
}

case "$1" in
-l|--listen)
trap ctrl_c INT
listen
;;
*)
usage
exit 1
;;
esac