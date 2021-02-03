import os
import copy
import json
import pdb

import psspy
import six

from .model import Dera
from .post_process import PostProcess
from .logutil import LogUtil


class App(Dera):
	def __init__(self):
		try:
			super(App,self).__init__()
			self.PostProcess=PostProcess()
			ierr=psspy.psseinit(0); assert ierr==0
			ierr=psspy.report_output(6,'',[]); assert ierr==0
			ierr=psspy.progress_output(6,'',[]); assert ierr==0
			baseDir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			self.__monitorID={'angle':1,'pelec':2,'qelec':3,'eterm':4,'efd':5,'pmech':6,'speed':7,
			'xadifd':8,'ecomp':9,'volt':13,'pload':25,'qload':26}
			self.__dera_rating_default=json.load(open(os.path.join(baseDir,'config','dera_rating.json')))
			self.__cmld_rating_default=json.load(open(os.path.join(baseDir,'config',\
			'composite_load_model_rating.json')))
			self._events={}
			self.conf=[]
			self.modelChanges={}
		except:
			LogUtil.exception_handler()

#=======================================================================================================================
	def load_case(self,rawFilePath=None,dyrFilePath=None,additionalDyrFilePath=None,
	adjustSystemOperatingPoint=False,reductionPercent=0):
		try:
			if adjustSystemOperatingPoint:
				assert rawFilePath and dyrFilePath and reductionPercent>0
				self.adjust_system_operating_point(rawFilePath=rawFilePath,dyrFilePath=dyrFilePath,
				reductionPercent=reductionPercent)
			else:
				if rawFilePath:
					ierr = psspy.read(0,rawFilePath.encode("ascii", "ignore"))
					assert ierr==0,"Reading raw file failed with error {}".format(ierr)

				if dyrFilePath:
					ierr=psspy.dyre_new([1,1,1,1],dyrFilePath.encode("ascii", "ignore"))
					assert ierr==0,"Reading dyr file failed with error {}".format(ierr)

				if additionalDyrFilePath:
					ierr=psspy.dyre_add(dyrefile=additionalDyrFilePath.encode("ascii", "ignore"))
					assert ierr==0,"Adding dyr file failed with error {}".format(ierr)
		except:
			LogUtil.exception_handler()

#=======================================================================================================================
	def run_powerflow(self,conf=None):
		try:
			if not conf:
				conf={}
			ierr=psspy.fnsl(**conf)
			assert ierr==0,"psspy.fnsl failed with error {}".format(ierr)
		except:
			LogUtil.exception_handler()

#=======================================================================================================================
	def init_dynamic(self,conf=None,outType='.out',ZIPLoadConversion=True):
		try:
			if psspy.psseversion()[1]>=35:
				outType2Vrn={'.out':0,'outx':1}
				ierr=psspy.set_chnfil_type(outType2Vrn[outType]); assert ierr==0
				assert outType2Vrn[outType]==psspy.set_chnfil_type()[0]

			if not conf:
				baseDir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
				conf={'cong':{},'conl':{'all':1,'apiopt':1,'status':[0,0],'loadin':[.3,.4,.3,.4]},
				'strt':{'outfile':os.path.join(baseDir,'data','out','result.out')}}
			assert 'cong' in conf and 'strt' in conf

			if ZIPLoadConversion:
				assert 'conl' in conf 
				ierr,_=psspy.conl(**conf['conl'])# initialize
				assert ierr==0,"psspy.conl failed with error {}".format(ierr)

				conf['conl'].update({'apiopt':2})
				ierr,_=psspy.conl(**conf['conl'])# convert
				assert ierr==0,"psspy.conl failed with error {}".format(ierr)

				conf['conl'].update({'apiopt':3})
				ierr,_=psspy.conl(**conf['conl'])# convert
				assert ierr==0,"psspy.conl failed with error {}".format(ierr)

			ierr=psspy.cong(**conf['cong'])
			assert ierr==0,"psspy.cong failed with error {}".format(ierr)

			ierr=psspy.strt(**conf['strt'])
			assert ierr==0,"psspy.strt failed with error {}".format(ierr)
		except:
			LogUtil.exception_handler()

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
					ierr=psspy.__dict__[thisEvent](**self._events[startTime])
					assert ierr==0,"psspy.{} failed with error {}".format(thisEvent,ierr)
				# run
				ierr=psspy.run(tpause=endTime)
				assert ierr==0,"psspy.run failed with error {}".format(ierr)
		except:
			LogUtil.exception_handler()

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
			ierr = psspy.delete_all_plot_channels()

			for entry in monitor:
				ierr=psspy.chsb(sid=0,all=1,status=[-1,-1,-1,1,self.__monitorID[entry],0])
				assert ierr==0
		except:
			LogUtil.exception_handler()

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
			LogUtil.exception_handler()

