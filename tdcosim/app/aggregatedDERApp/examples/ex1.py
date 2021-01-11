import os
import copy

import psspy

from tdcosim.app.aggregatedDERApp import App, PostProcess, LogUtil


#=======================================================================================================================
if __name__=='__main__':
	try:
		thisApp=App()
		pp=PostProcess()

		# define data
		dataDir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'data')
		rawFilePath=os.path.join(dataDir,'118bus','case118_psse_v35.raw')
		dyrFilePath=os.path.join(dataDir,'118bus','case118_base.dyr')
		additionalDyrFilePath=None

		# define events. Any dist_* API from psspy can be used. For the given dist_* API the
		# correct set of keyworded input args must be provided. In addition, 'id' and 'time'
		# key,value pair must be present.
		events={'dist_bus_fault':{'id':'fault_on','time':.4,'ibus':80,'values':[0,-1e10]},
		'dist_clear_fault':{'id':'fault_off','time':.5,'ifault':1}}
		if psspy.psseversion()[1]==35:
			events['dist_clear_fault']['fault']=events['dist_clear_fault'].pop('ifault')

		# setup
		scenarioid=[]; tag=[]
		for n in range(1):# define the scenarios
			scenarioid.append('{}'.format(n))
			tag.append('no_solar')
			tend=1
			# as an example we apply fault at bus 80, 81, etc. One at a time i.e. each fault represents one scenario run.
			thisEvent=copy.deepcopy(events)
			thisEvent['dist_bus_fault']['ibus']=80+n
			thisApp.create_run(rawFilePath,dyrFilePath,additionalDyrFilePath,events,scenarioid[-1],tag[-1],tend)

		# run
		thisApp.run_batch()

		#df
		for n in range(1):
			if n==0:
				df=pp.outfile2df(os.path.join(dataDir,'out','result_{}.out'.format(n)),scenarioid=n)
			else:
				df=df.append(pp.outfile2df(os.path.join(dataDir,'out','result_{}.out'.format(n)),\
				scenarioid=n),ignore_index=True)

		df.to_pickle(os.path.join(dataDir,'out','result_no_dera.p'))
	except:
		LogUtil.exception_handler()


