import os
import pdb

from tdcosim.model.opendss.opendss_server import OpenDSSServer
from tdcosim.global_data import GlobalData


class OpenDSSModel:
    def __init__(self):
        self._opendss_server = OpenDSSServer()

    def setup(self, logging=False, adjustOpPoint=True):
        # Either map based on manual feeder config, if false, then do auto feeder map
        GlobalData.data['DNet']['Nodes'] = {}
        if GlobalData.config['openDSSConfig']['manualFeederConfig']['nodes']:
            totalSolarGen=0; reductionPercent=0
            for entry in GlobalData.config['openDSSConfig']['manualFeederConfig']['nodes']:
                self.setDERParameter(entry, entry['nodenumber'])
                if adjustOpPoint:
                    totalSolarGen+=GlobalData.data['TNet']['BusRealPowerLoad'][entry['nodenumber']]*entry['solarPenetration']
            if adjustOpPoint:
                reductionPercent=totalSolarGen/GlobalData.data['TNet']['TotalRealPowerLoad']
        else:
            solarFlag=bool(GlobalData.config["openDSSConfig"]["defaultFeederConfig"]["solarFlag"])
            solarPenetration=GlobalData.config["openDSSConfig"]["defaultFeederConfig"]["solarPenetration"]
            for entry in GlobalData.data['TNet']['LoadBusNumber']:
                GlobalData.data['DNet']['Nodes'][entry]={}
                self.setDERParameter(GlobalData.config['openDSSConfig']['defaultFeederConfig'], entry)                
            reductionPercent=solarPenetration # the amount of syn gen reduction

        GlobalData.data['DNet']['ReductionPercent'] = reductionPercent

        for entry in GlobalData.data['DNet']['Nodes'].keys():
            if logging:
                GlobalData.data['DNet']['Nodes'][entry]['f_out']=open('dss_out_{}.txt'.format(entry),'w')
                GlobalData.data['DNet']['Nodes'][entry]['f_err']=open('dss_err_{}.txt'.format(entry),'w')
            else:
                GlobalData.data['DNet']['Nodes'][entry]['f_out']=GlobalData.data['DNet']['Nodes'][entry]['f_err']=open(os.devnull,'w')
            self._opendss_server.connect_opendssclient(entry)
    def initialize(self, targetS, Vpcc):
        power = self._opendss_server.initialize(targetS, Vpcc)
        return power
    def setVoltage(self, Vpcc):
        self._opendss_server.setVoltage(Vpcc)
    def getLoad(self):
        S = self._opendss_server.getLoad()
        return S

#===================================================================================================
    def scaleLoad(self,scale):
        self._opendss_server.scaleLoad(scale)
        return None

#===================================================================================================
    def monitor(self,msg):
        reply=self._opendss_server.monitor(msg)
        return reply
    def is_float(self, n):
        try:
            float(n)   # Type-casting the string to `float`.
                       # If string is not a valid `float`, 
                       # it'll raise `ValueError` exception
        except ValueError:
            return False
        return True

    def setDERParameter(self, entry, nodenumber):
        GlobalData.data['DNet']['Nodes'][nodenumber]={}
        GlobalData.data['DNet']['Nodes'][nodenumber]['filepath'] = entry['filePath'][0]

        if 'solarFlag' not in entry:
            entry['solarFlag'] = 0
        if 'DERSetting' not in entry:
            entry['DERSetting'] ='default'
        if 'DERModelType' not in entry:
            entry['DERModelType'] ='ThreePhaseUnbalanced'        
        if 'solarPenetration' not in entry:
            entry['solarPenetration'] = 0.0
        if 'DERParameters' not in entry:
            entry['DERParameters'] = {}
        if 'avoidNodes' not in entry['DERParameters']:
            entry['DERParameters']['avoidNodes'] = ['sourcebus','rg60']
        if 'dt' not in entry['DERParameters']:
            entry['DERParameters']['dt'] = 1/120.
        if 'default' not in entry['DERParameters']:
            entry['DERParameters']['default'] = {}        
        if 'solarPenetration' not in entry['DERParameters']['default']:
            entry['DERParameters']['default']['solarPenetration'] = 0.0
        if 'solarPenetrationUnit' not in entry['DERParameters']['default']:
            entry['DERParameters']['default']['solarPenetrationUnit'] = 'kw'        
        if 'powerRating' not in entry['DERParameters']['default']:
            entry['DERParameters']['default']['powerRating'] = 50
        if 'VrmsRating' not in entry['DERParameters']['default']:
            entry['DERParameters']['default']['VrmsRating'] = 175
        if 'steadyStateInitialization' not in entry['DERParameters']['default']:
            entry['DERParameters']['default']['steadyStateInitialization'] = True
        if 'LVRT' not in entry['DERParameters']['default']:
            entry['DERParameters']['default']['LVRT'] = {"0":{"V_threshold":0.5,"t_threshold":1.0,"mode":"momentary_cessation"},
                                               "1":{"V_threshold":0.7,"t_threshold ":10.0,"mode":"mandatory_operation"},
                                               "2":{"V_threshold ":0.88,"t_threshold ":20.0,"mode":"mandatory_operation"}}
        if 'HVRT' not in entry['DERParameters']['default']:
            entry['DERParameters']['default']['HVRT'] = {"0":{"V_threshold":1.12,"t_threshold":0.016,"mode":"momentary_cessation"},
                                               "1":{"V_threshold":1.06,"t_threshold":3.0,"mode":"momentary_cessation"}}
        if 'OUTPUT_RESTORE_DELAY' not in entry['DERParameters']['default']:
            entry['DERParameters']['default']['OUTPUT_RESTORE_DELAY'] = 0.5               
        if 'pvderScale' not in entry['DERParameters']['default']:
            entry['DERParameters']['default']['pvderScale'] = 1.0
        
        if entry['DERSetting'] == 'PVPlacement':
            for node in entry['DERParameters']['PVPlacement']:
                if 'VrmsRating' not in entry['DERParameters']['PVPlacement'][node]:
                    entry['DERParameters']['PVPlacement'][node]['VrmsRating'] = entry['DERParameters']['default']['VrmsRating']
        
        GlobalData.data['DNet']['Nodes'][nodenumber]['solarFlag']= bool(entry['solarFlag'])
        GlobalData.data['DNet']['Nodes'][nodenumber]['solarPenetration']= entry['solarPenetration']
        for key in entry['DERParameters']:
            if isinstance(entry['DERParameters'][key], basestring): #PYTHON3: isinstance(entry['DERParameters'][key], str)
                if entry['DERParameters'][key].lower() == 'true':
                    GlobalData.data['DNet']['Nodes'][nodenumber][key] = True
                elif entry['DERParameters'][key].lower() == 'false':
                    GlobalData.data['DNet']['Nodes'][nodenumber][key] = False
                elif self.is_float(entry['DERParameters'][key]):
                    GlobalData.data['DNet']['Nodes'][nodenumber][key] = float(entry['DERParameters'][key])
                else:
                    GlobalData.data['DNet']['Nodes'][nodenumber][key] = entry['DERParameters'][key]
            else:
                GlobalData.data['DNet']['Nodes'][nodenumber][key] = entry['DERParameters'][key]

