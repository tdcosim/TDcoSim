import cmath
import math
import pdb
import time
import copy
import json

import six
import numpy as np
from scipy.integrate import ode
from scipy.optimize import newton
from pvder.DER_wrapper import DERModel
from pvder.simulation_events import SimulationEvents
from pvder import utility_functions

from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.model.pvderaggregation.procedure.pvder_procedure import PVDERProcedure
from tdcosim.model.opendss.model.pvderaggregation.model.fast_der import FastDER


class PVDERAggregatedModel(object):
#===================================================================================================
	def __init__(self):
		OpenDSSData.data['DNet']['DER'] = {}
		OpenDSSData.data['DNet']['DER']['PVDERData'] = {}
		OpenDSSData.data['DNet']['DER']['PVDERData'].update({'lowSideV':{},'PNominal':{},'QNominal':{}})
		OpenDSSData.data['DNet']['DER']['PVDERMap'] = {}
		self._pvders = {}
		self._nEqs = {}
		self.profiler=0
		self.funcCalls={'jac':0,'f':0}
		self._stats={'_run_fast':0}

#===================================================================================================
	def import_diffeqpy(self):
		"""Import diffeqpy using lazy loading and creates an attribute so that loading happens only if required and loads in parallel.
		"""
		try:
			
			if self.der_solver_type == "diffeqpy":
				DERModelType = OpenDSSData.config['myconfig']['DERModelType']
				if six.PY3:
					tic = time.perf_counter()
				elif six.PY2:
					tic = time.clock()
				from diffeqpy import ode#,de
				from julia import Sundials
				
				self.de = ode
				self.sundials = Sundials
				
				from julia import Main
				from julia import LinearAlgebra
				
				LinearAlgebra.BLAS.set_num_threads(18) #Set number of threads to be used by DiffEqPy if required
				OpenDSSData.log(level=20,msg="BLAS threads:{}".format(Main.eval("ccall((:openblas_get_num_threads64_, Base.libblas_name), Cint, ())"))) #Show number of threads being used by DiffEqPy
				if six.PY3:
					toc = time.perf_counter()
				elif six.PY2:
					toc = time.clock()
				OpenDSSData.log(level=10,msg="Time taken to import 'diffeqpy':{:.3f}".format(toc - tic))
		
		except:
			OpenDSSData.log()

#===================================================================================================
	def getDERRatedPower(self,powerRating,voltageRating):
		"""Return actual real and reactive power rating of DER for given power and voltage rating.
		Args:
			 powerRating (float): Rated power of DER in kW. 
			 voltageRating (float): Rated voltage of DER in L-G RMS. 
		"""
		try:
			DERFilePath = OpenDSSData.config['myconfig']['DERFilePath']
			DERModelType = OpenDSSData.config['myconfig']['DERModelType']

			Va = cmath.rect(voltageRating*math.sqrt(2),0.0)
			Vb = utility_functions.Ub_calc(Va)
			Vc = utility_functions.Uc_calc(Va)
		
			PVDER_model = DERModel(modelType=DERModelType,events=events,configFile=DERFilePath,
									powerRating = powerRating*1e3,VrmsRating = voltageRating,
									gridVoltagePhaseA = Va,
									gridVoltagePhaseB = Vb,
									gridVoltagePhaseC = Vc,
									gridFrequency=2*math.pi*60.0,
									standAlone=False,steadyStateInitialization=True)
			self.PV_model = PVDER_model.DER_model

			return DER_model.S_PCC.real*DER_model.Sbase,DER_model.S_PCC.imag*DER_model.Sbase
		except:
			OpenDSSData.log()

#===================================================================================================
	def setup(self, S0, V0, V0pu=None):
		try:
			pvderMap=None
			self.der_solver_type = OpenDSSData.config['myconfig']['DEROdeSolver']
			if 'DEROdeMethod' in OpenDSSData.config['myconfig']:
				self.ode_solver_method = OpenDSSData.config['myconfig']['DEROdeMethod']
			else:
				self.ode_solver_method = "euler"
			if self.der_solver_type.replace('_','').replace('-','').lower()=='fastder':
				pvderMap=self._setup_fast(S0,V0,V0pu)
			else:
				pvderMap=self._setup_detailed(S0,V0)

			return pvderMap
		except:
			OpenDSSData.log()

