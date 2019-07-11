# Getting started with TDcoSim

In this section, we go through how you can get started within using TDcoSim to perform co-simulation.

## 1. Setup TDcoSim

1. System requirements can be found  [**here**](user_guide_sys_requirements.md).
2. Installation instructions for can be found [**here**](user_guide_installation.md). 

## 2. Define desired power system configuration

1. Define parameters for the power system to be analyzed:
   
   * Transmission system
        * Transmission system model (e.g. IEEE 118 bus system)
        * Buses where distribution system models are attached
   * Distribution system
        * Distribution system model (for e.g. IEEE 123 node feeder)
        * Solar PV penetration as a fraction of the distribution system load.
   * DER configuration (optional)
        * DER voltage and power ratings (for e.g. 50 kW, 175 V)
        * DER ride through settings
   
2. Define whether simulation is static or dynamic.

3. Define length of simulation (for e.g. 5 s).

4. Define transmission bus fault events (optional).

   * Start and end time of fault (for e.g. 0.5 s, 0.667 s)
   * Bus at which fault occurs and fault impedance.

## 3. Transferring the configuration to TDcoSim

The power system configuration defined in previous step can be transferred to TDcoSim using the **config** file (detailed explanations for every entry in the config file is provided [here](user_guide_cosimulation_details.ipynb).) The file formats currently supported are:

* Transmission system model: *.raw, *.dyr
* Distribution system model: *.dss

## 4.  Starting co-simulation

Once the **config** file has been defined, the user can start the co-simulation by running **runtdcosim.py** Python script . To do this open a [command line prompt ](user_guide_visual_guide.md) within the folder containing the **runtdcosim.py** and run the following script.

```
python runtdcosim.py > log_file.txt
```

***
***Note:*** rundtdcosim.py is the default name of script that starts the co-simulation. If desired the user can write his own script by following the instructions given [here](user_guide_using_tdcosim.md).

***
***
***Note:*** Logs generated during co-simulation are written to log_file.txt (or any other user specified **.txt file**).

***


## 4.  Results

Outputs the co-simulation are saved as **.xls** file at the end of the co-simulation.

[Continue to Installation](user_guide_installation.md) 