# Performance Guide

TDcoSim has the capability to scale from a single distribution feeder with a single DER to thousands of distribution feeders with a hundreds of DER. Due to difference in computing effort and memory footprint, the solution time increases.

In this guide we provide suggestions on reducing solution time for a given co-simulation project.

## Solution time
The total solution time is comprised of three parts:
***Tsolution = Tinitialize + Tco-sim + Tpost-process***
Where, *Tinitialize* is the time take to setup the co-simulation, *Tco-sim* is the time taken for co-simulation time stepping, and *Tpost-process* is the time take for post-processing the simulation time. Not that each solution time component is comprised of multiple tasks.

* Tinitialize: Here individual components co-simulation is initialized. 
	* Read  JSON configuration files
	* Launch sub-processes
	* Setup DER model integrators (for dynamic simulation)
	* Initialize co-simulation to steady state
* Tco-sim: Here we do time stepping for individual component.
    * PSS/E model:
       * Solve power flow for transmission system model.
       * Perform integration for dynamic models with a time step of one half-cycle (1/120 s).
       * Write to *.out* file
    * OpenDSS model: Solve non-linear algebraic problem
    * PV-DER model:
        * Fast-DER: Perform integration with a fixed time step.
        * Dynamic Phasor: Perform integration with variable time step
    * Write to disk if memory threshold is exceeded.
* Tpost-process: Here we post process the output and write them to user defined file type from memory.

### Solution time contributors
The solution time may also be expressed as a function of the specific T&D+DER co-simulation model.
**Tsolution = f(nBus) + f(nFeeder) + nDERFeeder*f(nDERperFeeder)**

## Solution time benchmarks on test systems 

The following benchmark times were obtained for the following scenario using workstation with the recommended specifications mentioned in [System requirements](user_guide_sys_requirements.md):

T system: IEEE 118 bus system

D feeder: IEEE 123 node feeder

Simulation time: 20.0 s

Events: Three phase fault from 0.2 s to 0.3 s

Number of T nodes with feeders and DER: 97 

| DER Model type               | DER solver type      | PV penetration (%) | DER models | Solution time/Simulation  time/DER (s/s/DER) |
| ---------------------------- | -------------------- | ------------------ | ---------- | -------------------------------------------- |
| ThreePhaseBalanced - 50 kW   | DiffEqPy (CVODE_BDF) | 25                 | 1746       | 0.047                                        |
| ThreePhaseUnBalanced - 50 kW | DiffEqPy (CVODE_BDF) | 25                 | 1746       | 0.054                                        |
| Fast DER - 50kW              | Forward Euler        | 25                 | 1746       | **0.038**                                    |

