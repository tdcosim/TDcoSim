import os
import time
import pdb

from tdcosim.global_data import GlobalData
from tdcosim.procedure.procedure import Procedure
from tdcosim.model.opendss.opendss_data import OpenDSSData


def main():
	'''
	Main function to run the T&D Cosimulation	
	'''
	try:
		GlobalData.set_config('config_tonly_dera_68bus.json')
		GlobalData.set_TDdata()
		simulate()
	except:
		raise

def simulate():
	'''
	Run the simulation
	'''
	proc = Procedure()
	proc.simulate()

if __name__ == "__main__":
	startTime = time.time()
	main()
	print('Solution time:',time.time()-startTime)
