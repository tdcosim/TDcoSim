# Example 2: DER penetration and steady state initialization (detailed DER and fast DER)

In this test study, different penetration level of DERs within one distribution system connected to a transmission bus is studied. The purpose of this study is to test the ability of the tool to properly initialize the states of all the dynamic components of the system. Without any disturbance introduced in the system through changes in operating points or faults, it is expected that the responses of the various components in the system be a flat profile if the state of the various components are properly initialized i.e. all the variables should have a constant value throughout the duration of simulation.

## Co-simulation setup

1. **T system:** 118 bus system

```json
"psseConfig": {    
		       "rawFilePath": "data\\transmission\\118bus\\case118.raw",
			   "dyrFilePath": "data\\transmission\\118bus\\case118.dyr"
               }
```

2. **D + DER system:** 123 node feeder connected to bus 1 of 118 bus system.
   * DER penetration: Varied from 0 % (0.0) to 50 % (0.5) of distribution system load in 10 % increments.
   * DER rated capacity: 50 kVA
   2a. **DER model type:** Detailed DER model

```json
"manualFeederConfig":{
                        "nodes": [
                            {
                                "nodenumber": 1,
                                "filePath": ["\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
                                "solarFlag":1,
                                "DERModelType": "ThreePhaseUnbalanced",
                                "solarPenetration": 0.1,
                                "initializeWithActual": true,
                                "DERFilePath": "config\\detailed_der_default.json", 
                                "DERParameters":{
                                "default":{
                                     "pvderScale": 1, 
                                     "steadyStateInitialization": true, 
                                     "derId": "50"                 
                                          }
                                               }
                            }
                        ]
                    }
```
2b. **DER model type:** Fast DER model

```json
"manualFeederConfig": {
         "nodes": [
            {
               "solarFlag": 1, 
               "solarPenetration": 0.1, 
               "DERParameters": {
                  "default": {
                     "qref": 0, 
                     "pvderScale": 1, 
                     "pref": 50, 
                     "sbase": 50
                  }
               }, 
               "nodenumber": 1, 
               "filePath": ["data\\distribution\\123Bus\\case123ZIP.dss"
               ]
            }
         ]
      }
```

3. **Simulation configuration:** The co-simulation is run for 10 s and no faults are applied on the T side buses:

```json
"simulationConfig":{
        "protocol": "loose_coupling", 
        "simType":"dynamic",
        "dynamicConfig":{
            "events":{                
                "1":{
                    "time":10.0,
                    "type":"simEnd"                    
                    }
                     }}
```
## Results
Figures 1-3 shows the flat start performance of the TDcosim tool for different penetration level of DER. It can be observed that with the DER added into the test system, TDcosim tool takes couple of secs to reach the steady state active power consumption at the DER connected bus. Also, note that the settling value of the net active power is slightly below to the calculated net load power based on DER penetration. One of the reason for this is that the addition of DER within the distribution feeder doesn't amount to an exact amount of net load drop within the distribution feeder. This depends on the various factors like power output of the DER, location of DER, nature of the loads modelled and so on. We are working to have the net load initialized properly.

![Pload comparison](C:/Users/splathottam/Box Sync/GitHub/TDcoSim/docs/user_guide/examples/use_case_results/example_2/pload_comparison_bus_1.png)
Figure 1: Load observed in bus 1 for the different cases considered - (No DER,10% DER, 20% DER, 30% DER, 40% DER, 50% DER).

![Qload comparison](C:/Users/splathottam/Box Sync/GitHub/TDcoSim/docs/user_guide/examples/use_case_results/example_2/qload_comparison_bus_1.png)
Figure 2: Reactive power observed in bus 1 for the different cases considered - (No DER, 10% DER, 20% DER, 30% DER, 40% DER, 50% DER)

![Qload comparison](C:/Users/splathottam/Box Sync/GitHub/TDcoSim/docs/user_guide/examples/use_case_results/example_2/qload_comparison_bus_100.png)
Figure 3: Reactive power observed in bus 100 for the different cases considered. (No DER, 10% DER, 20% DER, 30% DER, 40% DER, 50% DER)

Figure 2 shows the reactive power observed in bus 1 for the different cases considered. It can be observed that the reactive power consumed at the DS & DER connected bus decreases as DER penetration increases. Figure 3 shows no change in the reactive power for a random bus (bus 100).

![Voltage_1 comparison](C:/Users/splathottam/Box Sync/GitHub/TDcoSim/docs/user_guide/examples/use_case_results/example_2/volt_comparison_bus_1.png)
Figure 4: Voltage profile observed in bus 1 for the different cases considered - (No DER, 10% DER, 20% DER, 30% DER, 40% DER, 50% DER)

![Voltage_2_100_ comparison](C:/Users/splathottam/Box Sync/GitHub/TDcoSim/docs/user_guide/examples/use_case_results/example_2/volt_comparison_bus_2_and_100.png)
Figure 5: Voltage profile observed in bus 2 and bus 100 for the different cases considered - (No DER, 10% DER, 20% DER, 30% DER, 40% DER, 50% DER)

Figure 4 shows the voltage plot for bus 1 for the different cases considered. It can be observed that the with the DER added in the system, the bus voltage settles at a higher steady state voltage and it takes almost 4 secs for the system to reach a steady state. Similar settling time were observed in the buses nearby the DER connected buses as shown in Figure 5, but not observed in electrically distant buses as shown in Figure 5.

![frequency_bus1_100_comparison](C:/Users/splathottam/Box Sync/GitHub/TDcoSim/docs/user_guide/examples/use_case_results/example_2/genspeed_comparison_bus_1_and_100.png)
Figure 6: Frequency plot for the generators at bus 1 and bus 100 for different levels of DER penetration.

Figure 6 shows the generator speed profile for different levels of DER penetration at bus 1 and bus 100. It can be observed that the system frequency is initialized at exactly 60 Hz and stays constant at 60 Hz throughout the simulation. It can be observed that the generator speed has few oscillations that dies down slowly over time. The oscillations are due to the mismatch in the calculation of initial conditions for load and generation.

Please note that the tool takes few simulation seconds for the system to reach a steady state solution for the dynamic cases when using detailed DER. The developers are working on the initialization of system dynamic states so as to obtain a steady state solution from time t=0+. So for the current version of the tool, to study the system dynamics change of operating points and disturbances are applied only after the system reaches a certain steady state threshold i.e. at least 0.5 seconds.

\pagebreak