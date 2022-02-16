# Understanding the config file

The **DER config** file exposes the parameters of the DER. It allows user to develop user customized DER models.

## DER configuration

**der_key (dict):** A user specified key that serves as identifier to the DER configuration or ride-through settings.

   *  **parent_config (string):** The previous DER configuration on which the current DER is based on.
   *   **basic_specs (dict):** The basic specifications for the model.
      
      * **model_type (dict):** The type of model this configuration is meant for. Valid options are: "ThreePhaseUnbalanced","ThreePhaseBalanced","ThreePhaseUnbalancedConstantVdc".
   *   **module_parameters (dict):** The parameters of the solar PV module.
      * *Np (int):* The number of cells in parallel connection.
      * *Ns (int):* The number of cells in series connection.
   *   **inverter_ratings (dict):** The parameters defining the power electronic inverter.
      * *Srated (float):* The rated capacity of the inverter (kVA).
      * *Vdcrated (float):* The rated DC link voltage of the inverter (V).
      * *Ioverload (float):* The maximum overload current (fraction of rated current).
      * *Vrmsrated (float):* The rated RMS voltage of the inverter (V).

   * **circuit_parameters (dict):** The parameters defining the power electronic inverter.
      * *Rf_actual (float):* The inverter terminal filter resistance (Ohm).
      * *Lf_actual (float):* The inverter terminal filter inductance (Henry).
      * *C_actual (float):* The inverter DC link capacitor capacitance (Farad).
   * **controller_gains (dict):** The parameters defining the power electronic inverter.
      * *Kp_GCC (float):* Proportional constant for current controller.
      * *Ki_GCC (float):* Integral constant for current controller.
      * *Kp_DC (float):* Proportional constant for DC link voltage controller.
      * *Ki_DC (float):* Integral constant for DC link voltage controller.
      * *Kp_Q (float):* Proportional constant for reactive power controller.
      * *Ki_Q (float):* Integral constant for reactive power controller.
   * **verbosity (string):** The logging level ('DEBUG', INFO', or 'ERROR').
   * **LVRT/HVRT (dict):**  These are settings for the Low voltage/high voltage ride through feature. There are two options available for providing the settings. The available settings for each voltage threshold level are also listed below.
       1. Specify a pre-defined configuration available in *config_der.json*, which may be provided through the *config_id* field as a string that corresponds to an existing key in the DER configuration file (recommended).
       2. Specify the ride through settings in-place by providing them as a dictionary through the *config* field.

       * *V_threshold (float):* Specifies the voltage threshold for low/high voltage anomaly in p.u. 
       * *t_threshold (float):* Specifies the trip time threshold for low/high voltage anomaly in seconds. 
       * *t_min_ridethrough:* Specifies the minimum time for which the DER will remain actively supplying power during an voltage anomaly before entering into momentary cessation or trip mode.
       * *mode (string):* Specifies the DER operating behavior during ride through (options: 'momentary_cessation','mandatory_operation').            
   * **VRT_delays (dict):** Time delay settings for power output cessation and output restoration.
       
       * *output_cessation_delay (float):* Specifies the time delay before power output from DER ceases.
       * *output_restore_delay (float):* Specifies the time delay before DER starts restoring power output after momentary cessation.
