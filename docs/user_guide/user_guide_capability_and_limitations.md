# Capability and Limitations

**TDcoSim** uses PSS®E as transmission system simulator and OpenDSS as Distribution system simulator. In general, **TDcoSim** can be used for analysis that is supported by PSS®E and OpenDSS. On the other end of the spectrum **TDcoSim** is limited by the limitations of PSS®E and OpenDSS. PSS®E is a positive sequence simulator, as a result, studies that involve unbalanced faults on the transmission side cannot be studied in detail.

## Types of Analysis

* Quasi-static time series (QSTS)
   * Solves power flow for both transmission and distribution system
   * Uses a tightly-coupled scheme to interface T&D systems
   * Use of tightly-coupled scheme ensures that the obtained boundary solutions are stable. In other words the solution will be the same (within a user defined tolerance) if one were to solve both the T&D system together as a single large system.
   * Load shapes can be provided in the configuration file to model the change in load over time. It is assumed that all the loads in a given distribution feeder follow the same load shape.

* Dynamic simulation
   * Unlike the QSTS, which solves a set of algebraic equations on both the T and the D side, the dynamic simulation solves differential algebraic equations (DAEs) on the T-side and D-side
   * OpenDSS solves power flow for the distribution system
   * When distributed solar generation is modeled, the dynamic model of [PVDER](https://github.com/sibyjackgrove/SolarPV-DER-simulation-utility) is used. Thus, the combination of OpenDSS and PVDER makes the D-side equations DAEs.
   * Depending on the configuration multiple pvder instances will be used
   * Balanced faults on the transmission side can be modeled
   * Cloud cover event -- particularly relevant for system studies involving large solar farms
   * Uses a loosely-coupled

## Assumptions on Reduction in System Inertia

**TDcoSim** was specifically designed to study distributed energy resource (DER) integration. Hence, it is designed to support two different viewpoints,
* The user can defined the system in detail using existing study models, or
* The user can setup future scenarios with varying levels of solar penetration

**TDcoSim** makes certain assumptions in the latter case. As an example, let us say the user wants to study 10 and 20 percent solar penetration scenarios. In both the cases, the user will provide the same T and D systems. This means certain amount of conventional generation from the transmission system needs to be reduced in order to accommodate the increased solar generation. The realistic way to accomplish this would be to find out the units committed for the given scenario, run an optimal power flow to find the generator set points, then start the simulation at that operating point. However, the data required to do that is not typically available and/or not provided by the user. **TDcoSim** overcomes this problem by making the following assumptions,

* Reduce generation of each unit by solar penetration value. For example, if solar penetration is 10 percent then reduce each generator output by 10 percent.
* Reduce the inertia constant of each generator the same way

\pagebreak