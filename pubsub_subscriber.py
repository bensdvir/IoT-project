# Created by Omer Shwartz (www.omershwartz.com)
#
# This script uses service credentials to subscribe to a topic of the Pub/Sub broker residing in
# Google Cloud.
# Using this code a server can receive messages from the device.
#
# This file may contain portions of cloudiot_mqtt_example.py licensed to Google
# under the Apache License, Version 2.0. The original version can be found in
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/iot/api-client/mqtt_example/cloudiot_mqtt_example.py
#
############################################################

import time
import os
import math
import smtplib
import logging
import sqlite3



from google.cloud import storage
from google.cloud import pubsub
from oauth2client.service_account import ServiceAccountCredentials

project_id = 'moshe-and-yuval-project'  # Enter your project ID here
topic_name = 'my-device-events'  # Enter your topic name here
subscription_name = 'my_subscription'  # Can be whatever, but must be unique (for the topic?)
service_account_json = 'service_account.json' # Location of the server service account credential file
maxPeople = 0
counter = 0
sumTemp = 0
emptyRoom = None

def minTemp(num):
  global maxPeople
  global counter
  global sumTemp
  return 23-math.log(num,3)

def maxTemp(num):
  global maxPeople
  global counter
  global sumTemp
  return 27-math.log(num,4)

def SendEmail(str):
  global maxPeople
  global counter
  global sumTemp
  global connection
  global cursor
  TO = 'dba413@gmail.com'
  SUBJECT = 'AC'
  TEXT = str
  #gmail credentials
  gmail_sender = 'dba413@gmail.com'
  gmail_pass = 'q1w1!q1w1!z'
  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.starttls()
  server.login('dba413@gmail.com', 'q1w1!q1w1!z')
  BODY = '\r\n'.join([
    'To: %s' % TO,
    'From: %s' % gmail_sender,
    'Subject: %s' % SUBJECT,
    '',
    TEXT
    ])
  try:
    server.sendmail(gmail_sender, TO, BODY)
    print("email sent")
  except:
    print("error sending mail")
  server.quit()
    
def calculate_temprature(temp, num):
  global maxPeople
  global counter
  global sumTemp
  global emptyRoom
  print("here")
  if num > 0 :
      if temp<minTemp(num):
        SendEmail("The temprature is: " + str(temp) + "C.\nTurn on the heat. Please set it on "+ str(int( minTemp(num)+minTemp(num)-temp))+"C")
        emptyRoom = None 
      elif temp>maxTemp(num):
        emptyRoom = None
        SendEmail("The temprature is: " + str(temp) + "C.\nTurn on the cold. Please set it on "+ str(int( maxTemp(num)+maxTemp(num)-temp))+"C")
      else :
        SendEmail("The temprature is: " + str(temp) + "C.\nEverything is good")
        emptyRoom = None
  else :
      if (emptyRoom == None):
      	SendEmail("The temprature is: " + str(temp) + "C.\nTurn off the AC (No people in the room)")
      	emptyRoom = True

  print("hi")

def handleData(time , date, temprature, numOfPeople):
    #save the data to cloud database
    global maxPeople
    global counter
    global sumTemp
    print 'here'
    sql = '''INSERT INTO records(date,time,number_of_people,temp) VALUES(?,?,?,?)'''
    data = (date,time,numOfPeople,temprature)
    connection = sqlite3.connect('iot.db')
    cursor = connection.cursor()
    cursor.execute(sql,data)
    connection.commit()
    print 'saved'

def on_message(message):
    """Called when a message is received"""
    global maxPeople
    global counter
    global sumTemp
    print('Received message: {}'.format(message))
    print(message.data)
    a= message.data.split()
    temprature = float(a[1])
    numOfPeople = float(a[3])
    time = a[6]
    date = a[5]
    print(temprature, numOfPeople, time, date)
    handleData(time , date, a[1], a[3])
    if numOfPeople > maxPeople:
        maxPeople = numOfPeople
    counter += 1
    sumTemp += temprature
    print(sumTemp)
    if counter == 5:
      calculate_temprature(sumTemp/5, maxPeople)
      counter = 0
      maxPeople = 0
      sumTemp = 0
    message.ack()


# Ugly hack to get the API to use the correct account file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_json

# Create a pubsub subscriber
subscriber = pubsub.SubscriberClient()

topic = 'projects/{project_id}/topics/{topic}'.format(
    project_id=project_id,
    topic=topic_name,
)

subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
    project_id=project_id,
    sub=subscription_name,
)

# Try to delete the subscription before creating it again
try:
    subscriber.delete_subscription(subscription_name)
except: # broad except because who knows what google will return
    # Do nothing if fails
    None

# Create subscription
subscription = subscriber.create_subscription(subscription_name, topic)

# Subscribe to subscription
print "Subscribing"




subscriber.subscribe(subscription_name, callback=on_message)

# Keep the main thread alive
while True:
    time.sleep(100)