#===================================================================================================
	def _find_three_phase_nodes(self, S0, V0):
		try:
			# set the random number seed
			randomSeed = 25000
			np.random.seed(randomSeed)

			DNet=OpenDSSData.data['DNet']
			myconfig=OpenDSSData.config['myconfig']
			defaultConfig=myconfig['DERParameters']['default']

			#### default settings
			if 'pref' not in defaultConfig:
				myconfig['DERParameters']['default']['pref']=10
			if 'qref' not in defaultConfig:
				myconfig['DERParameters']['default']['qref']=0
			if 'sbase' not in defaultConfig:
				myconfig['DERParameters']['default']['sbase']=10

			if myconfig['DERSetting'] == 'PVPlacement':
				PVPlacement = True
				nSolar=len(myconfig['DERParameters']['PVPlacement']) #Number of solarpv DERs
			elif myconfig['DERSetting'] == 'default':
				PVPlacement = False
				feeder_load=0 # rating will be in kVA as Default
				for entry in S0['P']: #Sum all the loads in the feeder
					if myconfig['DERParameters']['default']['solarPenetrationUnit']=='kva':
						feeder_load+=abs(S0['P'][entry]+S0['Q'][entry]*1j)
					elif myconfig['DERParameters']['default']['solarPenetrationUnit']=='kw':
						feeder_load+=S0['P'][entry]
				# number of 50 kVA solar installtions required
				if self.der_solver_type.replace('_','').replace('-','').lower()=='fastder':
					nSolar=int(np.ceil((feeder_load/defaultConfig['pref'])*\
					defaultConfig['solarPenetration']))
				else:
					nSolar=int(np.ceil((feeder_load/myconfig['DERParameters']['default']['powerRating'])*\
					myconfig['DERParameters']['default']['solarPenetration']))
			else:
				raise ValueError('{} is not a valid DER setting in config file'.format(
				myconfig['DERSetting']))

			# find all three phase nodes
			threePhaseNode=[]
			for node in V0:
				count=len(V0[node])
				if count==3 and node not in myconfig['DERParameters']['avoidNodes']: # three phase node
					threePhaseNode.append(node)

			if PVPlacement:
				invalid_nodes = set(myconfig['DERParameters']['PVPlacement'].keys()).difference(
				threePhaseNode)
				if not invalid_nodes:
					threePhaseNode=list(myconfig['DERParameters']['PVPlacement']) #Get list of D nodes
				else:
					raise ValueError('Config file contains following invalid nodes:{}'.format(
					invalid_nodes))
			OpenDSSData.log(level=10,msg="{} DERs will be created...".format(nSolar))
			return threePhaseNode,PVPlacement,nSolar
		except:
			OpenDSSData.log()

