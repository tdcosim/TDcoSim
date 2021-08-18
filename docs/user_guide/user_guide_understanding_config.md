# Understanding the config file

The **config** file is the primary user interface for the TDcoSim package. Before starting the operation of TDcoSim tool and running test cases, it is necessary to understand how the configuration file can be used to setup the simulation conditions. This chapter describes the options within the configuration file and aids the user in setting up a simulation. 

## Config file options

The config file can be divided into three sections. The purpose of each option in every section is explained below:

### cosimHome
 **cosimHome (string):** Specify the directory containing config file, and models for T and D systems (e.g. "C:\\\project_folder).

### Logging configuration

1. **level (int):** The logging level which can be either 10 (debug), 20 (info), 30 (warning) or 40 (error). Note that all log files will be saved in the **logs** folder.
2. **saveSubprocessOutErr (boolean):** Enable logging of error output corresponding to a T node  in seperate ***.err** file.

### PSSE configuration

1. **psseConfig (dict):** configuration for the transmission system.
   * ***installLocation (string)*** : full path for PSS/E transmission system python library location. If there isn't a specific location, system will look up the default installation path of PSS/E 33 (e.g. "C:\\Program Files\\PTI\\PSSE35\\35.0\\PSSPY27")
   * ***rawFilePath (string)*** : full path for the PSS/E transmission system loadflow case file (e.g. "C:\\\project_folder\\\data\\\TNetworks\\\118bus\\\\**case118.raw**").
   * ***dyrFilePath (string)***: full path for the PSS/E transmission system dynamic case file (e.g. "C:\\\project_folder\\\data\\\TNetworks\\\118bus\\\**case118.dyr**").

### OpenDSS + DER configuration

The default feeder configuration is **defaultFeederConfig**, which automatically assigns the same feeder to all the transmission system buses unless otherwise configured using **manualFeederConfig**.

1. **DEROdeSolver (string):**  If fast DER models, specify **fast_der** since they always use the forward euler solver implimented in TDcoSim. If detailed DER models are being used, specify the solver (either **scipy** or **diffeqpy**).
2. **DEROdeMethod (string):**  It is **not applicable** for fast DER models. It is used to specify the solver method for detailed DER models. The available options are **bdf** and **adams** for **scipy**, **CVODE_BDF** and **TRBDF2**for **diffeqpy**.

1. **openDSSConfig (dict):** Configuration for distribution feeders. The user can choose a default feeder configuration through defaultFeederConfig option or specify individual feeder for each transmission bus through manualFeederConfig option.
   * ***defaultFeederConfig (dict):*** Default feeder configuration that assigns identical distribution feeders to all the transmission buses.
     * *filePath (string):* Specifies the path for the OpenDSS File (e.g. "C:\\\project_folder\\\data\\\DNetworks\\\123bus\\\\**case123ZIP.dss**").
     
     * *solarFlag (Boolean):* Specifies presence or absence of PV-DERs in a feeder.
     
     * *solarPenetration (float):* Specifies the total rated capacity of PV-DERs as a percentage of the total feeder load in dynamic co-simulation (e.g. 0.1).
     
   * ***manualFeederConfig:*** Manually specify the distribution system configuration at the desired transmission bus.
     * *nodes (list of dict):* Specifies the configuration of the distribution system and DERs.
       * *nodenumber (integer)*: Specifies the transmission bus to which the distribution system will be connected.
       * *filePath (string)*: Specifies the path for the OpenDSS File containing the distribution system model. (e.g. "C:\\\project_folder\\\data\\\DNetworks\\\123bus\\\\case123ZIP.dss")
       * *solarFlag (bool):* Specifies presence or absence of PV-DERs in the distribution system.
       * *solarPenetration (float)*: Specifies the total rated capacity of PV-DERs as a percentage of the total feeder load in dynamic co-simulation (e.g. 0.1). It will only be used if *DERSetting* is *default*.
       * *fractionAggregatedLoad (dict):*  It specifies the type of load model used to model the load at the T node. The available options are: "cmld", "clod"
       * *DERFilePath (string)*: This is only applicable for detailed DER models. Specifies the path for the JSON file containing the parameters and settings defining the DER model. Note that a single file may contain settings for any number of DER models.  
       * *initializeWithActual (bool)*: This is only applicable if detailed DER models are being used in the feeder. If ***true***, the actual power output from the DER model instance will be used when setting up T+D co-simulation.  If ***false***, the rated power output given in DER settings will be used.
       * *DERSetting (string)*: Specifies DER configuration at each node. If ***PVPlacement***, the DER at each node will use a unique set of DER settings. If ***default***, DERs at all nodes will use the same DER settings.
       * *DERModelType (string)*: This is only applicable if detailed DER models are being used in the feeder. Specifies the type of detailed DER model to be used in each node of the particular feeder. Valid options are: "ThreePhaseUnbalanced","ThreePhaseBalanced","ThreePhaseUnbalancedConstantVdc", "ThreePhaseUnbalancedNumba"
       * *DERParameters (dict):* Specifies the configuration of PV-DERs to be used in the distribution system. If *PVPlacement* **is provided**, the DER at each node will need a separate set of DER settings. If *default* **is provided**, DERs at all nodes will use the same DER settings.
         * *default:* DER settings that will be used if *DERSetting* is *default*. Note that these settings are optional if *DERSetting* is *PVPlacement*.
           * *pvderScale (float):* Specifies the scaling factor with which to multiply the DER power output from any given node. A higher value of *pvderScale* for similar *solarPenetration* will result in lower number of DER model instances.
           * *pref:* This is only applicable if fast DER models are being used in the feeder. Specifies the rated active power output of the fast DER model.
           * *pref:* This is only applicable if fast DER models are being used in the feeder. Specifies the rated reactive power output of the fast DER model.
           * *interconnectionStandard:* This is only applicable if fast DER models are being used in the feeder. It specified the interconnection settings that must be used during voltage anomalies.
           * *derId (string):* This is only applicable if detailed DER models are being used in the feeder. The key word corresponding to DER model that is available in DER config file. Note that an exception will be thrown if a matching *derId* is not found in the DER config file.
           * *powerRating (float):* This is only applicable if detailed DER models are being used in the feeder. Specifies the rated power of DER in kVA. Note that value specified here will override the rated power given in the DER config file. 
           * *VrmsRating (float):* This is only applicable if detailed DER models are being used in the feeder.  Specifies the rated RMS voltage (L-G) of the DER in Volts. The tool automatically adds a transformer to connect the DER to the distribution system. Note that value specified here will override the rated voltage given in the DER config file. 
           * *steadyStateInitialization (bool):* This is only applicable if detailed DER models are being used in the feeder. Specifies whether the states in PV-DER model is to be initialized with steady state values before simulation is started.
           * *LVRT (dict):* This is only applicable if detailed DER models are being used in the feeder. Low voltage ride through settings.  Either a pre-defined configuration available in *config_der.json* may be provided or an arbitrary number of ride through settings may be defined based on voltage thresholds.
               * *config_id (string):* Specifies the LVRT configuration available in the *config_der.json* that should be used.
               * *V_threshold (float):* Specifies the voltage threshold for low voltage anomaly in p.u. 
               * *t_threshold (float):* Specifies the trip time threshold for low voltage anomaly in seconds. 
               * *mode (string):* Specifies the DER operating behavior during ride through (options: 'momentary_cessation','mandatory_operation'). 
           
           * *HVRT (dict):* High voltage ride through settings. An arbitrary number of ride through settings may be defined based on voltage thresholds.
               * *V_threshold (float):* Specifies the voltage threshold for high voltage anomaly in p.u. 
               * *t_threshold (float):* Specifies the trip time threshold for high voltage anomaly in seconds. 
               * *mode (string):* Specifies the DER operating behavior during ride through (options: 'momentary_cessation','mandatory_operation'). 
           * *VRT_delays (dict):* Time delay settings for power output cessation and output restoration.
               * *output_cessation_delay (float):* Specifies the time delay before power output from DER ceases.
               * *output_restore_delay (float):* Specifies the time delay before DER starts restoring power output after momentary cessation.
         * *PVPlacement (dict):* Specifies the distribution system node and the details of the DER to be connected to that node. Note that these settings are optional if *DERSetting* is *default*.
           * *node (string):* Any three phase node in the OpenDSS model. Note that the keyword ***node*** must be replaced with the actual node name.
             *  *derId (string):* This is only applicable if detailed DER models are being used in the feeder. The key word corresponding to DER model that is available in DER config file. Note that an exception will be thrown if a matching *derId* is not found in the DER config file.
             *  *powerRating (float):* This is only applicable if detailed DER models are being used in the feeder. Specifies the rated power of DER in kVA. Note that value specified here will override the rated power given in the DER config file. 
             *  *pvderScale (float):* This is only applicable if detailed DER models are being used in the feeder. Specifies the scaling factor with which to multiply the DER power output from any given node.
             *  *VrmsRating (float):* This is only applicable if detailed DER models are being used in the feeder. Specifies the rated RMS voltage (L-G) of the DER in Volts. The tool automatically adds a transformer to connect the DER to the distribution system. Note that value specified here will override the rated voltage given in the DER config file. 
         
***
***Note:*** Please check sections 6.4.1 and 6.4.2 in [IEEE 1547-2018](https://standards.ieee.org/standard/1547-2018.html) for more information on voltage ride-through and trip settings.

***

### Simulation configuration

1. **simulationConfig (dict):** Configuration options for the simulation.
   * ***simType (string):*** A string specifying whether the simulation is **'static'** or **'dynamic'**.
   * ***defaultLoadType***: The default load model that is attached to the T node's that do not have distribution system feeder models connected to it. Available options are: "cmld", "clod"
   * ***dynamicConfig (dict):*** Configuration options for **'dynamic'** simulation.
     * *events (dict):* Specifies the various events in the dynamic simulation listed sequentially.
       * *time (float):* Specifies the time at which an event occurs.
       * *type (string):* Specifies the type of an event (**'simEnd'**, **'faultOn'** or **'faultOff'** ).
       * *faultBus (integer):* Specifies the transmission bus at which the fault occurs.
       * faultImpedance (list of floats): Specifies the impedance of the fault.
   * ***staticConfig (dict):*** Configuration options for **'static'** simulation.
     * *loadShape (list of floats):* Load served by the T+D system at each time interval (e.g. [0.81,0.75,0.72,..])
   *  ***protocol (string):*** Specifies the nature of coupling between Transmission system and Distribution System (valid options:**'loose_coupling'**,**'tight_coupling'**).
   *  ***memoryThreshold (float):*** Specifies the threshold before the co-simulation results collected in memory (RAM) are written to disk. This should be adjusted by the user depending upon the system memory to avoid crashes due to out of memory errors.
***
***Note:*** Tight coupling protocol is only available for static co-simulation in current version.

***
***
***Note:*** For static co-simulation, solar penetration needs to be implemented through the **.dss** file. Option to add solar shape through config file will be implemented in next version.

***
### Output configuration

1. **outputConfig (dict):** Configuration options for the data generated during simulation..
   * ***simID***: The main identifier string for the co-simulation. It will also be used to name the folder which will store the co-simulation results..
   * ***scenarioID***: An additional identifier string for the co-simulation. It will be included in the dataframe containing the co-simulation results.
   * ***outputDir (string):*** Main folder within which the results generated during co-simulation would be stored. There will be sub-folders corresponding to the **simID** within this folder.
   * ***outputfilename (string):*** File names given to the **.pkl** file containing the co-simulation results.
   * ***type (string):*** Format in which the results generated during simulation would be stored. Available options are: **dataframe**, **csv**.

## config.json example
The example below shows the **config** file for a T & D **dynamic** co-simulation with a [IEEE 118 bus transmission system](https://icseg.iti.illinois.edu/ieee-118-bus-system/) having [IEEE 123 node test feeder](http://sites.ieee.org/pes-testfeeders/resources/) connected to all the buses for a simulation lasting for **1.0** seconds, with **0 %** PV-DER penetration.

```json
{
    "cosimHome":"C:\\Users\\username\\Documents\\TDcoSim\\CoSimulator",
    "logging": {
         "level": 20, 
         "saveSubprocessOutErr": true},
    "psseConfig":{
        "rawFilePath":"C:\\Users\\username\\Documents\\TDcoSim\\SampleData\\TNetworks\\118bus\\case118.raw",
        "dyrFilePath":"C:\\Users\\username\\Documents\\TDcoSim\\SampleData\\TNetworks\\118bus\\case118.dyr"        
    },
    "openDSSConfig":{"DEROdeSolver":"fast_der",       
        "defaultFeederConfig":{
            "filePath":["CC:\\Users\\username\\Documents\\TDcoSim\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
            "solarFlag":0,
            "solarPenetration":0.0,
            "DERParameters": {
						"default": {
							"pvderScale": 1, 
							"pref":10,
							"qref":0,
							"sbase":10
						}
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
            },
"memoryThreshold": 20480.0, 
"protocol":"loose_coupling",
"outputConfig": {
   "simID": "test", 
   "type": "dataframe", 
   "outputDir": "..\\output", 
   "outputfilename": "test", 
   "scenarioID": "0percent"
}
}
```

\pagebreak
