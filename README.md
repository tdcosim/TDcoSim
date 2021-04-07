**Status:** Expect regular updates and bug fixes.

**Technical support:** support.tdcosim@anl.gov

# Utilitiy to perform Co-Simulation of Transmission, and Distribution systems with DER's

TDcoSim (T & D co-simulation tool) is a Python package that can be used to perform co-simulations containing a transmission system simulator (TSS), multiple distribution system simulator (DSS) instances, and multiple solar PV-DER instances. It is capable of both static and dynamic co-simulations for power systems models containing hundreds of transmission buses, distribution feeder nodes, and DER's.

![schematic of TDcoSim](docs/user_guide/images/software_simple_block_diagram.png)

## Links
* Source code repository: https://github.com/tdcosim/TDcoSim
* User guide: [Markdown](docs/user_guide/user_guide_TOC.md), [PDF](docs/user_guide/TDcoSim_user_guide_version_1_1.pdf), [DOCX](docs/user_guide/TDcoSim_user_guide_version_1_1.docx)
* API Documentation: [API doc](docs/api-html/index.html)

## Installation
You can install the module directly from github with following commands:
```
    git clone https://github.com/tdcosim/TDcoSim.git
    cd
    pip install -e .
```

### Dependencies:
* External software: [PSS®E](https://new.siemens.com/global/en/products/energy/services/transmission-distribution-smart-grid/consulting-and-planning/pss-software/pss-e.html), [OpenDSS](https://sourceforge.net/projects/electricdss/)
* Python packages: [pvder](https://github.com/sibyjackgrove/SolarPV-DER-simulation-utility), SciPy, Numpy, Matlplotlib, PyWin

## Quick start

The [config.json file](config.json) provided in the repository can be used to do a co-simulation after editing in the path names (with any text editor). Then open a command line prompt within the folder containing the **tdcosimapp.py** file (for e.g. by typing Shift+C+M+D) and run the following script to start the co-simulation.

```
python tdcosimapp.py > log_file.txt
```
### Use cases:
Following example use cases are provided:
1. [118 bus T + 123 bus D + DER](docs/user_guide/examples/Example_1_system_state_initialization_test.md)

## Package details
Technical information on the package can be found here:
1. [T&D Co-simulation](docs/user_guide/user_guide_cosimulation_details.md)
2. [Software components](docs/user_guide/user_guide_software_details.md)

## Issues & Support
Please feel free to raise an issue for bugs or feature requests or reach out to support.tdcosim@anl.gov.

## Who is responsible?
**Project PI:**

- Karthikeyan Balasubramaniam kbalasubramaniam@anl.gov (September 2019 to present)

**Core developers:**

- Karthikeyan Balasubramaniam kbalasubramaniam@anl.gov
- Sang-il Yim yim@anl.gov

**Co-developers:**

- Siby Jose Plathottam splathottam@anl.gov

**Previous contributors:**

- Ning Kang ning.kang@inl.gov (January 2018 to August 2019)
- Rojan Bhattarai rbhattarai@anl.gov

## Acknowledgement
We want to acknowledge [Shrirang Abhyankar](https://github.com/abhyshr) for his contributions to the code base development.

We would like to recognize the support of the EPRI technical team led by [Roger Dugan](https://www.linkedin.com/in/roger-dugan-974b2812/) and [Davis Montenegro](https://www.linkedin.com/in/davis-montenegro-martinez-11269345/) and the use of the [EPRI OpenDSS open source software](http://smartgrid.epri.com/SimulationTool.aspx). 

This project is supported by Ali Ghassemian and Dan Ton, [U.S. DOE Office of Electricity, Advanced Grid Research and Development](https://www.energy.gov/oe/mission/advanced-grid-research-and-development).

## Citation
If you use this code please cite it as:
```
@misc{TDcoSim,
  title = {Transmission and Distribution System Co-simulation Tool}: A co-simulation utility},
  author = "{Karthikeyan Balasubramaniam, Sang-il Yim, Ning Kang}",
  howpublished = {\url{https://github.com/tdcosim/TDcoSim}},
  url = "https://github.com/tdcosim/TDcoSim",
  year = 2019,
  note = "[Online; accessed 23-August-2019]"
}
```
### Copyright and License
Copyright © 2019, UChicago Argonne, LLC

Transmission and Distribution System Co-simulation Tool (TDcoSim) is distributed under the terms of [BSD-3 OSS License.](LICENSE.md)
