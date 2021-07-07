# User Interaction

TDcoSim is a declarative tool, where the user defines specification for the cosimulation. The specifications are given as a JSON file. In order to speed up the process, TDcoSim comes with tdcosimapp. The *tdcosimapp* is to *TDcoSim* what *kubectl* is to *kubernetes*. The *tdcosimapp* allows users to,

1. Create configuration template
2. Validate user provided configuration, providing helpful hints to troubleshoot issues, if there are any.
3. Provide information/help about any declaration used in configuration file.
4. Run the co-simulation
5. Launch browser based dashboard to analyze the results

## Create Configuration Template

```
python tdcosimapp.py --type template --templatePath config.json --simType static
```

Let us go over the above command. **--type template** specifies that the user is interested in using tdcosimapp to create configuration template. Next, **--templatePath config.json** specifies that the user wants to store the created configuration in the current working directory under the name config.json. Finally, the type of configuration is specified using **--simType static**. One can create the configuration template for a dynamic co-simulation using,

```
python tdcosimapp.py --type template --templatePath config.json --simType dynamic
```

## Configuration File Help

```
python tdcosimapp.py --configHelp outputConfig
```
This will show the following information,

```
outputConfig
------------
Output/results setup

Check:
outputConfig.simID
outputConfig.type
outputConfig.outputDir
outputConfig.outputfilename
outputConfig.scenarioID
```

In case one wants to know more information about outputConfig.type,

```
python tdcosimapp.py --configHelp outputConfig.type
```

which will result in,

```
outputConfig.type
-----------------

Type of output. Default is dataframe.
```

## Run the Co-Simulation

Running the co-simulation is as simple as,

```
python tdcosimapp.py --type run --config config.json
```
The user will see a progress bar similar to the one shown below,

```
             INITIATED ON WED, JUN 02 2021  14:54
Simulation Progress : ====================> 100.04000000000013%(0.5002000000000006s/0.5s)
Solution time: 9.066482067108154
```

## Dashboard

```
python tdcosimapp.py --type dashboard
```

