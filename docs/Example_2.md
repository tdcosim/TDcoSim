### Example 2: Dynamic Case Study with Single Distribution System with different DER penetration and no disturbances

In this test study, different penetration level of DERs within one distribution system connected to a transmission bus is studied. The purpose of this study is to test the ability of the tool to properly initialize all the dynamic components of the system. Without any disturbance introduced in the system through changes in operating point or faults, it is expected that the responses observed at the various point in the system be a flat profile.

The study was done with distribution system connected to bus 1 of the 118 bus system and five different DER penetration ranging from 0 to 40% with the step increment of 10% is studied.


![Pload comparison](Use%20Case%20Results/Study%202/active_power_comparison_bus_1.png)
Figure 6: Active Power observed in bus 1 for the different cases considered (Green: No DER, Red: 10% DER, Cyan: 20% DER, Black: 30% DER, Blue: 40% DER).

![Qload comparison](Use%20Case%20Results/Study%202/reactive_power_comparison_bus_1.png)
Figure 7: Reactive power observed in bus 1 for the different cases considered. (Green: No DER, Red: 10% DER, Cyan: 20% DER, Black: 30% DER, Blue: 40% DER)

![Qload comparison](Use%20Case%20Results/Study%202/reactive_power_comparison_bus_100.png)
Figure 8: Reactive power observed in bus 100 for the different cases considered. (Green: No DER, Red: 10% DER, Cyan: 20% DER, Black: 30% DER, Blue: 40% DER)



Figure 6 shows the flat start performance of the TDcosim tool for different penetration level of DER. It can be observed that with the DER added into the test system, TDcosim tool takes couple of secs to reach the steady state active power consumption at the DER connected bus. Also, note that the settling value of the net active power is slightly below to the calculated net load power based on DER penetration.
Figure 7 shows the reactive power observed in bus 1 for the different cases considered. It can be observed that the reactive power consumed at the DS & DER connected bus decreases as DER penetration increases. Figure 8 shows no change in the reactive power for a random bus (bus 100) other than DER connected bus at different DER penetration level.
