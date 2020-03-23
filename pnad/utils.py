import os
from pathlib import Path

import numpy as np
from sidekick import deferred


#
# Paths
#
def data_path(sub=None) -> Path:
    """
    Return a Path object pointing to where PNAD data frames are stored.
    """
    base = _base() / 'data'
    return base if sub is None else base / sub


def cache_path(sub=None) -> Path:
    """
    Return a Path object pointing to where PNAD data frames are cached.
    """
    base = _base() / 'cache'
    return base if sub is None else base / sub


def _base():
    base = Path(__file__).parent
    if os.path.islink(base):
        base = os.readlink(base)
    return Path(base).parent


#
# Information about PNAD years
#
PNAD_YEARS = deferred(lambda: np.array(
    sorted(int(yy) for yy in os.listdir(str(data_path())) if yy.isdigit())))
HAS_FULL_RACE_INFO_YEARS = deferred(lambda: [1982, *years(1987, ...)])


def years(*args):
    """
    Return all years in the given range in which PNAD occurred. Can use None
    or Ellipsis (...) in either a or b in order to select an open range.

    Example:
        >>> years()                                         # doctest: +ELLIPSIS
        [1976, 1977, 1978, ...]  # Full list of years
        >>> years(..., 1980) # using ellipsis to select an open range.
        [1976, 1977, 1978, 1979]

        >>> years((1990, 1999))
        [1990, 1992, 1993, 1995, 1996, 1997, 1998, 1999]
    """
    if not args:
        args = [None]
    elif len(args) == 2:
        args = [args]
    elif len(args) > 2:
        raise TypeError('accepts 0, 1 or 2 arguments')
    yrs_range = args[0]

    if yrs_range is None:
        yrs_range = None, None
    a, b = yrs_range
    a = None if a is Ellipsis else a
    b = None if b is Ellipsis else b

    if a is not None and b is not None:
        return [y for y in PNAD_YEARS if a <= y <= b]
    elif b is not None:
        return [y for y in PNAD_YEARS if y <= b]
    elif a is not None:
        return [y for y in PNAD_YEARS if a <= y]
    else:
        return list(PNAD_YEARS)


def prepare_years(*args):
    """Prepare input and returna valid list of years

    Function signatures:
        prepare_years()            ==> return a list of all available years
        prepare_years((a, b))      ==> trunc the available years in the given
                                       range. (a or b can be None or Ellipsis
                                       in order to be ineffective)
        prepare_years(list)        ==> return the valid years in the given list
        prepare_years(y1, y2, ...) ==> return the given years, when valid
    """
    if not args:
        args = [None]
    elif len(args) > 1:
        args = [list(args)]

    yrs = args[0]
    if yrs is None or yrs is Ellipsis:
        return list(PNAD_YEARS)
    elif isinstance(yrs, tuple):
        return years(yrs)
    elif isinstance(yrs, int):
        return [yrs]
    else:
        return [yy for yy in yrs if yy in PNAD_YEARS]


def select_by_year(year, D):
    """Select year from specification given in dictionary or list of ranges.

    Examples:
        >>> spec = {(..., 1990): 'foo',
        ...                1991: 'bar',
        ...        (1992, 2000): 'foobar',
        ...         (2001, ...): 'blah'}
        >>> select_by_year(1990, spec)
        'foo'
        >>> select_by_year(1991, spec)
        'bar'
        >>> select_by_year(1999, spec)
        'foobar'
        >>> select_by_year(2010, spec)
        'blah'
    """

    # Must have a list of specifications
    if hasattr(D, 'items'):
        D = list(D.items())

    # We want a sorted and normalized list
    spec = []
    for item, value in D:
        if isinstance(item, (tuple, list)):
            a, b = item
        else:
            a = b = item
        a = -float('inf') if a in [..., None] else a
        b = float('inf') if b in [..., None] else b
        spec.append((a, b, value))
    spec.sort()

    # Now let us test each interval
    for a, b, value in spec:
        if a <= year <= b:
            return value
    else:
        raise ValueError('no valid range for year %s: %s' % (year, spec))


def filter_years(years, valid=None):
    """Restrict the values in the `years` specification to the ones present in
    the `valid` list.

    Args:
        years (years specification):
            Any argument for the prepare_years() function
        valid (None or list):
            If None, consider all valid pnad years, else, it is interpreted as a
            list or set of valid years.

    Return:
        A list of acceptable years.
    """

    years = prepare_years(years)
    if valid is None:
        return years
    else:
        return [yy for yy in years if yy in valid]
