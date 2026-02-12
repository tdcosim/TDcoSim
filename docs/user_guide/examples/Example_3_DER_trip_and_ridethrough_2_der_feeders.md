
# Example 3: Impact of DERs in two Distribution Systems tripping and riding through fault.

* DERs trip instantaneously below level "0" voltage threshold.
* DERs ride through during the voltage anomaly

## Co-simulation setup
1. **T system:** 118 bus system
The configuration is same as that of Example 1.
2. **D + DER system:** 123 node feeder connected to bus 2 and bus 3 of 118 bus system.
   * DER penetration: 10% of distribution system load
   * DER model type: Detailed DER model
      * DER model sub-type:Three Phase Unbalanced

```json
"manualFeederConfig":{
                        "nodes": [
                            {
                                "nodenumber": 2,
                                "filePath": ["\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
                                "solarFlag":1,
                                "DERModelType": "ThreePhaseUnbalanced",
                                "solarPenetration": 0.1,
                                "DERFilePath": "config\\detailed_der_default.json", 
                                "DERParameters":{
                                "default":{
                                     "pvderScale": 1,
                                     "derId": "50_instant_trip"        
                                          }
                                               }
                            },
                            {
                                "nodenumber": 3,
                                "filePath": ["\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
                                "solarFlag":1,
                                "DERModelType": "ThreePhaseUnbalanced",
                                "solarPenetration": 0.1,
                                "DERFilePath": "config\\detailed_der_default.json", 
                                "DERParameters":{
                                "default":{
                                     "pvderScale": 1,
                                     "derId": "50_instant_trip"        
                                          }
                                               }
                            }
                        ]
                    }
```

2. With distribution system connected to Bus 2 and Bus 3 of 118 bus system where the DER penetration level is 10% of distribution system load.

3. distribution system Ride Through the fault causing voltage sag below level "0" voltage threshold. The DER configuration for bus 2 and bus 3 is same as that in example 1a.

The disturbance applied in this case is the fault on bus 5. The simulation configuration to apply fault on bus 5 is shown below.

```json
        "simulationConfig":{
        "simType":"dynamic",
        "dynamicConfig":{
            "events":{
                "1":{
                     "time":0.5,
                    "type":"faultOn",
                    "faultBus":5,
                    "faultImpedance":[0.0,-2.0E11]
                },
                "2":{
                    "type":"faultOff",
                    "time":0.6,
                    "faultBus":5
                },
                "3":{
                    "type":"simEnd",
                    "time":10.0
                }
            }
        },
        "staticConfig":{
            "loadShape": [1,1.1,1.2,0.9]
        },
        "protocol":"loose_coupling"
    },
    "outputConfig":{
        "outputfilename": "output.csv",
        "type": "csv"
    }
}
```
![Pload comparison](.\use_case_results\example_3\example_3_pload_bus2.png)

Figure 1: Active component of load as observed at the T-bus ‘2’ for the cases considered. (A): 10% DER penetration with DER RT Settings, (B): 0% DER penetration and (C) 10% DER penetration with DER TRIP Settings.

![Pload comparison](.\use_case_results\example_3\example_3_pload_bus3.png)

Figure 2: Active component of load as observed at the T-bus ‘3’ for the cases considered. (A): 10% DER penetration with DER RT Settings, (B): 0% DER penetration and (C) 10% DER penetration with DER TRIP Settings.

![Pload comparison](.\use_case_results\example_3\example_3_pload_bus1.png)

Figure 3: Active component of load as observed at the T-bus ‘1’ for the cases considered. (A): 10% DER penetration with DER RT Settings, (B): 0% DER penetration and (C) 10% DER penetration with DER TRIP Settings.

Figure 1 and 2 above compares the active power component of the load observed in the T-bus (2 and 3 where the DER connected distribution system is modelled) for the three cases considered. It can be observed that case B, without DER on the DS starts off with higher initial net load. Case A and Case C has a lower initial net load due to the DER connected in the distribution system masking the portion of total load in the system. A fault is applied in bus 5 of the T-system which causes a lower voltage sag in the D-system connected in bus 2 and bus 3. For the DER trip case, Case C, it can be observed that the net load observed in the bus increases to a value equal to the case without any DERs in the system, which is an expected response of the system. 

A similar response can be observed for the reactive power component of the net load for bus ‘2’ and bus ‘3’ in the system as shown in Figure 4 and 5. In case of reactive power, the offset in reactive power with DERs connected was due to the differences in the load flow within the distribution system due to DER interconnection.

Figure 3 compares the active power component of the load observed in bus 1 of the T-system, as no DER connected distribution system was modelled for this bus, the load profile for all the three cases considered are the same.

A similar response can be observed in Figure 6 for reactive power component of net load connected at bus ‘1’ as no distribution system was connected in bus 1.

![Qload comparison](.\use_case_results\example_3\example_3_qload_bus2.png)

Figure 4: Reactive component of load as observed at the T-bus ‘2’ for the cases considered. (A): 10% DER penetration with DER RT Settings, (B): 0% DER penetration and (C) 10% DER penetration with DER TRIP Settings.

![Qload comparison](.\use_case_results\example_3\example_3_qload_bus3.png)

Figure 5: Reactive component of load as observed at the T-bus ‘3’ for the cases considered. (A): 10% DER penetration with DER RT Settings, (B): 0% DER penetration and (C) 10% DER penetration with DER TRIP Settings.

![Qload comparison](.\use_case_results\example_3\example_3_qload_bus1.png)

Figure 6: Reactive component of load as observed at the T-bus ‘1’ for the cases considered. (A): 10% DER penetration with DER RT Settings, (B): 0% DER penetration and (C) 10% DER penetration with DER TRIP Settings.


![volt comparison](.\use_case_results\example_3\example_3_volt_bus2.png)

Figure 7: Voltage of bus 2 for the cases considered. (A): 10% DER penetration with DER RT Settings, (B): 0% DER penetration and (C) 10% DER penetration with DER TRIP Settings.

![volt comparison](.\use_case_results\example_3\example_3_volt_bus3.png)

Figure 8: Voltage of bus 3 for the cases considered. (A): 10% DER penetration with DER RT Settings, (B): 0% DER penetration and (C) 10% DER penetration with DER TRIP Settings.

Figure 7 and Figure 8 shows the transmission bus voltage for bus 2 and bus 3 respectively, for the three cases considered. It can be observed that the voltage at bus 2 and bus 3 is almost the same for all the cases considered which could be associated with the low DER penetration and effect of nearby synchronous machine’s voltage regulation. 

More studies with higher DER penetration level with distribution system in large number of buses are also conducted and discussed in following subsections. 

\pagebreak