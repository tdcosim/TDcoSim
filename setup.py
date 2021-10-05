import os
import platform
from setuptools import setup

# The text of the README file
f=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'README.md'))
README=f.read()
f.close()

if platform.architecture()[0]=='64bit':
	setup(name='tdcosim',
      version=open("tdcosim/_version.py").readlines()[-1].split()[-1].strip("\"'"),
      packages=setuptools.find_packages(),
      include_package_data=True,
      description='Transmission and Distribution Network co-Simulation for Power System',
      long_description=README,
      long_description_content_type="text/markdown",
      url ='https://github.com/tdcosim/TDcoSim',
      author = 'TDcoSim Team',
      author_email='yim@anl.gov',
      license= 'LICENSE.txt',
      classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
      ],
      install_requires=['pywin32==228','matplotlib>=2.0.2','numpy>=1.16.2','scipy>=1.2.1',
      'xlsxwriter>=1.1.8','psutil>=5.7.0','pandas>=0.24.2','dash>=1.21.0','networkx','pvder'],
      extras_require={'diffeqpy': ['diffeqpy>=1.1.0']},
      package_data={'tdcosim':['data/**/**/*','logs/.*','config/*','examples/*']}
      )
else:
	setup(name='tdcosim',
      version=open("tdcosim/_version.py").readlines()[-1].split()[-1].strip("\"'"),
      packages=setuptools.find_packages(),
      include_package_data=True,
      description='Transmission and Distribution Network co-Simulation for Power System',
      long_description=README,
      long_description_content_type="text/markdown",
      url ='https://github.com/tdcosim/TDcoSim',
      author = 'TDcoSim Team',
      author_email='yim@anl.gov',
      license= 'LICENSE.txt',
      classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
      ],
      install_requires=['pywin32==224','matplotlib>=2.0.2','numpy>=1.16.2','scipy>=1.2.1',
      'xlsxwriter==1.1.8','psutil==5.7.0','pandas>=0.24.2','dash>=1.21.0','networkx','pvder'],
      extras_require={'diffeqpy': ['diffeqpy>=1.1.0']},
      package_data={'tdcosim':['data/**/**/*','logs/.*','config/*','examples/*']}
      )
