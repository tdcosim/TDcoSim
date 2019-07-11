# Using TDcoSim in Python scripts
### Importing TDcoSim
The TDcoSim module can be imported and used like a normal Python module. Note that package name is in lower case.

 ```python
   import tdcosim
 ```

### Quick start a simulation using the default config file

To start the simulation with the default config file, open a [command line prompt ](user_guide_visual_guide.md) within the CoSimulator folder in TDcoSim repository and run the **runtdcosim.py** file. 

### Using TDcoSim within your script
The basic steps to write your own co-simulation program are as follows:

1. Setup desired T+D or T+D+DER system by making necessary entries in the [**config**](docs/chapter_2_understanding_config_file.md) file.

2. Import necessary classes.

   ```python
      from report import generateReport
      from global_data import GlobalData
      from procedure.procedure import Procedure
   ```

3. Read the **config** file and initialize the T&D system.

   ```python
       GlobalData.set_config('config.json')
       GlobalData.set_TDdata()
   ```

4. Create a procedure object for the simulation and call *simuate()* method.

   ```python
       procedure = Procedure()
       procedure.simulate()
   ```

5. Generate report after *simuate()* exits.

   ```python
       generateReport(tdcosim.GlobalData,fname='report.xlsx')
   ```

[Continue to Software details](user_guide_software_details.md)