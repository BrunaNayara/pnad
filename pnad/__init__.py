"""
A toolbox for analysing data from the Brazilian PNAD survey.
"""
__author__ = 'Fábio Macëdo Mendes'
__version__ = '0.1.0'
from .loader import load, load_household
from .enums import Race, Gender, State
from .utils import years, filter_years