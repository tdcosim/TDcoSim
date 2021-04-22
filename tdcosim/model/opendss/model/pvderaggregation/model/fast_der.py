import os
import json
import copy
import pdb

import numpy as np
from scipy.optimize import fsolve


class FastDER(object):
	"""Sample call: 
	conf={'vref_ang': 0.16196655458507378, 'vref': 1.025, 'pref': 1.63, 'qref': 0.0665}
	foo=DER(**{'config':conf})
	foo.compute_initial_condition(1.63,.0665,1.025,9.28*np.pi/180)  
	foo.func_val(foo.x)
	"""
#===================================================================================================
	def __init__(self,inverterStandard='ieee_2018_category_3',\
	inverterStandardConfig='fast_der_ride_through.json',**kwargs):
		try:
			self._baseDir=os.path.abspath(__file__)
			nLevel=7 # number of levels to root/base dir
			for n in range(nLevel):
				self._baseDir=os.path.dirname(self._baseDir)
			
			self.defaultConfig=json.load(open(os.path.join(self._baseDir,'config','fast_der_default.json')))
			thisConfig=copy.deepcopy(self.defaultConfig)
			thisModel={'pwm':False,'ppriority':True,'qpriority':False,'qlimiter':False,\
			'plimiter':False,'elimiter':True,'modelName':'m1'}

			# load ride through settings
			self._ride_through_flags={'momentary_cessation':False,'trip':False,'enter_service':False}
			self._ride_through_settings=json.load(open(\
			os.path.join(self._baseDir,'config',inverterStandardConfig)))
			self._ride_through_settings=self._ride_through_settings[inverterStandard]
			rts=self._ride_through_settings
			for entry in rts:
				if entry!='normal_operation' and entry!='enter_service':
					for thisZone in rts[entry]:
						rts[entry][thisZone]['time_in_zone']=0
						assert rts[entry][thisZone]['action']=='momentary_cessation' or \
						rts[entry][thisZone]['action']=='trip',"action is not momentary_cessation or trip"

			if kwargs and 'config' in kwargs:
				thisConfig.update(copy.deepcopy(kwargs['config']))
			if kwargs and 'model' in kwargs:
				thisModel.update(copy.deepcopy(kwargs['model']))

			# standardize -- convert all config parameters to lower case, should be of format foo_bar
			self.data={'config':{},'model':{}}
			config=self.data['config']
			model=self.data['model']

			for entry in thisConfig:
				config[entry.lower()]=thisConfig[entry]

			for entry in thisModel:
				model[entry.lower()]=thisModel[entry]

			# transforms
			self.transforms={}
			self.transforms['abc2dq0']=lambda a,b,c,theta:\
			(2/3)*np.array([[np.cos(theta),np.cos(theta-2*np.pi/3),np.cos(theta+2*np.pi/3)],
			[-np.sin(theta),-np.sin(theta-2*np.pi/3),-np.sin(theta+2*np.pi/3)],
			[1/2,1/2,1/2]]).dot(np.array([a,b,c]))

			self.transforms['dq02abc']=lambda d,q,z,theta:\
			np.array([[np.cos(theta),-np.sin(theta),1],
			[np.cos(theta-2*np.pi/3),-np.sin(theta-2*np.pi/3),1],
			[np.cos(theta+2*np.pi/3),-np.sin(theta+2*np.pi/3),1]]).dot(np.array([d,q,z]))

			# f and J
			assert model['modelname']=='m1' or model['modelname']=='m2',"modelname should be m1 or m2"
			config['nvars']=6 if model['modelname']=='m1' else 7
			self.f=np.zeros(config['nvars'])
			self.J=np.zeros((config['nvars'],config['nvars']))

			# elimiter func
			self.func_elimiter=lambda x,pcmdFinal,qcmdFinal:\
			((self.data['model']['vd']-qcmdFinal/x*self.data['config']['xf'])**2+\
			(self.data['model']['vq']+pcmdFinal/x*self.data['config']['xf'])**2)**.5-\
			(self.data['config']['vdc']/2)

			# other initializations
			config['pref_predisturbance']=None
			config['qref_predisturbance']=None
			config['enter_service_countdown']=\
			self._ride_through_settings['enter_service']['intentional_delay']
			self._integrator_data={'time_values':[0]}
		except:
			raise

