===========
Python PNAD
===========

This package exposes microdata about the Brazilian PNAD survey using a convenient Python
interface. Data are exposed as DataFrames using the load_person, or load_household functions:

>>> import pnad
>>> df = pnad.load_person(2012, ['income', 'gender', 'race', 'age', 'education_years'])
>>> data = df[df.age >= 18]
>>> [['income', 'race']].groupby('race').mean()
