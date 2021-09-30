import os
import inspect

import tdcosim


if __name__=="__main__":
	tdcosimDir=os.path.dirname(inspect.getfile(tdcosim))
	tdcosimapp=os.path.join(tdcosimDir,'tdcosimapp.py')
	os.system('reg add "HKEY_CURRENT_USER\Software\Microsoft\Command Processor" /v AutoRun /d "doskey tdcosim=python \"{}\" $*"'.format(tdcosimapp))