#!/usr/bin/env python
#-*- coding: UTF-8 -*-

'''

@author Sam Cheng

@desc this is a monitor script for sending the istd_faillog_exist_status to the STD_MO_MONITOR

@date 2020-07-10

'''

import json
import requests
import os
import sys
import socket
import time
import random

def getPlayerId():
	playerId = os.popen("/bin/DMS-broadsignID").read().strip()
	playerId = int(playerId)
	return playerId

def getIpAddress():
	ip = [(s.connect(('114.114.114.114', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
	return ip

def getHostname():
	hostname = os.popen("/usr/bin/hostname").read().strip()
	return hostname

def getState():
	failFile = "/var/opt/iSTD/req_fail_"+time.strftime("%Y-%m", time.localtime())+".log"
	bakupFail = "/var/opt/iSTD/back_req_fail_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
	if os.path.isfile(failFile):
		if os.path.getsize(failFile) == 0:
			if os.path.isfile(bakupFail):
				return 1
			else:																	                                	return 0
		else:
			return 1
	else:
		return 0

def get_requests():
	para = {"url": "http://10.179.10.128:5000/","header": {'Content-Type': 'application/json;charset=UTF-8'}}
	msg = {}
	msg["player_name"] = getHostname()
	msg["player_id"] = getPlayerId()
	msg["state"] = getState()
	msg["ip_addr"] = getIpAddress()
	
	try:
		r = requests.post(para["url"],data=json.dumps(msg),headers=para["header"])
		if r.status_code == 200:
			pass
		else:
			pass
	except Exception as e:
		print(e)

if __name__=='__main__':
	time.sleep(random.randint(1,60))
	get_requests()
