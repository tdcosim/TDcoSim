"""Example to illustrate DER_A comparison."""

import os
import pdb

import psspy

from tdcosim.app.aggregatedDERApp import App, PostProcess, LogUtil


#=======================================================================================================================
if __name__=='__main__':
	try:
		# path
		baseDir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		dataDir=os.path.join(baseDir,'data','118bus')
		rawFilePath=os.path.join(dataDir,'case118_psse_v35.raw')
		dyrFilePath=os.path.join(dataDir,'case118_base.dyr')

		#======================non DER_A app======================
		# no DER generation
		nonDERAApp=App()
		pp=PostProcess()
		nonDERAApp.load_case(rawFilePath,dyrFilePath)

		# output. Default output location is data/out/result.out
		nonDERAApp.add_monitor()

		# init
		nonDERAApp.init_dynamic()

		# define events. Any dist_* API from psspy can be used. For the given dist_* API the
		# correct set of keyworded input args must be provided. In addition, 'id' and 'time'
		# key,value pair must be present.
		events={'dist_bus_fault':{'id':'fault_on','time':.4,'ibus':2,'values':[0,-1e10]},
		'dist_clear_fault':{'id':'fault_off','time':.5,'ifault':1}}
		if psspy.psseversion()[1]==35:
			events['dist_clear_fault']['fault']=events['dist_clear_fault'].pop('ifault')
		nonDERAApp.add_events(events)

		# run
		nonDERAApp.run_dynamic(conf={'tpause':1})

		#create df and save
		df_nonDERA=pp.outfile2df(os.path.join(baseDir,'data','out','result.out'))
		df_nonDERA.to_pickle(os.path.join(baseDir,'data','out','result_ex3_nonDERA.p'))

		#======================DER_A app======================
		DERAApp=App()
		DERAApp.load_case(rawFilePath,dyrFilePath)

		# add DER_A to case. DER_A that follows IEEE 1547 2003
		# standard will be added to buses 2 and 3
		rating=[{'pg':20,'qg':0,'pt':20,'pb':0,'qt':10,'qb':-10}]*2
		DERAApp.add_dera_to_case({'1547_2003':[2,3]},rating=rating)

		# output. Default output location is data/out/result.out
		DERAApp.add_monitor()

		# init
		DERAApp.init_dynamic()

		# define events. Any dist_* API from psspy can be used. For the given dist_* API the
		# correct set of keyworded input args must be provided. In addition, 'id' and 'time'
		# key,value pair must be present.
		events={'dist_bus_fault':{'id':'fault_on','time':.4,'ibus':2,'values':[0,-1e10]},
		'dist_clear_fault':{'id':'fault_off','time':.5,'ifault':1}}
		if psspy.psseversion()[1]==35:
			events['dist_clear_fault']['fault']=events['dist_clear_fault'].pop('ifault')
		DERAApp.add_events(events)

		# run
		DERAApp.run_dynamic(conf={'tpause':1})

		#create df and save
		df_dera=pp.outfile2df(os.path.join(baseDir,'data','out','result.out'))
		df_dera.to_pickle(os.path.join(baseDir,'data','out','result_ex3_dera.p'))
	except:
		LogUtil.exception_handler()

