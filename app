#!/usr/bin/env python3
import socket
import sflow
import sqlite3
import time
from datetime import datetime
import _thread
from appconf import *
from configparser import ConfigParser
from functions import *

# Initialize database
initdb=init_db()

# Start sflow collector
_thread.start_new_thread(collector,(initdb.db,initdb.cur,config.get('sflow','bind'),config.get('sflow','port'),))

# Start Analyzer
_thread.start_new_thread(analyze,(initdb.db,initdb.cur,config,))

# Loop through flows
while True:
	cur=initdb.db.cursor()
	cur.execute("SELECT * FROM flows ORDER BY time ASC")
	for x in cur.fetchall():
		svlan=x[0]
		dvlan=x[1]
		srcip=x[4]
		dstip=x[5]
		protoip=x[6]
		srcport=x[7]
		dstport=x[8]
		pktlen=x[9]
		timestamp=x[10]
		#print("\n>flow\nSource-VLan: ",svlan," Dest-VLan: ",dvlan,"\nSource: ",srcip+":"+str(srcport)," Dest-IP: "+dstip+":"+str(dstport)+", Protocol: ",protoip,"\nLength: ",pktlen,"bytes, Time: ",datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))
	time.sleep(1)
