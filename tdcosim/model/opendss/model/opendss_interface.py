import os
import math
import pdb
import time

import six
import numpy as np
import win32com.client

from tdcosim.model.opendss.opendss_data import OpenDSSData


class OpenDSSInterface(object):
	def __init__(self):
		try:
			startingDir=os.getcwd()
			self._engine = win32com.client.Dispatch("OpenDSSEngine.DSS")
			os.chdir(startingDir)  
			self.busname2ind={}
			self._stats={'getVoltage':0,'getS':0,'setVoltage':0}
			if self._engine.Start("0") == True:#DSS started OK
				self.flg_startComm=1 # pass
				self.Circuit=self._engine.ActiveCircuit

				self.Text = self._engine.Text
				self.Solution = self.Circuit.Solution
				self.CktElement = self.Circuit.ActiveCktElement
				self.Bus = self.Circuit.ActiveBus
				self.Meters = self.Circuit.Meters
				self.PDElement = self.Circuit.PDElements
				self.Loads = self.Circuit.Loads
				self.Lines = self.Circuit.Lines
				self.Transformers = self.Circuit.Transformers
				self.Monitors = self.Circuit.Monitors
				self.startingDir=os.getcwd()
				self.__enumerations()# populate enumerations
				self.K=1 # initial scaling is 1
				self.unitConversion=1 # initial unit conversion is 1
			else:
				OpenDSSData.log(level=50,msg="DSS Failed to Connect")
				exit(1)
		except:
			OpenDSSData.log()

#===================================================================================================
	def __enumerations(self):
		try:
			self.enum={}
			mode=self.enum['solutionMode']={}

			modes=['Snap','Daily','Yearly','MI','LD1','Peakday','DUtycycle','DIrect','MF',\
			'FaultStudy','M2','M3','LD2','Autoadd','Dynamic','Harmonic']

			for n in range(0,len(modes)):
				mode[modes[n]]=n
		except:
			OpenDSSData.log("Failed Enumeration")

#===================================================================================================
	def setup(self):
		try:
			# Always a good idea to clear the DSS before loading a new circuit
			self._engine.ClearAll()			

			#			self.Text.Command = "compile [" + self.fname + "]"
			self.Text.Command = "Redirect [" + OpenDSSData.config['myconfig']['filePath'][0] + "]"
			os.chdir(self.startingDir)# openDSS sets dir to data dir, revert back

			# once loaded find the base load			
			self.S0=self.getLoads()	
		except:
			OpenDSSData.log ("Failed to setup OpenDSS")

