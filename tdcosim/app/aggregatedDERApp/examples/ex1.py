import os
import copy
import sys

pssePath="C:\\Program Files (x86)\\PTI\\PSSE33\\PSSBIN" # Default PSSEPY path is PSSE33
sys.path.append(pssePath)
os.environ['PATH']+=';'+pssePath
		
from tdcosim.app.aggregatedDERApp import App, PrintException


#=======================================================================================================================
if __name__=='__main__':
	try:
				
		thisApp=App()

		# define data
		dataDir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+os.path.sep+'data'
		rawFilePath=dataDir+os.path.sep+'118bus'+os.path.sep+'case118_psse_v35.raw'
		dyrFilePath=dataDir+os.path.sep+'118bus'+os.path.sep+'case118_base.dyr'
		additionalDyrFilePath=None

		# define events. Any dist_* API from psspy can be used. For the given dist_* API the
		# correct set of keyworded input args must be provided. In addition, 'id' and 'time'
		# key,value pair must be present.
		events={'dist_bus_fault':{'id':'fault_on','time':.4,'ibus':80,'values':[0,-1e10]},
		'dist_clear_fault':{'id':'fault_off','time':.5}}

		# setup
		scenarioid=[]; tag=[]
		for n in range(2):# define the scenarios
			scenarioid.append('{}'.format(n))
			tag.append('no_solar')
			tend=1
			# as an example we apply fault at bus 80, 81, etc. One at a time i.e. each fault represents one scenario run.
			thisEvent=copy.deepcopy(events)
			thisEvent['dist_bus_fault']['ibus']=80+n
			thisApp.create_run(rawFilePath,dyrFilePath,additionalDyrFilePath,events,scenarioid[-1],tag[-1],tend)

		# run
		thisApp.run_batch()

		# post process
		# first define search scope. This is the list of scenarios that you want in the database
		thisApp.PostProcess.search_scope(scenarioid,tag)# we use all the scenarios we generated above
		df=thisApp.PostProcess.filter_node(busid=['80','81'])# get all information for bus 80 across all runs
		print('properties available for bus 80 :',set(df[df.busid=='80'].property))

		# plot all buses voltages such that vmin<=vmag<=vmax is true for any time t
		#thisApp.PostProcess.show_voltage_violations(vmin=.4,vmax=.6)
		
		
		
		# vmin<=vmag<=vmax for duration>=maxRecoveryTime
		thisApp.PostProcess.show_voltage_recovery(vmin=.4,vmax=.6,maxRecoveryTime=.03)
		ST = thisApp.PostProcess.get_voltage_stability_time(vmin=.4,vmax=0.6,maxRecoveryTime=0.03,error_threshold=0.001)

	except:
		PrintException()


