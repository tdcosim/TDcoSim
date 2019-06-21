# Chapter 3

## Starting a simulation in TDcoSim

This chapter walks the user through the step to start the simulation after setting up the configuration file. To start the simulation the user needs to open the folder where the TDcoSim tool is installed. Once the folder where the tool is installed is identified the user needs to open the "CoSimulator" branch and open up a command window from the "CoSimulator" folder. To do that the user needs to go the box on the folder where we specify path and type Shift+C+M+D as shown in below.

![Open_CMD](images/Open_CMD.png)

Figure: Opening Command Window from Cosimulator Folder.

Once the command window is opened. The user can type in the following command, as shown in Figure below, followed by Enter to start the simulation using TDcoSim tool.

                        "python main2.py > log_file.txt"

![Starting_TDcoSim_tool](images/Starting_TDcoSim_tool.PNG)

Figure: Starting TDcoSim tool from Command Window.

Python starts the python process and runs the python code "main2.py" which starts the TDcoSim tool. '>' specifies the output logfile. In the example above the output log file name is 'log_file.txt'.