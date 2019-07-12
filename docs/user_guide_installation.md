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
* [Python, version = 2.7.5](https://www.python.org/)
* Power system simulator: [PSS®E, version =  33](https://new.siemens.com/global/en/products/energy/services/transmission-distribution-smart-grid/consulting-and-planning/pss-software/pss-e.html) 
* Distribution system simulator: [OpenDSS, version >= 8.6.1.1](https://sourceforge.net/projects/electricdss/) 
* DER simulator: [**Solar PV-DER simulation utility**](https://github.com/sibyjackgrove/SolarPV-DER-simulation-utility)
* Python packages: SciPy, Numpy, Matlplotlib, Pywin32, XlsxWriter

***
***Note:*** Either demo (limited to 50 buses) or full version of PSS/E can be used.  OpenDSS is an open source software and can be installed for free.

***
***
***Note:*** All Python packages can be installed with *pip* (e.g. *pip install scipy*)

***
***
***Note:*** Python 3.6/3.7 support will be added in the future.

***

