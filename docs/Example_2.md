### Example 1: Dynamic Case Study with Single Distribution System with different DER penetration and no disturbances

In this test study, different penetration level of DERs within one distribution system connected to a transmission bus is studied. The purpose of this study is to test the ability of the tool to properly initialize all the dynamic components of the system. Without any disturbance introduced in the system through changes in operating point or faults, it is expected that the responses observed at the various point in the system be a flat profile if the state of the various components are properly initialized.

The DER configuration used in this case is as follows, where the "solarPenetartion" was incremented with 10% increment for each of the cases: 

    "manualFeederConfig":{
            "nodes": [
                {
                    "nodenumber": 1,
                    "filePath": ["C:\\Rojan\\NERC_TnD_Project\\pvder_refac\\NERC_PSSE_OpenDSS\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
                    "solarFlag":1,
                    "solarPenetration":0.0,  
                    "DERParameters":{
                        "power_rating": 50,
                        "voltage_rating":174,
                        "SteadyState": true,
                        "V_LV1": 0.70,
                        "V_LV2": 0.88,
                        "t_LV1_limit": 10.0,  
                        "t_LV2_limit": 20.0,
                        "LVRT_INSTANTANEOUS_TRIP": false,
                        "LVRT_MOMENTARY_CESSATION": false
                    }
                }
            ]
        }

The study was done with 123 node distribution system connected to bus 1 of the IEEE 118 bus system and five different DER penetration level relative to load in bus 1 ranging from 0 to 40% with the step increment of 10% is studied.


![Pload comparison](Use%20Case%20Results/Study%202/active_power_comparison_bus_1.png)

Figure 6: Active Power observed in bus 1 for the different cases considered (Green: No DER, Red: 10% DER, Cyan: 20% DER, Black: 30% DER, Blue: 40% DER).

![Qload comparison](Use%20Case%20Results/Study%202/reactive_power_comparison_bus_1.png)

Figure 7: Reactive power observed in bus 1 for the different cases considered. (Green: No DER, Red: 10% DER, Cyan: 20% DER, Black: 30% DER, Blue: 40% DER)

![Qload comparison](Use%20Case%20Results/Study%202/reactive_power_comparison_bus_100.png)

Figure 8: Reactive power observed in bus 100 for the different cases considered. (Green: No DER, Red: 10% DER, Cyan: 20% DER, Black: 30% DER, Blue: 40% DER)



Figure 6 shows the flat start performance of the TDcosim tool for different penetration level of DER. It can be observed that with the DER added into the test system, TDcosim tool takes couple of secs to reach the steady state active power consumption at the DER connected bus. Also, note that the settling value of the net active power is slightly below to the calculated net load power based on DER penetration.

Figure 7 shows the reactive power observed in bus 1 for the different cases considered. It can be observed that the reactive power consumed at the DS & DER connected bus decreases as DER penetration increases. Figure 8 shows no change in the reactive power for a random bus (bus 100).

![Voltage_1 comparison](Use%20Case%20Results/Study%202/voltage_profile_comparison_bus_1.png)

Figure 9: Voltage profile observed in bus 1 for the different cases considered. (Green: No DER, Red: 10% DER, Cyan: 20% DER, Black: 30% DER, Blue: 40% DER)

![Voltage_2 comparison](Use%20Case%20Results/Study%202/voltage_profile_comparison_bus_2.png)

Figure 10: Voltage profile observed in bus 2 for the different cases considered. (Green: No DER, Red: 10% DER, Cyan: 20% DER, Black: 30% DER, Blue: 40% DER)


![Voltage_100 comparison](Use%20Case%20Results/Study%202/voltage_profile_comparison_bus_100.png)

Figure 11: Voltage profile observed in bus 100 for the different cases considered. (Green: No DER, Red: 10% DER, Cyan: 20% DER, Black: 30% DER, Blue: 40% DER):


Figure 9 shows the voltage plot for bus 1 for the different cases considered. It can be observed that the with the DER added in the system, the bus voltage settles at a higher steady state voltage and it takes almost 4 secs for the system to reach a steady state. Similar settling time were observed in the buses nearby the DER connected buses as shown in Figure 10.

Such differences in settling time were not observed in electrically distant buses as shown in Figure 11, even though steady state differences were observed between different cases.

Please note that the tool takes few simulation seconds for the system to reach a steady state solution for the dynamic cases. The developers are working on the initialization of system dynamic states so as to obtain a steady state solution from time t=0+. So for the current version of the tool, to study the system dynamics change of operating points and disturbances are applied only after the system reaches a certain steady state threshold. i.e. at least 0.5 seconds.
