import sys
import linecache
import json
import pdb


#===================================================================================================
#==============================================CONFIG===============================================
#===================================================================================================
class ConfigHelper():
    """A class to help the user create config for cosimulation.
    Most methods are names add_* and remove_*. add _* adds a
    particular configuration while remove_* will undo the change.
    There is also a read, write, show and validate methods to
    read an existing config file, write the current self.data
    to a file, show the contents of self.data and validate the
    configuration in self.data.
    
    Typical usage,
    foo=ConfigHelper()
    foo.add_*()
    foo.validate()
    foo.write()"""
    def __init__(self):
        self.data={}
        return None

#===================================================================================================
    def add_pssepath(self,rawFilePath,dyrFilePath):
        try:
            psseConfig=self.data['psseConfig']={}
            psseConfig['rawFilePath']=rawFilePath
            psseConfig['dyrFilePath']=dyrFilePath
        except:
            self.PrintException()

#===================================================================================================
    def remove_pssepath(self):
        try:
            self.data.pop('psseConfig')
        except:
            self.PrintException()

#===================================================================================================
    def add_cosimhome(self,cosimHome):
        try:
            self.data['cosimHome']=cosimHome
        except:
            self.PrintException()

#===================================================================================================
    def remove_cosimhome(self):
        try:
            self.data.pop('cosimHome')
        except:
            self.PrintException()

#===================================================================================================
    def add_defaultfeederconfig(self,filePath,solarFlag,solarPenetration):
        try:
            if 'openDSSConfig' not in self.data:
                self.data['openDSSConfig']={}
            defConf=self.data['openDSSConfig']['defaultFeederConfig']={}
            defConf['filePath']=filePath
            defConf['solarFlag']=solarFlag
            defConf['solarPenetration']=solarPenetration
        except:
            self.PrintException()

#===================================================================================================
    def remove_defaultfeederconfig(self):
        try:
            self.data['openDSSConfig'].pop('defaultFeederConfig')
        except:
            self.PrintException()

#===================================================================================================
    def add_manualfeederconfig(self,nodenumber,filePath,solarFlag,solarPenetration):
        """Each input should be a list such that the entries in the list index should match.
        for ex:nodenumber=[1,2],filePath=['case13.dss','case123.dss'],solarFlag=[0,1],
        solarPenetration=[0,50] implies case13.dss is attached to transmission bus 1 and that there
        is no solar generation in the distribution system."""
        try:
            if 'manualFeederConfig' not in self.data['openDSSConfig']:
                self.data['openDSSConfig']['manualFeederConfig']={}
                self.data['openDSSConfig']['manualFeederConfig']['nodes']=[]

            data=self.data['openDSSConfig']['manualFeederConfig']['nodes']
            for nodenum,fPath,sFlag,sPenetration in zip(nodenumber,filePath,solarFlag,solarPenetration):
                thisNodeData={}
                thisNodeData['nodenumber']=nodenum
                thisNodeData['filePath']=fPath
                thisNodeData['solarFlag']=sFlag
                thisNodeData['solarPenetration']=sPenetration
                data.append(thisNodeData)
        except:
            self.PrintException()

#===================================================================================================
    def remove_manualfeederconfig(self):
        try:
            self.data['openDSSConfig']['manualFeederConfig'].pop('nodes')
        except:
            self.PrintException()

#===================================================================================================
    def add_derparameters(self,nodenumber,power_rating=50,voltage_rating=174,SteadyState=True,
    V_LV1=0.7,V_LV2=0.88,t_LV1_limit=10.0,t_LV2_limit=20.0,LVRT_INSTANTANEOUS_TRIP=False,
    LVRT_MOMENTARY_CESSATION=False):
        """Add DER parameters to a given nodenumber (nodeID/busID/busNumber)"""
        try:
            assert 'openDSSConfig' in self.data and \
            'manualFeederConfig' in self.data['openDSSConfig'] and \
            'nodes' in self.data['openDSSConfig']['manualFeederConfig'],"""
            Please use add_manualfeederconfig method to define nodes at which solar is present
            before running this method."""

            nodes=self.data['openDSSConfig']['manualFeederConfig']['nodes']
            nodenum2ind={}#recompute at each call as the user could add nodes one at a time
            pdb.set_trace()
            for n in range(len(self.data['openDSSConfig']['manualFeederConfig']['nodes'])):
                nodenum2ind[nodes[n]['nodenumber']]=n

            if nodenumber in nodenum2ind:# modify existing data
                thisNode=nodes[nodenum2ind[nodenumber]]
                derprop=thisNode['DERParameters']={}#overwrite even if previous data exists
                derprop['power_rating'],derprop['voltage_rating'],derprop['SteadyState'],
                derprop['V_LV1'],derprop['V_LV2'],derprop['t_LV1_limit'],derprop['t_LV2_limit'],
                derprop['LVRT_INSTANTANEOUS_TRIP'],derprop['LVRT_MOMENTARY_CESSATION']=\
                power_rating,voltage_rating,SteadyState,V_LV1,V_LV2,t_LV1_limit,t_LV2_limit,
                LVRT_INSTANTANEOUS_TRIP,LVRT_MOMENTARY_CESSATION
        except:
            self.PrintException()

