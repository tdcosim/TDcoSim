# Introduction

The TDcoSim tool can be used to perform static and dynamic co-simulation of transmission and distribution networks with distributed energy resources (PV-DER's). The following figure illustrates the various components that can simulated using the TDcoSim tool. Note that transmission and distribution network are simulated in PSS/E, and OpenDSS respectively while PV-DER's are simulated using [Solar PV-DER simulation-utility.](https://github.com/sibyjackgrove/SolarPV-DER-simulation-utility)

![14-bus transmission, 13-bus distribution network, and Solar PVDER](images/simulation_objects.png)

<p align="center">
  <strong>Fig. 1.</strong>Components that can be simulated using TDcoSim.
</p>

This guide is intended to introduce the user to the basic functionalities of the TDcoSim tool and allow them to get started with using the tool within a short amount of time. Multiple case studies, have also been included which can be used by the user as a starting point.

TDcoSim can be installed and used as a normal Python module. Detailed installation instructions for can be found [**here**](user_guide_installation.md). 

## Intended use cases

TDcoSim is intended to be a generic co-simulation platform like HELIC's. It is specifically meant to be used as a tool for studying static and dynamic impact of distributed energy resources on the transmission system. A few of the intended use cases are specified below:

* Static studies
  1. Analyze generator dispatch with DER over 24 hours.
  2. Analyze voltage profile.

* Dynamic studies
  1. Study impact of DER's tripping during transmission system faults.
  2. Study impact of DER's riding through during transmission system faults.
  3. Study impact of cloud cover event on transmission system.

## Solution time

The solution time for a T+D+DER co-simulation primarily depends on the number of OpenDSS instances and PV-DER instances. The solution times 10 %, and 25 % penetration for various power system configurations are given in Table I and Table II respectively. The configuration of the work station used to run the co-simulation is provide in the appendix.

<p align="center">
  <strong>Table I.</strong> Solution times for 10 % penetration.
</p>

| Transmission system buses|Distribution system nodes|PV-DER rating|Solution time|
|----------|:-------------:|:------:|:------:|
| 14 |13| 50 | |
| 118|123|50 | |
| 118|8500|50 | |

<p align="center">
  <strong>Table II.</strong> Solution times for 25 % penetration.
</p>

| Transmission system buses|Distribution system nodes|PV-DER rating|Solution time|
|----------|:-------------:|:------:|:------:|
| 14 |13| 50 ||
| 118|123|50 ||
| 118|8500|50 ||

[Continue to What is T&D cosimulation?](user_guide_cosimulation_details.ipynb) 