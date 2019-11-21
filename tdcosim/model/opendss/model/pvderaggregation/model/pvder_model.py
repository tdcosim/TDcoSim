import copy
import os
import math
import pdb

from tdcosim.model.opendss.opendss_data import OpenDSSData

from pvder.DER_components_single_phase import SolarPV_DER_SinglePhase
from pvder.DER_components_three_phase  import SolarPV_DER_ThreePhase
from pvder.grid_components import Grid
from pvder.dynamic_simulation import DynamicSimulation
from pvder.simulation_events import SimulationEvents
from pvder.simulation_utilities import SimulationUtilities,SimulationResults
from pvder import utility_functions

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
                if 'DERParameters' in OpenDSSData.config['myconfig']:
                    pvderConfig = OpenDSSData.config['myconfig']['DERParameters']
                    power_rating = OpenDSSData.config['myconfig']['DERParameters']['power_rating']*1e3
                    voltage_rating = OpenDSSData.config['myconfig']['DERParameters']['voltage_rating']
                    SteadyState = OpenDSSData.config['myconfig']['DERParameters']['SteadyState']
                    UnbalancedInitialization  = True#OpenDSSData.config['myconfig']['DERParameters']['UnbalancedInitialization']
                
                if 'nodenumber' in OpenDSSData.config['myconfig']:
                    DER_location = str(os.getpid()) + '-' + 'bus_' + str(OpenDSSData.config['myconfig']['nodenumber']) +'-'+ 'node_' + nodeid          
                else:
                    DER_location = str(os.getpid()) + '-' + 'node_' + nodeid    
                
            else:
                print('DERParameters not found in `OpenDSSData` object - using default ratings and parameters!')
                pvderConfig = None
                SteadyState = True
                DER_location = 'node_' + nodeid
                UnbalancedInitialization = True
                if SinglePhase:
                    power_rating = 10.0e3
                else:
                    power_rating = 50.0e3
            
            #Va = (.50+0j)*Grid.Vbase
            #Vb = (-.25-.43301270j)*Grid.Vbase
            #Vc = (-.25+.43301270j)*Grid.Vbase
            
            #Find turns ratio based on node voltage at HV side and user defined voltage rating
            a = utility_functions.Urms_calc(V0['a'],V0['b'],V0['c'])/OpenDSSData.config['myconfig']['DERParameters']['voltage_rating'] 
            Va = (V0['a']/a)  #Convert node voltage at HV side to LV
            Vb = (V0['b']/a)
            Vc = (V0['c']/a)
            
            events = SimulationEvents()
            
            if SinglePhase:
                self.PV_model=PV_model = SolarPV_DER_SinglePhase(events=events,
                                                                 Sinverter_rated = power_rating,Vrms_rated = voltage_rating,
                                                                 gridVoltagePhaseA = Va*VpuInitial,
                                                                 gridVoltagePhaseB = Vb*VpuInitial,
                                                                 gridVoltagePhaseC = Vc*VpuInitial,
                                                                 gridFrequency=2*math.pi*60.0,
                                                                 standAlone=False,STEADY_STATE_INITIALIZATION=SteadyState,allow_unbalanced_m = UnbalancedInitialization,
                                                                 pvderConfig=pvderConfig,identifier=DER_location)
            else:
                self.PV_model=PV_model = SolarPV_DER_ThreePhase(events=events,
                                                                Sinverter_rated = power_rating,Vrms_rated = voltage_rating,
                                                                gridVoltagePhaseA = Va*VpuInitial,
                                                                gridVoltagePhaseB = Vb*VpuInitial,
                                                                gridVoltagePhaseC = Vc*VpuInitial,
                                                                gridFrequency=2*math.pi*60.0,
                                                                standAlone=False,STEADY_STATE_INITIALIZATION=SteadyState,allow_unbalanced_m = UnbalancedInitialization,
                                                                pvderConfig=pvderConfig,identifier=DER_location)

            self.PV_model.LVRT_ENABLE = True  #Disconnects PV-DER based on ride through settings in case of low voltage anomaly
            self.PV_model.HVRT_ENABLE = True  #Disconnects PV-DER based on ride through settings in case of high voltage anomaly
            self.PV_model.use_frequency_estimate=True #Estimate frequency from phase angles
            self.PV_model._del_t_frequency_estimate = 1/120.0
            self.sim = DynamicSimulation(PV_model=PV_model,events = events,LOOP_MODE=True,COLLECT_SOLUTION=True)
            self.sim.jacFlag = True      #Provide analytical Jacobian to ODE solver
            self.sim.DEBUG_SOLVER = False #Check whether solver is failing to converge at any step
            OpenDSSData.log('Voltage:{},{},{}'.format(abs(Va),abs(Vb),abs(Vc)))
            OpenDSSData.log('Duty cycles:{},{},{}'.format(abs(self.PV_model.ma),abs(self.PV_model.mb),abs(self.PV_model.mc)))
            self.results = SimulationResults(simulation = self.sim,PER_UNIT=True)
            self.lastSol=copy.deepcopy(self.sim.y0) # mutable,make copy
            self.lastT=0
        except Exception as e:
            OpenDSSData.log("Failed Setup PVDER at node:{}!".format(nodeid))            

    def prerun(self,gridVoltagePhaseA,gridVoltagePhaseB,gridVoltagePhaseC):
        """Prerun will set the required data in pvder model. This method should be run before
        running the integrator."""
        try:
            # set grid voltage. This value will be kept constant during the run
            # as opendss will sync will grid_simulation only once during the run call.
            # opendss will solve power flow and will set gridVoltagePhase value.
            self.PV_model.gridVoltagePhaseA=gridVoltagePhaseA*math.sqrt(2)/Grid.Vbase
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
            