#===================================================================================================
    def remove_derparameters(self,nodenumber):
        """Remove DER parameters of a given nodenumber (nodeID/busID/busNumber)"""
        try:
            if 'openDSSConfig' in self.data and \
            'manualFeederConfig' in self.data['openDSSConfig'] and \
            'nodes' in self.data['openDSSConfig']['manualFeederConfig']:

                nodes=self.data['openDSSConfig']['manualFeederConfig']['nodes']
                nodenum2ind={}#recompute at each call as the user could add nodes one at a time
                for n in range(len(self.data['openDSSConfig']['manualFeederConfig']['nodes'])):
                    nodenum2ind[nodes[n]['nodenumber']]=n
                if nodenumber in nodenum2ind:
                    nodes.pop(nodenum2ind[nodenumber])
        except:
            self.PrintException()

#===================================================================================================
    def add_simulationconfig(self,simType,protocol):
        try:
            if 'simulationConfig' not in self.data:
                self.data['simulationConfig']={}
            simConf=self.data['simulationConfig']
            simConf['simType']=simType
            simConf['protocol']=protocol
        except:
            self.PrintException()

#===================================================================================================
    def remove_simulationconfig(self):
        try:
            self.data.pop('simulationConfig')
        except:
            self.PrintException()

#===================================================================================================
    def add_loadshape(self,loadShape):
        try:
            if 'simulationConfig' not in self.data:
                self.data['simulationConfig']={}
            self.data['simulationConfig']['staticConfig']={}
            self.data['simulationConfig']['staticConfig']['loadShape']=loadShape
        except:
            self.PrintException()

#===================================================================================================
    def remove_loadshape(self):
        try:
            self.data['simulationConfig']['staticConfig'].pop('loadShape')
        except:
            self.PrintException()

#===================================================================================================
    def add_fault(self,faultBus,faultImpedance,faultOnTime,faultOffTime):
        try:
            if 'simulationConfig' not in self.data:
                self.data['simulationConfig']={}

            if 'dynamicConfig' not in self.data['simulationConfig']:
                self.data['simulationConfig']['dynamicConfig']={}
                self.data['simulationConfig']['dynamicConfig']['events']={}

            events=self.data['simulationConfig']['dynamicConfig']['events']

            if events.keys():
                prevEvents=[]
                for entry in events.keys():
                    prevEvents.append(int(entry))
            else:
                prevEvents=[0]
            nextEvent=max(prevEvents)+1

            events[str(nextEvent)]={}
            events[str(nextEvent)]['time'],events[str(nextEvent)]['faultBus'],\
            events[str(nextEvent)]['faultImpedance']=faultOnTime,faultBus,faultImpedance
            events[str(nextEvent)]['type']='faultOn'
            
            events[str(nextEvent+1)]={}
            events[str(nextEvent+1)]['time']=faultOffTime
            events[str(nextEvent+1)]['faultBus']=faultBus
            events[str(nextEvent+1)]['type']='faultOff'
        except:
            self.PrintException()

#===================================================================================================
    def remove_fault(self,faultBus,faultOnTime,faultOffTime):
        try:
            events=self.data['simulationConfig']['dynamicConfig']['events']

            popID=[]
            for entry in events:
                if events[entry]['faultBus']==faultBus and events[entry]['type']=='faultOn' and \
                events[entry]['time']==faultOnTime:
                    popID.append(entry)
                if events[entry]['faultBus']==faultBus and events[entry]['type']=='faultOff' and \
                events[entry]['time']==faultOffTime:
                    popID.append(entry)

            for entry in popID:
                events.pop(entry)
        except:
            self.PrintException()