#===================================================================================================
	def _setup_fast(self, S0, V0, V0pu):
		try:
			DNet=OpenDSSData.data['DNet']
			myconfig=OpenDSSData.config['myconfig']
			threePhaseNode,PVPlacement,nSolar=self._find_three_phase_nodes(S0, V0)

			# now map each solar to the available nodes
			nThreePhaseNode=len(threePhaseNode)
			count=0
			DNet['DER']['PVDERData']['nSolar_at_this_node']={}

			totalPercentage=0; interconnectionStandard={}
			for entry in myconfig['interconnectionStandard']:
				interconnectionStandard[entry]=[totalPercentage,\
				totalPercentage+myconfig['interconnectionStandard'][entry]]
				totalPercentage+=myconfig['interconnectionStandard'][entry]

			if not PVPlacement:
				np.random.shuffle(threePhaseNode)
			randomPickData={}
			interconnectionStandardKeys=interconnectionStandard.keys()
			if six.PY3:
				interconnectionStandardKeys=list(interconnectionStandardKeys)
			for n in range(nSolar):
				thisConf={}
				thisKey=threePhaseNode[count%nThreePhaseNode]
				if thisKey not in DNet['DER']['PVDERMap']:
					DNet['DER']['PVDERMap'][thisKey]={}
					DNet['DER']['PVDERMap'][thisKey]['nSolar_at_this_node']=0
				DNet['DER']['PVDERMap'][thisKey][DNet['DER']['PVDERMap'][thisKey]\
				['nSolar_at_this_node']]=n
				DNet['DER']['PVDERMap'][thisKey]['nSolar_at_this_node']+=1

				DNet['DER']['PVDERData']['lowSideV'][thisKey]=\
				myconfig['DERParameters']['default']['VrmsRating']
				DNet['DER']['PVDERData']['PNominal'][thisKey]=\
				myconfig['DERParameters']['default']['pref'] #### kw
				DNet['DER']['PVDERData']['QNominal'][thisKey]=\
				myconfig['DERParameters']['default']['qref'] #### kvar
				if thisKey not in DNet['DER']['PVDERData']['nSolar_at_this_node']:
					DNet['DER']['PVDERData']['nSolar_at_this_node'][thisKey]=0
				DNet['DER']['PVDERData']['nSolar_at_this_node'][thisKey]+=1

				thisConf['vref']=abs(V0pu[thisKey]['a'])
				thisConf['vref_ang']=np.angle(V0pu[thisKey]['a'])
				defaultConfig=myconfig['DERParameters']['default']
				thisConf['pref']=defaultConfig['pref']/defaultConfig['sbase']
				thisConf['qref']=defaultConfig['qref']/defaultConfig['sbase']
				thisConf['sbase']=defaultConfig['sbase']

				thisRandomPick=np.random.random()
				for entry in interconnectionStandardKeys:
					if entry in interconnectionStandard:
						if entry not in randomPickData:
							randomPickData[entry]=0
						if interconnectionStandard[entry][0]<thisRandomPick<=\
						interconnectionStandard[entry][1]:
							thisInterconnectionStandard=entry
							randomPickData[entry]+=1
							if randomPickData[entry]>=np.ceil(\
							(interconnectionStandard[entry][1]-interconnectionStandard[entry][0])*nSolar):
								interconnectionStandard.pop(entry)

				self._pvders[n]=FastDER(interconnectionStandard=thisInterconnectionStandard,\
				**{'config':thisConf})
				#### self._pvders[n].data['config']['pref']=myconfig['DERParameters']['default']['pref']
				#### self._pvders[n].data['config']['qref']=myconfig['DERParameters']['default']['qref']
				self._pvders[n].compute_initial_condition(\
				thisConf['pref'],thisConf['qref'],thisConf['vref'],thisConf['vref_ang'])
				count+=1

			# assign data object
			for entry in DNet['DER']['PVDERMap']:
				thisNode=DNet['DER']['PVDERData'][entry]={}
				thisNode['Vmag']={}

			# sort keys
			self.pvIDIndex=self._pvders.keys() # index for variables based on ID
			if six.PY3:
				self.pvIDIndex=list(self.pvIDIndex)
			self.pvIDIndex.sort()# sort the index and use this as the order
			if self.ode_solver_method == 'adams':
				y0=[]; t0=0.0
				for n in range(len(self.pvIDIndex)):
					y0.extend(self._pvders[self.pvIDIndex[n]].x)
					self._nEqs[self.pvIDIndex[n]]=len(self._pvders[self.pvIDIndex[n]].x)
				
				self.integrator=ode(self.funcval_fastder).set_integrator('vode',method='adams',max_step=1/240.,rtol=1e-4,atol=1e-4)
				self.integrator.set_initial_value(y0,t0)
				OpenDSSData.log(level=10,msg="FastDER model integrator using Adams method initialized at {:.3f} seconds".format(time.time()))
				
			else:
				OpenDSSData.log(level=10,msg="FastDER model integrator using {} initialized at {:.3f} seconds".format(self.ode_solver_method,time.time()))
			
			return DNet['DER']['PVDERMap']
		except:
			OpenDSSData.log()

