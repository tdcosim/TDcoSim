# Release 2.0.0
## Highlights
* Major changes to JSON configuration file.
* Support for dynamic current injection models (**fast_der**) and high performance ODE solvers.
* Support for **DER_A** model in PSS/E
* Interactive dashboard for analytics  and additional methods for data analytics
* Performance improvements
* Release on PyPI

## Major Features and Improvements
* Performance has been improved for post-processing and saving of data at the end of co-simulation.
* Dynamic current injection models have been added. These models reduce solution time by 10X to 100X when compared to the detailed DER models. These can be used by specifying `fast_der` in the `DEROdeSolver` field of the config file. 
* Option to use high performance ODE solvers available in [DifferentialEquations.jl](https://github.com/SciML/DifferentialEquations.jl) has been added for detailed DER models. These solvers reduce time by almost 2 to 10X when compared to the **SciPy** ODE solvers for a given PV penetration level. These can be selected by selecting `diffeqpy` in the `DEROdeSolver` field.
* Module `dashboard` for visualizing co-simulation data using an browser based interactive dashboard was created. The module can be launched through **app.py**.
* Option to replace T side load with complex load models. This can be used by specifying `cmld` in the the `defaultLoadType`.
* Option to log detailed error messages at feeder level. This can be enabled by setting `saveSubprocessOutErr` field to True.
* Added **tdcosimapp.py** to generate configuration files using a template.
* Added additional configurations in the examples folder: `config_fast_der.json`, `config_fast_der_118bus_full_td.json`, `config_fast_der_68bus_full_td.json`
* Added additional analysis methods in the `DataAnalytics` module: `compute_stability_time`, ` lag_finder`, `instances_of_violation`
* Added additional plotting methods in the `DataAnalytics` module: `plot_omega`,  `plot_t_vmag`, `plot_t_delayed_voltage_recovery`
* Support for additional detailed DER model types: `SolarPVDERThreePhaseNumba`, `SolarPVDERSinglePhaseConstantVdc`.
## Behavioral and Breaking Changes
* Default configuration will now correctly configure all the buses which were not specified through `manualFeederConfig` using  the configuration provided through  `defaultFeederConfig`.
* Feeders won't be connected to T nodes which are not load buses.
* The folder to store the results needs to be specified through the `output` and `simID` field in the configuration file.
## Bug Fixes
* Fixed numerous bugs related to performance and logging.
## backward-incompatible Changes
* Not compatible with **pvder 0.5.0.** and below.
* Not compatible with configuration used in V1.2.0

## Thanks to our Contributors


# Release 1.2.0
## Highlights
* Supported PSSE35
* Added DER models, compatible with **pvder 0.3.0.**
* Extended the maximum network size and simulation time

## Major Features and Improvements
* Supported PSSE35 with new configuration option:
```json
"psseConfig": {"installLocation": "C:\\Program Files\\PTI\\PSSE35\\35.0\\PSSPY27"}
```
* Support for following DER model types has been added: ```SolarPVDERThreePhase```, ```SolarPVDERThreePhaseBalanced```,  and ```SolarPVDERThreePhaseConstantVdc``` which can be selected through the [DER configuration file](\examples\config_der.json) as shown below:
```json
"basic_specs":{"model_type":"SolarPVDERThreePhase"}
```
* Support for fully customizing the DER model parameters through the [DER configuration file](\examples\config_der.json) as shown below:
```json
"basic_options":{"Sinsol":100.0},
"module_parameters":{"Np":11,"Ns":735,"Vdcmpp0":550.0,"Vdcmpp_min": 525.0,"Vdcmpp_max": 650.0},
"inverter_ratings":{"Srated":50e3,"Vdcrated":550.0,"Ioverload":1.3,"Vrmsrated":177.0},
"circuit_parameters":{"Rf_actual":0.002,"Lf_actual":25.0e-6,
                            "C_actual":300.0e-6,"R1_actual":0.0019,"X1_actual":0.0561},
"controller_gains":{"Kp_GCC":6000.0,"Ki_GCC":2000.0,
                          "Kp_DC":-2.0,"Ki_DC":-10.0,
                          "Kp_Q":0.2,"Ki_Q":10.0,"wp": 20e4}
```

## Behavioral changes
* Extended the memory limit to simulate a large scale network and operation time:
To avoid the **out of memory error**, TDcoSim generates reports according to the memory threshold.
The memory threshold is automatically calculated during the simulation by the input network and system memory size.

## Breaking Changes
Following breaking changes were introduced in the config file:

* Replaced keywords: n_phases in **basic_specs** in DER setting with **model_type**:
```json
"basic_specs":{n_phases":3}
```
to
```json
"basic_specs":{"model_type":"SolarPVDERThreePhase"}
```
## Bug Fixes and Other Changes
* Added **psutil** as an additional dependency
* Fixed unit test to compatible with the DER and PSSE updates
## backward-incompatible Changes
* Not compatible with **pvder 0.2.0.**

## Thanks to our Contributors
This release contains contributions from Karthikeyan Balasubramaniam @karthikbalasu, Sang-il Yim @yim0331, and Siby Jose Plathottam @sibyjackgrove at Argonne National Laboratory.
We thank suggestions from Ning Kang (INL) and Rojan Bhattarai (INL)

# Release 1.1.0
## Highlights
* Increased user flexibility w.r.t. DER placement, and voltage ride through.
* Compatible with **pvder 0.2.0.**
## Major Features and Improvements
* Ride through refactoring based on configurable thresholds: 
```json
"LVRT":{"0":{"V_threshold":0.5,"t_threshold":1.0,"mode":"momentary_cessation"}}
```
* Configuring unique DERs at each node using ```PVPlacement```:
```json
"PVPlacement":{"50":{"derId":"50","powerRating":50,"pvderScale":1}}
```
* Exposure of DER settings through ```derId``` and [DER configuration file](\examples\config_der.json):
```json
"50":{"circuit_parameters":{"Rf_actual":0.002,"Lf_actual":25.0e-6, "C_actual":300.0e-6}}
```
## Behavioral changes
* Ride through: There are two modes for each threshold.
  **momentary_cessation**: Power output reduced to zero temporarily
  **mandatory_operation**: Try to maintain rated power output

  In all the modes, once the ```t_threshold``` times are breached, the DER is tripped (i.e. power output reduced to zero permanently). The config will be expected to work with any number of elements (>0) in the ```LVRT``` and ```HVRT``` dictionaries.

*  If ```initializeWithActual``` is  *True*, ```PNominal``` and ```QNominal``` at each feeder node will be initialized with the actual power output from DER at 100 % insolation. If *False*, they will be initialized with rated apparent power output of DER.

## Breaking Changes
Following breaking changes were introduced in the config file:

* Replaced keywords: *power_rating* replaced with ***powerRating***, *voltage_rating* replaced with ***VrmsRating*** replaced with, *SteadyState* replaced with ***steadyStateInitialization***
* Removed keywords: *V_LV0/1/2*,*t_LV0/1/2/_limit*,*V_HV1/2*,*t_HV1/2_limit*,*VRT_INSTANTANEOUS_TRIP*,*VRT_MOMENTARY_CESSATION*,
## Bug Fixes and Other Changes
* Fixed the handlers not found warning from logger when DER instances are created. 
## Backwards-Incompatible Changes
* Not compatible with ***pvder 0.1.0***.

## Thanks to our Contributors
This release contains contributions from Karthikeyan Balasubramaniam @karthikbalasu, Sang-iL Yim @yim0331, and Siby Jose Plathottam @sibyjackgrove at Argonne National Laboratory.
We thank suggestions from Ning Kang (INL) Rojan Bhattarai (INL), and Deepak Ramasubramanian (EPRI)).

# Release 1.0.0
Initial release of TDcoSim.
