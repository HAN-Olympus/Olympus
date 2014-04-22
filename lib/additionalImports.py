"""additionalImports is used by Core scripts to allow access into the lib and modules directory including any subdirectory of in the case of 'modules'."""
# Allow importing modules from the lib and modules directories
import os, sys
currentDir = os.path.dirname(__file__)
relLibDir = currentDir + "../../core"
absLibDir = os.path.abspath(relLibDir)
sys.path.insert(0, absLibDir)

# Get all the modules directories
relModuleDir = currentDir + "/../modules"
absModuleDir = os.path.abspath(relModuleDir)
for moduleType in os.listdir(absModuleDir):
	sys.path.insert(0, absModuleDir+"/"+moduleType)

def test_Import():
	for file in os.listdir(absLibDir):
		if file[-3:] == ".py":
			__import__(file[:-3])