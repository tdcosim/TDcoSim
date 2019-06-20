# Test of TDcoSim

## Dynamic Case Study with Single Distribution System with and without DER

In this test, the TDcosim tool is tested for three different scenarios:
1. With distribution system connected to Bus 1 of 118 bus system where the DER penetration level is 10% of distribution system load and the DERs connected in the distribution system TRIP instantaneously below UV2 voltage level.
2. With distribution system connected to Bus 1 of 118 bus system where the DER penetration level is 10% of distribution system load and the DERs connected in the distribution system Ride Through the fault causing voltage sag below UV2 voltage level.
3. With distribution system connected to Bus 1 of 118 bus system without any DERs on the distribution system.

![Pload comparison](Use%20Case%20Results/Study%201/Pload_comparison_study_1.png)
Figure 1: Active component of load as observed at the T-bus for the cases considered. (A): 10% DER penetration with DER TRIP Settings, (B): 10% DER penetration with DER RT Settings and (C) 0% DER penetration.

Figure 1 above compares the active power component of the load observed in the T-bus for the three cases considered. It can be observed that case C, without DER on the DS starts off with higher initial net load. Case A and Case B has a lower initial net load due to the DER connected in the distribution system masking the portion of total load in the system. A fault is applied in bus of the T-system which causes a lower voltage sag in the D-system connected in bus 1. For the DER trip case, Case A, it can be observed that the net load observed in the bus increases to a value equal to the case without any DERs in the system, which is an expected response of the system. A similar response can be observed for the reactive power component of the net load in the system as shown in Figure 2.


# Chapter 1
## Introduction to the Tutorial

This tutorial is intended to introduce the user to the TDcoSim tool. The user will be guided
through the creation and development of multiple test cases so as to gain familiarity with the 
basic features and functionalities of the tool. The tutorial project is developed in a 
sequential manner in which each of the use case builds upon what has been completed in the 
previous test case. 

***
Note: In order to execute the Tutorial, user needs to have PSSE version 30.0.0 or latest and 
OpenDSS v1.0 or latest.
***

# Chapter 2

## Exercise 1: Understanding the Config File

Before starting the operation of TDcoSim tool and running test cases, it is mandatory to understand the configuration file which sets up the simulation conditions. This chapter describes the different components of the configuration file and guides the user methods to set up the simulation.

1. "cosimHome":"C:\\Rojan\\NERC_TnD_Project\\pvder_refac\\NERC_PSSE_OpenDSS\\CoSimulator"

Variable "cosimHome" defines the parent path of the TDcoSim tool. The user needs to specify the parent path of the tool once the tool is installed in their workstation.

2. "psseConfig":{
        "rawFilePath":"C:\\Rojan\\NERC_TnD_Project\\pvder_refac\\NERC_PSSE_OpenDSS\\SampleData\\TNetworks\\118bus\\case118.raw",
        "dyrFilePath":"C:\\Rojan\\NERC_TnD_Project\\pvder_refac\\NERC_PSSE_OpenDSS\\SampleData\\TNetworks\\118bus\\case118.dyr"        
    }
    
 Variable "psseConfig" defines the path for the PSS/E transmission system loadflow and dynamic case file that will be used in the TDcoSim tool. "rawFilePath" specifies the path for the loadflow case file for the transmission system. "dyrFilePath" specifies the path for the dynamic case file for the transmission system.
 
 3. "openDSSConfig":{        
        "defaultFeederConfig":{
            "filePath":["C:\\Rojan\\NERC_TnD_Project\\pvder_refac\\NERC_PSSE_OpenDSS\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
            "solarFlag":0,
            "solarPenetration":0.0
            }
            }
            
 Variable "openDSSConfig" defines the path for the distribution system network used in the TDcoSim tool and configuration for the DER in the distribution system. There are two configuration used for the distribution system and DER, namely : "defaultFeederConfig" and "manualFeederConfig". For each configuration there are other variables that specify the path of the distribution network, penetration level of DER and status of the DER. 
 
 Variable "filePath" specifies the path for the OpenDSS File used in the tool.
 
 Variable "solarFlag" specifies whether the DER are present in the distribution system or not.
 
 Variable "solarPenetration" specifies the penetration level of DER within the distribution network.
            
        

