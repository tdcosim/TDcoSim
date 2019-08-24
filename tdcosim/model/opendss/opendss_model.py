import os
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
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]={}
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['filepath'] = entry['filePath'][0]

                if 'solarFlag' not in entry:
                    entry['solarFlag'] = 0
                if 'solarPenetration' not in entry:
                    entry['solarPenetration'] = 0.0
                if 'DERParameters' not in entry:
                    entry['DERParameters'] = {}
                if 'power_rating' not in entry['DERParameters']:
                    entry['DERParameters']['power_rating'] = 50
                if 'voltage_rating' not in entry['DERParameters']:
                    entry['DERParameters']['voltage_rating'] = 174
                if 'SteadyState' not in entry['DERParameters']:
                    entry['DERParameters']['SteadyState'] = False
                if 'V_LV1' not in entry['DERParameters']:
                    entry['DERParameters']['V_LV1'] = 0.70
                if 'V_LV2' not in entry['DERParameters']:
                    entry['DERParameters']['V_LV2'] = 0.88
                if 't_LV1_limit' not in entry['DERParameters']:
                    entry['DERParameters']['t_LV1_limit'] = 1.0
                if 't_LV2_limit' not in entry['DERParameters']:
                    entry['DERParameters']['t_LV2_limit'] = 2.0
                if 'LVRT_INSTANTANEOUS_TRIP' not in entry['DERParameters']:
                    entry['DERParameters']['LVRT_INSTANTANEOUS_TRIP'] = False
                if 'LVRT_MOMENTARY_CESSATION' not in entry['DERParameters']:
                    entry['DERParameters']['LVRT_MOMENTARY_CESSATION'] = False
                if 'pvderScale' not in entry['DERParameters']:
                    entry['DERParameters']['pvderScale'] = 1.0
                if 'solarPenetrationUnit' not in entry['DERParameters']:
                    entry['DERParameters']['solarPenetrationUnit'] = 'kw'
                if 'avoidNodes' not in entry['DERParameters']:
                    entry['DERParameters']['avoidNodes'] = ['sourcebus','rg60']
                if 'dt' not in entry['DERParameters']:
                    entry['DERParameters']['dt'] = 1/120.
                

                
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['solarFlag']= bool(entry['solarFlag'])
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['solarPenetration']= entry['solarPenetration']
                if adjustOpPoint:
                    totalSolarGen+=GlobalData.data['TNet']['BusRealPowerLoad'][entry['nodenumber']]*entry['solarPenetration']
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['power_rating'] = entry['DERParameters']['power_rating']
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['voltage_rating'] = entry['DERParameters']['voltage_rating']
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['SteadyState'] = entry['DERParameters']['SteadyState']
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['V_LV1'] = entry['DERParameters']['V_LV1']
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['V_LV2'] = entry['DERParameters']['V_LV2']
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['t_LV1_limit'] = entry['DERParameters']['t_LV1_limit']
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['t_LV2_limit'] = entry['DERParameters']['t_LV2_limit']
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['LVRT_INSTANTANEOUS_TRIP'] = bool(entry['DERParameters']['LVRT_INSTANTANEOUS_TRIP'])
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['LVRT_MOMENTARY_CESSATION'] = bool(entry['DERParameters']['LVRT_MOMENTARY_CESSATION'])
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['pvderScale'] = entry['DERParameters']['pvderScale']
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['solarPenetrationUnit'] = entry['DERParameters']['solarPenetrationUnit']
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['avoidNodes'] = entry['DERParameters']['avoidNodes']
                GlobalData.data['DNet']['Nodes'][entry['nodenumber']]['dt'] = entry['DERParameters']['dt']
            
            if adjustOpPoint:
                reductionPercent=totalSolarGen/GlobalData.data['TNet']['TotalRealPowerLoad']
        else:
            solarFlag=bool(GlobalData.config["openDSSConfig"]["defaultFeederConfig"]["solarFlag"])
            solarPenetration=GlobalData.config["openDSSConfig"]["defaultFeederConfig"]["solarPenetration"]
            for entry in GlobalData.data['TNet']['LoadBusNumber']:
                GlobalData.data['DNet']['Nodes'][entry]={}
                GlobalData.data['DNet']['Nodes'][entry]['filepath']=GlobalData.config['openDSSConfig']['defaultFeederConfig']['filePath'][0]
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