#===================================================================================================
	def setupDER(self, pvdermap):	
		try: 
			# for each node where there is pvder, create a bus,
			# attach high side of tfr to that bus and low side of tfr to
			# the node in pvderMap. pv is attached as a negative load (generator)
			# to the low side of the tfr.
			V=self.getVoltage(vtype='actual')
			Vpu=self.getVoltage(vtype='pu')

			for node in pvdermap:
				thisTransformer="Transformer.{}_pvder".format(node)
				lowSideV=OpenDSSData.data['DNet']['DER']['PVDERData']['lowSideV'][node]*math.sqrt(3)*1e-3
				self.Text.Command="New {}  Phases=3   Windings=2  XHL=1".format(thisTransformer)
				self._changeObj([[thisTransformer,'Wdg',1,'set']])# set for winging 1
				self._changeObj([   [thisTransformer,'Conn','wye','set'],
									[thisTransformer,'Kv',lowSideV,'set'],
									[thisTransformer,'Kva',1000,'set'],
									[thisTransformer,'%r',.1,'set'],
									[thisTransformer,'XHL',1,'set'],
									[thisTransformer,'bus','{}_tfr'.format(node),'set']
								])# will create a new bus

				highSideV = math.ceil(abs(V[node]['a']) * abs(1/Vpu[node]['a'])*math.sqrt(3))*1e-3

				self._changeObj([[thisTransformer,'Wdg',2,'set']])# set for winging 2
				self._changeObj([   [thisTransformer,'Conn','wye','set'],
									[thisTransformer,'Kv',highSideV,'set'],
									[thisTransformer,'Kva',100,'set'],
									[thisTransformer,'%r',.1,'set'],
									[thisTransformer,'XHL',1,'set'],
									[thisTransformer,'bus',node,'set']
								]) # high side to existing bus

				nSolar_at_this_node=OpenDSSData.data['DNet']['DER']['PVDERData']['nSolar_at_this_node'][node]
				kv=lowSideV
				kw=-OpenDSSData.data['DNet']['DER']['PVDERData']['PNominal'][node]*nSolar_at_this_node #-ve load=>gen
				kvar=-OpenDSSData.data['DNet']['DER']['PVDERData']['QNominal'][node]*nSolar_at_this_node
				directive='New Load.{}_pvder Bus1={}_tfr Phases=3 Conn=Wye '.format(node,node)
				directive+='Model=1 kV={} kW={} kvar={} '.format(kv,kw,kvar)
				directive+='vminpu=0.5 vmaxpu=1.2 vlowpu=0.0'# connect to low side bus of tfr
				self.Text.Command=directive

			# buses are not instantiated until required buy opendss.
			# Force bus instantiation and then compute voltage bases.
			self.Text.Command="MakeBusList"
			self.Text.Command="CalcVoltageBases"

			# update
			for n in range(0,self.Circuit.NumBuses):
				self.busname2ind[self.Circuit.Buses(n).Name]=n
		except:
			OpenDSSData.log("Failed setupDER in OpenDSS Interface")

#===================================================================================================
	def getLoads(self):
		"""Get the load setting for every load in the system. Please note that this 
		is not the actual load consumed. To get that you need a meter at the load bus.
		All values are reported in KW and KVar"""
		try:
			S={}
			S['P']={}
			S['Q']={}
			self.Loads.First # start with the first load in the list
			for n in range(0,self.Loads.Count):
				S['P'][self.Loads.Name],S['Q'][self.Loads.Name] = self.Loads.kW,self.Loads.kvar
				self.Loads.Next # move to the next load in the system

			return S
		except:
			OpenDSSData.log ("Failed Get Loads in OpenDSS Interface")

#===================================================================================================
	def getVoltage(self,vtype='actual',busID=None):
		"""Needs to be called after solve. Gathers Voltage (complex) of all buses into a,b,c phases
		and populates a dictionary and returns it."""
		try:
			Voltage={}
			entryMap={}
			entryMap['1']='a'
			entryMap['2']='b'
			entryMap['3']='c'

			if not busID:
				for n in range(0,self.Circuit.NumBuses):
					Voltage[self.Circuit.Buses(n).Name]={}
					if vtype=='actual':
						V=self.Circuit.Buses(n).Voltages
					elif vtype=='pu':
						V=self.Circuit.Buses(n).puVoltages

					count=0
					for entry in self.Circuit.Buses(n).Nodes:
						Voltage[self.Circuit.Buses(n).Name][entryMap[str(int(entry))]]=\
						V[count]+1j * V[count+1]
						count+=2
			else:
				assert isinstance(busID,list) or isinstance(busID,tuple),'busID: {}'.format(busID)
				for entry in busID:
					Voltage[entry]={}
					if vtype=='actual':
						V=self.Circuit.Buses(self.busname2ind[entry]).Voltages
					elif vtype=='pu':
						V=self.Circuit.Buses(self.busname2ind[entry]).puVoltages

					count=0
					for item in self.Circuit.Buses(self.busname2ind[entry]).Nodes:
						Voltage[entry][entryMap[str(int(item))]]=\
						V[count]+1j*V[count+1]
						count+=2

			return Voltage
		except:
			OpenDSSData.log('Failed Get Voltage in OpenDSS Interface')

