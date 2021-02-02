import platform
from setuptools import setup

if platform.architecture()[0]=='64bit':
	setup(name='tdcosim',
      version=open("tdcosim/_version.py").readlines()[-1].split()[-1].strip("\"'"),
      packages=setuptools.find_packages(),
      description='Transmission and Distribution Network co-Simulation for Power System',
      author = 'TDcoSim Team',
      author_email='yim@anl.gov',
      license= 'LICENSE.txt',
      install_requires=['pywin32==228','matplotlib>=2.0.2','numpy==1.16.2','scipy==1.2.1',
      'xlsxwriter==1.1.8','psutil==5.7.0','pandas==0.24.2'],
      )
else:
	setup(name='tdcosim',
      version=open("tdcosim/_version.py").readlines()[-1].split()[-1].strip("\"'"),
      packages=setuptools.find_packages(),
      description='Transmission and Distribution Network co-Simulation for Power System',
      author = 'TDcoSim Team',
      author_email='yim@anl.gov',
      license= 'LICENSE.txt',
      install_requires=['pywin32==224','matplotlib==2.0.2','numpy==1.16.2','scipy==1.2.1',
      'xlsxwriter==1.1.8','psutil==5.7.0','pandas==0.24.2'],
      )

