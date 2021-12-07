# Using the configuration template

TDcoSim is a declarative tool, where the user defines specification for the co-simulation. The specifications are given through a JSON configuration file. 
## Create Configuration Template
Example configuration files which can be used as a template can be generated using the **tdcosimapp**. 

```
tdcosim template --templatePath config.json --simType static
```

Let us go over the above command. **template** specifies that the user is interested in using tdcosimapp to create configuration template. Next, **--templatePath config.json** specifies that the user wants to store the created configuration in the current working directory under the name config.json. Finally, the type of configuration is specified using **--simType static**. 

Configuration template for a dynamic co-simulation using fast DER:

```
tdcosim template --templatePath config.json --simType dynamic
```
Configuration template for a dynamic co-simulation using detailed DER:

```
tdcosim template --templatePath config.json --simType dynamic_detailed_der
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

\pagebreak