#!/usr/bin/env python3
import json
import socket
from uuid import getnode as get_mac
import os 
import sys
import logging

class Settings:

  def __init__(self, etcf):
    self.etcfname = etcf
    #self.log = log                    # may not be usable, yet
    self.mqtt_server = "192.168.1.7"   # From json
    self.mqtt_port = 1883              # From json
    self.mqtt_client_name = "detection_1"   # From json
    self.machines = {}
    # IP and MacAddr are not important (should not be important).
    if sys.platform.startswith('linux'):
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
      s.connect(('<broadcast>', 0))
      self.our_IP =  s.getsockname()[0]
      # from stackoverflow (of course):
      self.macAddr = ':'.join(("%012x" % get_mac())[i:i+2] for i in range(0, 12, 2))
      self.host_name = socket.gethostname() 
    elif sys.platform.startswith('darwin'):
      self.host_name = socket.gethostname() 
      self.our_IP = socket.gethostbyname(self.host_name) 
      self.macAddr = ':'.join(("%012x" % get_mac())[i:i+2] for i in range(0, 12, 2))
    else:
      # TODO somebody else can deal with Windows
      self.our_IP = "192.168.1.255"
      self.macAddr = "de:ad:be:ef"
    self.macAddr = self.macAddr.upper()
    
    print(f"Settings from {self.etcfname}")
    self.load_settings(self.etcfname)
      

  def load_settings(self, fn):
    print(f"loading settings from {fn}")
    conf = json.load(open(fn))
    self.mqtt_server = conf.get("mqtt_server_ip", None)
    self.mqtt_port = conf.get("mqtt_port", 1883)
    self.mqtt_client_name = conf.get("mqtt_client_name", "Bad Client")
    self.email = conf.get("email", None)
    self.node = conf.get("node", None)
    self.processes = conf.get("processes", None)
    self.dockers = conf.get("dockers", None)
    self.nfs = conf.get("nfs", None)
    self.smtp_svr = conf.get("smtp_svr", "cecil.coupe@gmail.com")
    self.smtp_port = conf.get("smtp_port", 25)

  def display(self):
    self.log.info("==== Settings ====")
    self.log.info("%s", self.settings_serialize())
  
  def settings_serialize(self):
    st = {}
    st['mqtt_server_ip'] = self.mqtt_server
    st['mqtt_port'] = self.mqtt_port
    st['mqtt_client_name'] = self.mqtt_client_name
    st['node'] = self.node
    st['processes'] = self.processes
    st['email'] = self.email
    return str


