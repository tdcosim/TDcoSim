
### Example 2: Dynamic Case Study with Single Distribution System with different DER penetration level and disturbance.

In this test, the TDcosim tool is tested for three different scenarios:
1. With distribution system connected to Bus 1 of 118 bus system where the DER penetration level is 10% of distribution system load and the DERs connected in the distribution system TRIP instantaneously below V_LV1 voltage level. The DER configuration used for this case is shown below:

                    "nodenumber": 1,
                    "filePath: ["C:\\Rojan\\NERC_TnD_Project\\pvder_refac\\NERC_PSSE_OpenDSS\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
                    "solarFlag":1,
                    "solarPenetration":0.1,
                    "DERParameters":{
                        "power_rating": 50,
                        "voltage_rating":174,
                        "SteadyState": true,
                        "V_LV1": 0.70,
                        "V_LV2": 0.88,
                        "t_LV1_limit": 10.0,  
                        "t_LV2_limit": 20.0,
                        "LVRT_INSTANTANEOUS_TRIP": true,
                        "LVRT_MOMENTARY_CESSATION": false,
                        "pvderScale": 1.0,
                        "solarPenetrationUnit":"kw",
                        "avoidNodes":["sourcebus","rg60"],
                        "dt":0.008333
                    


2. With distribution system connected to Bus 1 of 118 bus system where the DER penetration level is 10% of distribution system load and the DERs connected in the distribution system Ride Through the fault causing voltage sag below V_LV1 voltage level. The DER configuration used for this case is shown below:


                    "nodenumber": 1,
                    "filePath: ["C:\\Rojan\\NERC_TnD_Project\\pvder_refac\\NERC_PSSE_OpenDSS\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
                    "solarFlag":1,
                    "solarPenetration":0.1,
                    "DERParameters":{
                        "power_rating": 50,
                        "voltage_rating":174,
                        "SteadyState": true,
                        "V_LV1": 0.70,
                        "V_LV2": 0.88,
                        "t_LV1_limit": 10.0,  
                        "t_LV2_limit": 20.0,
                        "LVRT_INSTANTANEOUS_TRIP": false,
                        "LVRT_MOMENTARY_CESSATION": false,
                        "pvderScale": 1.0,
                        "solarPenetrationUnit":"kw",
                        "avoidNodes":["sourcebus","rg60"],
                        "dt":0.008333
                        
3. With distribution system connected to Bus 1 of 118 bus system without any DERs on the distribution system. The DER configuration used for this case is shown below:


        "nodenumber": 1,
                    "filePath: ["C:\\Rojan\\NERC_TnD_Project\\pvder_refac\\NERC_PSSE_OpenDSS\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
                    "solarFlag":0,
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
                        "LVRT_MOMENTARY_CESSATION": false,
                        "pvderScale": 1.0,
                        "solarPenetrationUnit":"kw",
                        "avoidNodes":["sourcebus","rg60"],
                        "dt":0.008333
                        

![Pload comparison](Use%20Case%20Results/Study%201/Pload_comparison_study_1.png)
Figure 1: Active component of load as observed at the T-bus for the cases considered. (A): 10% DER penetration with DER TRIP Settings, (B): 10% DER penetration with DER RT Settings and (C) 0% DER penetration.

Figure 1 above compares the active power component of the load observed in the T-bus for the three cases considered. It can be observed that case C, without DER on the distribution starts off with higher initial net load. Case A and Case B has a lower initial net load due to the DER connected in the distribution system masking the portion of total load in the system. Here net load is defined as the difference of the total load in the distribution system and the DER connected in the distribution system. 

A fault is applied in bus 5 of the T-system which causes a lower voltage sag in the D-system connected in bus 1. The simulation configuration to apply fault on bus 5 is shown below.


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


For the DER trip case, Case A, it can be observed that the net load observed in the bus increases to a value equal to the case without any DERs in the system, case C, which is an expected response of the system as net load in the T-bus reverts back to the total load as DER in the distribution system trips. A similar response can be observed for the reactive power component of the net load in the system as shown in Figure 2, which shows that the net reactive power equals the total reactive power as when DER trips, the system reverts back to the operational condition before DER connection in the system.

![Qload comparison](Use%20Case%20Results/Study%201/Qload_comparison_study_1.png)
Figure 2: Reactive component of load as observed at the T-bus for the cases considered. (A): 10% DER penetration with DER TRIP Settings, (B): 10% DER penetration with DER RT Settings and (C) 0% DER penetration.

![Vload comparison](Use%20Case%20Results/Study%201/Vload_comparison_study_1.png)
Figure 3:  T-bus 1 voltage comparison for the cases considered. (A): 10% DER penetration with DER TRIP Settings, (B): 10% DER penetration with DER RT Settings and (C) 0% DER penetration.

![speed comparison](Use%20Case%20Results/Study%201/Generator1_speed_study_1.png)
Figure 4:  Generator 1 Speed Comparison for the different cases considered.

Figure 3 shows the transmission bus voltage for bus 1 for the three cases considered. It can be observed that the voltage at bus 1 is same for all the cases considered. This is because for this case bus 1, where distribution system is connected, also had a synchronous generator connected to it which was regulating the bus voltage. Figure 4 shows the generator rotor frequency for the cases considered. It can be observed that the frequency nadir following system fault close to the fault location is lower for the case with DER trip. More tests with more distribution system and DERs should be performed to properly study the impact of DERs on system frequency response.