#===================================================================================================
	def update_model(self,va,vb=None,vc=None,**kwargs):
		try:
			model=self.data['model']

			# update vt
			model['vt']=abs(va)
			model['vt_angle']=np.angle(va)

			# update vdqz
			model['vd'],model['vq'],model['vz']=self.transforms['abc2dq0'](\
			model['vt']*np.cos(model['vt_ang']),\
			model['vt']*np.cos(model['vt_ang']-2*np.pi/3),\
			model['vt']*np.cos(model['vt_ang']+2*np.pi/3),\
			model['vt_ang'])
		except:
			PrintException()

#===================================================================================================
	def create_config(self,**kwargs):
		try:
			self.config=copy.deepcopy(self.defaultConfig)
			self.config.update(kwargs)
		except:
			PrintException()

#===================================================================================================
	def func_val(self,x):
		try:
			model=self.data['model']
			config=self.data['config']
			f=self.f

			# compute vd,vq
			phi=model['vt_ang']
			va=model['vt']*np.cos(phi); vb=model['vt']*np.cos(phi-2*np.pi/3)
			vc=model['vt']*np.cos(phi+2*np.pi/3)
			model['vd'],model['vq'],model['vz']=self.transforms['abc2dq0'](va,vb,vc,phi)

			# P control
			f[0]=(1/config['trv'])*(model['dw']-x[0])#dw-->(1/1+sTrv)-->x[0] i.e. dw_filt

			u_temp=x[0]*(1/config['rp'])
			# deadband for dw
			u_temp=u_temp if u_temp<=config['db_dw_up'] and u_temp>=config['db_dw_down'] else 0
			pcmd_ref=u_temp+config['pref']
			# model m2
			if model['modelname']=='m2':
				x[6]=config['kip']*pcmd_ref
				if pcmd_ref!=0:#
					x[6]+=config['kpp']*(1/config['trv'])*(model['dw']-x[6])*(1/config['rp'])
		# pmax,pmin limiter
			pcmd_ref=config['pmax'] if pcmd_ref>config['pmax'] else pcmd_ref
			pcmd_ref=config['pmin'] if pcmd_ref<config['pmin'] else pcmd_ref

			f[1]=(1/config['tpord'])*(pcmd_ref-x[1])#u2-->(1/1+sTpord)-->x[1] i.e. governor
			#id_cmd
			id_cmd=x[1]/x[3] # id_cmd=x[1]/x[3] i.e. output_governor/vt_mag_filt
			# idmax,idmin limiter
			id_cmd=config['id_max'] if id_cmd>config['id_max'] else id_cmd
			id_cmd=config['id_min'] if id_cmd<config['id_min'] else id_cmd # --> current limiter logic

			# Q control
			f[3]=(1/config['trv'])*(model['vt']-x[3]) # vt_mag_filt
			# verr
			verr=config['vref']-x[3]
			# deadband for verr
			verr=verr if verr<=config['db_v_up'] and verr>=config['db_v_down'] else 0
			qcmd_ref=-(config['qref']/x[3])+verr
			# qmax,qmin limiter
			u5=config['qmax'] if qcmd_ref>config['qmax'] else qcmd_ref
			u5=config['qmin'] if qcmd_ref<config['qmin'] else qcmd_ref

			f[4]=(1/config['tiq'])*(u5-x[4]) # --> current limiter logic

			# current limiter logic
			iq_cmd=x[4]
			if model['ppriority']:
				if id_cmd>config['imax']:
					id_cmd=config['imax']
				if abs(id_cmd+1j*x[4])>config['imax']:
					iq_cmd=np.sqrt(config['imax']**2-id_cmd**2)
			if model['qpriority']:
				if iq_cmd>config['imax']:
					iq_cmd=config['imax']
				if abs(id_cmd+1j*iq_cmd)>config['imax']:
					id_cmd=np.sqrt(config['imax']**2-iq_cmd**2)
			if model['elimiter']:
				if ((model['vd']-iq_cmd*config['xf'])**2+\
				(model['vq']-id_cmd*config['xf'])**2)**.5>(config['vdc']/2):# then m>1
					res=fsolve(self.func_elimiter,[1],(id_cmd,iq_cmd),full_output=1)
					if res[2]==1:# converged
						id_cmd=id_cmd/res[0][0]
						iq_cmd=iq_cmd/res[0][0]
					else:
						pass ####TODO: fix logic

			u3=id_cmd; u6=iq_cmd
			# iq and lag block
			f[2]=(1/config['tg'])*(u3-x[2]) # u3=output of current limiter logic
			f[5]=(1/config['tg'])*(u6-x[5]) # u3=output of current limiter logic

			# coupling equation
			model['ed']=model['vd']-x[2]*config['xf'] # Ed=vd-iq*xf
			model['eq']=model['vq']+x[5]*config['xf'] # Eq=vq+id*xf

			if model['pwm']:
				# pwm, Vdc is assumed to be constant due to appropriately sized capacitor
				# modulation index m is computed
				m=abs(model['ed']+1j*model['eq'])*(2/config['vdc'])
				m=1 if m>1 else m
				Emag=(1/2)*m*config['vdc']
				phi=np.angle(model['ed']+1j*model['eq'])
				Ea=Emag*np.cos(phi); Eb=Emag*np.cos(phi-2*np.pi/3); Ec=Emag*np.cos(phi+2*np.pi/3)
				Ed_final,Eq_final,E0_final=self.transforms['abc2dq0'](Ea,Eb,Ec,phi)

			return copy.deepcopy(f)
		except:
			raise

