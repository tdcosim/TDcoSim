
# Example 4: Test Example with Eight Distribution System comparing the impact of DER Tripping with DER riding through fault.

In this test, the TDcoSim tool is tested for three different scenarios:
1. With distribution system connected to Bus 2, 3, 7, 11,13,14,16, and 117 of 118 bus system where the DER penetration level is 10% of distribution system load and the DERs connected in the distribution system TRIP instantaneously below "0" voltage level. The DER configuration used for this case is shown below (for bus number 2):

                ```json
                "manualFeederConfig":{
                        "nodes": [
                            {
                                "nodenumber": 1,
                                "filePath": ["\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
                                "solarFlag":1,                
                                "DERParameters":{
                                "default":{
                                    "solarPenetration":0.1, 
                                    "powerRating": 50,
                                    "VrmsRating":174,
                                 "LVRT":"1":{"V_threshold":0.88,
                                             "t_threshold":2.0,
                                             "mode":"momentary_cessation"
                                             }
                                            }
                                                 }
                            }            
                        ]
                    }
                ```
            

Same configuration was used for DERs in distribution system in bus number Bus 3,7,11,13,14,16 and 117.

2. With distribution system connected to Bus 2,3,7,11,13,14,16 and 117 of 118 bus system where the DER penetration level is 10% of distribution system load and the DERs connected in the distribution system Ride Through the fault causing voltage sag below level "1" voltage threshold. The DER configuration used for this case is shown below (for bus number 3):


```json
"manualFeederConfig":{
        "nodes": [
            {
                "nodenumber": 1,
                "filePath": ["\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
                "solarFlag":1,                
                "DERParameters":{
                "default":{
                    "solarPenetration":0.1, 
                    "powerRating": 50,
                    "VrmsRating":174,
                 "LVRT":"1":{"V_threshold":0.88,
                             "t_threshold":2.0,
                             "mode":"mandatory_operation"
                             }
                            }
                                 }
            }            
        ]
    }
```

Same configuration was used for DERs in distribution system in bus number Bus 3,7,11,13,14,16 and 117.

3. With distribution system connected to Bus 2,3,7,11,13,14,16 and 117 of 118 bus system without any DERs on the distribution system. The DER configuration used for this case is shown below:


       "manualFeederConfig":{
            "nodes": [
                {
                    "nodenumber": 1,
                    "filePath": ["\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
                    "solarFlag":1,                
                    "DERParameters":{
                    "default":{
                        "solarPenetration":0.0
                               }
                                     }
                }            
            ]
        }

Same configuration was used for DERs in distribution system in bus number Bus 3,7,11,13,14,16 and 117.


The disturbance applied in this case is the fault on bus 5. The simulation configuration to apply fault on bus 5 is shown below.


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

![Pload comparison](./use_case_results/study_4/no_DER_vs_DER_RT.png)

Figure 1: Active component of load as observed at the distribution system connected T-buses for the case with no DER and with DER with Ride Through Settings.

Figure 1 shows that the with the DER added into the distribution system connected at various buses, the net load on those buses decreases. The ride through settings of the DER is working as its supposed on the TDcoSim tool as the net load of the bus before and after the fault is same.

![Pload comparison](./use_case_results/study_4/DER_Trip_vs_no_DER.png)

Figure 2: Active component of load as observed at the distribution system connected T-buses for the case with DER with Instantaneous Trip settings and with DER with Ride Through Settings.

Figure 2 shows the comparison of the net load in the distribution system connected buses with two different settings implemented in DER. With the ride through settings, the net load before and after the fault is same. However, with the instantaneous trip settings the net load after the fault is higher due to the DER tripping.

![Pload comparison](./use_case_results/study_4/DER_Trip_vs_DER_RT.png)

Figure 3: Active component of load as observed at the distribution system connected T-buses for the case with no DER and with DER with Instantaneous Trip Settings.

Figure 3 shows the comparison of the net load in the distribution system connected buses with instantaneous trip settings implemented in DER and with no DER in the distribution system. With the instantaneous trip settings, the net after the fault is same as the case with no DER. The difference between the post fault net load and pre-fault net load is the amount of DER that tripped due to the disturbance event.

![Volt comparison](./use_case_results/study_4/Transmission_bus_volt_no_DER_vs_DER_trip.png)

Figure 4: Transmission bus voltage comparison of the 118 bus system for the case with no DER with the case with DER with instantaneous trip settings.

Figure 4 compares the transmission bus voltage of the 118 bus system for the case with No DER and the case with instantaneous trip settings in DER. Much difference was not observed in this case as the overall DER penetration was low.

![Qload comparison](./use_case_results/study_4/Gen_speed_no_DER_vs_DER_trip.png)

Figure 5: Generator Frequency comparison of the 118 bus system for the case with no DER with the case with DER with instantaneous trip settings.

Figure 5 compares the generator speed of the various generators in the 118 bus test system for the case with No DER and case with 10% DER with instantaneous trip settings. The speed response of the generators for these two cases are identical as the DER penetration level compared to the overall system is insignificant. However, some impact can be observed locally as in the case of generator 4 as shown in Figure 6. Figure 6 shows that the frequency response of the generator 4 is worst in the case in the DER in the system trip instantaneously.

![Qload comparison](./use_case_results/study_4/Generator_4_speed.PNG)

Figure 6: Generator Speed comparison of generator 4 for the three cases considered. a) No DER Case b) 10% DER with Ride Through Settings and c) 10% DER with instantaneous trip settings.

\pagebreak