from setuptools import setup, find_packages

with open("requirements.txt") as requirements:
    requiredList = requirements.read().split("\n")

setup(
    name = "Olympus",
    version = "0.3",
    author = "Stephan Heijl",
    install_requires = requiredList,
    packages=find_packages()
)