# Chapter 4
## Software details

### Features
1. Capable of launching sub-processes for individual feeders.
2. Capable of configuring each feeder with different DER penetration levels, DER ratings, and ride through settings.
3. Introduce fault events during simulation.
4. Capture and report data for each transmission for the entirety of the simulation.

### Main components
The T&D co-simulation tool comprises a transmission simulator, a distribution simulator, an interface module linking T&D simulators with sockets and interaction protocols, and a synchronization module.

**1. T&D interface:**
A Python program that passes along and iterates information (voltages, currents, and powers) between T&D simulators through loosely coupled or tightly coupled protocols.
  * Loosely coupled methods: There is a one-step lag in information exchange between transmission and distribution, but less computation is required. 

**2. D+DER interface:**
A Python program that exchanges information between the distribution system and the dynamic DER model.

**3. Configuration file:**
It is the main user interface that allows user to configure a T+D or T+D+DER co-simulation. 

### External components
1.[PSS®E](https://new.siemens.com/global/en/products/energy/services/transmission-distribution-smart-grid/consulting-and-planning/pss-software/pss-e.html)
It is an off-the-shelf positive-sequence dynamic simulator, is a transmission simulator. 

2.[OpenDSS](https://www.epri.com/#/pages/sa/opendss)
It is a three-phase unbalanced distribution system dynamic simulator, is a distribution simulator.

3.[Solar PV-DER simulation utility](https://github.com/sibyjackgrove/SolarPV-DER-simulation-utility)
It is Python utility than can simulate dynamics of grid connected solar PV-DER systems. It uses dynamic phasor models and has single and three phase PV-DER's. 

### Software architecture
A schematic showing the software architecture of the TDcoSim package is shown in the figure below:
![schematic of software architecture](images/cosim_software_architecture.png)


Copyright © 2019, UChicago Argonne, LLC
