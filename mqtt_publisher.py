# Created by Omer Shwartz (www.omershwartz.com)
#
# This script uses device credentials to publish events to the MQTT broker residing in Google Cloud.
# Using this code a device can 'talk' to the server.
#
# This file may contain portions of cloudiot_mqtt_example.py licensed to Google
# under the Apache License, Version 2.0. The original version can be found in
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/iot/api-client/mqtt_example/cloudiot_mqtt_example.py
#
############################################################

from google.cloud import vision
import datetime
import time
import os, sys
from oauth2client.client import GoogleCredentials

import jwt
import paho.mqtt.client as mqtt
from PIL import Image
import io
import os

import base64
import datetime
import json

import googleapiclient
import jwt
import requests
from google.oauth2 import service_account
from googleapiclient import discovery

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

import sys
from sense_hat import SenseHat
import time
import pygame  # See http://www.pygame.org/docs
from pygame.locals import *
x= sys.argv[1]
y=x[5:]
z=y[:-2]
print "cpu: " ,z
sense = SenseHat()
sense.clear()  # Blank the LED matrix
temp = sense.get_temperature()
FahrenheitCpu = 9.0/5.0 * float(z) + 32
FahrenheitRoom = 9.0/5.0 * temp + 32
temp_calibrated = FahrenheitRoom - ((FahrenheitCpu - FahrenheitRoom)/5.466)
CelsiusRoomFinal = (temp_calibrated - 32) * 5.0/9.0
print ("The Temprature is:" ,CelsiusRoomFinal)
sense.clear()

project_id = 'moshe-and-yuval-project'  # Enter your project ID here
registry_id = 'yuval-and-moshe-registry'  # Enter your Registry ID here
device_id = 'raspberry-pi12'  # Enter your Device ID here
ca_certs = 'roots.pem'  # The location of the Google Internet Authority certificate, can be downloaded from https://pki.google.com/roots.pem
private_key_file = 'rsa_private.pem'  # The location of the private key associated to this device

# Unless you know what you are doing, the following values should not be changed
cloud_region = 'us-central1'
algorithm = 'RS256'
mqtt_bridge_hostname = 'mqtt.googleapis.com'
mqtt_bridge_port = 443  # port 8883 is blocked in BGU network
mqtt_topic = '/devices/{}/{}'.format(device_id, 'events')  # Published messages go to the 'events' topic that is bridged to pubsub by Google
###

def compressMe(file, verbose=False):
	filepath = os.path.join(os.getcwd(), file)
	oldsize = os.stat(filepath).st_size
	picture = Image.open(filepath)
	dim = picture.size
	
	#set quality= to the preferred quality. 
	#I found that 85 has no difference in my 6-10mb files and that 65 is the lowest reasonable number
	picture.save("Compressed_"+file,"JPEG",optimize=True,quality=85) 
	
	newsize = os.stat(os.path.join(os.getcwd(),"Compressed_"+file)).st_size
	percent = (oldsize-newsize)/float(oldsize)*100
	if (verbose):
		print "File compressed from {0} to {1} or {2}%".format(oldsize,newsize,percent)
	return percent



def create_jwt():
    """Creates a JWT (https://jwt.io) to establish an MQTT connection.
        Args:
         project_id: The cloud project ID this device belongs to
         private_key_file: A path to a file containing either an RSA256 or
                 ES256 private key.
         algorithm: The encryption algorithm to use. Either 'RS256' or 'ES256'
        Returns:
            An MQTT generated from the given project_id and private key, which
            expires in 20 minutes. After 20 minutes, your client will be
            disconnected, and a new JWT will have to be generated.
        Raises:
            ValueError: If the private_key_file does not contain a known key.
        """

    token = {
        # The time that the token was issued at
        'iat': datetime.datetime.utcnow(),
        # The time the token expires.
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        # The audience field should always be set to the GCP project id.
        'aud': project_id
    }

    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()

    print('Creating JWT using {} from private key file {}'.format(
        algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm)

def get_client():
    """Returns an authorized API client by discovering the IoT API and creating
    a service object using the service account credentials JSON."""
    api_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    api_version = 'v1'
    discovery_api = 'https://cloudiot.googleapis.com/$discovery/rest'
    service_name = 'cloudiotcore'

    credentials = service_account.Credentials.from_service_account_file(
        service_account_json)
    scoped_credentials = credentials.with_scopes(api_scopes)

    discovery_url = '{}?version={}'.format(
        discovery_api, api_version)

    return discovery.build(
        service_name,
        api_version,
        discoveryServiceUrl=discovery_url,
        credentials=scoped_credentials)



def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    print('on_connect', mqtt.connack_string(rc))


def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    print('on_disconnect', error_str(rc))


def on_publish(unused_client, unused_userdata, unused_mid):
    """Paho callback when a message is sent to the broker."""
    print('on_publish')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./service_account.json"
#GOOGLE_APPLICATION_CREDENTIALS = './service_account.json' 
img = Image.open("picture.jpg")
payload = 'Message {} Time {}'.format(img, str(datetime.datetime.now()))
client = vision.ImageAnnotatorClient()

# The name of the image file to annotate
#file_name = os.path.join(
 #   os.path.dirname(__file__),
  #  'picture.jpg')

# Loads the image into memory
#with io.open(file_name, 'rb') as image_file:
#    content = image_file.read()

#image = types.Image(content=content)

#Performs label detection on the image file
#response = client.label_detection(image=image)
compressMe('picture.jpg')
file_name = os.path.join(
    os.path.dirname(__file__),
    'Compressed_picture.jpg')

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()
    
image = types.Image(content=content)

print("hi")

# Performs label detection on the image file
response = client.face_detection(image=image)
print ("weird")
numOfPeople = len(response.face_annotations)
print (numOfPeople)

# Create our MQTT client. The client_id is a unique string that identifies
# this device. For Google Cloud IoT Core, it must be in the format below.
client = mqtt.Client(
    client_id=('projects/{}/locations/{}/registries/{}/devices/{}'.format(
        project_id,
        cloud_region,
        registry_id,
        device_id)))

# With Google Cloud IoT Core, the username field is ignored, and the
# password field is used to transmit a JWT to authorize the device.
client.username_pw_set(
    username='unused',
    password=create_jwt())

# Enable SSL/TLS support.
client.tls_set(ca_certs=ca_certs)

# Register message callbacks. https://eclipse.org/paho/clients/python/docs/
# describes additional callbacks that Paho supports. In this example, the
# callbacks just print to standard out.
client.on_connect = on_connect
client.on_publish = on_publish
client.on_disconnect = on_disconnect

# Connect to the Google MQTT bridge.
client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

# Start the network loop.
client.loop_start()



# Publish num_messages mesages to the MQTT bridge once per second.

payload = 'Temprature {} NumOfPeople {} Time {}'.format(
  CelsiusRoomFinal,numOfPeople, str(datetime.datetime.now()))
print('Publishing Message')

    # Publish "payload" to the MQTT topic. qos=1 means at least once
    # delivery. Cloud IoT Core also supports qos=0 for at most once
    # delivery.
client.publish(mqtt_topic, payload, qos=1)

    # Send events every second    

# End the network loop and finish.
client.loop_stop()
print('Finished.')


