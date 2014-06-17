
from setuptools import setup
import os

print os.getcwd()

setup(
    name = "Olympus generated package",
    version = "0.3",
    author = "Stephan Heijl",
	packages = [],
    py_modules=['Olympus.lib.controls.Float', 'Olympus.lib.Log', 'Olympus.lib.Module', 'Olympus.lib.Storage', 'Olympus.lib.controls.Text', 'Olympus.lib.Collection', 'Olympus.modules.acquisition.AcquisitionModule', 'Olympus.lib.controls.Integer', 'Olympus.lib.Config', 'Olympus.lib.StoredObject', 'Olympus.lib.Article', 'Olympus.lib.Singleton', 'Olympus.lib.Control']
)		
		