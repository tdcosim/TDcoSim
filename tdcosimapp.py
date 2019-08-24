import os
os.environ["PATH"] += os.getcwd()
import time
import pdb

from tdcosim.report import generateReport
from tdcosim.global_data import GlobalData
from tdcosim.procedure.procedure import Procedure


def main():
    '''
    Main function to run the T&D Cosimulation    
    '''
    
    GlobalData.set_config('config.json')
    GlobalData.set_TDdata()
    startTime=time.time()        
    simulate()
#    GlobalData.print_data()
    print ('Simulation time: ' + str(time.time()-startTime) + "sec")
    generateReport(GlobalData,fname='report.xlsx',sim=GlobalData.config['simulationConfig']['simType'])
    return 0

def simulate():
    '''
    Run the simulation
    '''
    proc = Procedure()
    proc.simulate()

if __name__ == "__main__":
    main()
