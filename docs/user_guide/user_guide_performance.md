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

The following benchmark times were obtained for various test co-simulation (7s).

| DER Model type               | DER solver type      | Feeders with DER | PV penetration | Solution time/DER/Simulation  time (s/DER/s) |
| ---------------------------- | -------------------- | ---------------- | -------------- | -------------------------------------------- |
| ThreePhaseBalanced - 50 kW   | DiffEqPy (CVODE_BDF) | 97               | 40 %           | 0.06                                         |
| ThreePhaseUnBalanced - 50 kW | DiffEqPy (CVODE_BDF) | 97               | 40             | 0.07                                         |
| Fast DER - 100 kW            | Forward Euler        | 97               | 40             | 0.04                                         |
|                              |                      |                  |                |                                              |

