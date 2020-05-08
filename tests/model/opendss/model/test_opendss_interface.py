import unittest
import sys
import os

import tdcosim
from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.model.opendss_interface import OpenDSSInterface
from tdcosim.test import der_test_manual_config

dirlocation= os.path.dirname(tdcosim.__file__)
dirlocation = dirlocation[0:len(dirlocation)-8]
print('Home directory:{}'.format(dirlocation))

OpenDSSData.config['myconfig'] = der_test_manual_config.test_config

class TestOpenDSSInterface(unittest.TestCase):
    
    def test_init(self):
        model = OpenDSSInterface()
        self.assertIsInstance(model, OpenDSSInterface)
    
    def test_setup(self):
        model = OpenDSSInterface()
        model.setup()
        self.assertNotEqual(model.S0['P'], 0)
        self.assertNotEqual(model.S0['Q'], 0)
    
    def test_initialize(self):
        model = OpenDSSInterface()
        model.setup()
        Vpcc = 0.99      
        targetS = [70.0, 23.0]
        tol = 0.0001
        OpenDSSData.config['myconfig']['solarFlag'] = 0
        P, Q, convergedFlg = model.initialize(Vpcc, targetS, tol)
        self.assertNotEqual(P, 0)
        self.assertNotEqual(Q, 0)
        OpenDSSData.config['myconfig']['solarFlag'] = 1
        
    
    def test_setupDER(self):
        model = OpenDSSInterface()
        model.setup()
        Vpcc = 0.99      
        targetS = [70.0, 23.0]
        tol = 0.0001
        OpenDSSData.config['myconfig']['solarFlag'] = 0
        P0, Q0, convergedFlg = model.initialize(Vpcc, targetS, tol)

        model = OpenDSSInterface()
        model.setup()      
        pvdermap = {
            '49': {
                0: 5, 
                'nSolar_at_this_node': 1
                }, 
            '300': {
                0: 7, 
                'nSolar_at_this_node': 1
                }, 
            '149': {
                0: 3, 
                'nSolar_at_this_node': 1
                }, 
            '150r': {
                0: 1, 
                'nSolar_at_this_node': 1
                }, 
            '62': {
                0: 4, 
                'nSolar_at_this_node': 1
                }, 
            '72': {
                0: 0, 
                'nSolar_at_this_node': 1
                }, 
            '67': {
                0: 6, 
                'nSolar_at_this_node': 1
                }, 
            '105': {
                0: 2, 
                'nSolar_at_this_node': 1
                }
            }
        OpenDSSData.data['DNet']['DER'] = {
            'PVDERData':{}
        }
        
        OpenDSSData.data['DNet']['DER']['PVDERData'].update({'lowSideV':{},'PNominal':{},'QNominal':{}})
        for node in pvdermap:
            OpenDSSData.data['DNet']['DER']['PVDERData']['PNominal'][node] = 46.0
            OpenDSSData.data['DNet']['DER']['PVDERData']['QNominal'][node] = 0.0
            OpenDSSData.data['DNet']['DER']['PVDERData']['lowSideV'][node] = 174.0
            
        model.setupDER(pvdermap)
        Vpcc = 0.99      
        targetS = [70.0, 23.0]        
        tol = 0.0001
        P, Q, convergedFlg = model.initialize(Vpcc, targetS, tol)        
        self.assertNotEqual(Q, Q0)
       
    def test_getLoad(self):
        model = OpenDSSInterface()
        model.setup()
        Vpcc = 0.99      
        targetS = [70.0, 23.0]
        tol = 0.0001
        OpenDSSData.config['myconfig']['solarFlag'] = 0
        P0, Q0, convergedFlg = model.initialize(Vpcc, targetS, tol)
        S = model.getLoads()
        self.assertNotEqual(S['P'], 0)
        self.assertNotEqual(S['Q'], 0)
    
    def test_getVoltage(self):
        model = OpenDSSInterface()
        model.setup()
        Vpcc = 0.99      
        targetS = [70.0, 23.0]
        tol = 0.0001
        OpenDSSData.config['myconfig']['solarFlag'] = 0
        P0, Q0, convergedFlg = model.initialize(Vpcc, targetS, tol)
        V = model.getVoltage()        
        self.assertNotEqual(V, {})

    def test_setVoltage(self):
        model = OpenDSSInterface()
        model.setup()
        Vpcc = 0.99      
        Vpcc2 = 1.2
        targetS = [70.0, 23.0]
        tol = 0.0001
        OpenDSSData.config['myconfig']['solarFlag'] = 0
        P0, Q0, convergedFlg = model.initialize(Vpcc, targetS, tol)
        S0 = model.getS()        
        model.setVoltage(Vpcc2)
        S1 = model.getS()           
        self.assertNotEqual(S0, S1)

    def test_getS(self):
        model = OpenDSSInterface()
        model.setup()
        Vpcc = 0.99      
        Vpcc2 = 1.2
        targetS = [70.0, 23.0]
        tol = 0.0001
        OpenDSSData.config['myconfig']['solarFlag'] = 0
        P0, Q0, convergedFlg = model.initialize(Vpcc, targetS, tol)
        S0 = model.getS()        
        self.assertNotEqual(S0[0], 0)   
        self.assertNotEqual(S0[1], 0)   
    
    def test_pvderInjection(self):
        OpenDSSData.data['DNet']['DER'] = {
            'DERParameters': {},
            'PVDERData': {}
        }
        OpenDSSData.config['myconfig']['DERParameters']['pvderScale'] = 1.0
        OpenDSSData.data['DNet']['DER']['PVDERMap'] = {u'48': {0: 3, 'nSolar_at_this_node': 1}, u'49': {0: 5, 'nSolar_at_this_node': 1}, u'300': {0: 7, 'nSolar_at_this_node': 1}, u'44': {0: 0, 'nSolar_at_this_node': 1}, u'149': {0: 3, 'nSolar_at_this_node': 1}, u'150r': {0: 1, 1: 5, 'nSolar_at_this_node': 2}, u'98': {0: 1, 'nSolar_at_this_node': 1}, u'62': {0: 4, 'nSolar_at_this_node': 1}, u'63': {0: 6, 'nSolar_at_this_node': 1}, u'72': {0: 0, 'nSolar_at_this_node': 1}, u'7': {0: 7, 'nSolar_at_this_node': 1}, u'67': {0: 6, 'nSolar_at_this_node': 1}, u'100': {0: 2, 'nSolar_at_this_node': 1}, u'67_tfr': {0: 4, 'nSolar_at_this_node': 1}, u'105': {0: 2, 'nSolar_at_this_node': 1}}        
        model = OpenDSSInterface()
        model.setup()
        Vpcc = 0.99      
        Vpcc2 = 1.2
        targetS = [70.0, 23.0]
        tol = 0.0001
        OpenDSSData.config['myconfig']['solarFlag'] = 0
        P0, Q0, convergedFlg = model.initialize(Vpcc, targetS, tol)        
        derP = {u'48': -44.69103342903622, u'49': -44.68064050719606, u'300': -44.69106249193092, u'44': -44.68063934322397, u'149': -44.718762087964095, u'150r': -89.41020467637001, u'98': -44.719429553534326, u'62': -44.69105434902211, u'63': -44.691054548732076, u'72': -44.70889191108346, u'7': -44.708146180554635, u'67': -44.71909186975394, u'100': -44.6910616004745, u'67_tfr': -44.7351812582093, u'105': -44.708465001022766}
        derQ = {u'48': 2.7087276146591264e-05, u'49': 2.7275438870380825e-05, u'300': 3.884907059227724e-05, u'44': 2.6806615256708347e-05, u'149': -3.094056994715726e-05, u'150r': -2.79567973725623e-05, u'98': 1.1422168051453575e-05, u'62': 3.601215152282528e-05, u'63': 3.6357942899110594e-05, u'72': 7.5089284429261965e-06, u'7': -2.0303052103797546e-05, u'67': 4.201785867901799e-06, u'100': 3.848086404529585e-05, u'67_tfr': 2.188912391977697e-06, u'105': 6.33840605716954e-06}
        model.pvderInjection(derP, derQ)
        self.assertNotEqual(OpenDSSData.data['DNet']['DER']['PVDERData']['P'], 0)
        self.assertNotEqual(OpenDSSData.data['DNet']['DER']['PVDERData']['Q'], 0)



if __name__ == '__main__':
    unittest.main()
