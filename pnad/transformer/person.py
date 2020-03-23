import numpy as np

from ..utils import select_by_year
from .base import Transformer, Field, function
from .economy import OccupationDataMixin, IncomeDataMixin
from ..enums import State, Race, Gender


class SocialDataMixin:
    """
    Basic social variables.
    """
    year: int

    @function()
    def gender_id(self, df):
        """Gender id. Uses the same values adopted in the Gender enum."""

        year = self.year
        gender = np.ones(len(df), dtype=np.uint8)
        has_undefined = False

        if year == 1976:
            males = df.V2103 == 1
            females = df.V2103 == 2

        elif year == 1977:
            males = df.V16 == 1
            females = df.V16 == 2

        elif 1978 <= year <= 1979:
            males = df.V2203 == 1
            females = df.V2203 == 2

        elif 1981 <= year <= 1990:
            males = df.V303 == 1
            females = df.V303 == 3

        elif year >= 1992:
            males = df.V0302 == 2
            females = df.V0302 == 4

        else:
            raise ValueError('cannot compute gender for year %s' % year)

        if not has_undefined:
            assert (males | females).all()

        np.putmask(gender, gender, Gender.UNKNOWN)
        np.putmask(gender, males, Gender.MALE)
        np.putmask(gender, females, Gender.FEMALE)
        return gender

    @function()
    def gender(self, df):
        """Categorical gender data."""

        return Gender.categorical(df.gender_id)

    @function()
    def age(self, df):
        """Age of each individual"""

        year = self.year
        age = np.ones(len(df), dtype=np.int8)

        if year == 1976:
            age = df.V2105
        elif year == 1977:
            # It seems that small values (<100) are estimated age, while
            # large values >800 are the last tree digits of the year the
            # person was born
            age = np.array(df.V22)
            np.putmask(age, age > 800, 1977 - (age + 1000))

        elif year < 1981:
            age = df.V2805
        elif year < 1992:
            age = df.V805
        elif year >= 1992:
            age = df.V8005

        # Prepare to return
        age = np.array(age, dtype=np.float16)
        for missing in [999]:
            np.putmask(age, age == missing, float('nan'))
        return age

    @function()
    def race_id(self, df):
        """Race as described in the Race enum."""

        year = self.year

        # Create masks
        indigenous = np.zeros(len(df), dtype=bool)
        if year == 1976:
            race = np.array(df['V303'], dtype=int)
            white = race == 1
            black = race == 2
            asian = race == 3
            brown = race == 4
            # empty = race == 5, but there are some outliers: 6, 8

        elif year in [1982, 1984, 1985, 1986]:
            key = {
                1982: 'V6302',  # complete
                1984: 'V2301',  # fertility survey, only women
                1985: 'V2301',  # minors supplement, only ages in [0, 17]
                1986: 'V2201',  # health care supplement - random respondents
            }[year]
            race = np.array(df[key], dtype=int)
            white = race == 1
            black = race == 3
            brown = race == 5
            asian = race == 7
            # empty = (race == 9) | (race == 0) | (race == -2)

        elif 1987 <= year <= 1990:
            race = np.array(df['V304'], dtype=int)
            white = race == 2
            black = race == 4
            brown = race == 6
            asian = race == 8
            # empty = (race == 9) | (race == 7)

        elif year >= 1992:
            race = np.array(df['V0404'], dtype=int)
            indigenous = race == 0
            white = race == 2
            black = race == 4
            asian = race == 6
            brown = race == 8
            # empty = race == 9

        else:
            return None

        # Save correct values
        race = np.zeros(len(race), dtype=np.uint8)  # Race.unknown
        np.putmask(race, indigenous, Race.INDIGENOUS)
        np.putmask(race, white, Race.WHITE)
        np.putmask(race, black, Race.BLACK)
        np.putmask(race, asian, Race.ASIAN)
        np.putmask(race, brown, Race.BROWN)
        return race

    def race(self, df):
        """Race as categorical data."""
        race = df.race_id
        return race if race is None else Race.categorical(race)

    @function()
    def education_years(self, df):
        """
        Estimated number of years required to reach the respondent education
        level.
        """

        year = self.year

        if year == 1977:
            y_edu = np.array(df.V136, dtype=float)
            y_edu[y_edu == 9] = 10.0
            y_edu[y_edu == 10] = 12.0

        elif year < 1992:
            field = select_by_year(year, {
                (1976, 1978): 'V2511',
                1979: 'V2507',
                (1981, ...): 'V318',
            })
            data = np.array(df[field])
            y_edu = np.array(data - 1, dtype=float)

            # Field (10 - 1) => 9 means 9 to 11 yrs
            # Field (11 - 1) => 10 means 12 or more yrs
            y_edu[data == 10] = 10.0
            y_edu[data == 11] = 12.0
            y_edu[data >= 12] = float('nan')

        else:
            field = select_by_year(year, {
                (..., 2006): 'V4703',
                (2007, ...): 'V4803',
            })
            y_edu = np.array(df[field] - 1, dtype=float)
            y_edu[y_edu >= 16] = float('nan')

        y_edu[y_edu < 0] = float('nan')
        return y_edu


