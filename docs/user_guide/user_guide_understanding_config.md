# Understanding the config file

The **config** file is the primary user interface for the TDcoSim package. Before starting the operation of TDcoSim tool and running test cases, it is necessary to understand how the configuration file can be used to setup the simulation conditions. This chapter describes the options within the configuration file and aids the user in setting up a simulation. 

## Config file options

The config file can be divided into three sections. The purpose of each option in every section is explained below:

### PSSE configuration

1. **cosimHome:** directory containing config file, and models for T and D systems (e.g. "C:\\\project_folder).

2. **psseConfig:** configuration for the transmission system.
   * ***rawFilePath***: full path for the PSS/E transmission system loadflow case file (e.g. "C:\\\project_folder\\\data\\\TNetworks\\\118bus\\\\**case118.raw**").
   * ***dyrFilePath***: full path for the PSS/E transmission system dynamic case file (e.g. "C:\\\project_folder\\\data\\\TNetworks\\\118bus\\\**case118.dyr**").

### OpenDSS + DER configuration

The default feeder configuration is **defaultFeederConfig**, which automatically assigns the same feeder to all the transmission system buses unless otherwise configured using **manualFeederConfig**.

1. **openDSSConfig:** configuration for distribution feeders. The user can choose a default feeder configuration through defaultFeederConfig option or specify individual feeder for each transmission bus through manualFeederConfig option.
   * ***defaultFeederConfig:*** Default feeder configuration that assigns identical distribution feeders to all the transmission buses.
     * *filePath (string):* Specifies the path for the OpenDSS File (e.g. "C:\\\project_folder\\\data\\\DNetworks\\\123bus\\\\**case123ZIP.dss**").
   
     * solarFlag (Boolean): Specifies presence or absence of PV-DERs in a feeder.
   
     * *solarPenetration (float):* Specifies the total rated capacity of PV-DERs as a percentage of the total feeder load in dynamic co-simulation (e.g. 0.1).
   
   * ***manualFeederConfig:*** Manually specify the distribution system configuration at the desired transmission bus.
     * *nodes:* Specifies the configuration of the distribution system.
     * *nodenumber (integer)*: Specifies the transmission bus where the distribution system is to be connected.
   
     * *filePath (string)*: Specifies the path for the OpenDSS File. (e.g. "C:\\\project_folder\\\data\\\DNetworks\\\123bus\\\\**case123ZIP.dss**")
       
     * *solarFlag (Boolean):* Specifies presence or absence of PV-DERs in a feeder.
     
     * solarPenetration (float) : Specifies the total rated capacity of PV-DERs as a percentage of the total feeder load in dynamic co-simulation (e.g. 0.1).
     
     * *DERParameters*: Specifies the configuration of PV-DERs to be used in the distribution system.
       * *power_rating (float):* Specifies the power rating of DER in kW (valid options: 50, 250).
       
       * *voltage_rating (float):* Specifies the voltage rating of the PV-DER in Volts (L-G RMS). The tool automatically adds a transformer to connect the DER to the distribution system.
       
       * *SteadyState (Boolean):* Specifies whether the states in PV-DER model is to be initialized with steady state values before connecting to the distribution system.
         
       * *V_LV1 (float):* Specifies the under-voltage 1 trip voltage set point in p.u. This is the lower limit of the DER trip voltage.
         
       * *V_LV2 (float):* Specifies the under-voltage 2 trip voltage set point in p.u. This is the upper limit of the DER trip voltage.
         
       * *t_LV1_limit (float):* Specifies the under-voltage 1 trip time set point in seconds. This is the trip time associated with lower limit of the DER trip voltage.
         
       * *t_LV2_limit (float):* Specifies the under-voltage 2 trip time set point in seconds. This is the trip time associated with upper limit of the DER trip voltage.
         
       * *LVRT_INSTANTANEOUS_TRIP (Boolean):* Specifies whether DER should trip immediately (within one cycle) after under-voltage 2 trip voltage set point has been breached.
       
       * *LVRT_MOMENTARY_CESSATION (Boolean):* Specifies whether DER should ramp back to nominal power when voltage recovers above the under-voltage 2 trip voltage set point.

       * *pvderScale (float):* Specifies the scaling factor associated with the DER power output from the feeder. A higher value of *pvderScale* for similar *solarPenetration* will result in lower number of DER model instances.

***
***Note:*** Please check sections 6.4.1 and 6.4.2 in [IEEE 1547-2018](https://standards.ieee.org/standard/1547-2018.html) for more information on voltage ride-through and trip settings.

***

### Simulation configuration

1. **simulationConfig:** Configuration options for the simulation.
   * ***simType:*** A string specifying whether the simulation is **'static'** or **'dynamic'**.
   * ***dynamicConfig:*** Configuration options for **'dynamic'** simulation.
     * *events (key):* Specifies the various events in the dynamic simulation listed sequentially.
       * *time (float):* Specifies the time at which an event occurs.
       * *type (string):* Specifies the type of an event (**'simEnd'**, **'faultOn'** or **'faultOff'** ).
       * *faultBus (integer):* Specifies the transmission bus at which the fault occurs.
       * faultImpedance (list of floats): Specifies the impedance of the fault.
   * ***staticConfig:*** Configuration options for **'static'** simulation.
     * *loadShape (list of floats):* Load served by the T+D system at each time interval (e.g. [0.81,0.75,0.72,..])
   *  ***protocol (string):*** Specifies the nature of coupling between Transmission system and Distribution System (valid options:**'loose_coupling'**,**'tight_coupling'**).

***
***Note:*** Tight coupling protocol is only available for static co-simulation in current version.

***
***
***Note:*** For static co-simulation, solar penetration needs to be implemented through the **.dss** file. Option to add solar shape through config file will be implemented in next version.

***

## config.json example
The example below shows the **config** file for a T & D **dynamic** co-simulation with a [IEEE 118 bus transmission system](https://icseg.iti.illinois.edu/ieee-118-bus-system/) having [IEEE 123 node test feeder](http://sites.ieee.org/pes-testfeeders/resources/) connected to all the buses for a simulation lasting for **1.0** seconds, with **0 %** PV-DER penetration.

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
        "protocol":"loose_coupling"
    }
}
```
