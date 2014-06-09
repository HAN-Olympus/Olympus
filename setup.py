from setuptools import setup

with open("requirements.txt") as requirements:
    requiredList = requirements.read().split("\n")

setup(
    name = "Olympus",
    version = "0.3",
    author = "Stephan Heijl",
    packages = ['Olympus'],
    install_requires = requiredList
)
