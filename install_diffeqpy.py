# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 09:23:44 2021

@author: splathottam
"""
import subprocess
import sys
import time

try:
    import julia
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'julia'])
finally:
    import julia

julia.install()

try:
    import diffeqpy
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'diffeqpy'])
finally:
    import diffeqpy

diffeqpy.install()

tic = time.perf_counter()
from diffeqpy import de
toc = time.perf_counter()
print("'diffeqpy' was imported in {:.3f} seconds".format(toc - tic))
