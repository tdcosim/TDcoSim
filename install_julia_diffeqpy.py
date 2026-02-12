# -*- coding: utf-8 -*-
"""
Created on Tue Dec 07 12:00:00 2021

@author: splathottam
"""

def setup_pyjulia_env(path_to_project="."):
    """
    This method was developed by 'Federico Simonetta'. Original source:https://github.com/JuliaPy/pyjulia/issues/473
    A function that installs all dependencies for current environment.
    This should be the same as what `juliacall` does at every import time.
    * `path_to_project` is the path to the project that will be instantiated.
    If `None`, no project will be instantiated. Defaults: to the current
    working directory.
    """
    import jill.install  # noqa: autoimport
    import os  # noqa: autoimport
    import shutil  # noqa: autoimport
    
    if shutil.which('julia') is None:
        print(
            "No Julia executable found, installing the latest version using `jill`")
        jill.install.install_julia("stable", confirm=True)
        if shutil.which('julia') is None:
            print(f"Please add {os.environ['JILL_SYMLINK_DIR']} to your path")
    import julia  # noqa: autoimport
    # the following installs dependencies for pyjulia
    julia.install()
    from julia.api import LibJulia  # noqa: autoimport

    if path_to_project is not None:
        api = LibJulia.load()
        api.init_julia([f"--project={path_to_project}"])

        from julia import Main  # noqa: autoimport

        Main.eval('using Pkg')
        Main.eval('Pkg.instantiate()')

def install_diffeqpy():
    """Method to install diffeqpy and Sundials"""
    import time
    print('Setting up diffeqpy...')
    import diffeqpy
    diffeqpy.install()
    
    from julia import Pkg

    try:
        from julia import Sundials
    except ImportError:
        Pkg.add("Sundials")
    finally:
        from julia import Sundials
    print('Updating Julia packages...')
    Pkg.update() #Update all Julia packages

    tic = time.perf_counter()
    from diffeqpy import de
    toc = time.perf_counter()
    print("'diffeqpy' was imported in {:.3f} seconds".format(toc - tic))
    

setup_pyjulia_env(path_to_project=".")
install_diffeqpy()