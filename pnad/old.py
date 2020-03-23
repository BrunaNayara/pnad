def _load_field_worker(field, year, which, use_cache=USE_CACHE, save_pnad=False):
    """Worker function for load_field"""

    global CURRENT_PNAD_DF

    if CURRENT_PNAD_DF is not None:
        return CURRENT_PNAD_DF[field]
    elif use_cache:
        key = (field, year, which)
        cached = get_from_cache(key)
        if cached is MISSING:
            data = _load_field_worker(field, year, which, False)
            return add_to_cache(key, data)
        return pd.Series(cached)
    else:
        key = '%s%s/%s' % (which, year, field)
        try:
            with pnadlib.get_store('pnad') as store:
                return store[key]
        except KeyError:
            pnad = load_pnad(year, which=which)
            data = pnad[field]
            with pnadlib.get_store('pnad', 'w') as store:
                store[key] = data
                if save_pnad:
                    CURRENT_PNAD_DF = pnad
            return data



def load_year(year, which='person'):
    """Return a lazy data frame object that loads the fields for some given
    year on demand

    Example
    -------

    It starts with a data frame which only as indexing information

    >>> df = load_year(2002)
    >>> len(df)
    385431

    But fields are loaded lazily when requested

    >>> df.income.mean(), len(df)
    (629.48045162605774, 385431)

    It is expected that the resulting lazy data frame would accept some fairly
    extensive modifications (such as filtering, reindexing, etc). Only if
    you plan to modify these objects very extensively, it is advisable to make
    a copy.

    >>> df[df.age == 42].income.mean()
    778.27248157248152

    You can always create a regular data frame, just in case

    >>> df.as_dataframe()                                  # doctest: +ELLIPSIS
            income  age
    0          250   58
    1          200   50
    2          200   37
    3          NaN   23
    4          NaN   15
    5          200   50
    ...

    """

    # Loads a small field in order to compute the size of the population
    N = len(load_field('gender', year, which=which))
    return PnadDF(year=year, which=which, size=N)


def load_years(field, years=None, which='person'):
    """Return a DataFrame with the given field evaluated in all specified
    years.

    `years` can be any valid argument for the prepare_years() function.
    """

    df = pd.DataFrame()
    for yy in prepare_years(years):
        df[yy] = load_field(field, yy, which)
    return field


def load_panel(fields, years=None, which='person'):
    """Load a PPanel object that aggregates data from all the given fields in
    all the given years.

    `years` can be any valid argument for the prepare_years() function.
    """

    out = pd.Panel()
    for yy in prepare_years(years):
        out[yy] = load_fields(fields, yy, which)
    return out


def load_dict(fields, years=None, which='person'):
    """Load a PPanel object that aggregates data from all the given fields in
    all the given years.

    `years` can be any valid argument for the prepare_years() function.
    """

    out = PanelDict()
    for yy in prepare_years(years):
        out[yy] = load_fields(fields, yy, which)
    return out


###############################################################################
#                 Remove data from local cache
###############################################################################

def remove_raw(*args, which='person'):
    """Remove the given years from local raw data cache.

    The arguments can be specific years or any input compatible with
    `prepare_years()`"""

    if which == 'all':
        remove_raw(*args, which='person')
        remove_raw(*args, which='household')
        return

    with pnadlib.get_store('raw', 'w') as store:
        for year in prepare_years(*args):
            key = which + str(year)
            if key in store:
                del store[key]


def remove_years(*args, which='person'):
    """Remove the given years from the post-processed pnad cache

    The arguments can be specific years or any input compatible with
    `prepare_years()`"""

    if which == 'all':
        remove_years(*args, which='person')
        remove_years(*args, which='household')
        return

    with pnadlib.get_store('pnad', 'w') as store:
        for year in prepare_years(*args):
            key = which + str(year)
            if key in store:
                del store[key]


def remove_fields(*args, which='person'):
    """Remove all occurences of the given fields from the post-processed pnad
    cache."""

    if which == 'all':
        remove_fields(*args, which='person')
        remove_fields(*args, which='household')
        return

    with pnadlib.get_store('pnad', 'w') as store:
        for year in prepare_years():
            for field in args:
                key = ''.join([which, str(year), '/', field])
                if key in store:
                    del store[key]


def describe_cache(kind='pnad'):
    """Print a list of all keys in the given cache"""

    if kind == 'all':
        print('\n\npnad data\n---------\n')
        describe_cache('pnad')

        print('\n\nraw data\n--------\n')
        describe_cache('raw')

        print('\n\ngroups data\n-----------\n')
        describe_cache('groups')
        return

    with pnadlib.get_store(kind) as D:
        keys = D.keys()
        if keys:
            print('\n'.join(sorted(keys)))
        else:
            print('**empty**')


def add_to_cache(key, value):
    """Adds an item from cache and automatically control cache size

    Example
    -------

    >>> series = load_field('age', 2002) # takes longer
    >>> series = load_field('age', 2002) # very quick
    """

    global CACHE_WEIGHT

    if value is None:
        NULL_FIELDS.add(key)
        return

    # Check if key is on cache to update
    if key in CACHE:
        n, cached = CACHE[key]
        CACHE[key] = n + CACHE_WEIGHT, cached
        return value

    # Check if CACHE has overflown
    if len(CACHE) >= MAX_CACHE_SIZE:
        del_key = min((v, k) for (k, v) in CACHE.items())[1]
        del CACHE[del_key]

    # Reset CACHE_WEIGHT if it is too big
    if CACHE_WEIGHT > 1e10:
        CACHE_WEIGHT = 1
        for k, (n, cached) in CACHE.items():
            CACHE[k] = (n * 1e-6, cached)

    # Add new item to cache
    CACHE_WEIGHT *= 1.05
    CACHE[key] = CACHE_WEIGHT, np.array(value, copy=True)
    return value


def get_from_cache(key):
    """Retrieve an item from cache, or return None, if not present"""

    if key in NULL_FIELDS:
        return None
    out = CACHE.get(key, (0, MISSING))[1]
    if out is MISSING:
        return MISSING
    else:
        return out.copy()


