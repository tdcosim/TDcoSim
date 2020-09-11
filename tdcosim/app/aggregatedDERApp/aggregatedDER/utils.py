import os
import sys
import linecache
import six
import inspect

import psspy


#===============================EXCEPTION===============================
def PrintException(debug=False):
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	six.print_("Exception in Line {}".format(lineno))
	six.print_("Error in Code: {}".format(line.strip()))
	six.print_("Error Reason: {}".format(exc_obj))
	raise
	if debug:
		return lineno,line,exc_obj

#==================================================================================
def psse_version():
	psseDir=os.path.dirname(inspect.getfile(psspy))
	psseVersion=''
	for version in ['33','34','35']:
		if os.path.exists(psseDir+os.path.sep+'psse{}.py'.format(version)):
			psseVersion=version
			break
	return psseVersion