#=======================================================================================================================
	def add_dera_to_case(self,conf,rating=None,additionalDyrFilePath='dera.dya',
	solarPercentage=0,cleanup=True):
		"""Given conf and additionalDyrFilePath, this method adds dera model as an additional
		dyr/dya file that can then be read using psspy.dyre_add method. conf should be of the form
		conf={'standard':[busID]} for example conf={'1547_2003':[1,2,3]} will add dera model which
		follows IEEE 1547 2003 standard at buses 1,2 and 3. Also adds plant data at the said buses
		and changes WMOD to 1."""
		try:
			if 'dera' not in self.modelChanges:
				self.modelChanges['dera']={}
			mc=self.modelChanges['dera']

			if solarPercentage>0:# update conf to have all busIDs
				if six.PY2:
					LogUtil.logger.info(\
					'Updating conf to use {} for all load buses as solarPercentage>0'.format(conf.keys()[0]))
				elif six.PY3:
					LogUtil.logger.info(\
					'Updating conf to use {} for all load buses as solarPercentage>0'.format(list(conf.keys())[0]))
				# get load info
				ierr,loadBusNumberAll=psspy.aloadint(-1,1,'NUMBER')
				assert ierr==0,'psspy.aloadint failed with error {}'.format(ierr)
				loadBusNumberAll=loadBusNumberAll[0]
				ierr,genBusNumber=psspy.agenbusint(-1,1,'NUMBER')
				assert ierr==0,'psspy.agenbusint failed with error {}'.format(ierr)
				genBusNumber=genBusNumber[0]
				ierr,SAll=psspy.alodbuscplx(string='MVAACT')
				assert ierr==0,"reading complex load failed with error {}".format(ierr)
				SAll=SAll[0]

				# only non-gen buses
				loadBusNumber=[];S=[]
				for thisBus,thisS in zip(loadBusNumberAll,SAll):
					if thisBus not in genBusNumber:
						loadBusNumber.append(thisBus)
						S.append(thisS)

				# update
				if six.PY2:
					thisStandard=conf.keys()[0]
				elif six.PY3:
					thisStandard=list(conf.keys())[0]
				conf={thisStandard:loadBusNumber}

			# generate dera params and write .dya file
			thisConf={}; busID=[]
			for entry in conf:
				thisConf.update(self.generate_config(conf[entry],entry))
				busID.extend(conf[entry])
			self.dera2dyr(thisConf,additionalDyrFilePath)

			# rating
			realarData=[self.__dera_rating_default['default']]*len(busID)
			if rating and solarPercentage==0:
				assert isinstance(rating,list) and len(rating)==len(busID)
				for thisRating,thisRealarData in zip(rating,realarData):
					if isinstance(thisRating,dict):
						thisRealarData.update(thisRating)
			elif solarPercentage>0:
				realarData=[self.__dera_rating_default['default']]*len(loadBusNumber)
				for thisBus,thisS,thisRealarData in zip(loadBusNumber,S,realarData):
					thisRating={'pg':thisS.real*solarPercentage,'qg':0.0,
					'pt':thisS.real*solarPercentage,'pb':0.0,
					'qt':thisS.imag*solarPercentage,'qb':-thisS.imag*solarPercentage}
					thisRealarData.update(thisRating)

			ind2name=self.__dera_rating_default['ind2name']
			for thisBusID,thisRealarData in zip(busID,realarData):
				mc[thisBusID]=thisRealarData
				ierr=psspy.bus_data_2(thisBusID,[2,1,1,1])# convert to a gen bus
				assert ierr==0, 'error code {}'.format(ierr)
				ierr=psspy.plant_data(thisBusID)
				assert ierr==0, 'error code {}'.format(ierr)
				realar=[thisRealarData[ind2name[str(n)]] for n in range(len(thisRealarData))]
				ierr=psspy.machine_data_2(i=thisBusID,intgar=[1,1,0,0,0,1],realar=realar)
				assert ierr==0

			# add dera to base case
			ierr=psspy.dyre_add(dyrefile=additionalDyrFilePath); assert ierr==0

			# cleanup
			if cleanup:
				os.system('del {}'.format(additionalDyrFilePath))
		except:
			LogUtil.exception_handler()

