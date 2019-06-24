# Chapter 2
## Understanding the config file

The **config** file is the primary user interface for the TDcoSim package. Before starting the operation of TDcoSim tool and running test cases, it is necessary to understand how the configuration file can be used to setup the simulation conditions. This chapter describes the options within the configuration file and aid the user in setting up a simulation. 
## Config file options

The config file can be divided into three sections. The purpose of each option in every section is explained below:

### PSSE configuration

1. **cosimHome:** Directory containing config file, and models for T and D system.

2. **psseConfig:** Configuration for  transmission system.

   * ***rawFilePath***: Full path for the PSS/E transmission system loadflow case file (***.raw** ).
   * ***dyrFilePath***: Full path for the PSS/E transmission system dynamic case file (***.dyr** ).

### OpenDSS + DER configuration

1. **openDSSConfig:** Configuration for distribution feeder. There is option to provide a default feeder configuration or individually for each feeder.
   * ***defaultFeederConfig:*** Default feeder configuration (applies to feeders on all buses).
     * *filePath (string):* Specifies the path for the OpenDSS File **( *.dss)**.
   
     * solarFlag (Boolean): Specifies presence or absence of PV-DER's in the feeder.
   
     * *solarPenetration (float):* Specifies the total rated capacity of PV-DER's as a fraction of the total feeder load.
   
   * ***manualFeederConfig:*** Manually specify the configuration of the distribution network.
     * *nodes:* Specifies the configuration each of the distribution system.
     * *nodenumber (integer)*: Specifies the transmission bus where the distribution system is to be connected.
   
     * *filePath (string)*: Specifies the path for the OpenDSS File **( *.dss)**.
       
     * *solarFlag (Boolean):* Specifies whether the DER are present in the distribution system or not.
     
     * solarPenetration (float) : Specifies the total rated capacity of DER's as a fraction of the total feeder load.
     
     * *DERParameters*: Specifies the configuration of DERs to be used in the distribution system.
       * *power_rating (float):* Specifies the power rating of DER in kW.
       
       * *voltage_rating (float):* Specifies the voltage rating of the DER in Volts (L-G RMS). The tool automatically adds a transformer to connect the DER with the distribution system.
       
       * *SteadyState (Boolean):* Specifies whether the states in DER model is to be initialized with steady state values before connecting to the distribution system.
         
       * *V_LV1 (float):* Specifies the under-voltage 1 trip voltage set point in V p.u. This is the lower limit of the DER trip voltage.
         
       * *V_LV2 (float):* Specifies the under-voltage 2 trip voltage set point in V p.u. This is the upper limit of the DER trip voltage.
         
       * *t_LV1_limit (float):* Specifies the under-voltage 1 trip time set point in seconds. This is the trip time associated with lower limit of the DER trip voltage.
         
       * *t_LV2_limit (float):* Specifies the under-voltage 2 trip time set point in seconds. This is the trip time associated with upper limit of the DER trip voltage.
         
       * *LVRT_INSTANTANEOUS_TRIP (Boolean):* Specifies whether DER should trip immediately (within one cycle) after under-voltage 2 trip voltage set point has been breached.
       
       * *LVRT_MOMENTARY_CESSATION (Boolean):* Specifies whether DER should ramp back to nominal power when voltage recovers above the under-voltage 2 trip voltage set point.
       
       * *pvderScale (float):* Specifies the scaling factor associated with the DER power output from the feeder. A higher value of *pvderScale* for similar *solarPenetration* will result in lower number of DER model instances.
         
       * *solarPenetrationUnit (string):*  specifies the unit of solar penetration in the distribution system.
         
       * *avoidNodes (list of strings):* Specifies the nodes in the distribution system that are to be avoided when placing the DER. The tool automatically places the DER at different nodes of the distribution system while avoiding the nodes specified here.
         
       * *dt:* Specifies the time step at which voltage/power information is exchanged with DER model instance.
         
### Simulation configuration

1. **simulationConfig:** Configuration options for the simulation.
   * ***simType:*** A string specifying whether the simulation is **'static'** or **'dynamic'**.
   * ***dynamicConfig:*** Configuration options for **'dynamic'** simulation.
     * *events (key):* Specifies the various events in the dynamic simulation listed sequentially.
       * *time (float):* Specifies the time at which event occurs.
       * *type (string):* Specifies type of event (**'simEnd'**, **'faultOn'** or **'faultOff'** ).
       * *faultBus (integer):* Specifies the transmission bus at which fault occurs.
       * faultImpedance (list of floats):* Specifies the impedance of fault.
   * ***staticConfig:*** Configuration options for **'static'** simulation.
     * *loadShape (list of floats):* N/A
   *  ***protocol (string):*** Specifies the nature of coupling between Transmission system and Distribution System (**'loose_coupling'**).

config.json example
----
The example below shows the **config** file for a T+D dynamic simulation with a [IEEE 118 bus transmission system](https://icseg.iti.illinois.edu/ieee-118-bus-system/) having [IEEE 123 node test feeder](http://sites.ieee.org/pes-testfeeders/resources/) connected to all the buses for a simulation lasting for 1.0 seconds.

```json
{
    "cosimHome":"C:\\Users\\username\\Documents\\TDcoSim\\CoSimulator",
    "psseConfig":{
        "rawFilePath":"C:\\Users\\username\\Documents\\TDcoSim\\SampleData\\TNetworks\\118bus\\case118.raw",
        "dyrFilePath":"C:\\Users\\username\\Documents\\TDcoSim\\SampleData\\TNetworks\\118bus\\case118.dyr"        
    },
    "openDSSConfig":{        
        "defaultFeederConfig":{
            "filePath":["CC:\\Users\\username\\Documents\\TDcoSim\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
            "solarFlag":0,
            "solarPenetration":0.0
                             },
                    },
    "simulationConfig":{
        "simType":"dynamic",
        "dynamicConfig":{
            "events":{
                "1":{
                    "type":"simEnd",
                    "time":1.0
                    }
                     }
        },
        "staticConfig":{
            "loadShape": [1,1.1,1.2,0.9]
        },
        "protocol":"loose_coupling"
    }
}
```

Copyright © 2019, UChicago Argonne, LLC
