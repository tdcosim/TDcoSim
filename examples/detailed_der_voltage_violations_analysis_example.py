# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 21:15:33 2020

@author: splathottam
"""

import tdcosim
import pandas as pd
import matplotlib.pyplot as plt
from tdcosim.app.aggregatedDERApp.aggregatedDER.post_process import PostProcess
import cufflinks as cf

PostProcess=PostProcess()

excel_data = pd.read_excel(open(r'reportfin.xlsx', 'rb'), sheet_name=None)
der_df = PostProcess.dict2df(data=excel_data,scenarioid='1',inputType='tdcosim-excel')

recovery_list = PostProcess.show_voltage_recovery_der(vmin=0.59,vmax = 1.0,maxRecoveryTime=0.10,df=der_df)

violations_list = PostProcess.show_voltage_violations_der(vmin=0.75,vmax = 1.0,df=der_df)
