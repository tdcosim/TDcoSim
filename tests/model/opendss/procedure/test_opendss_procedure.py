from __future__ import division
import sys
import os
import math
import argparse

import matplotlib.pyplot as plt
import unittest

import tdcosim
from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.procedure.opendss_procedure import OpenDSSProcedure
from tdcosim.test import der_test_manual_config


dirlocation= os.path.dirname(tdcosim.__file__)
dirlocation = dirlocation[0:len(dirlocation)-8]
print('Home directory:{}'.format(dirlocation))

OpenDSSData.config['myconfig'] = der_test_manual_config.test_config

S_load = [70000.0, 23000.0]
Vpcc0=0.9868730306625366
tol=1e-05

def suite():
	"""Define a test suite."""
	
	tests = test_options.options #['LVRT1'] #,,'LVRT2','LVRT3'
	print('Following unittest scenarios will be run:{}'.format(tests))
	suite = unittest.TestSuite()
	
	for test in tests:
		suite.addTest(TestOpenDSSProcedure('test_OpenDSS_'+ test))
											   
	return suite

class TestOpenDSSProcedure(unittest.TestCase):
	
	test_scenarios = { 'LVRT1':{'LVRT_ENABLE':True,'tfault_start':4.0,'tfault_duration':0.5},
					   'LVRT2':{'LVRT_ENABLE':True,'tfault_start':4.0,'tfault_duration':2.0},
					   'LVRT3':{'LVRT_ENABLE':True,'tfault_start':4.0,'tfault_duration':2.0}}					   
	   
	
	def test_OpenDSS_LVRT1(self):
		"""Test PV-DER + OpenDSS procedure with LVRT."""
			
		self.opendss_model = OpenDSSProcedure()
		self.opendss_model.setup()
		self.opendss_model.initialize(targetS=S_load,Vpcc=Vpcc0,tol=1e-05)
		
		self.check_num_solar_instances()
			   
		n_time_steps,t_t,Pfeeder_t,Qfeeder_t = self.run_simulation(tEnd = 10.0,scenario='LVRT1')		
		
		self.loop_and_check(n_time_steps)
		self.plot_feeder_loads(t_t,Pfeeder_t,Qfeeder_t)
	
	def test_OpenDSS_LVRT2(self):
		"""Test PV-DER + OpenDSS procedure with LVRT."""
			
		self.opendss_model = OpenDSSProcedure()
		self.opendss_model.setup()
		self.opendss_model.initialize(targetS=S_load,Vpcc=Vpcc0,tol=1e-05)
		
		self.check_num_solar_instances()
		
		n_time_steps,t_t,Pfeeder_t,Qfeeder_t = self.run_simulation(tEnd = 10.0,scenario='LVRT2')		
		
		self.loop_and_check(n_time_steps)
		self.plot_feeder_loads(t_t,Pfeeder_t,Qfeeder_t)		
	
	def test_OpenDSS_LVRT3(self):
		"""Test PV-DER + OpenDSS procedure with LVRT."""
			
		self.opendss_model = OpenDSSProcedure()
		self.opendss_model.setup()
		self.opendss_model.initialize(targetS=S_load,Vpcc=Vpcc0,tol=1e-05)
		
		self.check_num_solar_instances()
		
		n_time_steps,t_t,Pfeeder_t,Qfeeder_t = self.run_simulation(tEnd = 10.0,scenario='LVRT3')		
		
		self.loop_and_check(n_time_steps)
		self.plot_feeder_loads(t_t,Pfeeder_t,Qfeeder_t)  
		
	def check_num_solar_instances(self):
		"""Test PV-DER + OpenDSS procedure with LVRT."""
		
		nSolar = 0
		node_list = []
		for node in OpenDSSData.data['DNet']['DER']['PVDERMap']:
			nSolar = nSolar + OpenDSSData.data['DNet']['DER']['PVDERMap'][node]['nSolar_at_this_node']
			node_list.append(node)
		
		self.assertTrue(nSolar==len(self.opendss_model._pvderAggProcedure._pvderAggModel._pvders), msg='Expected number of PV-DER instances is {}, but actual number of PV-DER instances is {}!'.format(nSolar,len(self.opendss_model._pvderAggProcedure._pvderAggModel._pvders)))
		
		print('Number of PV-DER instances:{}'.format(nSolar))
		print('Nodes to which PV-DER instances were connected:{}'.format(node_list))		
	
	def specify_scenario(self,scenario='LVRT1'):
		"""Specify scenario for unit test."""
		
		self.tfault_start = self.test_scenarios[scenario]['tfault_start'] 
		self.tfault_duration = self.test_scenarios[scenario]['tfault_duration'] 
		
		for pvder in self.opendss_model._pvderAggProcedure._pvderAggModel._pvders:
			pvder_object =  self.opendss_model._pvderAggProcedure._pvderAggModel._pvders[pvder]._pvderModel.PV_model
			
			pvder_object.LVRT_ENABLE = self.test_scenarios[scenario]['LVRT_ENABLE']  
		   
	
	def run_simulation(self,tEnd = 3.0,scenario='LVRT1'):
		"""Test PV-DER + OpenDSS procedure with LVRT."""
		
		Pfeeder_t=[]
		Qfeeder_t=[]
		t_t=[0.0]
		dt=1/120
		tEnd = tEnd		
		
		pccName='Vsource.source'
		Vfault = 0.8
		Vnominal = 1.0
		
		self.specify_scenario(scenario=scenario)

		n_time_steps = int(tEnd/(1/120.0))
		
		while t_t[-1]<tEnd-1e-3:
			
			if t_t[-1] >= self.tfault_start and t_t[-1] < self.tfault_start + dt:
				print('Decreasing voltage to {} V at {} s'.format(Vfault,self.tfault_start))
				self.opendss_model.setVoltage(Vpu=Vfault,Vang=0.0,pccName=pccName)
			
			if t_t[-1] >= self.tfault_start + self.tfault_duration and t_t[-1] < self.tfault_start + self.tfault_duration + dt:
				print('Restoring voltage from {} V to {} V at {} s'.format(Vfault,Vnominal,self.tfault_start))
				self.opendss_model.setVoltage(Vpu=Vnominal,Vang=0.0,pccName=pccName)
			
			Pfeeder,Qfeeder,flag,derX = self.opendss_model.getLoads(pccName=pccName)
			print('{:.2f}:{}-Pfeeder:{:.2f}'.format(t_t[-1],scenario,Pfeeder))
			if flag:
				Pfeeder_t.append(Pfeeder)
				Qfeeder_t.append(Qfeeder)
				t_t.append(t_t[-1]+dt)
			else:
				print('Convergence failure - exiting')
				break
				
		return n_time_steps,t_t,Pfeeder_t,Qfeeder_t		 
	
	def loop_and_check(self,n_time_steps):
		"""Loop trhough DER instances and check."""
		
		for pvder in self.opendss_model._pvderAggProcedure._pvderAggModel._pvders:
			pvder_object =  self.opendss_model._pvderAggProcedure._pvderAggModel._pvders[pvder]._pvderModel.PV_model
			sim_object =  self.opendss_model._pvderAggProcedure._pvderAggModel._pvders[pvder]._pvderModel.sim
			results_object =  self.opendss_model._pvderAggProcedure._pvderAggModel._pvders[pvder]._pvderModel.results
			
			for convergence_failure in sim_object.convergence_failure_list:
				print('Failure event:{}'.format(convergence_failure))
			
			self.show_DER_status(pvder_object)
			self.check_DER_state(pvder_object)
			#self.plot_DER_trajectories(results_object)
			 
			#self.assertTrue(len(sim_object.t_t) == len(sim_object.Vdc_t) == n_time_steps+1, msg='{}:The number of states collected should be {} but it is actually {}!'.format(sim_object.name,n_time_steps+1,len(sim_object.t_t)))

			self.check_LVRT_status(pvder_object)
	
	def check_DER_state(self,pvder_object):
		"""Check whether DER states are nominal."""
		
		#Check if DC link voltage within inverter limits.
		self.assertTrue(pvder_object.Vdc*pvder_object.Vdcbase >= pvder_object.Vdcmpp_min or pvder_object.Vdc*pvder_object.Vdcbase <= pvder_object.Vdcmpp_max, msg='{}:DC link voltage {:.2f} V exceeded limit!'.format(pvder_object.name,pvder_object.Vdc*pvder_object.Vdcbase))
		
		#Check current reference output within inverter limits.
		self.assertTrue(abs(pvder_object.ia_ref)<= pvder_object.iref_limit, msg='{}:Inverter current exceeded limit by {:.2f} A!'.format(pvder_object.name,(abs(pvder_object.ia_ref) - pvder_object.iref_limit)*pvder_object.Ibase))
		
		#Check power output within inverter limits.
		self.assertTrue(abs(pvder_object.S_PCC)<=pvder_object.Sinverter_nominal, msg='{}:Inverter power output exceeded limit by {:.2f}  VA!'.format(pvder_object.name,(abs(pvder_object.S_PCC) -pvder_object.Sinverter_nominal)*pvder_object.Sbase))
	
	def check_LVRT_status(self,pvder_object):
		"""Check whether ride through is working."""
		
		if pvder_object.DER_TRIP: #Check if DER trip flag is True
			#Check if LVRT momentary cessation is True is connected
			self.assertTrue(pvder_object.LVRT_TRIP, msg='{}: LVRT trip should be true!'.format(pvder_object.name))
			#Check if DER is connected
			self.assertFalse(pvder_object.DER_CONNECTED, msg='{}: DER connected despite trip!'.format(pvder_object.name))
			#Check if DER stopped supplying power
			self.assertAlmostEqual(abs(pvder_object.S_PCC), 0.0, places=4, msg='{}:Inverter power output is {:.2f} VA despite trip status!'.format(pvder_object.name,pvder_object.S_PCC*pvder_object.Sbase))
			#Check if DC link voltage limits are breached
			self.assertTrue(pvder_object.Vdc*pvder_object.Vdcbase >= pvder_object.Vdcmpp_min or pvder_object.Vdc*pvder_object.Vdcbase <= pvder_object.Vdcmpp_max, msg='{}:DC link voltage exceeded limits!'.format(pvder_object.name))
				
		elif pvder_object.DER_MOMENTARY_CESSATION:
			#Check if LVRT momentary cessation is True is connected
			self.assertTrue(pvder_object.LVRT_MOMENTARY_CESSATION, msg='{}: LVRT momentary cessation should be true!'.format(pvder_object.name))
			#Check if DER is connected
			self.assertFalse(pvder_object.DER_CONNECTED, msg='{}: DER connected despite momentary cessation!'.format(pvder_object.name))
				 
	def show_DER_status(self,pvder_object):
		"""Show DER states."""	 
		
		pvder_object.show_PV_DER_states(quantity='power')
		pvder_object.show_PV_DER_states(quantity='current')
		pvder_object.show_PV_DER_states(quantity='voltage')				
		pvder_object.show_PV_DER_states(quantity='duty cycle')
		pvder_object.show_RT_settings(settings_type='LVRT')	
	
	def plot_DER_trajectories(self,results_object):
		"""PLot DER trajectory."""
		
		results_object.PER_UNIT = False
		results_object.PLOT_TITLE = True
		results_object.font_size = 18
		
		results_object.plot_DER_simulation(plot_type='active_power_Ppv_Pac_PCC')#
		results_object.plot_DER_simulation(plot_type='reactive_power')
		results_object.plot_DER_simulation(plot_type='current')
		results_object.plot_DER_simulation(plot_type='voltage_Vdc')
		results_object.plot_DER_simulation(plot_type='voltage_LV')
		results_object.plot_DER_simulation(plot_type='duty_cycle')		   
	
	def plot_feeder_loads(self,t_t,Pfeeder_t,Qfeeder_t,show_plot=True):
		"""Plot feeder loads."""
		
		plt.plot(t_t[1::],Pfeeder_t)
		plt.ylabel('Active load (kW)',weight = "bold", fontsize=12)
		plt.xlabel('Time (s)',weight = "bold", fontsize=12)
		if show_plot:
		   plt.show()

		plt.plot(t_t[1::],Qfeeder_t)
		plt.ylabel('Reactive load (kVAR)',weight = "bold", fontsize=12)
		plt.xlabel('Time (s)',weight = "bold", fontsize=12)
		if show_plot:
		   plt.show()

parser = argparse.ArgumentParser(description='Unit tests for LVRT operation in OpenDSS - PVDER simulation.')

test_options = TestOpenDSSProcedure.test_scenarios.keys()
test_options.sort()
parser.add_argument('-i', '--item', action='store', dest='options',
					type=str, nargs='*', default=test_options,choices=test_options,
					help="Examples: -i LVRT1 LVRT2, -i LVRT3")
test_options = parser.parse_args()
		
if __name__ == '__main__':
		
	runner = unittest.TextTestRunner()
	runner.run(suite())
