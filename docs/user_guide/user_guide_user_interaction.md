# Using the configuration template

TDcoSim is a declarative tool, where the user defines specification for the cosimulation. The specifications are given through a JSON configuration file which can be  manually populated as explained in [Getting Started](user_guide_getting_started.md). An alternative and faster option is to use the **tdcosimapp**. The *tdcosimapp* is to *TDcoSim* what *kubectl* is to *kubernetes*. The *tdcosimapp* allows users to,

1. Create configuration template
2. Validate user provided configuration, providing helpful hints to troubleshoot issues, if there are any.
3. Provide information/help about any declaration used in configuration file.
4. Run the co-simulation
5. Launch browser based dashboard to analyze the results

***
***Note:*** The **tdcosimapp** can be invoked using the *tdcosim* command from the command line .

***

## Create Configuration Template

```
tdcosim template --templatePath config.json --simType static
```

Let us go over the above command. **template** specifies that the user is interested in using tdcosimapp to create configuration template. Next, **--templatePath config.json** specifies that the user wants to store the created configuration in the current working directory under the name config.json. Finally, the type of configuration is specified using **--simType static**. One can create the configuration template for a dynamic co-simulation using,

```
tdcosim template --templatePath config.json --simType dynamic
```

## Configuration File Help

```
tdcosim template --configHelp outputConfig
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
tdcosim template --configHelp outputConfig.type
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
tdcosim run --config config.json
```
The user will see a progress bar similar to the one shown below,

```
             INITIATED ON WED, JUN 02 2021  14:54
Simulation Progress : ====================> 100.04000000000013%(0.5002000000000006s/0.5s)
Solution time: 9.066482067108154
```

## Dashboard

```
tdcosim dashboard -o "path/to/dataframefiles"
```