#=======================================================================================================================
	def create_run(self,rawFilePath,dyrFilePath,additionalDyrFilePath,events,scenarioid,tag,tend):
		try:
			thisRun={'rawFilePath':rawFilePath,'dyrFilePath':dyrFilePath,'additionalDyrFilePath':additionalDyrFilePath,
			'events':events,'scenarioid':scenarioid,'tag':tag,'tend':tend}
			self.conf.append(thisRun)
		except:
			LogUtil.exception_handler()

#=======================================================================================================================
	def run_batch(self):
		try:
			requiredInput=['rawFilePath','dyrFilePath','additionalDyrFilePath','events',
			'scenarioid','tag','tend']

			baseDir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			runID=0
			for thisRun in self.conf:
				for thisRequirement in requiredInput:
					assert thisRequirement in thisRun,'{} not found'.format(thisRequirement)
				self.load_case(thisRun['rawFilePath'],thisRun['dyrFilePath'],thisRun['additionalDyrFilePath'])
				self.add_monitor()
				config={'cong':{},'conl':{'all':1,'apiopt':1,'status':[0,0],'loadin':[.3,.4,.3,.4]},
				'strt':{'outfile':os.path.join(baseDir,'data','out','result_{}.out'.format(runID))}}
				self.init_dynamic(config)
				self.add_events(thisRun['events'])
				self.run_dynamic({'tpause':thisRun['tend']})
				runID+=1
		except:
			LogUtil.exception_handler()

#=======================================================================================================================
	def __run_batch(self):
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
				#config={'rawFilePath':thisRun['rawFilePath'],'dyrFilePath':thisRun['dyrFilePath'],
				#'additionalDyrFilePath':thisRun['additionalDyrFilePath'],'events':self._events}
				#self.PostProcess.add_metadata(scenarioid=thisRun['scenarioid'],tag=thisRun['tag'],config=config)
				#df=self.PostProcess.load_outfile('result.out')
				#self.PostProcess.save(df)
		except:
			LogUtil.exception_handler()

#=======================================================================================================================
	def adjust_system_operating_point(self,rawFilePath,dyrFilePath,reductionPercent):
		try:
			loadType = 0
			offset=3
			ind={}
			ind['GENCLS']=0
			ind['GENDCO']=4
			ind['GENROE']=4
			ind['GENROU']=4
			ind['GENSAE']=3
			ind['GENSAL']=3
			ind['GENTPJU1']=4
			ind['GENTRA']=1

			dyrPath=dyrFilePath.encode("ascii", "ignore")
			f=open(dyrPath)
			dyrData=f.read().splitlines()
			f.close()

			dyrDataStr=''; Zr={}; Zx={}
			for line in dyrData:
				line=line.lstrip().rstrip()
				if line[-1]==r'/':
					line=line[0:-1]
				if "," not in line:
					line=re.sub('\s{1,}',',',line)
				entry=line.split(',')
				for item in ind:
					if entry[1]=="'{}'".format(item):
						entry[offset+ind[item]]=\
						str(float(entry[offset+ind[item]])*(1-reductionPercent))
						break
				dyrDataStr+=','.join(entry+['\n'])

			tempDyrPath=dyrPath.split('.dyr')[0]+'_temp.dyr'
			f=open(tempDyrPath,'w')
			f.write(dyrDataStr)
			f.close()

			# load raw file
			ierr = psspy.read(0,rawFilePath.encode("ascii", "ignore"))
			assert ierr==0,"Reading raw file failed with error {}".format(ierr)
			ierr,loadBusNumber=psspy.aloadint(-1,1,'NUMBER')
			assert ierr==0,'psspy.aloadint failed with error {}'.format(ierr)
			loadBusNumber=loadBusNumber[0]

			# load updated dyr file and delete the file
			ierr=psspy.dyre_new([1,1,1,1],tempDyrPath.encode("ascii", "ignore")); assert ierr==0
			os.system('del {}'.format(tempDyrPath))

			# adjust load data
			ierr,S=psspy.alodbuscplx(string='MVAACT')
			assert ierr==0,"reading complex load failed with error {}".format(ierr)

			for busID,val in zip(loadBusNumber,S[0]):
				# constP,Q,IP,IQ,YP,YQ
				loadVal=[0]*6
				loadVal[loadType*2],loadVal[loadType*2+1]=\
				val.real*(1-reductionPercent),val.imag*(1-reductionPercent)
				if psspy.psseversion()[1]<=35:
					ierr=psspy.load_chng_4(busID,realar=loadVal)
				elif psspy.psseversion()[1]>=35:
					ierr=psspy.load_chng_6(busID,realar=loadVal)
				assert ierr==0,"load change failed with error {}".format(ierr)
		except:
			LogUtil.exception_handler()

