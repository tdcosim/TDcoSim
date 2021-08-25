# Installation
TDcoSim can be installed from GitHub through command line as shown below.

    git clone https://github.com/tdcosim/TDcoSim.git
    cd tdcosim/
    pip install -e .

***
***Note:*** [Git](https://git-scm.com/) needs to installed  (incase it is not already available) before TDcoSim can be installed.

***

## Dependencies:
The packages listed below must be installed separately:

### Required

* [Python](https://www.python.org/) version = 2.7.5 for PSS®E, version =  33.3.0, version >= 3.5 for PSS®E, version =  35.0.0
* Power system simulator: [PSS®E, version =  33.3.0 or PSS®E, version =  35.0.0](https://new.siemens.com/global/en/products/energy/services/transmission-distribution-smart-grid/consulting-and-planning/pss-software/pss-e.html)
* Distribution system simulator: [OpenDSS, version >= 8.6.1.1](https://sourceforge.net/projects/electricdss/) 
* DER simulator: [**Solar PV-DER simulation utility**](https://github.com/sibyjackgrove/SolarPV-DER-simulation-utility)
* Python packages: SciPy, Numpy, Matlplotlib, Pywin32, XlsxWriter, Psutil

***
***Note:*** Either demo (limited to 50 buses) or full version of PSS/E can be used.  OpenDSS is an open source software and can be installed for free.
***
***
***Note:*** PSS/E 35.0.0  and above support will support both 32 and 64 bit versions of Python.
***

### Optional

* TDcoSim dashboard: Dash, Plotly

* High performance ODE solver *diffeqpy*: [diffeqpy, version >= 1.1.0](https://github.com/SciML/diffeqpy)
  * Download and install Julia interpreter: [Julia, version >= 1.5](https://julialang.org/downloads/)
  * Add Julia to system PATH environment variables as shown [here](https://julialang.org/downloads/platform/) (Only for Windows OS).
  * CD into thee TDcoSim respository and run the following script from command line:
       ```python
       python install diffeqpy
       ```

***
***Note:*** If co-simulations involving more than 10 pvder models are to be run, it is recommended to select *diffeqpy* as the ODE solver.

***
***
***Note:*** All Python packages can be installed with *pip* (e.g. *pip install scipy*)

***

