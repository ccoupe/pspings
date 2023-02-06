import paho.mqtt.client as mqtt
import json
import time
import json
import argparse
import warnings
import sys
import subprocess
from lib.Settings import Settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def on_connect(client, userdata, flags, rc):
    print("Connection returned result: "+mqtt.connack_string(rc))

def initialise_mqtt_clients(cname):
    client= mqtt.Client(cname,False) #don't use clean session
    client.on_connect= on_connect        #attach function to callback
    #client.on_message=on_message        #attach function to callback
    client.topic_ack=[]
    client.run_flag=False
    client.running_loop=False
    client.subscribe_flag=False
    client.bad_connection_flag=False
    client.connected_flag=False
    client.disconnect_flag=False
    return client
    
    
def send_email(addr, subj, errlns):
  global settings
  with open('missing.txt', 'w') as f:
    for line in errlns:
      f.write("%s\n" % line)
  # https://www.geeksforgeeks.org/send-mail-attachment-gmail-account-using-python/
  # instance of MIMEMultipart
  msg = MIMEMultipart()
  # storing the senders email address  
  msg['From'] = addr
    
  # storing the receivers email address 
  msg['To'] = addr
    
  # storing the subject 
  msg['Subject'] = subj
    
  # string to store the body of the mail
  body = '\n'.join(errlns)
  
  # attach the body with the msg instance
  msg.attach(MIMEText(body, 'plain'))
  
  # creates SMTP session
  s = smtplib.SMTP(settings.smtp_svr, settings.smtp_port)
  
  # talk to server
  s.ehlo()
  
  # Authentication - none
  # Converts the Multipart msg into a string
  text = msg.as_string()
    
  # sending the mail
  s.sendmail(addr, addr, text)
    
  # terminating the session
  s.quit()
  

def main(argList=None):
  global subscribe_list, openrgb_machines, settings, client
  ap = argparse.ArgumentParser()
  loglevels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
  ap.add_argument("-c", "--conf", required=True, type=str,
    help="path and name of the json configuration file")
  ap.add_argument("-s", "--syslog", action = 'store_true',
    default=False, help="use syslog")
  
  args = vars(ap.parse_args())  
  settings = Settings(args['conf'])
  client = initialise_mqtt_clients(settings.mqtt_client_name)
  client.connect(settings.mqtt_server, settings.mqtt_port)
  
  errlns = []
  cmd = ["ps", "ax"]
  proc_lines = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  for line in proc_lines.stdout.readlines():
    ln = str(line[29:])
    for proc in settings.processes:
      if ln.find(proc['name']) > -1:
        proc['running'] = True
        break
        
  for sts in settings.processes:
    if not sts['running']:
      errlns.append(f"{settings.node} is missing {sts['name']}")
  
  # always publish to mqtt - the reciever can figure out
  if len(errlns) <= 0:
    client.publish("network/processes", f'["{settings.node} is OK"]')
  else:
    client.publish("network/processes", json.dumps(errlns))
    
  # do we have something to email and do we have an address?
  if len(errlns) > 0 and settings.email:
    send_email(settings.email, f"Errors from {settings.node} pspings", errlns)
    
    
if __name__ == '__main__':
  sys.exit(main())

   
