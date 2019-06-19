**Status:** Expect regular updates and bug fixes.
# Utilitiy to perform Co-Simulation of Transmission and Distribution systems

Description of T&D co-simulation.

![schematic of TDcoSim]()

## Basics
The dynamics of the DER are modelled using dynamic phasors. Detailed description of the concepts behind this utility can be found in the IEEE publication **Dynamic Modeling of Solar PV Systems for Distribution System Stability Analysis** and detailed list of equations can be found in the [Model specification document.](docs/PV_DER_model_specification_rev3.docx)

## Links
* Source code repository: https://github.com/tdcosim/TDcoSim
* API Documentation:

## Installation
You can install the module directly from github with following commands:
```
git clone
cd
pip install -e .
```
## Using the module
The module can be imported as a normal python module:
```
import tdcosim
```
The following features are available currently:
1. Co-simulation with trasmission system defined in PSSE and distribution system defined in OpenDSS.
2. 
### Example: T&D co-simulation with 118 bus IEEE system
The following steps are required:
1. First import the following classes:
```
from from procedure.procedure import Procedure
```

## Module details
A schematic showing the software architecture of the package is shown in the figure below:
![schematic of software architecture](docs/pvder_integration_info_flow.pdf)

Dependencies: SciPy, Numpy, Matlplotlib

## Issues
Please feel free to raise an issue when bugs are encountered or if you are need further documentation.

## Who is responsible?
- Ning Kang kang@anl.gov
- Karthikeyan Balasubramaniam kbalasubramaniam@anl.gov
- Sang-il Yim yim@anl.gov

## Acknowledgement
The authors would like to acknowledge [Shrirang Abhyankar](https://github.com/abhyshr) for his contribution.

## Citation
If you use this code please cite it as:
```

```
### Copyright and License
Copyright © 2019, UChicago Argonne, LLC

Transmission and Distribution System Co-simulation Tool (TDcoSim) is distributed under the terms of [BSD-3 OSS License.](LICENSE.md)
