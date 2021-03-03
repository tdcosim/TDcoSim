import os
os.environ["PATH"] += os.getcwd()
import argparse
from tdcosim.global_data import GlobalData
from tdcosim.procedure.procedure import Procedure
from tdcosim.data_analytics import DataAnalytics
import time

def main(configfile):
	'''
	Main function to run the T&D Cosimulation	
	'''
	
	GlobalData.set_config(configfile)
	GlobalData.set_TDdata()	
	startTime=time.time()		
	simulate()
	solutiontime = time.time()-startTime
	print('Solution time:',solutiontime)
	da=DataAnalytics()
	df=da.get_simulation_result(GlobalData.config['outputConfig']['outputDir'])# output folder path\
	df.to_csv(GlobalData.config['outputConfig']['outputDir']+'//dataframe.csv', index=False)
	da.generateSummary(GlobalData, solutiontime)

def simulate():
	'''
	Run the simulation
	'''
	proc = Procedure()
	proc.simulate()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Set configuration file for TDcosim')
	parser.add_argument('--config', default='config.json', type=str, help='The configfile location')	

	args = parser.parse_args()
	print("input configuration: " + args.config)
	main(args.config)
