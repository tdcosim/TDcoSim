
### Example 4: Dynamic Case Study with Eight Distribution System with different DER penetration level and Ride Through Settings and disturbances applied.

In this test, the TDcosim tool is tested for three different scenarios:
1. With distribution system connected to Bus 2,3,7,11,13,14,16 and 117 of 118 bus system where the DER penetration level is 10% of distribution system load and the DERs connected in the distribution system TRIP instantaneously below V_LV1 voltage level. The DER configuration used for this case is shown below (for bus number 2):

                    "nodenumber": 2,
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
                    

Same configuration was used for DERs in distribution system in bus number Bus 3,7,11,13,14,16 and 117.

2. With distribution system connected to Bus 2,3,7,11,13,14,16 and 117 of 118 bus system where the DER penetration level is 10% of distribution system load and the DERs connected in the distribution system Ride Through the fault causing voltage sag below V_LV1 voltage level. The DER configuration used for this case is shown below (for bus number 3):


                    "nodenumber": 2,
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
                        
Same configuration was used for DERs in distribution system in bus number Bus 3,7,11,13,14,16 and 117.

3. With distribution system connected to Bus 2,3,7,11,13,14,16 and 117 of 118 bus system without any DERs on the distribution system. The DER configuration used for this case is shown below:


        "nodenumber": 2,
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

![Pload comparison](Use%20Case%20Results/Study%204/no_DER_vs_DER_RT.png)
Figure 1: Active component of load as observed at the distribution system connected T-buses for the case with no DER and with DER with Ride Through Settings.

![Pload comparison](Use%20Case%20Results/Study%204/DER_Trip_vs_no_DER.png)
Figure 2: Active component of load as observed at the distribution system connected T-buses for the case with DER with Instantaneous Trip settings and with DER with Ride Through Settings.

![Pload comparison](Use%20Case%20Results/Study%204/DER_Trip_vs_DER_RT.png)
Figure 3: Active component of load as observed at the distribution system connected T-buses for the case with no DER and with DER with Instantaneous Trip Settings.

![Volt comparison](Use%20Case%20Results/Study%204/Transmission_bus_volt_no_DER_vs_DER_trip.png)
Figure 4: Transmission bus voltage comparison of the 118 bus system for the case with no DER with the case with DER with instantaneous trip settings.

![Qload comparison](Use%20Case%20Results/Study%204/Gen_speed_no_DER_vs_DER_trip.png)
Figure 5: Generator Frequency comparison of the 118 bus system for the case with no DER with the case with DER with instantaneous trip settings.

![Qload comparison](Use%20Case%20Results/Study%204/Generator_4_speed.PNG)
Figure 6: Generator Speed comparison of generator 4 for the three cases considered. a) No DER Case b) 10% DER with Ride Through Settings and c) 10% DER with instantaneous trip settings.