#===================================================================================================
	def _changeObj(self,objData):
		"""set/get an object property.
		Input: objData should be a list of lists of the format,
		[[objName,objProp,objVal,flg],...]

		objName -- name of the object.
		objProp -- name of the property.
		objVal -- val of the property. If flg is set as 'get', then objVal is not used.
		flg -- Can be 'set' or 'get'

		P.S. In the case of 'get' use a value of 'None' for objVal. The same object i.e.
		objData that was passed in as input will have the result i.e. objVal will be
		updated from 'None' to the actual value.

		Sample call: self._changeObj([['PVsystem.pv1','kVAr',25,'set']])
		self._changeObj([['PVsystem.pv1','kVAr','None','get']])
		"""
		try:
			for entry in objData:
				self.Circuit.SetActiveElement(entry[0])# make the required element as active element

				if entry[-1]=='set':
					self.CktElement.Properties(entry[1]).Val=entry[2]
				elif entry[-1]=='get':
					entry[2]=self.CktElement.Properties(entry[1]).Val
		except:
			OpenDSSData.log("Failed changeobj")

#===================================================================================================
	def initialize(self, Vpcc, targetS, tol): 
		try:
			dQ=10.0 # in kvar
			maxIter=200
			dQChange=0
			iterCount=0
			currentPF = 0
			targetPF = 0
			self.Solution.Solve()
			self.setVoltage(Vpcc)

			P,Q,convergedFlg=self.getS() # override pvder dynamic model

			if convergedFlg:
				targetPF=np.cos(np.angle(np.complex(targetS[0],targetS[1])))
				currentPF=np.cos(np.angle(np.complex(P,Q)))

			while abs(currentPF-targetPF)>tol and iterCount<maxIter and convergedFlg:

				if dQChange>abs(currentPF-targetPF):# reduce dQ if needed
					dQ=dQ/2
				self.Loads.First # start with the first load in the list
				for n in range(0,self.Loads.Count):
					if '_pvder' not in self.Loads.Name:# don't scale pvder
						if currentPF>targetPF and self.Loads.kvar!=0: # increase Q
							self.Loads.kvar=self.Loads.kvar+dQ
						elif currentPF<targetPF and self.Loads.kvar!=0: # reduce Q
							self.Loads.kvar=self.Loads.kvar-dQ
					self.Loads.Next # move to the next load in the system
				P,Q,convergedFlg=self.getS()
				if convergedFlg:
					currentPFNew=np.cos(np.angle(np.complex(P,Q)))
					dQChange=abs(currentPF-currentPFNew)
					currentPF=currentPFNew
					iterCount+=1	  

			# find scaling
			if convergedFlg:
				self.K=targetS[0]/P # scaling
				self.unitConversion=10**3*10**-6 # convert from kW to watt and then to MW
			else:
				print("power flow solve diverged. Using base case to find K with mismatch on Q.")
				self.setup()# reload the case
				self.K=1
				P,Q,flg=self.getS()
				if flg:
					self.K=targetS[0]/P
					self.unitConversion=10**3*10**-6
				else:
					print("OpenDSS Input File is not able to converge")
					exit(1)

			#return P, Q, convergedFlg
			return self.K*P*self.unitConversion,self.K*Q*self.unitConversion, convergedFlg
		except:
			OpenDSSData.log("Failed initialSolve in OpenDSS Interface")

#===================================================================================================
	def setVoltage(self,Vpu,Vang=0,pccName='Vsource.source'):
		try:
			self._changeObj([[pccName,'pu',Vpu,'set'],[pccName,'angle',Vang,'set']])
		except:
			OpenDSSData.log('Failed to Set Voltage to OpenDSS')

#===================================================================================================
	def getS(self, pccName='Vsource.source'):
		try:
			self.Solution.Solve()
			if self.Solution.Converged:
				self.Circuit.SetActiveElement(pccName)
				# -ve sign convention
				P,Q=self.Circuit.ActiveCktElement.SeqPowers[2]*-1,\
				self.Circuit.ActiveCktElement.SeqPowers[3]*-1

				# scale P and Q
				P=self.K*P*self.unitConversion
				Q=self.K*Q*self.unitConversion
			else:
				P,Q=None,None

			return P,Q,self.Solution.Converged
		except:
			OpenDSSData.log('Failed to get S from OpenDSS')

