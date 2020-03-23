import pandas as pd

from .transformer import PersonTransformer
from .utils import data_path


def load(year, fields=None):
    """Load person data from PNAD survey for the given year.

    This function automatically caches the results and can be much
    slower to execute the first time than subsequent executions.

    Args:
        year : int
            The year for the desired PNAD survey.
        fields : list
            List of column names to load. If not given, select all columns.
    """
    return _load('person', year, fields)


def load_household(year, fields=None):
    """Load household data from PNAD survey for the given year.

    This function automatically caches the results and can be much
    slower to execute the first time an year is requested than subsequent
    executions.

    Args:
        year : int
            The year for the desired PNAD survey.
        fields : list
            List of column names to load. If not given, select all columns.
    """
    return _load('household', year, fields)


def load_raw(year, which):
    """
    Load raw data frame for given year. `which` must be either 'person' or
    'household'.
    """
    name = {'person': 'pes', 'household': 'dom'}
    path = f'{data_path()}/{year}/{name[which]}{year}.pnad'
    return pd.read_pickle(path, 'gzip')


def _load(which, year, fields):
    loader_class = {'person': PersonTransformer}[which]
    loader = loader_class(year, fields, loader=lambda: load_raw(year, which))
    return loader()
