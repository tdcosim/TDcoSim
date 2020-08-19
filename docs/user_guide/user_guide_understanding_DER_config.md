# Understanding the config file

The **DER config** file exposes the parameters of the DER. It allows user to develop user customized DER models.

## DER configuration

**der_key (dict):** A user specified key that serves as identifier to the DER configuration.
   *  **parent_config (string):** The previous DER configuration on which the current DER is based on.
   *   **basic_specs (dict):** The basic specifications for the model.
      * **model_type (dict):** The type of model this configuration is meant for. Valid options are: "ThreePhaseUnbalanced","ThreePhaseBalanced","ThreePhaseUnbalancedConstantVdc".
   *   **module_parameters (dict):** The parameters of the solar PV module.
      * *Np (int):* The numper of parallely connected cells.
      * *Ns (int):* The numper of series connected cells.
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
      * **Ki_Q (float):** Integral constant for reactive power controller.

   * **verbosity (string):** The logging level.
   * **LVRT/HVRT (dict):** LVRT/HVRT ride-through levels.
      * *config_id (string):* Specifies the LVRT/HVRT configuration id available in the *config_der.json* that should be used with this DER configuration.
      * *V_threshold (float):* Specifies the voltage threshold for low voltage anomaly in p.u. 
      * *t_threshold (float):* Specifies the trip time threshold for low voltage anomaly in seconds. 
      * *mode (string):* Specifies the DER operating behavior during ride through (options: 'momentary_cessation','mandatory_operation'). 