#===================================================================================================
	def jac_val(self,x):
		try:
			model=self.data['model']
			config=self.data['config']
			J=self.J

			J[0,0]=-1/config['trv']
			J[1,0]=(1/config['tpord'])*(1/config['rp'])
			J[1,1]=-1/config['tpord']
			J[2,1]=(1/config['tg'])*(1/x[3])
			J[2,2]=-1/config['tg']
			J[3,3]=-1/config['trv']
			J[4,4]=-1/config['tiq']
			J[5,4]=1/config['tiq']
			J[5,5]=-1/config['tiq']

			eps=1e-4
			fOrg=self.func_val(x)
			if model['modelname']=='m1':
				f3=self.func_val(x+np.array([0,0,0,eps,0,0]))
			elif model['modelname']=='m2':
				f3=self.func_val(x+np.array([0,0,0,eps,0,0,0]))
			J[:,3]=(f3-fOrg)/eps
			if model['modelname']=='m2':
				f6=self.func_val(x+np.array([0,0,0,0,0,0,eps]))
				J[:,6]=(f6-fOrg)/eps

			return J
		except:
			raise

#===================================================================================================
	def compute_initial_condition(self,pref,qref,vt,vt_ang):
		try:
			config=self.data['config']
			model=self.data['model']

			model['pref'],model['qref']=pref,qref
			model['vt'],model['vt_ang']=vt,vt_ang
			model['dw']=0

			# init condition
			self.x=[0,model['pref'],model['pref']/model['vt'],
			model['vt'],-model['qref']/model['vt'],-model['qref']/model['vt']]
			if model['modelname']=='m2':
				self.x.append(model['pref'])
			self.x=np.array(self.x)

			# update model
			self.update_model(vt*(np.cos(vt_ang)+1j*np.sin(vt_ang)))
		except:
			raise

#===================================================================================================
	def integrate(self,dt):
		try:
			#self.data['model']['vt'] should have been updated prior to this call
			self.ride_through_logic(vmag=self.data['model']['vt'],dt=dt)
			recompute_initial_condition=self.enter_service(dt=dt)

			flags=self._ride_through_flags
			if flags['momentary_cessation'] or flags['trip']:
				if not self.data['config']['pref_predisturbance']:
					self.data['config']['pref_predisturbance']=self.data['config']['pref']
				if not self.data['config']['qref_predisturbance']:
					self.data['config']['qref_predisturbance']=self.data['config']['qref']
				self.data['config']['pref']=0
				self.data['config']['qref']=0
				self.x=self.x*0 # will not integrate
				# to sync with global time
				self._integrator_data['time_values'].append(self._integrator_data['time_values'][-1]+dt)
			else:
				if recompute_initial_condition:
					self.compute_initial_condition(self.data['config']['pref'],\
					self.data['config']['qref'],self.data['model']['vt'],\
					self.data['model']['vt_angle'])

				self.x=self.x+dt*self.func_val(self.x)
				self._integrator_data['time_values'].append(self._integrator_data['time_values'][-1]+dt)
		except:
			raise

