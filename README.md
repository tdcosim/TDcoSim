**Status:** Expect regular updates and bug fixes.

**Technical support:** support.tdcosim@anl.gov

# Utilitiy to perform Co-Simulation of Transmission, and Distribution systems with DER's

TDcoSim (T & D co-simulation tool) is a Python package that can be used to perform co-simulations containing a transmission system simulator (TSS), multiple distribution system simulator (DSS) instances, and multiple solar PV-DER instances. 

For a more detailed introduction of TDcosim, please refer to [introduction flyer](docs/user_guide/TDcoSim_Flyer.pdf) and [introduction video](https://www.youtube.com/watch?v=6twEspWzTZw&t=53s).

The key features include:
* Transmission system modeling using PSS®E
* Distribution system modeling using OpenDSS
* Detailed dynamic DER modeling using PVDER
* Support for static and dynamic simulation
* Built-in data visualization and data analytics tools
* Capable of simulating large interconnections (250K+  T&D nodes).

![schematic of TDcoSim](docs/user_guide/images/software_simple_block_diagram.png)

It is capable of both static and dynamic co-simulations for power systems models containing hundreds of transmission buses, distribution feeder nodes, and DERs.

The example cases include:
* Study impact of aggregated DER model parameters
* Study impact of DER penetration on T&D systems
* Post-contingency analysis of faults involving DER
* Study impact of DER interconnection standards

***
***Note:*** Energy storage based studies are currently possible for both QSTS and dynamics. 
However, dynamics T+D case has a caveat. In PSSE, the DER_A model can be used to model both generator type DERs and energy storage, the only difference in setup being a single flag to switch between the two. 
Since we are doing transient stability studies, it is not essential to model the energy storage SOC. Similar to what DER_A model does, the same approach can be used for T+D but it should be noted that we have not developed a separate energy storage model.
***

## Links
* Source Code Repository: https://github.com/tdcosim/TDcoSim
* User Guide: [Markdown](docs/user_guide/user_guide_TOC.md), [PDF](docs/user_guide/TDcoSim_user_guide_version_2_0.pdf), [DOCX](docs/user_guide/TDcoSim_user_guide_version_2_0.docx)
* API Documentation: [API doc](docs/api-html/index.html)
* Introduction Flyer: [Flyer PDF](docs/user_guide/TDcoSim_Flyer.pdf)
* Introduction Video: [Youtube Link](https://www.youtube.com/watch?v=6twEspWzTZw&t=53s)

## Installation
You can install tdcosim by running the following command on command line.

    pip install git+https://github.com/tdcosim/TDcoSim.git@master


In the event you do not have git installed on your machine, you can alternatively run the following from command line.

    pip install https://github.com/tdcosim/TDcoSim/archive/master.zip

After installation open a new command prompt and run the following to set psse path,

    tdcosim setconfig -p "path\to\psse_installation"  

If PSSE 35 is being used the following may be used:

```
tdcosim setconfig -p "C:\Program Files\PTI\PSSE35\35.0\PSSPY37" 
```
If PSSE 33 is being used the following may be used:

```
tdcosim setconfig -p "C:\Program Files (x86)\PTI\PSSE33\PSSBIN" 
```

Due to the embeded compatibility requirements between PSSE and Python, please refer to the following compatibility table when paring PSSE with Python.

![Compatibility Table PSSE-Python](docs/user_guide/images/Compatibility_table_PSSE_Python.png)

### Dependencies:
* External software: [PSS®E](https://new.siemens.com/global/en/products/energy/services/transmission-distribution-smart-grid/consulting-and-planning/pss-software/pss-e.html), [OpenDSS](https://sourceforge.net/projects/electricdss/)
* Python packages: [pvder](https://github.com/sibyjackgrove/SolarPV-DER-simulation-utility), SciPy, Numpy, Matlplotlib, PyWin

## Quick start

The [config.json file](config.json) provided in the [examples folder](https://github.com/tdcosim/TDcoSim/tree/v2_test/examples) can be used to do a co-simulation after editing the path names (with any text editor). Then open a command line prompt and use the following  commands to to run a co-simulation. Note that *config_td.json* could be replaced by the name of any other configuration file.

```
   tdcosim run -c ".\examples\config_td.json"
```
To visualize the co-simulation results using the dashboard, please refer to [visualization and analytics section](docs/user_guide/user_guide_visualization_analytics.md)

Detailed documentation on running a co-simulation may be found within the [user guide](https://github.com/tdcosim/TDcoSim/blob/v2_test/docs/user_guide/user_guide_getting_started.md). Additional examples are available [here](https://github.com/tdcosim/TDcoSim/tree/v2_test/docs/user_guide/examples).

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
