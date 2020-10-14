import socket
import sflow
import sqlite3
import time
import appconf

# Create in-memory sqlite3 db
class init_db():
	def __init__(initdb):
		db=sqlite3.connect(":memory:",check_same_thread=False)
		cur=db.cursor()
		init_db = """CREATE TABLE IF NOT EXISTS flows (
srcvl INT(4),
dstvl INT(4),
srcmac VARCHAR(30),
dstmac VARCHAR(30),
srcip VARCHAR(254),
dstip VARCHAR(254),
ipproto INT(3),
srcport INT(5),
dstport INT(5),
pktlen INT(10),
time INT(32)
);"""
		cur.execute(init_db)
		db.commit()
		initdb.cur=cur
		initdb.db=db

# Calculate measures
class measures:
	def __init__(self, pkt_count, avg_pktsize, sample_rate):
		self.pps=int((pkt_count * int(sample_rate)) / 5)
		self.bps=int(((((avg_pktsize * 8) * self.pps) / 1000) / 1000))

# Cleanup old ressources
def cleanup_flows(db,cur,age):
	time_start=int(time.time())-age
	cur.execute("DELETE FROM flows WHERE time < "+str(time_start))
	db.commit()

# Run sflow collector
def collector(db,cur,bind,port):
	sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((bind, int(port)))

	while True:                                                
		data, addr = sock.recvfrom(3000) 
		sFlowData = sflow.sFlow(data)
		for i in range(sFlowData.NumberSample):
				for j in range(sFlowData.samples[i].recordCount):
					if sFlowData.samples[i].records[j].sampleType == 1:
							if sFlowData.samples[i].records[j].format == 1 and sFlowData.samples[i].records[j].enterprise == 0:
								record = sflow.sFlowRawPacketHeader(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
							if sFlowData.samples[i].records[j].format == 1001:
								record2 = sflow.sFlowExtendedSwitch(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
					if j == 1:
						cur.execute("INSERT INTO flows (srcvl,dstvl,srcmac,dstmac,srcip,dstip,ipproto,srcport,dstport,pktlen,time)VALUES("+str(record2.srcVLAN)+","+str(record2.dstVLAN)+",'"+str(record.srcMAC.decode("utf-8"))+"','"+str(record.dstMAC.decode("utf-8"))+"','"+record.srcIp+"','"+record.dstIp+"','"+str(record.headerProtocol)+"','"+str(record.srcPort)+"','"+str(record.dstPort)+"','"+str(record.frameLength)+"','"+str(int(time.time()))+"')")
						db.commit()

# Run sflow analyzer
def analyze(db,cur,config):
	# Wait a bit after thread start
	time.sleep(5)
	while True:
		time_now=int(time.time())
		time_start=time_now-5
		cur=db.cursor()
		cur.execute("SELECT COUNT(*) FROM flows WHERE time > "+str(time_start)+" AND (srcvl=51 or srcvl=71) ORDER BY time ASC")
		packets=int(cur.fetchone()[0])
		cur.execute("SELECT SUM(pktlen) FROM flows WHERE time > "+str(time_start)+" AND (srcvl=51 or srcvl=71) ORDER BY time ASC")
		measure=measures(packets,(int(cur.fetchone()[0])/packets),config.get('sflow','sample_rate'))
		print("Packets: "+str(measure.pps/1000)+"kpps, Traffic: "+str(measure.bps)+"mbps")
		cur.execute("SELECT COUNT(*) FROM flows")
		print("Flows in db: "+str(cur.fetchone()[0]))
		cleanup_flows(db,cur,30)
		time.sleep(1)
