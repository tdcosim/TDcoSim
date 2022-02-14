# Introduction

Argonne’s transmission and distribution systems  co-simulation tool (**TDcoSim**) is a tool to conduct studies that capture short- and long-term interactions between transmission and distribution systems with and without distributed energy resources (DER). It is capable of performing steady-state and dynamic simulations, as well as perfuming analytics on the results from the simulation . Consideration of inverter-based DER dynamics along with its protection and controls are among the most salient features of this tool.  Additionally, the tool is capable of efficiently simulating tens of thousands of individual DER models. **TDcoSim** is designed to be used in offline planning, operational, and control studies. Transmission system entities can use the tool to study high-penetration DER scenarios, which will assist in ensuring secure, reliable, and economic grid planning and operations.

This manual intends to introduce users to **TDcoSim**, provide a step-by-step guide to its installation and use, and offer examples of its capabilities as a tool for conducting studies. A list of case studies possible with **TDcoSim** can be found [here](#types-of-studies) and a brochure with FAQ related to the project goals can found [here](https://www.wecc.org/Administrative/ANL-TD%20co-simulation%20tool%20informational%20brochure.pdf). 

## What is TDcoSim?

**TDcoSim** is a software tool that can be used to perform static and dynamic co-simulation of transmission and distribution networks as well as DER. Currently, the tool has incorporated dynamic photovoltaic (PV) systems (referred to as PV-DER) for its dynamic simulation capabilities. Dynamic models of other inverter-based distributed generations (DG) (e.g. battery energy storage systems (BESS), wind turbines (WT)) will be included in future versions. Interested users can also integrate their own dynamic DER models into the tool. 

Fig. 1. below illustrates the various components that currently can be simulated using **TDcoSim**. It features a representative IEEE 14-bus transmission system, IEEE 13-bus distribution systems, and solar PV-DERs. Please note that [Solar PV-DER simulation-utility](https://github.com/sibyjackgrove/SolarPV-DER-simulation-utility) is used to simulate PV-DER's in dynamic T&D co-simulations. Default OpenDSS standard generator models for PV or other DER are used in steady-state T&D co-simulations.


![14-bus transmission, 13-bus distribution network, and Solar PVDER](images/simulation_objects.png)

<p align="center">
  <strong>Fig. 1. </strong>Components that can be simulated using TDcoSim.
</p>

Note that **TDcoSim** can also simulate advanced models like DER_A, composite load model (CMLD), and complex load mode (CLOD) that available in PSS/E.

## How can I use it?

**TDcoSim** is available as an open source Python package and can be installed at no cost from its [GitHub repository](https://github.com/tdcosim/TDcoSim) . Additionally, the user needs to separately install  [PSS®E](https://new.siemens.com/global/en/products/energy/services/transmission-distribution-smart-grid/consulting-and-planning/pss-software/pss-e.html) for simulating a transmission network, [OpenDSS](https://sourceforge.net/projects/electricdss/) for simulating distribution networks. 

Detailed installation instructions and links to the requisite supporting software can be found [here](user_guide_installation.md#installation).

## What are the inputs?

In order to run a co-simulation using **TDcoSim**, the user needs to provide the following inputs:

* A Transmission system model in a format compatible with PSS/E (required)
* Distribution system models in a format compatible with OpenDSS (required)
* Simulation type - steady-state or dynamic (required)
* DER penetration levels (required for dynamic co-simulation)
* DER ratings and ride through settings (optional)
* Simulation events (optional)
* Presence of ZIP, Composite load model (CMLD), Complex load model (CLOD),
* Presence of aggregate DER model (DER_A) (only available in PSS/E 35)

Detailed description of each input can be found [here](user_guide_getting_started.md).

## What are the outputs?

**TDcoSim** provides following outputs from each component of the T&D co-simulation:

* Transmission bus: voltage, frequency, load active and reactive power consumption (if a bus is connected with a load), generator active and reactive power output (if a bus is connected with a generator).
* Distribution feeder node: voltage, active and reactive load, DER active and reactive power output (if a bus is connected with a DER).

Please note that the output comes in an interval of half-a-cycle for dynamic simulations. For steady-state simulations, the output comes at an interval corresponding to the time step of users’ choice, which can range from seconds, minutes, hours, to years. 

The output format include Excel spreadsheet and more can be found in the dashboard visualization example.

## Types of studies

**TDcoSim** is intended to be used as a tool for studying static and dynamic impacts of distributed energy resources on the transmission system. Studies that can be conducted with the current version of the software are listed below:

* Steady-state studies

  1. Impact of DER on bulk power system load following or ramping requirements throughout the day and over the course of the seasons.
  2. Analyze voltage profile of both T-system and D-system with varying levels of DER penetrations.
  3. Impact of different DER penetration levels on the voltage stability of BES via continuations power flow analysis.
  
* Dynamic studies

  1. Impact of DER’s tripping/ride-through settings on bulk power system stability (both frequency and voltage) during and post transmission system faults.
  2. Parameterization and performance verification of DER_A and composite load model. 
  3. Impact of DER on the small-signal stability of bulk power system

***
***Note:*** Examples of dynamic studies performed with TDcoSim are included in the **Examples** section.

***

## Future development

The studies that can be conducted in the next version of the software are listed below:

* Dynamic studies

  1. Impact of cloud cover events on conventional synchronous generators and operations of bulk power system.
  2. Impact of DER dynamic reactive power support on bulk power system stability (both frequency and voltage) during and post transmission system faults.  
  3. Impact of line outages on bulk power system operations and stability under high-DER-penetration scenarios.
  4. Impact of generator and/or load outages on system frequency under high DER penetration.
  5. Impact of sudden load increase/decrease on the stability of bulk power system.

* Protection studies

  1. Analyze impact of high DER penetration on coordination among distribution-system protection devices and DER protection relays, and other protection schemes such as under voltage load shedding (UVLS) and under frequency load shedding (UFLS) schemes.
  2. Determine (a) appropriate DER frequency and voltage ride-through settings; and (b) distribution system protection devices settings. These settings will help ensure bulk system reliability and also satisfy distribution-system safety requirements (e.g. prevention of unintentional islanding).
  3. Short-circuit analysis.

* T&D operations coordination studies

  1. Aggregation of DER is an effective approach to integrate DER as a dispatchable resource into the planning and operation of distribution and transmission systems. DERMS has emerged as an effective tool sitting between the transmission and distribution operators to manage the aggregation of DERs at the substation and feeder level.
  2. TDcoSim, in conjunction with DERMS, can be used to manage DERs to provide T&D coordinated congestion management, system balancing, frequency and voltage control, and flexibility. 

The following figure illustrates how **TDcoSim** can assist in T&D planning and operations coordination for future high-DER-penetration grid.

![T & D planning and operations](images/TD_planning_operations.png)

Following capabilities are planned in be added in the future:

* Capability to include other types of DERs such as energy battery storage system.
* Capability to introduce insolation change events.
* Capability to simulate generator tripping, line outages, load increase/decrease.
* Capability to consider distribution system Under Frequency Load Shedding (UFLS) and Under Voltage Load Shedding (UVLS) schemes. 

## Scalability and solution time

The scale of the T & D system (including PV-DERs) to be co-simulated is limited only by the available memory (RAM) in the workstation where **TDcoSim** is installed. The solution time for the dynamic co-simulation depends on the number of distribution feeder instances, the number and type of DER instances, the type of ODE solver being used, and on the number of logical cores available in the workstation.

[Continue to Getting Started](user_guide_getting_started.md)

\pagebreak