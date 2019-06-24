# Chapter 3

## How to use TDcoSim?
The TDcoSim module can be imported and used like a normal Python module.

### Quick start
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


## Using TDcoSim from command line
This chapter walks the user through the step to start the simulation after setting up the configuration file. To start the simulation the user needs to open  a command line prompt inside the folder containing the main.py file (for e.g. type Shift+C+M+D as shown below).

![Open_CMD](images/Open_CMD.png)

*Figure:* Opening command line window.

Once the command window is opened. The user can type in the following command, as shown in Figure below, followed by Enter to start the simulation using TDcoSim tool.

                        "python main.py > log_file.txt"

![Starting_TDcoSim_tool](images/Starting_TDcoSim_tool.PNG)

*Figure:* Starting TDcoSim tool from Command Window.

Python starts the python process and runs the python code **"main.py"** which starts the TDcoSim tool. '>' specifies the output logfile. In the example above the output log file name is 'log_file.txt'.