#===================================================================================================
	def rollback(self):
		try:
			# reset x and vars
			self.x=self.lastKnownSol[-1]
		except:
			raise

#===================================================================================================
	def numjac(self,x,f=None,eps=1e-6):
		try:
			if not f:
				f=self.func_val
			baseF=f(x)
			nx=len(x)
			J=np.zeros((nx,nx))
			xOrg=copy.deepcopy(x)
			for n in range(nx):
				x=copy.deepcopy(xOrg)
				x[n]+=eps
				J[:,n]=(f(x)-baseF)/eps

			return J
		except:
			raise

#===================================================================================================
	def ride_through_logic(self,vmag,dt):
		try:
			rts=self._ride_through_settings
			flags=self._ride_through_flags

			if vmag<rts['normal_operation']['voltage_range'][0]:# abnormal LV operation
				for thisZone in rts['lvrt']:
					thisVmin,thisVmax=rts['lvrt'][thisZone]['voltage_range']
					if rts['lvrt'][thisZone]['time_in_zone']>=\
					rts['lvrt'][thisZone]['minimum_ride_through_time']:
						flags[rts['lvrt'][thisZone]['action']]=True
					rts['lvrt'][thisZone]['time_in_zone']+=dt
			elif vmag>rts['normal_operation']['voltage_range'][1]:# abnormal HV operation
				for thisZone in rts['hvrt']:
					thisVmin,thisVmax=rts['lvrt'][thisZone]['voltage_range']
					if rts['hvrt'][thisZone]['time_in_zone']>=\
					rts['hvrt'][thisZone]['minimum_ride_through_time']:
						flags[rts['hvrt'][thisZone]['action']]=True
					if thisVmin<vmag<=thisVmax:
						rts['hvrt'][thisZone]['time_in_zone']+=dt
			else:# normal operation, then reset time by default in all zones
				# reset flags
				if flags['trip']:
					flags['enter_service']=True
				flags['momentary_cessation']=False
				flags['trip']=False

				for entry in self._ride_through_settings:
					if entry!='normal_operation' and entry!='enter_service':
						for thisZone in self._ride_through_settings[entry]:
							self._ride_through_settings[entry][thisZone]['time_in_zone']=0
		except:
			raise

#===================================================================================================
	def enter_service(self,dt):
		try:
			rts=self._ride_through_settings
			flags=self._ride_through_flags
			recompute_initial_condition=False

			if flags['enter_service']:# linear increase in q based on pmax
				# first enter service step, recompute initial condition
				if self.data['config']['pref']==0 and self.data['config']['qref']==0:
					recompute_initial_condition=True

				if self.data['config']['pref']<self.data['config']['pref_predisturbance']:
					if self.data['config']['enter_service_countdown']==0:
						self.data['config']['pref']+=self.data['config']['pref_predisturbance']*\
						(self.data['config']['pmax']/rts['enter_service']['reconnection_window'])*dt
						self.data['config']['qref']+=self.data['config']['qref_predisturbance']*\
						(self.data['config']['pmax']/rts['enter_service']['reconnection_window'])*dt
					else:
						self.data['config']['enter_service_countdown']-=dt
						if self.data['config']['enter_service_countdown']<0:
							self.data['config']['enter_service_countdown']=0
				else:
					flags['enter_service']=False
					self.data['config']['pref']=self.data['config']['pref_predisturbance']
					self.data['config']['qref']=self.data['config']['qref_predisturbance']
					self.data['config']['pref_predisturbance']=None
					self.data['config']['qref_predisturbance']=None
					self.data['config']['enter_service_countdown']=\
					self._ride_through_settings['enter_service']['intentional_delay']

			return recompute_initial_condition
		except:
			raise