#===================================================================================================
	def _setup_detailed(self, S0, V0):
		try:
			#self.der_solver_type = OpenDSSData.config['myconfig']['DEROdeSolver']#"scipy"#"diffeqpy"
			#self.ode_solver_method = OpenDSSData.config['myconfig']['DEROdeMethod']#"bdf"/"CVODE_BDF"
			self.import_diffeqpy() #Import diffeqpy if required as an attribute

			DNet=OpenDSSData.data['DNet']
			threePhaseNode,PVPlacement,nSolar=self._find_three_phase_nodes(S0, V0)

			# create instances of pvder
			for n in range(nSolar):
				self._pvders[n]=PVDERProcedure()

			# now map each solar to the available nodes
			nThreePhaseNode=len(threePhaseNode); count=0
			for entry in self._pvders:
				if not PVPlacement:
					thisKey=threePhaseNode[np.random.randint(0,nThreePhaseNode)]
				else:
					thisKey=threePhaseNode[count]
					
				if thisKey not in DNet['DER']['PVDERMap']:
					DNet['DER']['PVDERMap'][thisKey]={}
					DNet['DER']['PVDERMap'][thisKey]['nSolar_at_this_node']=0
				DNet['DER']['PVDERMap'][thisKey][DNet['DER']['PVDERMap'][thisKey]\
				['nSolar_at_this_node']]=entry
				DNet['DER']['PVDERMap'][thisKey]['nSolar_at_this_node']+=1

				self._pvders[entry].setup(thisKey,V0[thisKey])#Pass both node id and V during DER setup
				self.initialize_PQVnominal(thisKey,self._pvders[entry]._pvderModel.PV_model)
				count+=1

			for entry in DNet['DER']['PVDERMap']:
				thisNode=DNet['DER']['PVDERData'][entry]={}
				thisNode['Vmag']={}

			self.pvIDIndex=self._pvders.keys() # index for variables based on ID
			if six.PY3:
				self.pvIDIndex=list(self.pvIDIndex)
			self.pvIDIndex.sort()# sort the index and use this as the order

			y0=[]; t0=0.0
			for n in range(len(self.pvIDIndex)):
				y0.extend(self._pvders[self.pvIDIndex[n]]._pvderModel.lastSol)
				self._nEqs[self.pvIDIndex[n]]=self._pvders[self.pvIDIndex[n]]._pvderModel.PV_model.n_ODE
			
			if six.PY3:
				tic = time.perf_counter()
			elif six.PY2:
				tic = time.clock()
			if self.der_solver_type == "scipy":
				if self.ode_solver_method in ['bdf','adams']:
					self.integrator=ode(self.funcval,self.jac).set_integrator('vode',method=self.ode_solver_method,rtol=1e-4,atol=1e-4)
				else:
					ode_solver_default_method = 'bdf' 
					OpenDSSData.log(level=30,msg="'{}' is not a valid method for {} DER ODE solver - switching to default method {}".format(self.ode_solver_method,self.der_solver_type,ode_solver_default_method))
					self.ode_solver_method = ode_solver_default_method
					self.integrator=ode(self.funcval,self.jac).set_integrator('vode',method=self.ode_solver_method,rtol=1e-4,atol=1e-4)
				self.integrator.set_initial_value(y0,t0)
			elif self.der_solver_type == "diffeqpy":
				if self.ode_solver_method in ['TRBDF2','KenCarp4','FBDF','QNDF']:
					solver_type = eval("self.de.{}()".format(self.ode_solver_method)) #self.de.TRBDF2()
					
				elif self.ode_solver_method in ['CVODE_BDF','ARKODE']:
					solver_type = eval("self.sundials.{}()".format(self.ode_solver_method))
				else:
					ode_solver_default_method = 'self.de.TRBDF2()'
					OpenDSSData.log(level=30,msg="'{}' is not a valid method for {} DER ODE solver - switching to default method {}".format(self.ode_solver_method,self.der_solver_type,ode_solver_default_method))
					self.ode_solver_method = ode_solver_default_method
					solver_type = eval(ode_solver_default_method)
				julia_f = self.de.ODEFunction(self.funcval_diffeqpy, jac=self.jac_diffeqpy)
				diffeqpy_ode = self.de.ODEProblem(julia_f, y0, (t0, 1/120.),[])
				self.integrator = self.de.init(diffeqpy_ode,solver_type,saveat=1/120.,abstol=1e-4,reltol=1e-4)#
			
			else:
				raise ValueError("'{}' is not a valid DER model solver type - valid solvers are:scipy,diffeqpy".format(self.der_solver_type))
			if six.PY3:
				toc = time.perf_counter()
			elif six.PY2:
				toc = time.clock()
			OpenDSSData.log(level=10,msg="{} integrator using {} method initialized at {:.3f} seconds in {:.3f} seconds".format(self.der_solver_type,self.ode_solver_method,toc,toc - tic))
			"""
			tic = time.time()
			if self.der_solver_type == "scipy":
				y=self.integrator.integrate(self.integrator.t+1/120.)
			elif self.der_solver_type == "diffeqpy":
				self.de.step_b(self.integrator,1/120.,True)
			toc = time.time()
			OpenDSSData.log(level=10,msg="{} test integration completed at {:.3f} seconds in {:.3f} seconds".format(self.der_solver_type,toc,toc - tic))
			"""
			return DNet['DER']['PVDERMap']
		except:
			OpenDSSData.log(msg="Failed Setup PVDERAGG")