#=======================================================================================================================
	def convert_load_to_cmld(self,conf=None,cleanup=True,avoidBus=None):
		try:
			if not avoidBus:
				avoidBus=[]
			
			if 'cmld' not in self.modelChanges:
				self.modelChanges['cmld']={}

			if not conf:# use defaults for all loads
				# get load info
				ierr,loadBusNumber=psspy.aloadint(-1,1,'NUMBER')
				assert ierr==0,'psspy.aloadint failed with error {}'.format(ierr)
				loadBusNumber=loadBusNumber[0]
				default=self.__cmld_rating_default['default']
				ind2name=self.__cmld_rating_default['ind2name']
				defaultVal=[default[ind2name[str(n)]] for n in range(len(default))]
				prefix=["'USRLOD'",1,"'CMLDBLU2'",12,1,2,133,27,146,48,0,0]
				tempCMLDDyrFile='tempCMLDDyrFile.dyr'
				f=open(tempCMLDDyrFile,'w')

				mc=self.modelChanges['cmld']
				for thisBus in set(loadBusNumber).difference(avoidBus):
					thisData=[thisBus]+prefix+defaultVal
					mc[thisBus]=thisData
					thisStr=''; thisLineLen=0
					for thisItem in thisData:
						thisStr+='{}'.format(thisItem)+','
						thisLineLen+=len('{}'.format(thisItem)+',')
						if thisLineLen>180:# break long lines so that PSSE can read without error
							thisStr+='\n'
							thisLineLen=0
					f.write(thisStr[0:-1]+' /\n')
				f.close()

				# load cmld file
				ierr=psspy.dyre_add(dyrefile=tempCMLDDyrFile.encode("ascii", "ignore"))
				assert ierr==0,"Adding dyr file failed with error {}".format(ierr)

				# clean up
				if cleanup:
					os.system('del {}'.format(tempCMLDDyrFile))
		except:
			LogUtil.exception_handler()

#=======================================================================================================================
	def convert_load_to_complex_load(self,conf=None,cleanup=True,avoidBus=None):
		try:
			if not avoidBus:
				avoidBus=[]
			
			if 'complex_load' not in self.modelChanges:
				self.modelChanges['complex_load']={}

			if not conf:# use defaults for all loads
				# get load info
				ierr,loadBusNumber=psspy.aloadint(-1,1,'NUMBER')
				assert ierr==0,'psspy.aloadint failed with error {}'.format(ierr)
				loadBusNumber=loadBusNumber[0]
				defaultVal=[.2,.2,.2,.2,.1,2,.04,.08]
				prefix=["'CLODBL'",1]
				tempCMLDDyrFile='tempCMLDDyrFile.dyr'
				f=open(tempCMLDDyrFile,'w')

				mc=self.modelChanges['complex_load']
				for thisBus in set(loadBusNumber).difference(avoidBus):
					thisData=[thisBus]+prefix+defaultVal
					mc[thisBus]=thisData
					thisStr=''; thisLineLen=0
					for thisItem in thisData:
						thisStr+='{}'.format(thisItem)+','
						thisLineLen+=len('{}'.format(thisItem)+',')
						if thisLineLen>180:# break long lines so that PSSE can read without error
							thisStr+='\n'
							thisLineLen=0
					f.write(thisStr[0:-1]+' /\n')
				f.close()

				# load cmld file
				ierr=psspy.dyre_add(dyrefile=tempCMLDDyrFile.encode("ascii", "ignore"))
				assert ierr==0,"Adding dyr file failed with error {}".format(ierr)

				# clean up
				if cleanup:
					os.system('del {}'.format(tempCMLDDyrFile))
		except:
			LogUtil.exception_handler()