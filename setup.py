import os
import sys
import site
import platform
from setuptools import setup
from setuptools.command.install import install


def post_install():
	try:
		baseDir=site.getsitepackages()
	except AttributeError:
		baseDir=[os.path.join(site.PREFIXES[0],'lib','site-packages')]

	assert baseDir and 'site-packages'==baseDir[-1].split(os.path.sep)[-1]
	baseDir=baseDir[-1]
	tdcosimapp=os.path.join(baseDir,'tdcosim','tdcosimapp.py')
	pyExe=sys.executable.split('\\')[-1].replace('.exe','')
	os.system('mkdir "{}"'.format(os.path.join(baseDir,'tdcosim','install_logs')))
	directive='reg query "HKEY_CURRENT_USER\Software\Microsoft\Command Processor" /v AutoRun > {} 2>&1'.format(\
	os.path.join(baseDir,'tdcosim','install_logs','previous_reg_query.txt'))
	print('running directive,\n{}'.format(directive))
	os.system(directive)
	directive='reg add "HKEY_CURRENT_USER\Software\Microsoft\Command Processor" /v AutoRun /d "doskey tdcosim={} \\"{}\\" $*" /f'.format(pyExe,tdcosimapp)
	print('running directive,\n{}'.format(directive))
	os.system(directive)

class PostInstall(install):
	def run(self):
		install.run(self)
		post_install()

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
      install_requires=['pywin32>=301','matplotlib>=2.0.2','numpy>=1.16.2','scipy>=1.2.1',
      'xlsxwriter>=1.1.8','psutil>=5.7.0','pandas>=0.24.2','dash>=1.21.0','networkx','pvder','dask[dataframe]'],
      extras_require={'diffeqpy': ['diffeqpy>=1.1.0']},
      package_data={'tdcosim':['data/**/**/*','logs/.*','config/*','examples/*']},
      cmdclass={'install':PostInstall}
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
      'xlsxwriter==1.1.8','psutil==5.7.0','pandas>=0.24.2','dash>=1.21.0','networkx','pvder','dask[dataframe]'],
      extras_require={'diffeqpy': ['diffeqpy>=1.1.0']},
      package_data={'tdcosim':['data/**/**/*','logs/.*','config/*','examples/*']},
      cmdclass={'install':PostInstall}
      )