#===================================================================================================
	def initialize_PQVnominal(self,node,DERModel):
		"""Initialize Pnominal and Qnominal."""
		try:
			myconfig=OpenDSSData.config['myconfig']
			initializeWithActual = myconfig['initializeWithActual']
		
			if initializeWithActual:
				DERRatingReal = DERModel.S_PCC.real*DERModel.Sbase
				DERRatingImag = DERModel.S_PCC.imag*DERModel.Sbase
		
			if myconfig['DERSetting'] == 'PVPlacement':
				 lowSideV = myconfig['DERParameters']['PVPlacement'][node]['VrmsRating'] 
				 
				 if initializeWithActual:
					 PNominal = (DERRatingReal/1e3)*\
					 myconfig['DERParameters']['PVPlacement'][node]['pvderScale']
					 QNominal = (DERRatingImag/1e3)*\
					 myconfig['DERParameters']['PVPlacement'][node]['pvderScale']
				 else:
					 PNominal = myconfig['DERParameters']['PVPlacement'][node]['powerRating']*\
					 myconfig['DERParameters']['PVPlacement'][node]['pvderScale']
					 QNominal = 0 * myconfig['DERParameters']['PVPlacement'][node]['pvderScale']
			elif myconfig['DERSetting'] == 'default':
				 lowSideV = myconfig['DERParameters']['default']['VrmsRating'] 
				 
				 if initializeWithActual:
					 PNominal = (DERRatingReal/1e3)*myconfig['DERParameters']['default']['pvderScale']
					 QNominal = (DERRatingImag/1e3)*myconfig['DERParameters']['default']['pvderScale']
				 else:
					 PNominal = myconfig['DERParameters']['default']['powerRating']*\
					 myconfig['DERParameters']['default']['pvderScale']
					 QNominal = 0 * myconfig['DERParameters']['default']['pvderScale']
		
			OpenDSSData.data['DNet']['DER']['PVDERData']['lowSideV'][node] = lowSideV
			OpenDSSData.data['DNet']['DER']['PVDERData']['PNominal'][node] = PNominal
			OpenDSSData.data['DNet']['DER']['PVDERData']['QNominal'][node] = QNominal
		except:
			OpenDSSData.log()

#===================================================================================================
	def funcval_fastder(self,t,y,nEqs=6):
		try:
			fvalue=[]
			for n in range(len(self.pvIDIndex)):
				nEqs = self._nEqs[self.pvIDIndex[n]]
				fvalue.extend(self._pvders[self.pvIDIndex[n]].func_val_combined(y[n*nEqs:(n+1)*nEqs],t))
			self.funcCalls['f']+=1

			return fvalue
		except:
			OpenDSSData.log()

	def funcval_fastder_diffeqpy(self,dy,y,p,t):
		try:
			for n in range(len(self.pvIDIndex)):
				dy[n*self._nEqs[n]:(n+1)*self._nEqs[n]] = self._pvders[self.pvIDIndex[n]].func_val_combined(y[n*self._nEqs[n]:(n+1)*self._nEqs[n]],t)
			return dy
		except:
			OpenDSSData.log()

#===================================================================================================
	def funcval(self,t,y,nEqs=23):
		try:
			fvalue=[]
			for n in range(len(self.pvIDIndex)):
				nEqs = self._nEqs[self.pvIDIndex[n]]
				fvalue.extend(self._pvders[self.pvIDIndex[n]]._pvderModel.sim.ODE_model(
				y[n*nEqs:(n+1)*nEqs],t))
			self.funcCalls['f']+=1

			return fvalue
		except:
			OpenDSSData.log()
