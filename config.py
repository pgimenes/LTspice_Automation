import re
import numpy as np

# -------------------- ENVIRONMENT PARAMETERS ---------------------------
LTSPICE_PATH = r"<PATH TO LTSPICE EXECUTABLE>" # eg "C:\\Program Files\\LTC\\LTspiceXVII\\XVIIx64.exe"
PROJECT_PATH = r"<PATH TO PROJECT PATH>" # eg "C:\\Users\\Joe\\LTspice_project\\", include trailing \\
SCHEMATIC = r"<SCHEMATIC FILE>" # eg "boost_converter.asc"
RESULTS_FILE = r"<PATH TO RESULTS CSV FILE>" # eg "C:\\Users\\Joe\\LTspice_project\\results_dump.csv"

# -------------------- SIMULATION PARAMETERS ----------------------------
PARAMETER = '<DESIGN PARAMETER>' # eg 'Vin'
params = <PARAMETER LIST> # eg range(0, 100)
WAIT_TIME = <WAITING TIME> # in seconds, eg 30
pin_regex = re.compile('<PIN REGEX>') # regex for input power, eg re.compile('^pin: .*=([0-9.]*) FROM .*')
pout_regex = re.compile('<POUT REGEX>')# regex for output power, eg re.compile('^pout: .*=([0-9.]*) FROM .*')