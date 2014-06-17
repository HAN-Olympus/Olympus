
from setuptools import setup
from setuptools.command.build_py import build_py
import os

class my_build_py(build_py):
    pass
	


print os.getcwd()

setup(
    name = "Olympus generated package",
    version = "0.3",
    author = "Stephan Heijl",
	packages = [],
    py_modules=['Olympus.lib.controls.Float', 'Olympus.lib.Log', 'Olympus.lib.Module', 'Olympus.lib.Storage', 'Olympus.lib.controls.Text', 'Olympus.lib.Collection', 'Olympus.modules.acquisition.AcquisitionModule', 'Olympus.lib.controls.Integer', 'Olympus.lib.Config', 'Olympus.lib.StoredObject', 'Olympus.lib.Article', 'Olympus.lib.Singleton', 'Olympus.lib.Control']
	cmdclass={'build_py': my_build_py}
)		
		