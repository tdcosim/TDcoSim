import os
import time
import pdb

from tdcosim.report import generateReport
from tdcosim.global_data import GlobalData
from tdcosim.procedure.procedure import Procedure


def main():
    '''
    Main function to run the T&D Cosimulation    
    '''
    GlobalData.set_config('config_td.json')
    GlobalData.set_TDdata()
    simulate()  
    generateReport(GlobalData,fname='report.xlsx',sim=GlobalData.config['simulationConfig']['simType'])
    return 0

def simulate():
    '''
    Run the simulation
    '''
    proc = Procedure()
    proc.simulate()

if __name__ == "__main__":
    start_time = time.time()
    main()
    print('Solution time:',time.time()-start_time)
