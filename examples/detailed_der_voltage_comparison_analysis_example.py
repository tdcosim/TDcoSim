# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 21:15:33 2020

@author: splathottam
"""

import tdcosim
import pandas as pd
import matplotlib.pyplot as plt
from tdcosim.app.aggregatedDERApp.aggregatedDER.post_process import PostProcess

PostProcess=PostProcess()

excel_data = pd.read_excel(open(r'reportfin.xlsx', 'rb'), sheet_name=None)
der_df = PostProcess.dict2df(data=excel_data,scenarioid='1',inputType='tdcosim-excel')

ST = PostProcess.compare_voltages_der(vmin=0.4,vmax=0.6,maxRecoveryTime=0.03,error_threshold=0.001,df=der_df)
