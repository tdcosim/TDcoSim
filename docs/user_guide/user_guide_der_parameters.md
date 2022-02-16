# Fast DER and Detailed DER parameters

Detailed DER and Fast DER are two model types available to the user (through the **config** file). Detailed DER will use a Dynamic Phasor models while the Fast DER will use Dynamic current inject models. Since the modeling approaches are different, both the model use different set of parameters.


## Fast DER
The Fast DER is based on the DER_A model developed by EPRI and made available through commercial simulation software like PSS/E and PSLF. Note that the user need to populate the Fast DER parameters. They are automatically populated from the default values which can be accessed [here](https://github.com/tdcosim/TDcoSim/blob/v2_test/config/fast_der_default.json).

* **Circuit parameters**
  * *xf (float):* Voltage source reactance.

* **Reference values**
  * *Pref (float):* Active power reference value.
  * *Qref (float):* Reactive power reference value.
  * *vref (float):* Voltage magnitude reference setpoint.
  * *vref_ang (float):* Voltage angle reference setpoint.

* **Time constants**
  * *Trv (float):*  Voltage transducer time constant.
  * *Tfq (float):* Frequency transducer time constant.
  * *Tg (float):* Current (active and reactive) dynamics  time constant.  
  * *Tpord (float):* Active power dynamics time constant.
  * *Tiq (float):* Reactive current command time constant.
  * *Tid (float):* Active current command time constant.

* **Thresholds**
  * *Qmax (float):* Maximum reactive power setpoint.
  * *Qmax (float):* Maximum reactive power setpoint.
  * *Qmin (float):* Minimum reactive power setpoint.
  * *Pmax (float):* Maximum active power setpoint.
  * *Pmin (float):* Minimum active power setpoint.
  * *Imax (float):* Maximum allowed converter current.
  * *Id_max (float):* Maximum allowed active current.
  * *Id_min (float):* Minimum allowed active current.
  * *Id_min (float):* Minimum allowed active current.
  * *db_dw_up/db_dw_down (float):* Dead band in active power - frequency control.
  * *db_v_up/db_v_down (float):* Dead band in voltage - reactive power control.

* **Controller gains**
  * *Kp (float):* **Need to be added**
  * *Ki (float):* **Need to be added**
  * *Kpp/Kip (float):* Active power controller proportional/integral gain.
  * *Kpq/Kiq (float):* Reactive power controller proportional/integral gain. 
  * *Kfv (float):* **Need to be added**

## Detailed DER
The Detailed DER is based on the Dynamic Phasor model developed by ANL. It is available through the [pvder](https://github.com/tdcosim/SolarPV-DER-simulation-tool) Python package. The model parameters for detailed DER are described [here](user_guide_understanding_DER_config.md).

## Comparing DER parameters

| Parameter                       | Fast DER | Detailed DER          |
| ------------------------------- | -------- | --------------------- |
| Rated power                     | Pmax     | Srated, Np, Ns        |
| Rated voltage                   | vref     | Vrmsrated             |
| Rated current                   | Imax     | Ioverload             |
| Current controller gains        |          | Kp_GCC,Ki_GCC         |
| Active power controller gains   |    Kpp/Kip      | Kp_P,Ki_P,Kp_DC,Ki_DC |
| Reactive power controller gains | Kpq/Kiq | Kp_Q,Ki_Q             |

## Composite model parameters
If the composite model is connected to a T node, it is parameterized using the default values found [here] (https://github.com/tdcosim/TDcoSim/blob/v2_test/config/composite_load_model_rating.json). Note that the default values can be edited by the user.

## DER_A model parameters
If the DER_A model is connected to a T node, it is parameterized using the default values found [here] (https://github.com/tdcosim/TDcoSim/blob/v2_test/config/dera_rating.json). Note that the default values can be edited by the user.

\pagebreak
