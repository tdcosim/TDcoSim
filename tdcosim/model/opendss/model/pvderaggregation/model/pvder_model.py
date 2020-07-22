import copy
import os
import math
import cmath
import pdb
import logging

from tdcosim.model.opendss.opendss_data import OpenDSSData

from pvder.DER_wrapper import DERModel
from pvder.grid_components import Grid
from pvder.dynamic_simulation import DynamicSimulation
from pvder.simulation_events import SimulationEvents
from pvder.simulation_utilities import SimulationUtilities,SimulationResults
from pvder import utility_functions,templates,specifications

class PVDERModel:
    def __init__(self):
        self._pvModel = {}
        self._sim = {}
        self._lastSol = {}
        self._lastT = 0

    def setup(self, nodeid, V0):
        try:
            VpuInitial=1.0
            SinglePhase = False
            
            if 'myconfig' in OpenDSSData.config and 'DERParameters' in OpenDSSData.config['myconfig']:
                #pvderConfig = copy.deepcopy(OpenDSSData.config['myconfig']['DERParameters'])
                
                DERFilePath = OpenDSSData.config['myconfig']['DERFilePath']
                DERModelType = OpenDSSData.config['myconfig']['DERModelType']                
                DERSetting = OpenDSSData.config['myconfig']['DERSetting']                
                                
                DERParameters = OpenDSSData.config['myconfig']['DERParameters']
                
                if DERSetting == 'default':                    
                    pvderConfig = self.get_derconfig(DERParameters['default'])
                    DERArguments = self.get_derarguments(DERParameters['default'])
                    
                elif DERSetting == 'PVPlacement': # for manual feeder config based on PVPlacement
                    if nodeid in DERParameters['PVPlacement']:
                        pvderConfig = self.get_derconfig(DERParameters['PVPlacement'][nodeid])
                        DERArguments = self.get_derarguments(DERParameters['PVPlacement'][nodeid])                       
                    else:
                        raise ValueError('Distribution node {} not found in config file!'.format(nodeid))
                else:
                    raise ValueError('{} is not a valid DER setting in config file!'.format(DERSetting))
                
                if 'nodenumber' in OpenDSSData.config['myconfig']:
                    DERLocation = str(os.getpid()) + '-' + 'bus_' + str(OpenDSSData.config['myconfig']['nodenumber']) +'-'+ 'node_' + nodeid          
                else:
                    DERLocation = str(os.getpid()) + '-' + 'node_' + nodeid    
                
            else:
                print('DERParameters not found in `OpenDSSData` object - using default ratings and parameters!')
                DERArguments = {}
                pvderConfig = {}
                SteadyState = True
                if SinglePhase:
                    powerRating = 10.0e3
                else:
                    powerRating = 50.0e3
                DERLocation = 'node_' + nodeid 
                
                DERArguments.update({'pvderConfig':pvderConfig})
                DERArguments.update({'powerRating':powerRating}) 
                DERArguments.update({'SteadyState':SteadyState}) 
            
            #Va = cmath.rect(DERArguments['VrmsRating']*math.sqrt(2),0.0)
            #Vb = utility_functions.Ub_calc(Va)
            #Vc = utility_functions.Uc_calc(Va)
            a = utility_functions.Urms_calc(V0['a'],V0['b'],V0['c'])/DERArguments['VrmsRating'] 
            Va = (V0['a']/a)  #Convert node voltage at HV side to LV
            Vb = (V0['b']/a)
            Vc = (V0['c']/a)            
            
            DERArguments.update({'identifier':DERLocation})            
            DERArguments.update({'derConfig':pvderConfig})
            DERArguments.update({'standAlone':False})
            
            DERArguments.update({'gridFrequency':2*math.pi*60.0})
            DERArguments.update({'gridVoltagePhaseA':Va})
            DERArguments.update({'gridVoltagePhaseB':Vb})
            DERArguments.update({'gridVoltagePhaseC':Vc})
                        
            logging.debug('Creating DER instance of {} model for {} node.'.format(DERModelType,DERLocation))
            print('Creating DER instance of {} model for {} node.'.format(DERModelType,DERLocation))
            events = SimulationEvents()
            
            PVDER_model = DERModel(modelType=DERModelType,events=events,configFile=DERFilePath,**DERArguments)     
            self.PV_model = PVDER_model.DER_model
            
            self.PV_model.LVRT_ENABLE = True  #Disconnects PV-DER based on ride through settings in case of voltage anomaly
            self.sim = DynamicSimulation(PV_model=self.PV_model,events = events,LOOP_MODE=True,COLLECT_SOLUTION=True)
            if DERModelType in self.sim.jac_list:
                self.sim.jacFlag = True      #Provide analytical Jacobian to ODE solver
            else:
                self.sim.jacFlag = False
            self.sim.DEBUG_SOLVER = False #Check whether solver is failing to converge at any step
            self.results = SimulationResults(simulation = self.sim,PER_UNIT=True)
            
            self.lastSol=copy.deepcopy(self.sim.y0) # mutable,make copy
            self.lastT=0
        except Exception as e:
            OpenDSSData.log("Failed Setup PVDER at node:{}!".format(nodeid))            

    def get_derconfig(self,DERParameters):
        """DER config."""
        
        derConfig = {}
        
        for entry in DERParameters:            
            if entry in templates.VRT_config_template.keys():
               derConfig.update({entry:DERParameters[entry]})
               
        return derConfig

    def get_derarguments(self,DERParameters):
        """DER config."""
        
        DERArguments = {}
        
        for entry in specifications.DER_argument_spec:
            if entry in DERParameters:               
               DERArguments.update({entry:DERParameters[entry]})
            
        if 'powerRating' in DERArguments:
            DERArguments.update({'powerRating':DERArguments['powerRating']*1e3})
        
        return DERArguments
    
    def prerun(self,gridVoltagePhaseA,gridVoltagePhaseB,gridVoltagePhaseC):
        """Prerun will set the required data in pvder model. This method should be run before
        running the integrator."""
        try:
            # set grid voltage. This value will be kept constant during the run
            # as opendss will sync will grid_simulation only once during the run call.
            # opendss will solve power flow and will set gridVoltagePhase value.
            self.PV_model.gridVoltagePhaseA=gridVoltagePhaseA*math.sqrt(2)/Grid.Vbase
            if templates.DER_design_template[self.PV_model.DER_model_type]['basic_specs']['unbalanced']:
                self.PV_model.gridVoltagePhaseB=gridVoltagePhaseB*math.sqrt(2)/Grid.Vbase
                self.PV_model.gridVoltagePhaseC=gridVoltagePhaseC*math.sqrt(2)/Grid.Vbase
            self.sim.t = self.lastT + 1/120.0

            return None
        except Exception as e:
            OpenDSSData.log("Failed prerun in the pvder model")

    def postrun(self,sol,t,KVAbase=50):
        """Postrun will gather results. This method should be run after running the integrator."""
        try:
            if self.sim.COLLECT_SOLUTION:
                self.sim.collect_solution(sol,t)

            #np array is mutable, hence make a copy
            self.lastSol=copy.deepcopy(sol[-1])
            self.lastT=t[-1]

            # get S
            S=self._getS()

            return S*KVAbase
        except Exception as e:
            OpenDSSData.log("Failed postrun in the pvder model")

    def _run(self,gridVoltagePhaseA,gridVoltagePhaseB,gridVoltagePhaseC,KVAbase=50):
        #t = [self.lastT, self.lastT + OpenDSSData.data['DNet']['DER']['DERParameters']['dt']]
        t = [self.lastT, self.lastT + 1/120.0]
        
        try:
            # set grid voltage. This value will be kept constant during the run
            # as opendss will sync will grid_simulation only once during the run call.
            # opendss will solve power flow and will set gridVoltagePhase value.
            self.PV_model.gridVoltagePhaseA=gridVoltagePhaseA*math.sqrt(2)/Grid.Vbase
            self.PV_model.gridVoltagePhaseB=gridVoltagePhaseB*math.sqrt(2)/Grid.Vbase
            self.PV_model.gridVoltagePhaseC=gridVoltagePhaseC*math.sqrt(2)/Grid.Vbase
            self.sim.t = t
            
            sol,info,ConvergeFlag = self.sim.call_ODE_solver(self.sim.ODE_model,self.sim.jac_ODE_model,self.lastSol,t)

            if self.sim.COLLECT_SOLUTION:
                self.sim.collect_solution(sol,t)
            
            #sol,info=odeint(odeFunc,y0,t,Dfun=jac_odeFunc,full_output=1,printmessg=True,hmax = 1/120.,mxstep=50,atol=1e-4,rtol=1e-4)
            #sol,info=odeint(odeFunc,y0,t,full_output=1,printmessg=True,hmax = 1/120.,mxstep=50,atol=1e-4,rtol=1e-4)

            #np array is mutable, hence make a copy
            self.lastSol=copy.deepcopy(sol[-1])
            self.lastT=t[-1]

            # get S
            S=self._getS()

            return S*KVAbase
        except Exception as e:
            #OpenDSSData.log("Failed run in the pvder model")
            OpenDSSData.log("{}:ODE solver failed between {:.4f} s and {:.4f} s!".format(self.PV_model.name,t[0],t[-1]))
            
        S = 0
        return S

    def _getS(self):
        try:
            return self.sim.PV_model.S_PCC # value at end of PV-DER simulation
        except Exception as e:
            OpenDSSData.log("Failed getS in the pvder model")
            
