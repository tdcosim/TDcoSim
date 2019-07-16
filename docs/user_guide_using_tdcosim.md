# TDcoSim advanced usage

### Importing TDcoSim

TDcoSim can be imported and used like a normal Python module. Note that package name is in lower case.

 ```python
   import tdcosim
 ```

### Using TDcoSim within your script
The basic steps to write your own co-simulation program are as follows:

1. Setup desired T+D or T+D+DER system by making necessary entries in the [**config**](docs/chapter_2_understanding_config_file.md) file.

2. Import necessary classes.

   ```python
      from tdcosim.report import generateReport
      from tdcosim.global_data import GlobalData
      from tdcosim.procedure.procedure import Procedure
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
