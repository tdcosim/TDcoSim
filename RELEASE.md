# Release 2.0.0
## Highlights
* Major changes to JSON configuration file and full access to TDcoSim features using the **tdcosim** command.
* Support for dynamic current injection models (**fast_der**) on the D side and **DER_A** model on T side.
* Performance improvements and option to use high performance ODE solvers.
* Interactive dashboard for visualizing results and additional methods for data analytics
* Release on PyPI and updated user guide.

## Major Features and Improvements
* Performance has been improved for post-processing and saving of data at the end of co-simulation.

* Dynamic current injection models have been added. These models reduce solution time by 10X to 100X when compared to the detailed DER models. These can be used by specifying `fast_der` in the `DEROdeSolver` field of the config file. 

* Option to use high performance ODE solvers available in [DifferentialEquations.jl](https://github.com/SciML/DifferentialEquations.jl) has been added for detailed DER models. These solvers reduce time by almost 2 to 10X when compared to the **SciPy** ODE solvers for a given PV penetration level. These can be selected by selecting `diffeqpy` in the `DEROdeSolver` field.

* All TDcoSim features can be accessed through the **tdcosim** *feature* command on command line.

* Example **JSON** configuration files for static or dynamic co-simulation may be generated using the `template` feature.

* Co-simulation may be started using the `run` feature

* Co-simulation results may be visualized using a browser based interactive dashboard through the `dashboard` feature.

* `defaultLoadType` field has been added to `simulationConfig` to replace the T side load. The available options are **ZIP** load (**zip**) and composite load models (**cmld**).

* `cmldParameters` has been added to `psseConfig` to specify properties of composite load models.

  `simID`, `outputDir`, and `scenarioID` fields have been added to `outputConfig`.

* A `logs` field has been added to the config file. Logs generated during co-simulation will be stored in [/tdcosim/logs/](https://github.com/tdcosim/TDcoSim/tree/master/tdcosim/logs). Log level can be set using `level` (10, 20, 30, or 40). Error messages at feeder level can be enabled  by setting `saveSubprocessOutErr` to True.

* `excludenode` filed has been added to `defaultFeederConfig`. It is used to specify the list of T side nodes that will be excluded from being connected with a distribution feeder model.

* Added additional analysis methods in the `DataAnalytics` module: `compute_stability_time`, ` lag_finder`, `instances_of_violation`

* Added additional plotting methods in the `DataAnalytics` module: `plot_omega`,  `plot_t_vmag`, `plot_t_delayed_voltage_recovery`

* Support for additional detailed DER model types: `SolarPVDERThreePhaseNumba`, `SolarPVDERSinglePhaseConstantVdc`.
## Behavioral and Breaking Changes
* **run_time_domain.py** and **run_qsts.py** are no longer supported for running co-simulation and were removed. The functionality has been replaced with `tdcosim run -c "config.json"`from command line.
* The **examples** folder in root was relocated to [/tdcosim/examples](https://github.com/tdcosim/TDcoSim/tree/master/tdcosim/examples).  Older examples were removed and new examples were added.
* The **SampleData** folder in root was relocated to [/tdcosim/data](https://github.com/tdcosim/TDcoSim/tree/master/tdcosim/data).  
* The **output** folder in root was removed.  
* The **der_config.json** was moved to [/tdcosim/config/detailed_der_default.json](https://github.com/tdcosim/TDcoSim/blob/master/tdcosim/config/detailed_der_default.json)
* Default configuration will now correctly configure all the buses which were not specified through `manualFeederConfig` using  the configuration provided through  `defaultFeederConfig`.
* If the T side node is not a load bus, distribution feeders won't be connected to it and an error will be produced.
* The folder to store the results needs to be specified through the `output` and `simID` field in the configuration file.
## Bug Fixes
* Fixed numerous bugs related to performance and logging.
## backward-incompatible Changes
* Not compatible with **pvder 0.5.0.** and below.
* Not compatible with configuration files used in V1.2.0

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
