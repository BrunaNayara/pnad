import pandas as pd
import numpy as np

from .utils import cache_path


class Cache:
    def _path(self, year, col):
        return cache_path(f'cache-{col}-{str(year)}.npy')

    def save(self, year, data):
        """
        Save dataframe for given year.
        """
        if isinstance(data, pd.Series):
            data = pd.DataFrame(data)
        for name, col in data.items():
            path = str(self._path(year, name))
            np.save(path, col.values)

    def load(self, year, cols):
        """
        Load a data frame data at given years.
        """
        df = {}
        for col in cols:
            try:
                path = str(self._path(year, col))
                df[col] = np.load(path, allow_pickle=True)
            except FileNotFoundError as exc:
                raise CacheError(col) from exc
        df = pd.DataFrame(df, columns=cols)
        return df


class CacheError(Exception):
    """
    Raised when items are not found in cache.
    """
