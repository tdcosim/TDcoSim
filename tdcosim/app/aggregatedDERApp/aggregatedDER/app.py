import os
import copy
import json
import pdb

import psspy

from .model import Dera
from .post_process import PostProcess
from .utils import PrintException


class App(Dera):
	def __init__(self):
		super(App,self).__init__()
		self.PostProcess=PostProcess()
		self._psspy=psspy
		self._psspy.psseinit(0)
		self._psspy.report_output(6,'',[])
		self._psspy.progress_output(6,'',[])
		self.__monitorID={'angle':1,'pelec':2,'qelec':3,'eterm':4,'efd':5,'pmech':6,'speed':7,
		'xadifd':8,'ecomp':9,'volt':13,'pload':25,'qload':26}
		self._events={}
		self.conf=[]

#=======================================================================================================================
	def load_case(self,rawFilePath=None,dyrFilePath=None,additionalDyrFilePath=None):
		try:
			if rawFilePath:
				ierr = self._psspy.read(0,rawFilePath.encode("ascii", "ignore"))
				assert ierr==0,"Reading raw file failed with error {}".format(ierr)

			if dyrFilePath:
				ierr=self._psspy.dyre_new([1,1,1,1],dyrFilePath.encode("ascii", "ignore"))
				assert ierr==0,"Reading dyr file failed with error {}".format(ierr)

			if additionalDyrFilePath:
				ierr=self._psspy.dyre_add(dyrefile=additionalDyrFilePath.encode("ascii", "ignore"))
				assert ierr==0,"Adding dyr file failed with error {}".format(ierr)
				print("added composite load model",ierr,additionalDyrFilePath)
		except:
			PrintException()

#=======================================================================================================================
	def run_powerflow(self,conf=None):
		try:
			if not conf:
				conf={}
			ierr=self._psspy.fnsl(**conf)
			assert ierr==0,"self._psspy.fnsl failed with error {}".format(ierr)
		except:
			PrintException()

#=======================================================================================================================
	def init_dynamic(self,conf=None,outType='.out'):
		try:
			outType2Vrn={'.out':0,'outx':1}
			if not conf:
				conf={'cong':{},'conl':{'all':1,'apiopt':1,'status':[0,0],'loadin':[0,1,0,1]},
				'strt':{'outfile':os.getcwd()+os.path.sep+'result.out'}}
			assert 'cong' in conf and 'conl' in conf and 'strt' in conf

			ierr,_=self._psspy.conl(**conf['conl'])# initialize
			assert ierr==0,"self._psspy.conl failed with error {}".format(ierr)
			conf['conl'].update({'apiopt':2})
			ierr,_=self._psspy.conl(**conf['conl'])# convert
			assert ierr==0,"self._psspy.conl failed with error {}".format(ierr)
			conf['conl'].update({'apiopt':3})
			ierr,_=self._psspy.conl(**conf['conl'])# convert
			assert ierr==0,"self._psspy.conl failed with error {}".format(ierr)

			ierr=self._psspy.cong(**conf['cong'])
			assert ierr==0,"self._psspy.cong failed with error {}".format(ierr)

####			ierr=self._psspy.set_chnfil_type(outType2Vrn[outType])
####			assert ierr==0,"self._psspy.set_chnfil_type failed with error {}".format(ierr)
			ierr=self._psspy.strt(**conf['strt'])
			assert ierr==0,"self._psspy.strt failed with error {}".format(ierr)
		except:
			PrintException()

#=======================================================================================================================
	def run_dynamic(self,conf=None):
		try:
			if not conf:
				conf={'tpause':1}
			assert 'tpause' in conf, 'tpause needs to be specified'

			eventTimes=[0]+list(self._events.keys())
			eventTimes.sort()
			if eventTimes and conf['tpause']<eventTimes[-1]:
				conf['tpause']=self._events['t'][-1]
			eventTimes.append(conf['tpause'])

			for startTime,endTime in zip(eventTimes[0:-1],eventTimes[1::]):
				if self._events and startTime in self._events:# apply event
					thisEvent=self._events[startTime].pop('eventType')
					self._events[startTime].pop('time')
					self._events[startTime].pop('id')
					ierr=self._psspy.__dict__[thisEvent](**self._events[startTime])
					assert ierr==0,"self._psspy.{} failed with error {}".format(thisEvent,ierr)
				# run
				ierr=self._psspy.run(tpause=endTime)
				assert ierr==0,"self._psspy.run failed with error {}".format(ierr)
		except:
			PrintException()

#=======================================================================================================================
	def add_monitor(self,conf=None,fpath=None):
		try:
			monitor={}; fpathConf={}
			if fpath and os.path.exists(fpath) and fpath.split('.')[-1]=='.json':
				monitor.update(json.load(open(fpath)))
			if conf:
				monitor.update(conf)
			if not conf and not fpath:
				monitor=self.__monitorID.keys()

			# delete redundant channels
			ierr = self._psspy.delete_all_plot_channels()

			for entry in monitor:
				self._psspy.chsb(sid=0,all=1,status=[-1,-1,-1,1,self.__monitorID[entry],0])
		except:
			PrintException()

#=======================================================================================================================
	def add_events(self,events):
		"""Define events that needs to be executed. All events should be in the open interval
		(0,tend)"""
		try:
			for event in events:
				assert 'time' in events[event],'time is not specified'
				assert 'id' in events[event],'id is not specified'
				self._events[events[event]['time']]=copy.deepcopy(events[event])
				self._events[events[event]['time']]['eventType']=event
		except:
			PrintException()

#=======================================================================================================================
	def create_run(self,rawFilePath,dyrFilePath,additionalDyrFilePath,events,scenarioid,tag,tend):
		try:
			thisRun={'rawFilePath':rawFilePath,'dyrFilePath':dyrFilePath,'additionalDyrFilePath':additionalDyrFilePath,
			'events':events,'scenarioid':scenarioid,'tag':tag,'tend':tend}
			self.conf.append(thisRun)
		except:
			PrintException()

#=======================================================================================================================
	def run_batch(self):
		try:
			requiredInput=['rawFilePath','dyrFilePath','additionalDyrFilePath','events',
			'scenarioid','tag','tend']

			for thisRun in self.conf:
				for thisRequirement in requiredInput:
					assert thisRequirement in thisRun,'{} not found'.format(thisRequirement)
				self.load_case(thisRun['rawFilePath'],thisRun['dyrFilePath'],thisRun['additionalDyrFilePath'])
				self.add_monitor()
				self.init_dynamic()
				self.add_events(thisRun['events'])
				self.run_dynamic({'tpause':thisRun['tend']})

				# post process
				config={'rawFilePath':thisRun['rawFilePath'],'dyrFilePath':thisRun['dyrFilePath'],
				'additionalDyrFilePath':thisRun['additionalDyrFilePath'],'events':self._events}
				self.PostProcess.add_metadata(scenarioid=thisRun['scenarioid'],tag=thisRun['tag'],config=config)
				df=self.PostProcess.load_outfile('result.out')
				self.PostProcess.save(df)
		except:
			PrintException()


