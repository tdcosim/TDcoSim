# D + DER co-simulation

This section provides a brief overview of the D+DER co-simulation. For static co-simulation, TDcoSim uses the DER model (steady state) available in OpenDSS while for dynamic simulation TDcoSim uses the Solar PV-DER simulation utility (dynamic phasor model).

## Assumptions in current software version
**Static simulation:**
1. *To be added*

**Dynamic simulation:**
1. The DER is connected to a distribution system node through a 3 phase transformer (which is automatically created by TDcoSim) .
2. All DER's in a particular distribution feeder share power/voltage ratings, ride through settings, and operate at 100 % insolation for the full duration of the co-simulation.

## D & DER interface for static simulation
The DER is modelled as a negative load or generator injection.

## D & DER interface for dynamic simulation
The distribution system simulation and PV-DER simulation run as separate programs with their own solution methods. TDcoSim is responsible for initializing PV-DER instances, and exchanging data between D & DER, and synchronizing their runs. 

### DER Initialization
The desired number of PV-DER models instances is calculated based on following:
* Solar penetration (specified through **config** file)
* DER rated power (specified through **config** file)
* DER scaling factor (specified through **config** file)
* Total feeder load (calculated by **TDcoSim** from the distribution system model)

The feeders at which the DER instances will be connected is selected randomly and each DER instance is initialized separately.

### Data exchange
At each time-step (half a cycle), the PV-DER model computes the active and reactive power “injection” to the distribution feeder based on the node voltage value obtained from the feeder instance at the start of the time-step.
