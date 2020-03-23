import enum
import pandas as pd
import numpy as np


def with_category(cls):
    """
    Add methods for conversion to Categorical data.
    """
    items = [(x.name, x.value) for x in cls if bin(x.value).count('1') <= 1]
    items.sort(key=lambda x: x[1])
    to_cat = {y: x for x, y in items}
    from_cat = dict(items)

    cls.dtype = pd.CategoricalDtype([x for x, y in items])
    cls.to_category = lambda self: to_cat.get(self.value)
    cls.from_category = staticmethod(lambda cat: cls(from_cat[cat]))

    @classmethod
    def categorical(cls, n):
        if hasattr(n, 'apply'):
            default = cls.UNKNOWN
            df = n.apply(lambda x: to_cat.get(x, default))
            return df.astype(cls.dtype)
        elif isinstance(n, (np.ndarray, list, tuple)):
            return cls.categorical(pd.Series(n))
        return cls(n).to_category()

    cls.categorical = categorical
    return cls


@with_category
class Gender(enum.IntFlag):
    """
    Gender enumeration.
    """

    UNKNOWN = 0b000
    MALE = 0b001
    FEMALE = 0b010
    OTHER = 0b100
    NON_MALE = FEMALE | OTHER
    NON_FEMALE = MALE | OTHER
    NON_UNDEFINED = MALE | FEMALE
    KNOWN = MALE | FEMALE | OTHER


@with_category
class Race(enum.IntFlag):
    UNKNOWN = 0b00000
    ASIAN = 0b00001
    BLACK = 0b00010
    BROWN = 0b00100
    INDIGENOUS = 0b01000
    WHITE = 0b10000

    KNOWN = ASIAN | BLACK | BROWN | INDIGENOUS | WHITE
    COLORED = BLACK | BROWN | INDIGENOUS
    LIGHT = WHITE | ASIAN
    DARK = BLACK | BROWN

    NON_ASIAN = KNOWN & (~ASIAN)
    NON_BLACK = KNOWN & (~BLACK)
    NON_BROWN = KNOWN & (~BROWN)
    NON_INDIGENOUS = KNOWN & (~INDIGENOUS)
    NON_WHITE = KNOWN & (~WHITE)


@with_category
class State(enum.IntFlag):
    UNKNOWN = 0b0

    # Sul
    RS = 0b1001
    SC = 0b1010
    PR = 0b1100

    # Sudeste

    SP = 0b10001 << 4
    RJ = 0b10010 << 4
    MG = 0b10100 << 4
    ES = 0b11000 << 4

    # Centro-oeste
    MS = 0b10001 << 9
    MT = 0b10010 << 9
    GO = 0b10100 << 9
    DF = 0b11000 << 9

    # Nordeste
    BA = 0b1000000001 << 14
    AL = 0b1000000010 << 14
    SE = 0b1000000100 << 14
    PE = 0b1000001000 << 14
    PB = 0b1000010000 << 14
    RN = 0b1000100000 << 14
    CE = 0b1001000000 << 14
    PI = 0b1010000000 << 14
    MA = 0b1100000000 << 14

    # Norte
    TO = 0b10000001 << 24
    PA = 0b10000010 << 24
    AP = 0b10000100 << 24
    AM = 0b10001000 << 24
    RR = 0b10010000 << 24
    AC = 0b10100000 << 24
    RO = 0b11000000 << 24

    # Regions
    SUL = 0b1000
    SUDESTE = 0b10000 << 4
    CENTRO_OESTE = 0b10000 << 9
    NORDESTE = 0b10000 << 14
    NORTE = 0b10000 << 24

    # Masks
    ANY_REGION = SUL | SUDESTE | CENTRO_OESTE | NORTE | NORDESTE
    SUL_SUDESTE = SUL | SUDESTE
    NORTE_NORDESTE = NORTE | NORDESTE
    NON_SUL = ANY_REGION & ~SUL
    NON_SUDESTE = ANY_REGION & ~SUDESTE
    NON_CENTRO_OESTE = ANY_REGION & ~CENTRO_OESTE
    NON_NORDESTE = ANY_REGION & ~NORDESTE
    NON_NORTE = ANY_REGION & ~NORTE

    @property
    def verbose_name(self):
        if self in STATE_NAMES:
            return STATE_NAMES[self]
        return self.name


STATE_NAMES = {
    # Região norte
    State.RO: 'Rondônia', State.AC: 'Acre', State.AM: 'Amazonas', State.RR: 'Roraima',
    State.PA: 'Pará', State.AP: 'Amapá', State.TO: 'Tocantins',

    # Região nordeste
    State.MA: 'Maranhão', State.PI: 'Piauí', State.CE: 'Ceará',
    State.RN: 'Rio Grande do Norte', State.PB: 'Paraíba', State.PE: 'Pernambuco',
    State.AL: 'Alagoas', State.SE: 'Sergipe', State.BA: 'Bahia',

    # Região sudeste
    State.MG: 'Minas Gerais', State.ES: 'Espírito Santo', State.RJ: 'Rio de Janeiro',
    State.SP: 'São Paulo',

    # Região sul
    State.PR: 'Paraná', State.SC: 'Santa Catarina', State.RS: 'Rio Grande do Sul',

    # Região centro-oeste
    State.MS: 'Mato Grosso do Sul', State.MT: 'Mato Grosso', State.GO: 'Goiás',
    State.DF: 'Distrito Federal',
}

# Generic constants
FIELD_ENUMS = {
    'gender': Gender, 'race': Race, 'state': State,
}
