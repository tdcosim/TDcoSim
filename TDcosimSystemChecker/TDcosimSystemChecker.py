import requests
import zipfile
import os
import sys
import subprocess

print ('Checking System')
try:
	out = subprocess.Popen(['python', '--version'], 
	           stdout=subprocess.PIPE, 
	           stderr=subprocess.STDOUT)
	output, err = out.communicate()		
	if 'Python 2.7' in output:
		print("Installed python version: " + output)	
	else:
		print("Failed to find Python 2.7, Please check the Python 2.7 installation and environmental variables")	
		name = raw_input("Press enter key to finish ") 
		exit()
except:
	print("Failed to find Python 2.7, Please check the Python 2.7 installation and environmental variables")	
	print (sys.exc_info()[0])
	name = raw_input("Press enter key to finish ") 
	exit()


PTIPath = "C:\Program Files (x86)\PTI"
PSSE33Path = PTIPath + "\PSSE33"
PsspyPath = PSSE33Path + "\PSSBIN"
if os.path.isdir(PTIPath):	
	if os.path.isdir(PSSE33Path):	
		if os.path.isdir(PsspyPath):	
			sys.path.append(PsspyPath)			
			os.environ['PATH']+=';'+PsspyPath
			try:
				import psspy				
				print ("Success to load psspy")				
			except:
				print ("Failed to load psspy, Please check the PSSE33 Installation")			
				print (sys.exc_info()[0])
		else:
			print ("Failed to find psspy, Please check the PSSE33 Installation")
			name = raw_input("Press enter key to finish ") 
			exit()
	else:
		print ("Failed to find PSSE33, Please check the PSSE33 Installation")
		name = raw_input("Press enter key to finish ") 
		exit()
else:
	print ("Failed to find PSSE, Please check the PSSE33 Installation")
	name = raw_input("Press enter key to finish ") 
	exit()


import win32com.client
try:
	engine = win32com.client.Dispatch("OpenDSSEngine.DSS")      
	engine.Start("0")  
	print ("Success to load OpenDSS")
except:
	print ("Filed to load OpenDSS, Please check the OpenDSS Installation")
	print (sys.exc_info()[0])
	name = raw_input("Press enter key to finish ") 
	exit()


print ('Downloading PVDER')
url = 'https://github.com/sibyjackgrove/SolarPV-DER-simulation-utility/archive/master.zip'
r = requests.get(url)
with open('./pvder.zip', 'wb') as f:
	f.write(r.content)
print ('Installing PVDER')
with zipfile.ZipFile('./pvder.zip', 'r') as zip_ref:
    zip_ref.extractall('./pvder') #code is locate in .\pvder\SolarPV-DER-simulation-utility-master\
try:
	os.system("pip install -e ./pvder/SolarPV-DER-simulation-utility-master")
	os.system("python ./pvder/SolarPV-DER-simulation-utility-master/tests/test_PVDER_SinglePhase.py")
	print ('Success to test PVDER')
except:
	print ("Failed the PVDER test, Please contact TDcosim team with following infomation")
	print (sys.exc_info()[0])
	name = raw_input("Press enter key to finish ") 
	exit()


print ('Downloading TDcosim')
url = 'https://github.com/tdcosim/TDcoSim/archive/master.zip'
r = requests.get(url)
with open('./tdcosim.zip', 'wb') as f:
	f.write(r.content)
print ('Installing TDcosim')
with zipfile.ZipFile('./tdcosim.zip', 'r') as zip_ref:
    zip_ref.extractall('./tdcosim') #code is locate in .\tdcosim\TDcoSim-master
try:
	os.system("pip install -e ./tdcosim/TDcoSim-master")
	os.chdir('./tdcosim/TDcoSim-master/examples/')
	os.system("python ./run_qsts.py")
	os.chdir('../../../')
	print ('Success to test TDcosim')
except:
	print ("Failed the TDcosim test, Please contact TDcosim team with following infomation")
	print (sys.exc_info()[0])
	name = raw_input("Press enter key to finish ") 
	exit()

print ("TDCosim system checking is completed")
name = raw_input("Press enter key to finish ") 