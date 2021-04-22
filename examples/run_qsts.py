import os
import time
import pdb

from tdcosim.global_data import GlobalData
from tdcosim.procedure.procedure import Procedure


def main():
	'''
	Main function to run the T&D Cosimulation	
	'''
	startTime=time.time()
	GlobalData.set_config('config_qsts.json')
	GlobalData.set_TDdata()
	simulate()
	print("Total simulation time:",time.time()-startTime)

def simulate():
	'''
	Run the simulation
	'''
	proc = Procedure()
	proc.simulate()

if __name__ == "__main__":
	main()