#===================================================================================================
    def add_simend(self,simEndTime):
        try:
            if 'simulationConfig' not in self.data:
                self.data['simulationConfig']={}
            if 'dynamicConfig' not in self.data['simulationConfig']:
                self.data['simulationConfig']['dynamicConfig']={}
            if 'events' not in self.data['simulationConfig']['dynamicConfig']:
                self.data['simulationConfig']['dynamicConfig']['events']={}

            events=self.data['simulationConfig']['dynamicConfig']['events']
            if events.keys():
                prevEvents=[]
                for entry in events.keys():
                    prevEvents.append(int(entry))
            else:
                prevEvents=[0]
            nextEvent=max(prevEvents)+1
            
            events[nextEvent]={}
            events[nextEvent]['type']='simEnd'
            events[nextEvent]['time']=simEndTime
        except:
            self.PrintException()

#===================================================================================================
    def remove_simend(self):
        try:
            assert 'events' in self.data['simulationConfig']['dynamicConfig'],"add events first"
            events=self.data['simulationConfig']['dynamicConfig']['events']

            for entry in events:
                if events[entry]['type']=='simEnd':
                    events.pop(entry)
        except:
            self.PrintException()

#===================================================================================================
    def add_outputconfig(self,outputFileName,outputFileType):
        try:
            if 'outputConfig' not in self.data:
                self.data['outputConfig']={}
            self.data['outputConfig']['outputfilename']=outputFileName
            self.data['outputConfig']['type']=outputFileType
        except:
            self.PrintException()

#===================================================================================================
    def remove_outputconfig(self):
        try:
            self.data.pop('outputConfig')
        except:
            self.PrintException()

#===================================================================================================
    def write(self,fpath):
        """Will write the configuration data in self.data to the given filename."""
        try:
            json.dump(self.data,open(fpath,'w'))
        except:
            self.PrintException()

#===================================================================================================
    def read(self,fpath):
        """Will load the config data from an existing config file.
        Use this method to make modifications to an existing file.
        P.S. This will overwrite self.data."""
        try:
            self.data=json.load(open(fpath))
        except:
            self.PrintException()

#===================================================================================================
    def show(self):
        """Will print out the configuration data in self.data"""
        try:
            pprint(self.data)
        except:
            self.PrintException()

#===================================================================================================
    def validate(self):
        """Validates if the provided settings are valid.
        P.S. Validity in this context simply means that the provided options
        satisfy the minimum requirements. When the config options are validated
        by this method it does not mean that the cosimulation will run without
        errors. For instance, this method does not verify, if a given filepath
        exists.
        
        P.S. This method will not find the issues when used in optimized mode
        i.e. python -O foo.py or python -OO foo.py
        
        Sample call: self.validate() will return without error when config is correct."""
        try:
            assert 'psseConfig' in self.data,\
            ''.join(['psse options missing.\n','Please use add_pssepath'])#join is used for better
            # formatting while using self.PrintException()

            assert 'cosimHome' in self.data and self.data['cosimHome'],\
            ''.join(['cosimHome missing.\n','Please use add_cosimhome'])

            assert 'defaultFeederConfig' in self.data['openDSSConfig'] and \
            (len(self.data['openDSSConfig']['defaultFeederConfig'])>0 or \
            len(self.data['openDSSConfig']['manualFeederConfig'])>0),\
            ''.join(['Either default feeder config or manual feeder config should be set.\n',\
            'Use add_defaultfeederconfig or add_manualfeederconfig.'])

            assert 'simulationConfig' in self.data,\
            ''.join(['simulation config missing.\n',\
            'Use add_simulationconfig method to add simulation config.'])

            assert 'simType' in self.data['simulationConfig'],\
            ''.join(['Simulation type missing.\n',\
            'Use add_simulationconfig method to define simulation type.'])

            assert 'outputConfig' in self.data,\
            ''.join(['output config not set.\n',\
            'Use add_outputconfig method to set it.'])
            
            return True
        except:
            self.PrintException()
            return False

#===================PRINT EXCEPTION========================
    def PrintException(self):
         exc_type, exc_obj, tb = sys.exc_info()
         f = tb.tb_frame
         lineno = tb.tb_lineno
         filename = f.f_code.co_filename
         linecache.checkcache(filename)
         line = linecache.getline(filename, lineno, f.f_globals)
         print "Exception in Line {}".format(lineno)
         print "Error in Code: {}".format(line.strip())
         print "Error Reason: {}".format(exc_obj)