#===================================================================================================
	def numjac(self,ffunc,x,t,eps=1e-6):
		try:
			nDim=x.shape[0]
			jac=np.zeros((nDim,nDim))
			for n in range(nDim):
				xeps=copy.deepcopy(x)
				xeps[n]+=eps
				jac[:,n]=(ffunc(xeps,t)-ffunc(x,t))/eps

			return jac
		except:
			raise

#===================================================================================================
	def jac(self,t,y,nEqs=23):
		try:
			nPVDER=len(self.pvIDIndex)
			nEqs = self._nEqs[0]
			J=np.zeros((nPVDER*nEqs,nPVDER*nEqs))# zero out at every call to avoid stray values
			for n in range(nPVDER):
				nEqs = self._nEqs[self.pvIDIndex[n]]
				thisJ=self._pvders[self.pvIDIndex[n]]._pvderModel.sim.jac_ODE_model(y,t)
				row,col=np.where(thisJ)
				J[n*nEqs+row,n*nEqs+col]=thisJ[thisJ!=0]
				self.funcCalls['jac']+=1
	
			return J
		except:
			OpenDSSData.log()

#===================================================================================================
	def funcval_diffeqpy(self,dy,y,p,t):
		try:
			for n in range(len(self.pvIDIndex)):
				dy[n*self._nEqs[n]:(n+1)*self._nEqs[n]] = self._pvders[self.pvIDIndex[n]]._pvderModel.sim.ODE_model(y[n*self._nEqs[n]:(n+1)*self._nEqs[n]],t)
			return dy
		except:
			OpenDSSData.log()

#===================================================================================================
	def jac_diffeqpy(self,J,y,p,t):
		try:
			for n in range(len(self.pvIDIndex)):
				thisJ=self._pvders[self.pvIDIndex[n]]._pvderModel.sim.jac_ODE_model(y[n*self._nEqs[n]:(n+1)*self._nEqs[n]],t)
				row,col=np.where(thisJ)
				J[n*self._nEqs[n]+row,n*self._nEqs[n]+col]=thisJ[thisJ!=0]
			return J
		except:
			OpenDSSData.log()

#===================================================================================================
	def run(self,V,Vpu,t,dt=1/120.,nEqs=23):
		try:
			if self.der_solver_type.replace('_','').replace('-','').lower()=='fastder':
				if self.ode_solver_method == 'adams':
					P,Q,x=self._run_fast_combined(V=V,Vpu=Vpu,t=t,dt=dt)
				else:
					P,Q,x=self._run_fast(V=V,Vpu=Vpu,t=t,dt=dt)
			else:
				P,Q=self._run_detailed(V=V,Vpu=Vpu,nEqs=nEqs,t=t,dt=dt)
				x={}

			return P,Q,x
		except:
			OpenDSSData.log(msg="Failed run the pvder aggregated model")

#===================================================================================================
	def _run_fast(self,V,Vpu,t=None,dt=1/120.):
		try:
			P = {}
			Q = {}
			x={}
			# prerun for all pvder instances at this node
			for node in OpenDSSData.data['DNet']['DER']['PVDERMap']:# compute solar inj at each node
				lowSideNode='{}_tfr'.format(node)

				Va = Vpu[lowSideNode]['a']
				Vb = Vpu[lowSideNode]['b']
				Vc = Vpu[lowSideNode]['c']

				nodeP=0; nodeQ=0
				for pv in OpenDSSData.data['DNet']['DER']['PVDERMap'][node]:
					nSolar_at_this_node=\
					OpenDSSData.data['DNet']['DER']['PVDERMap'][node]['nSolar_at_this_node']
					if pv!='nSolar_at_this_node':
						pvID=OpenDSSData.data['DNet']['DER']['PVDERMap'][node][pv]
						thisPV=self._pvders[pvID]
						
						# compute initial condition
						thisT=thisPV._integrator_data['time_values'][-1]
						if thisT==0:
							thisConf={}
							thisConf['vref']=abs(Va)
							thisConf['vref_ang']=np.angle(Va)
							thisConf['pref']=thisPV.data['config']['pref']
							thisConf['qref']=thisPV.data['config']['qref']
							thisPV.compute_initial_condition(thisConf['pref'],\
							thisConf['qref'],thisConf['vref'],thisConf['vref_ang'])

						# update Voltage injection
						thisPV.update_model(Va)
						
						# integrate
						thisPV.integrate(dt=dt)
						thisId=thisPV.x[2]
						thisIq=thisPV.x[5]
						thisVd=thisPV.data['model']['vd']
						thisVq=thisPV.data['model']['vq']
						nodeP-=thisVd*thisId*thisPV.data['config']['sbase'] # -ve load => generation
						nodeQ-=-thisVd*thisIq*thisPV.data['config']['sbase']
						if node not in x:
							x[node]={}
						if pv not in x[node]:
							x[node][pv]={}
						x[node][pv]=copy.deepcopy(thisPV.x).tolist()
				
				P[node]=nodeP
				Q[node]=nodeQ
				OpenDSSData.data['DNet']['DER']['PVDERData'][node]['Vmag']['a']=Va
				OpenDSSData.data['DNet']['DER']['PVDERData'][node]['Vmag']['b']=Vb
				OpenDSSData.data['DNet']['DER']['PVDERData'][node]['Vmag']['c']=Vc

			return P,Q,x
		except:
			OpenDSSData.log(msg="Failed run the fast pvder aggregated model")

