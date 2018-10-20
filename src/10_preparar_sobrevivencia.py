import pandas as pd
import numpy as np
import sys
from os import listdir
from os.path import isfile, join
from datetime import date
from dateutil.relativedelta import relativedelta as rd
import scipy.stats as stats
from copy import deepcopy


caminho_xml = sys.argv[1]
caminho_csv = sys.argv[2]

