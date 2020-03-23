import pandas as pd
import numpy as np
from sidekick import Proxy

from ..cache import Cache, CacheError
from ..utils import select_by_year


class Transformer:
    """
    Transform a Pandas data frame.
    """

    def __init__(self, year, fields=None, *, loader):
        self.year = year
        self._cache = Cache()
        self._fields = tuple(fields or self._all_fields())
        self._loader = loader

    def __call__(self):
        df = self._load_cached()
        if len(df.columns) == len(self._fields):
            return df

        extra = {}
        new = DataFrameProxy(df, self, self._loader)
        for attr in self._fields:
            if attr == 'year':
                pass
            elif attr not in df.columns:
                col = getattr(new, attr)
                if col is not None:
                    extra[attr] = df[attr] = col
        if 'year' in self._fields:
            new['year'] = self.year
        if extra:
            self._cache.save(self.year, pd.DataFrame(extra))
        new = new[[c for c in self._fields if c in new.columns]]
        return new

    def _all_fields(self):
        return [attr for attr in dir(self) if not attr.startswith('_')]

    def _load_cached(self):
        data = pd.DataFrame()
        for attr in self._fields:
            if attr == 'year':
                continue
            try:
                data[attr] = self._cache.load(self.year, [attr])[attr]
            except CacheError as exc:
                pass
        return data


class DataFrameProxy(Proxy):
    def __init__(self, data, transformer, loader):
        super().__init__(data)
        self.__data = data
        self.__transformer = transformer
        self.__year = transformer.year
        self.__loader = loader
        self.__raw = None

    def __getattr__(self, item):
        try:
            return getattr(self.__data, item)
        except AttributeError as exc:
            return self._fallback(item, exc)

    def __getitem__(self, item):
        try:
            return self.__data[item]
        except KeyError as exc:
            return self._fallback(item, exc)

    def _fallback(self, item, exc):
        if hasattr(self.__transformer, item):
            fn = getattr(self.__transformer, item)
            col = self.__data[item] = fn(self)
            return col
        elif self.__raw is None:
            self.__raw = self.__loader()
        try:
            col = self[item] = self.__raw[item]
        except KeyError:
            raise exc
        return col


class Field:
    """
    Control final presentation of a field from the PNAD survey.

    Field objects implement the `Field.process(raw, final)` method that knows
    how to transform data from the raw values in the PNAD survey to the final
    values presented in the PFrame objects.

    The default implementation simply knows how to retrieve data from the a
    given variable in the raw PNAD data frame and converts the missing values
    to NaNs"""

    def __init__(self, spec, missing=-1, descr=''):
        self.spec = spec
        self.missing = missing
        self.descr = descr

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        def field_method(df):
            return self.transform(instance, df)

        return field_method

    def transform(self, loader, df):
        """
        Called with both the raw data frame and the partially
        constructed final output. Must return an array-like object that shall
        be appended in the corresponding field.
        """

        if isinstance(self.spec, str):
            field = self.spec
        elif isinstance(self.spec, (dict, list)):
            field = select_by_year(loader.year, self.spec)
            if field is None:
                return None
            elif isinstance(field, (int, float)):
                return np.ones(len(df), dtype=int) * field
        else:
            raise ValueError('raise invalid data: %r' % self.spec)

        try:
            col = np.array(df[field])
        except KeyError:
            return None
        if self.missing is not None:
            col = np.where(col == self.missing, float('nan'), col)
        return col


class IncomeField(Field):
    """
    The income field from PNAD survey.
    """

    def __init__(self, *args, **kwds):
        self.default_to_zero = kwds.pop('default_to_zero', False)
        super(IncomeField, self).__init__(*args, **kwds)

    def transform(self, loader, df):
        lst = super().transform(loader, df)
        if lst is None:
            return np.zeros(len(df), dtype=float) * float('nan')
        return self.remove_missing(lst)

    @staticmethod
    def remove_missing(lst):
        missing = [-1, 999999, 9999999, 99999999, 999999999, 999999999999]
        lst = np.asfarray(lst)
        for value in missing:
            lst[lst == value] = float('nan')
        return lst


class FunctionField(Field):
    """
    Field computed from a functional transformation. Can be initialized
    as a decorator to some method.
    """

    def __init__(self, func=None, descr=''):
        self.func = func
        super().__init__('<processed>', descr=descr or func.__doc__)

    def transform(self, loader, df):
        return self.func(loader, df)


#
# Decorators and utilities
#
def function(*args, **kwargs):
    """
    Decorates a method as a FunctionField().
    """
    return lambda fn: FunctionField(fn, *args, **kwargs)


#
# Utility functions
#
def sum_na(*args):
    """
    Sum all arguments by replacing nan by zero when necessary
    """

    x0, *others = map(np.asarray, args)

    # Create mask of null values
    isnull = np.isnan(x0)
    for x in others:
        isnull &= np.isnan(x)

    # Sum all inputs assuming nan == 0
    res = np.where(np.isnan(x0), 0.0, x0)
    for x in others:
        res += np.where(np.isnan(x), 0.0, x)

    # Make the entries in which all values are null, null again
    res[isnull] = float('nan')
    return res
