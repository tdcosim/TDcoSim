import os
os.environ["PATH"] += os.getcwd()
import time
import argparse
from tdcosim.report import generateReport
from tdcosim.global_data import GlobalData
from tdcosim.procedure.procedure import Procedure


def main(configfile):
    '''
    Main function to run the T&D Cosimulation    
    '''
    
    GlobalData.set_config(configfile)
    GlobalData.set_TDdata()
    setOutLocation()
    startTime=time.time()        
    simulate()
#    GlobalData.print_data()
    print ('Simulation time: ' + str(time.time()-startTime) + "sec")
    generateReport(GlobalData,fname=GlobalData.config["outputPath"] + "\\reportfin.xlsx",sim=GlobalData.config['simulationConfig']['simType'])
    return 0

def setOutLocation():
    t = time.localtime()
    current_time = time.strftime("%m-%d-%y-%H-%M-%S", t)
    print("output folder name: " + current_time)
    outputfoldername = os.getcwd() + "\\output\\" + str(current_time)

    try:
        os.mkdir(outputfoldername)
    except:
        print("Filead create output folder")

    GlobalData.config["outputPath"] = outputfoldername

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
