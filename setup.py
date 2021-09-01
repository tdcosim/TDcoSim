import platform
import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

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
      'xlsxwriter>=1.1.8','psutil>=5.7.0','pandas>=0.24.2','dash>=1.21.0','networkx>=2.6.2'],
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
      'xlsxwriter==1.1.8','psutil==5.7.0','pandas>=0.24.2'],
      )

