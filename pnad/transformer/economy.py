from .base import IncomeField, FunctionField, sum_na, Field


class IncomeDataMixin:
    """
    All income-related variables
    """
    year: int

    #
    # Main job
    #
    income_work_main_money_fixed = IncomeField({
        (1992, ...): 'V9532', (1981, 1990): 'V537', 1979: 'V2318', 1978: 'V2426',
        1977: 'V75', 1976: 'V2308',
    }, descr='Fixed monthly salary')

    income_work_main_money_variable = IncomeField({
        (1981, ...): None,  # do not ask this in recent surveys
        1979: 'V2338', 1978: 'V2446', 1977: 'V76', 1976: 'V2358',
    }, descr='Variable part of monthly salary')

    income_work_main_products = IncomeField({
        (1992, ...): 'V9535', (1981, 1990): 'V538', 1979: 'V2339', 1978: 'V2447',
        1977: 'V77', 1976: 'V2359',
    }, descr='Salary received in products')

    @FunctionField
    def income_work_main_money(self, df):
        """Sum of fixed + variable money income from main job"""

        return sum_na(df.income_work_main_money_variable,
                      df.income_work_main_money_fixed)

    @FunctionField
    def income_work_main(self, df):
        """Total income from main work"""

        # Also computed in PNAD as V4718 (yr > 1992)
        return sum_na(df.income_work_main_money, df.income_work_main_products)

    #
    # Secondary job
    #
    income_work_secondary_money_fixed = IncomeField(
        {(1992, ...): 'V9982', (1980, 1990): None, 1979: 'V2427', (..., 1978): None, },
        descr='Salary of secondary job (fixed part)')

    income_work_secondary_money_variable = IncomeField(
        {(1980, ...): None, 1979: 'V2457', (..., 1978): None, },
        descr='Salary of secondary job (variable)')

    income_work_secondary_products = IncomeField(
        {(1992, ...): 'V9985', (1980, 1990): None, 1979: 'V2458', (..., 1978): None, },
        descr='Salary of secondary job (products)')

    @FunctionField
    def income_work_secondary_money(self, df):
        """Total income from secondary job"""

        return sum_na(df.income_work_secondary_money_fixed,
                      df.income_work_secondary_money_variable)

    @FunctionField
    def income_work_secondary(self, df):
        """Total income from secondary job"""

        return sum_na(df.income_work_secondary_money, df.income_work_secondary_products)

    #
    # Other jobs
    #
    income_work_extra_money_fixed = IncomeField({
        (1992, ...): 'V1022', (1981, 1990): 'V549', 1979: 'V2319', 1978: 'V2428',
        1977: 'V85', 1976: 'V2362',
    }, descr='')

    income_work_extra_money_variable = IncomeField({
        (1992, ...): None, (1981, 1990): None, 1979: 'V2349', 1978: 'V2468', 1977: 'V86',
        1976: None,
    }, descr='')

    income_work_extra_products = IncomeField({
        (1992, ...): 'V1025', (1981, 1990): 'V550', 1979: 'V2350', 1978: 'V2469',
        1977: 'V87', 1976: None,
    }, descr='')

    @FunctionField
    def income_work_extra_money(self, df):
        """Total income from jobs other than primary and secondary"""

        return sum_na(df.income_work_extra_money_fixed,
                      df.income_work_extra_money_variable)

    @FunctionField
    def income_work_extra(self, df):
        """Total income from jobs other than primary and secondary"""

        return sum_na(df.income_work_extra_money, df.income_work_extra_products)

    @FunctionField
    def income_work_other_money(self, df):
        """Total income from jobs other than primary and secondary"""

        return sum_na(df.income_work_extra_money, df.income_work_secondary_money)

    @FunctionField
    def income_work_other_products(self, df):
        """Total income from jobs other than primary and secondary"""

        return sum_na(df.income_work_extra_products, df.income_work_secondary_products)

    @FunctionField
    def income_work_other(self, df):
        """Total income from jobs other than primary and secondary"""

        return sum_na(df.income_work_other_money, df.income_work_other_products)

    @FunctionField
    def income_work_money(self, df):
        """Total income from jobs other than primary and secondary"""

        return sum_na(df.income_work_extra_money, df.income_work_main_money)

    @FunctionField
    def income_work_products(self, df):
        """Total income from jobs other than primary and secondary"""

        return sum_na(df.income_work_extra_products, df.income_work_main_products)

    #
    # Social security
    #
    income_retirement_main = IncomeField({
        (1992, ...): 'V1252', (1981, 1990): 'V578', 1979: 'V2350', 1978: 'V2479',
        1977: 'V90', 1976: 'V2365',
        # actually, this is retirement + pension
    }, descr='')
    income_retirement_other = IncomeField({
        (1992, ...): 'V1258', (..., 1990): None,
    }, descr='')
    income_pension_main = IncomeField({
        (1992, ...): 'V1255', (1981, 1990): 'V579', 1979: None, 1978: 'V2480',
        1977: 'V91', 1976: None,
    }, descr='')

    income_pension_other = IncomeField({
        (1992, ...): 'V1261', (..., 1990): None,
    }, descr='')

    income_permanence_bonus = IncomeField(
        {(1992, ...): 'V1264', (1981, 1990): 'V580', (..., 1979): None},
        descr='Paid to workers that can retire, but decide to continue working', )

    @FunctionField
    def income_pension(self, df):
        return sum_na(df.income_pension_main, df.income_pension_other)

    @FunctionField
    def income_retirement(self, df):
        return sum_na(df.income_retirement_main, df.income_retirement_other)

    @FunctionField
    def income_social(self, df):
        return sum_na(df.income_pension, df.income_retirement,
                      df.income_permanence_bonus)

    #
    # Capital income
    #
    income_rent = IncomeField({
        (1992, ...): 'V1267', (1981, 1990): 'V581', 1979: 'V2363', 1978: 'V2482',
        1977: 'V93', 1976: 'V2363',
    }, descr='')
    income_investments = IncomeField({
        (1992, ...): 'V1273', (..., 1990): None,
        # does it have a better description?
        # OUTR. REC. EMPREG.CAPITA
        1979: 'V2361', 1978: 'V2483', 1977: 'V95', 1976: None,
    }, descr='All sources of financial yield except for rents')

    @FunctionField
    def income_capital(self, df):
        """All sources of capital income"""

        total = sum_na(df.income_rent, df.income_investiments)
        if self.year == 1977:
            sum_na(df.V94, df.V97)
        return total

    # Other income sources ####################################################
    income_other = IncomeField({
        (1992, ...): None, (1981, 1990): 'V582', (1978, 1979): None, 1977: 'V96',
        1976: 'V2366',
    }, descr='')
    income_donation = IncomeField({
        (1992, ...): 'V1270', (1981, 1990): None, 1979: 'V2362', 1978: 'V2481',
        1977: 'V92', 1976: 'V2364',
    }, descr='')

    @FunctionField
    def income_misc(self, df):
        return sum_na(df.income_donation, df.income_other)

    #
    # Total incomes
    #
    @FunctionField
    def income_work(self, df):  # @NoSelf
        """Sum of all income sources due to labor"""

        # Also computed in PNAD as V4719 (yr > 1992)
        total = sum_na(df.income_work_main, df.income_work_other)

        # These are used to quantify total income due to work for people who
        # do not want to declare each job separately
        if self.year > 1992 and 'V7122' in df and 'V7125' in df:
            T = IncomeField.remove_missing
            total = sum_na(total, T(df.V7122), T(df.V7125))

        return total

    @FunctionField
    def income(self, df):
        """Total income of an individual"""

        return sum_na(df.income_work, df.income_social, df.income_capital,
                      df.income_misc)

    #
    # Family and household
    #
    income_household = IncomeField(
        {(1992, ...): 'V4721', (1981, 1990): 'V410', (..., 1979): None, }, descr='')
    income_family = IncomeField(
        {(1992, ...): 'V4722', (1981, 1990): 'V5010', (..., 1979): None, }, descr='')
    income_household_per_capta = IncomeField(
        {(1992, ...): 'V4742', (1981, 1990): None, (..., 1979): None, }, descr='')
    income_family_per_capta = IncomeField(
        {(1992, ...): 'V4750', (1981, 1990): None, (..., 1979): None, }, descr='')


class OccupationDataMixin:
    occupation_week = Field({(1992, ...): 'V9906', (..., 1990): 'V503', }, descr='Occupation at the week the survey was taken')
    occupation_year = Field({(1992, ...): 'V9971', (..., 1990): None, }, descr='')
    occupation_secondary = Field({(1992, ...): 'V9990', (..., 1990): None, }, descr='')
    occupation_previous = Field({(1992, ...): 'V9910', (..., 1990): None, }, descr='')
    occupation_first = Field({(1992, ...): 'V1298', (..., 1990): None, }, descr='')
    occupation_father = Field({(1992, ...): 'V1293', (..., 1990): None, }, descr='')
    occupation_father_previous = Field({(1992, ...): 'V1258', (..., 1990): None, },
                                       descr='')
    is_occupied = Field({(1992, ...): 'V4705', (..., 1990): None, }, descr='')
    is_active = Field({(1992, ...): 'V4704', (..., 1990): None, }, descr='')
    work_duration = Field({(1992, ...): 'V4707', (..., 1990): None, }, descr='')

    @FunctionField
    def occupation(self, df):
        return df.occupation_week  # TODO: improve this!
