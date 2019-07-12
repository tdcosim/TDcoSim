# Getting started with TDcoSim

In this section, we describe how you can get started with using TDcoSim to conduct static or dynamic co-simulation studies for T & D systems with DER penetration and fault events. A list of studies possible with TDcoSim can be found [here](user_guide_introduction.md#studies).

## 1. Setup TDcoSim

1. System requirements can be found  [**here**](user_guide_sys_requirements.md).
2. Installation instructions for can be found [**here**](user_guide_installation.md). 

## 2. Specify power system configuration

1. Specify parameters for the power system to be analyzed:
   
   * Transmission system
        * Transmission system model (e.g. IEEE 118 bus system)
        * Buses where distribution system models are attached
   * Distribution system
        * Distribution system model (e.g. IEEE 123 node feeder)
        * Solar PV penetration as a fraction of the distribution system load
   * DER characteristics (optional)
        * DER voltage and power ratings (e.g. 50 kW, 175 V)
        * DER ride through settings (voltage)
   
2. Specify whether simulation is static or dynamic.

3. Specify length of simulation (e.g. 5 s).

4. Specify transmission bus fault events (optional).

   * Start and end time of fault (for e.g. 0.5 s, 0.667 s)
   * Bus at which fault occurs and fault impedance.

## 3. Transferring the configuration to TDcoSim

The power system configuration defined in previous step can be transferred to TDcoSim using the **config** file (detailed explanations for every entry in the config file is provided [here](user_guide_cosimulation_details.ipynb).) The file formats currently supported are:

* Transmission system model: *.raw, *.dyr
* Distribution system model: *.dss

***
***Note:*** The config file can be edited with Notepad++.

***

## 4.  Starting co-simulation

Once the **config** file has been filled with the required entries and saved, the user can start the co-simulation by running **runtdcosim.py** Python script. To do this open the [command line prompt ](user_guide_visual_guide.md) within the folder containing the **runtdcosim.py** and run following script.

```
python runtdcosim.py > log_file.txt
```

***
***Note:*** rundtdcosim.py is the default name of script that starts the co-simulation. If desired the user can write his own script by following the instructions given [here](user_guide_using_tdcosim.md).

***
***
***Note:*** Logs generated during co-simulation are written to log_file.txt (or any other user specified **.txt file**).

***

## 5.  Accessing the results

Outputs (from both transmission and distribution system) are saved as an MS Excel file (**.xlsx**) at the end of the co-simulation. Additionally a PSS/E channel output file (**.out**) is also created containing all the simulated quantities from PSS/E.
