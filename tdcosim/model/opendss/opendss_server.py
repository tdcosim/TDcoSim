import copy
import shlex
import json

import socket
import os
import subprocess
from tdcosim.global_data import GlobalData

class OpenDSSServer():
    def __init__(self):        
        self.__startServer()
        self._BUFFER_SIZE=1024*1024

    def __startServer(self, host='127.0.0.1', portNum=11000):
        try:
            print("Start Open DSS Server")
            self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.s.bind((host,portNum))
            self.s.listen(0)
        except Exception as e:
            GlobalData.log("Unable to open OpenDSS Connect Server")
            exit(1)
            
    def connect_opendssclient(self, nodeid):
        # start a subprocess asynchronously, one at a time                        
        openDSSClientPath = GlobalData.config['cosimHome'] + '\\model\\opendss\\opendss_client.py'
        GlobalData.data['DNet']['Nodes'][nodeid]['proc']=subprocess.Popen(shlex.split("python "
        + '"'+openDSSClientPath+'"'+" {} ".format(nodeid)), shell=True)        

        #accept connection from worker
        # process is connecting.
        GlobalData.data['DNet']['Nodes'][nodeid]['conn'] = self.s.accept()        
        # now load the case in client
        msg={}        
        msg['method']='setup'
        msg['config'] = GlobalData.config
        GlobalData.data['DNet']['Nodes'][nodeid]['conn'][0].send(json.dumps(msg))# send msg
        reply=json.loads(GlobalData.data['DNet']['Nodes'][nodeid]['conn'][0].recv(self._BUFFER_SIZE))        
        
    def initialize(self, targetS, Vpcc=1.0,tol=10**-5):
        try:
            # assume default values if not provided
            if not isinstance(Vpcc,dict):
                Vpcc_default=Vpcc
                Vpcc={}
                for entry in targetS.keys():
                    Vpcc[entry]=Vpcc_default
            if not isinstance(tol,dict):
                tol_default=tol
                tol={}
                for entry in targetS.keys():
                    tol[entry]=tol_default
            
            for entry in targetS.keys():# first send to all to allow computation to be run concurrently
                msg={}
                msg['method']='initialize'
                msg['targetS']=targetS[entry]
                msg['Vpcc']=Vpcc[entry]
                msg['tol']=tol[entry]
                GlobalData.data['DNet']['Nodes'][entry]['conn'][0].send(json.dumps(msg))# send msg
            
            power={}
            for entry in targetS.keys():# now receive replies
                try:
                    msg = GlobalData.data['DNet']['Nodes'][entry]['conn'][0].recv(self._BUFFER_SIZE)                    
                    power[entry]=json.loads(msg)                    
                except ValueError:
                    power[entry]={"faied":1}
            
            return power
        except Exception as e:
            GlobalData.log("Failed initialize in OpenDSS Server")            
            exit(1)
    def setVoltage(self, Vpu):
        for entry in Vpu.keys():
            msg = {}
            msg['method']='setvoltage'
            msg['Vpu']=Vpu[entry]
            msg['Vang']=0
            msg['pccName']='Vsource.source'
            GlobalData.data['DNet']['Nodes'][entry]['conn'][0].send(json.dumps(msg))# send msg
        
        replyMsg = {}
        for entry in Vpu.keys():
            ack = GlobalData.data['DNet']['Nodes'][entry]['conn'][0].recv(self._BUFFER_SIZE)
            
            replyMsg[entry]=json.loads(ack)

#===================================================================================================
    def getLoad(self):
        for entry in GlobalData.data['DNet']['Nodes'].keys():# first send to all to allow computation to be run concurrently
            msg={}
            msg['method']='getLoad'
            msg['pccName']='Vsource.source'
            GlobalData.data['DNet']['Nodes'][entry]['conn'][0].send(json.dumps(msg))# send msg
        
        replyMsg = {}
        for entry in GlobalData.data['DNet']['Nodes'].keys():# first send to all to allow computation to be run concurrently
            replyMsg[entry]=json.loads(GlobalData.data['DNet']['Nodes'][entry]['conn'][0].recv(self._BUFFER_SIZE))
        
        return replyMsg

#===================================================================================================
    def scaleLoad(self,scale):
        for entry in GlobalData.data['DNet']['Nodes'].keys():
            msg={}
            msg['method']='scaleLoad'
            msg['scale']=scale[entry]
            GlobalData.data['DNet']['Nodes'][entry]['conn'][0].send(json.dumps(msg))# send msg

        replyMsg={}
        for entry in GlobalData.data['DNet']['Nodes'].keys():# now receive replies
            replyMsg[entry]=json.loads(GlobalData.data['DNet']['Nodes'][entry]['conn'][0].recv(self._BUFFER_SIZE))

        return replyMsg

#===================================================================================================
    def monitor(self,msg):
        """msg should be a dictionary whose keys are T-D interface node and value is a list
        containing the variables requested.There should also be a method key with value 'monitor'"""
        for entry in GlobalData.data['DNet']['Nodes'].keys():
            thisMsg={}
            thisMsg['method']='monitor'
            thisMsg['varName']=msg['varName'][entry]
            GlobalData.data['DNet']['Nodes'][entry]['conn'][0].send(json.dumps(thisMsg))# send msg

        replyMsg={}
        for entry in GlobalData.data['DNet']['Nodes'].keys():# now receive replies
            replyMsg[entry]=json.loads(GlobalData.data['DNet']['Nodes'][entry]['conn'][0].recv(self._BUFFER_SIZE))

        return replyMsg