#===================================================================================================
	def _run_fast_combined(self,V,Vpu,t=None,dt=1/120.):
		try:
			P = {}
			Q = {}
			x={}
			# prerun for all pvder instances at this node
			for node in OpenDSSData.data['DNet']['DER']['PVDERMap']:# compute solar inj at each node
				lowSideNode='{}_tfr'.format(node)

				Va = Vpu[lowSideNode]['a']
				Vb = Vpu[lowSideNode]['b']
				Vc = Vpu[lowSideNode]['c']

				for pv in OpenDSSData.data['DNet']['DER']['PVDERMap'][node]:
					
					if pv!='nSolar_at_this_node':
						pvID=OpenDSSData.data['DNet']['DER']['PVDERMap'][node][pv]
						thisPV=self._pvders[pvID]
						
						# compute initial condition
						thisT=thisPV._integrator_data['time_values'][-1]
						if self.integrator.t==0.0:
							thisConf={}
							thisConf['vref']=abs(Va)
							thisConf['vref_ang']=np.angle(Va)
							thisConf['pref']=thisPV.data['config']['pref']
							thisConf['qref']=thisPV.data['config']['qref']
							thisPV.compute_initial_condition(thisConf['pref'],\
							thisConf['qref'],thisConf['vref'],thisConf['vref_ang'])

						# update Voltage injection
						thisPV.update_model(Va)
						thisPV.ride_through_logic(vmag=thisPV.x[3],dt=1/120.)
			
			if self.integrator.t==0.0:
				y0=[]; t0=0.0
				for n in range(len(self.pvIDIndex)):
					y0.extend(self._pvders[self.pvIDIndex[n]].x)
				self.integrator.set_initial_value(y0,t0)
				OpenDSSData.log(level=10,msg="FastDER model:integrator y0 at t=={}:{}".format(self.integrator.t,self.integrator.y))
				
			#integrate
			y=self.integrator.integrate(self.integrator.t+dt)
			
			if not self.integrator.successful():
				raise ValueError("Integration was not successul with return code:{}".format(self.integrator.get_return_code()))
			
			for node in OpenDSSData.data['DNet']['DER']['PVDERMap']:# compute solar inj at each node
				nodeP=0; nodeQ=0
				for pv in OpenDSSData.data['DNet']['DER']['PVDERMap'][node]:
					if pv!='nSolar_at_this_node':
						pvID=OpenDSSData.data['DNet']['DER']['PVDERMap'][node][pv]
						thisPV=self._pvders[pvID]
						thisT=thisPV._integrator_data['time_values'][-1]
						thisId=thisPV.x[2]
						thisIq=thisPV.x[5]
						thisVd=thisPV.data['model']['vd']
						thisVq=thisPV.data['model']['vq']
						
						nodeP-=thisVd*thisId*thisPV.data['config']['sbase'] # -ve load => generation
						nodeQ-=-thisVd*thisIq*thisPV.data['config']['sbase']
						if node not in x:
							x[node]={}
						if pv not in x[node]:
							x[node][pv]={}
						x[node][pv]=copy.deepcopy(thisPV.x).tolist()
				
				P[node]=nodeP
				Q[node]=nodeQ
				OpenDSSData.data['DNet']['DER']['PVDERData'][node]['Vmag']['a']=Va
				OpenDSSData.data['DNet']['DER']['PVDERData'][node]['Vmag']['b']=Vb
				OpenDSSData.data['DNet']['DER']['PVDERData'][node]['Vmag']['c']=Vc

			return P,Q,x
		except:
			OpenDSSData.log(msg="Failed run the fast pvder aggregated model")

