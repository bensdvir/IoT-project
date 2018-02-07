#!/bin/sh
a=10

until [ $a -lt 10 ]
do
   raspistill -o picture.jpg
   echo 'captured'
   result=$(/opt/vc/bin/vcgencmd measure_temp)
   python mqtt_publisher.py $result
   python sendPicPhp.py
done
