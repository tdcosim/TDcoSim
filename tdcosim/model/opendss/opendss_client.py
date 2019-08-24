import os
os.environ["PATH"] += os.getcwd()
import sys
import socket
import pdb
import json

from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.procedure.opendss_procedure import OpenDSSProcedure

def findConfig(nodeid):
    dssconfig = OpenDSSData.config['openDSSConfig']['defaultFeederConfig']
    if nodeid > 0:        
        for x in OpenDSSData.config['openDSSConfig']['manualFeederConfig']['nodes']:
            if x['nodenumber'] == int(nodeid):
                dssconfig = x
    
    return dssconfig

if __name__=="__main__":
    try:        
        
        nodeid = "-1"
        if len(sys.argv)>1:
            nodeid = sys.argv[1]        
        
        dssProcedure=OpenDSSProcedure()
        
        BUFFER_SIZE = 1024 * 1024        
        c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        c.connect(('127.0.0.1',11000))
        
        comm_end=0
        while comm_end==0:
            replyMsg = {}
            raw = c.recv(BUFFER_SIZE)
            
            msg=json.loads(raw)# expect the msg to be of json format            
            if msg.has_key('COMM_END'):
                comm_end=1
                c.send(json.dumps({"shutdown":1}))# reply back to handler
                c.shutdown(0)
                c.close() # close comm with server
                break
            elif msg['method'].lower()=='setup':                
                OpenDSSData.config = msg['config']                            
                OpenDSSData.config['myconfig'] = findConfig(nodeid)
                dssProcedure.setup()                
                replyMsg = {'response': nodeid}
            elif msg['method'].lower()=='initialize':    
                replyMsg['P'],replyMsg['Q']=dssProcedure.initialize(targetS=msg['targetS'],Vpcc=msg['Vpcc'],tol=msg['tol'])
            elif msg['method'].lower()=='setvoltage':
                dssProcedure.setVoltage(Vpu=msg['Vpu'],Vang=msg['Vang'],pccName=msg['pccName'])
                replyMsg = {"AckNode":nodeid}
            elif msg['method'].lower()=='getload':                
                replyMsg['P'],replyMsg['Q'],replyMsg['convergenceFlg']=dssProcedure.getLoads(pccName=msg['pccName'])
            elif msg['method'].lower()=='scaleload':
                dssProcedure.scaleLoad(scale=msg['scale'])
            elif msg['method'].lower()=='monitor':
                replyMsg=dssProcedure.monitor(msg=msg['varName'])
            c.send(json.dumps(replyMsg))# reply back to handler
    except ValueError:
        print ("Open DSS Client " + nodeid + " is ended")
    except Exception as e:
        OpenDSSData.log("End of OpenDSS Client " + nodeid)
    finally:
        exit(1)