#===================================================================================================
	def _run_detailed(self,V,Vpu,nEqs=23,t=0,dt=1/120.):
		try:
			P = {}
			Q = {}
			# prerun for all pvder instances at this node
			for node in OpenDSSData.data['DNet']['DER']['PVDERMap']:# compute solar inj at each node
				lowSideNode='{}_tfr'.format(node)
				Va = V[lowSideNode]['a']
				Vb = V[lowSideNode]['b']
				Vc = V[lowSideNode]['c']
 
				nodeP=0; nodeQ=0
				for pv in OpenDSSData.data['DNet']['DER']['PVDERMap'][node]:
					if pv!='nSolar_at_this_node':
						pvID=OpenDSSData.data['DNet']['DER']['PVDERMap'][node][pv]
						thisPV=self._pvders[pvID]
						thisPV.prerun(Va,Vb,Vc)
						#if self.integrator.t == 0.0:
						#	thisPV._pvderModel.PV_model.steady_state_calc() #Initialization is not perfect for some reason
			if self.integrator.t == 0.0:
				tic = time.time()
				for i in range(600): #600 half-cycles = 5 s.
					if self.der_solver_type == "scipy":
						y=self.integrator.integrate(self.integrator.t+dt)
						if not self.integrator.get_return_code() > 0:
							raise ValueError("Integration was not successful with return code:{}".format(self.integrator.get_return_code()))
					elif self.der_solver_type == "diffeqpy":
						self.de.step_b(self.integrator,dt,True)
						if not self.de.check_error(self.integrator) == 'Success':
							raise ValueError("Integration was not successful with return code:{}".format(self.de.check_error(self.integrator)))
				toc = time.time()
				OpenDSSData.log(level=20,msg="Integrator time after pre-run:{:.3f} s".format(self.integrator.t))
				OpenDSSData.log(level=10,msg="Time taken to do pre-run:{:.3f} s".format(toc - tic))
			# single large integrator for all pvder instances
			if self.der_solver_type == "scipy":
				y=self.integrator.integrate(self.integrator.t+dt)
				if not self.integrator.get_return_code() > 0:
					raise ValueError("Integration was not successul with return code:{}".format(self.integrator.get_return_code()))
			elif self.der_solver_type == "diffeqpy":
				self.de.step_b(self.integrator,dt,True)
				y = self.integrator.u
				if not self.de.check_error(self.integrator) == 'Success':
					raise ValueError("Integration was not successul with return code:{}".format(self.de.check_error(self.integrator)))

			# postrun for all pvder instances
			for node in OpenDSSData.data['DNet']['DER']['PVDERMap']:# compute solar inj at each node
				sP=0; sQ=0
				for pv in OpenDSSData.data['DNet']['DER']['PVDERMap'][node]:
					if pv!='nSolar_at_this_node':
						pvID=OpenDSSData.data['DNet']['DER']['PVDERMap'][node][pv]
						assert pvID in self.pvIDIndex, "pvID not found in self.pvIDIndex"
						nEqs = self._nEqs[pvID]
						thisPV=self._pvders[pvID]
						n=self.pvIDIndex.index(pvID)
						sol=np.append(thisPV._pvderModel.lastSol,y[n*nEqs:(n+1)*nEqs])
						sol=sol.reshape((-1,nEqs))
						val=thisPV.postrun(sol,[self.integrator.t-dt,self.integrator.t])
						sP-=val.real# -ve load => generation
						sQ-=val.imag
				P[node] = sP
				Q[node] = sQ
				OpenDSSData.data['DNet']['DER']['PVDERData'][node]['Vmag']['a']=Va
				OpenDSSData.data['DNet']['DER']['PVDERData'][node]['Vmag']['b']=Vb
				OpenDSSData.data['DNet']['DER']['PVDERData'][node]['Vmag']['c']=Vc

			return P, Q
		except:
			OpenDSSData.log(msg="Failed run the detailed pvder aggregated model")