class GeographicDataMixin:
    year: int

    @function()
    def state(self, df):
        """State in which the respondent lives"""

        s = State
        year = self.year
        D0 = {
            11: s.RO, 12: s.AC, 13: s.AM, 14: s.RR, 15: s.PA, 16: s.AP, 17: s.TO,
            21: s.MA, 22: s.PI, 23: s.CE, 24: s.RN, 25: s.PB, 26: s.PE, 27: s.AL,
            28: s.SE, 29: s.BA, 31: s.MG, 32: s.ES, 33: s.RJ, 35: s.SP, 41: s.PR,
            42: s.SC, 43: s.RS, 50: s.MS, 51: s.MT, 52: s.GO, 53: s.DF
        }
        D1 = {
            11: s.RJ, 12: s.RJ, 13: s.RJ, 14: s.RJ, 20: s.SP, 21: s.SP, 22: s.SP,
            23: s.SP, 24: s.SP, 25: s.SP, 26: s.SP, 27: s.SP, 28: s.SP, 29: s.SP,
            30: s.PR, 31: s.PR, 32: s.SC, 33: s.RS, 34: s.RS, 35: s.RS, 37: s.PR,
            41: s.MG, 42: s.MG, 43: s.ES, 51: s.MA, 52: s.PI, 53: s.CE, 54: s.RN,
            55: s.PB, 56: s.PE, 57: s.AL, 58: s.SE, 59: s.BA, 60: s.BA, 61: s.DF,
            71: s.RO, 72: s.AC, 73: s.AM, 74: s.RR, 75: s.PA, 76: s.AP, 81: s.MS,
            82: s.MT, 83: s.GO
        }
        D2 = {
            11: s.RJ, 21: s.SP, 31: s.PR, 32: s.SC, 33: s.RS, 41: s.MG, 43: s.ES,
            51: s.MA, 52: s.PI, 53: s.CE, 54: s.RN, 55: s.PB, 56: s.PE, 57: s.AL,
            58: s.SE, 59: s.BA, 61: s.DF, 71: s.RN, 72: s.AC, 73: s.AM, 74: s.RR,
            75: s.PA, 76: s.AP, 77: s.MT, 78: s.GO
        }

        # Make conversion
        def convert(data, map):
            out = np.zeros(len(data), dtype=np.uint32)
            mask = np.zeros(len(data), dtype=bool)

            for prev, final in map.items():
                mask_k = (data == prev)
                mask |= mask_k
                out[mask_k] = final

            if not mask.all():
                count(data[~mask])
                raise ValueError('missing states!', data[~mask])

            return out

        if year >= 1992:
            return convert(np.array(df.UF), D0)
        elif year > 1979:
            return convert(np.array(df.V10), D1)
        elif year == 1979:
            return convert(np.array(df.V17), D2)
        elif year == 1978:
            return convert(np.array(df.V6), D2)
        elif year == 1977:
            return convert(np.array(df.V2), D2)
        elif year == 1976:
            return convert(np.array(df.V3), D2)
        else:
            raise ValueError('invalid year', year)


class SuplementMixin:
    """
    Columns created for specific PNAD supplements.
    """
    year: int

    # TODO:
    #  - V582, yrs (1980-1990: is this capital gain (?)
    #    Descr: 582 VALOR OUTRAS               181   9        N

    @function()
    def number_of_children(self, df):
        """Number of children born alive"""

        if self.year == 1984:
            data = np.array(df.V2310, dtype=float)
            has_data = np.array(df.V2309, dtype=np.int8)
            data[(has_data == 9) | (has_data == -1)] = float('nan')
            data[(data == 99) | (data == -1)] = float('nan')
            data[has_data == 4] = 0.0
            return data


class PersonTransformer(SocialDataMixin, GeographicDataMixin, SuplementMixin,
                        OccupationDataMixin, IncomeDataMixin, Transformer):
    """
    Transform raw Person data Access data pertaining to individuals in the PNAD survey.
    """

    #
    # Basic survey data
    #
    weight = Field({
        (1992, ...): 'V4729',
        1990: 'V3091',
        (1981, 1989): 'V9991',
        1979: 'V2999',
        1978: 'V2997',
        1977: 'V187',
        1976: 'V2997',
    }, descr='')
    weight_family = Field({
        (1992, ...): 'V4732',
        (1981, 1990): 'V9971',
        1979: 'V2998',
        1978: 'V2996',
    }, descr='')
    weight_househould = Field({
        (1992, ...): 'V4732',
        1990: 'V1091',
        (1981, 1989): 'V9981',
        1979: 'V1997',
        1978: 'V1995',
        1977: 'V187',
        1976: 'V1997',
    }, descr='')
