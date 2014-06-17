
from setuptools import setup
import os
print os.getcwd()

setup(
    name = "Olympus generated package",
    version = "0.3",
    author = "Stephan Heijl",
	packages = [],
    py_modules=['Olympus.core.Worker', 'Olympus.core.Core', 'Olympus.core.Core']
)		
		