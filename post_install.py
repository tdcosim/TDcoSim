import os
import inspect


if __name__=="__main__":
	baseDir=os.path.dirname(inspect.getfile(os))
	tdcosimapp=os.path.join(baseDir,'site-packages','tdcosim','tdcosimapp.py')
	assert os.path.exists(tdcosimapp)
	os.system('reg add "HKEY_CURRENT_USER\Software\Microsoft\Command Processor" /v AutoRun /d "doskey tdcosim=python \"{}\" $*"'.format(tdcosimapp))