#===================================================================================================
	def pvderInjection(self, derP, derQ, busID=None):
		try:
			V=self.getVoltage(vtype='actual',busID=busID)# this will get the last known solution
			P_pv=0; Q_pv=0
			myconfig=OpenDSSData.config['myconfig']

			# compute solar injection at each node
			for node in OpenDSSData.data['DNet']['DER']['PVDERMap']:
				if myconfig['DERSetting'] == 'PVPlacement':
					pvderScale=myconfig['DERParameters']['PVPlacement'][node]['pvderScale']
				elif myconfig['DERSetting'] == 'default':
					pvderScale=myconfig['DERParameters']['default']['pvderScale']
				else:
					raise ValueError('{} is an invalid DER setting!'.format(myconfig['DERSetting']))

				P=derP[node]
				Q=derQ[node]

				# now update the injection
				directive='Edit Load.{}_pvder kW={} kvar={}'.format(node, P*pvderScale, Q*pvderScale)
				self.Text.Command=directive

				P_pv+=P*pvderScale
				Q_pv+=Q*pvderScale

			OpenDSSData.data['DNet']['DER']['PVDERData']['P']=P_pv
			OpenDSSData.data['DNet']['DER']['PVDERData']['Q']=Q_pv
		except:
			OpenDSSData.log('Failed to pvderInjection from OpenDSS Interface')

#===================================================================================================
	def scaleLoad(self,scale):
		"""Sets the load shape by scaling each load in the system with a scaling
			factor scale.
			Input: scale -- A scaling factor for loads such that P+j*Q=scale*(P0+j*Q0)
			P.S. loadShape should be called at every dispatch i.e. only load(t) is set.
			"""
		try:
			self.Loads.First # start with the first load in the list
			for n in range(0,self.Loads.Count):
				self.Loads.kW=self.S0['P'][self.Loads.Name]*scale
				self.Loads.kvar=self.S0['Q'][self.Loads.Name]*scale
				self.Loads.Next # move to the next load in the system
		except:
			OpenDSSData.log('Failed to complete scaleload from OpenDSS Interface')

#===================================================================================================
	def monitor(self,varName):
		try:
			res={}
			if 'voltage' in varName:
				V=self.getVoltage(vtype='pu')
				# cannot JSON serialize complex number, convert to mag and ang
				Vmag={}; Vang={}
				for node in V:
					Vmag[node]={}; Vang[node]={}
					for phase in V[node]:
						Vmag[node][phase]=np.abs(V[node][phase])
						Vang[node][phase]=np.angle(V[node][phase])
				res['Vmag']=Vmag; res['Vang']=Vang
			if 'der' in varName or 'DER' in varName:
				res['der']={}
				for node in OpenDSSData.data['DNet']['DER']['PVDERMap']:
					res['der'][node]={}
					qry=[]
					qry.append(['Load.{}_pvder'.format(node),'kW','None','get'])
					qry.append(['Load.{}_pvder'.format(node),'kvar','None','get'])
					self._changeObj(qry)
					res['der'][node]['P']=-float(qry[0][2])#-ve load => gen
					res['der'][node]['Q']=-float(qry[1][2])#-ve load => gen
			if 'voltage_der' in varName or 'DER' in varName:
				busID=OpenDSSData.data['DNet']['DER']['PVDERMap'].keys()
				if six.PY3:
					busID=list(busID)
				if busID:# only if DERs are present
					V=self.getVoltage(vtype='pu',busID=busID)
					# cannot JSON serialize complex number, convert to mag and ang
					Vmag={}; Vang={}
					for node in V:
						Vmag[node]={}; Vang[node]={}
						for phase in V[node]:
							Vmag[node][phase]=np.abs(V[node][phase])
							Vang[node][phase]=np.angle(V[node][phase])
					res['Vmag']=Vmag; res['Vang']=Vang

			return res
		except:
			OpenDSSData.log('Failed to complete scaleload from OpenDSS Interface')


