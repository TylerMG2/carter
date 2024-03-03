# data.py
import pandas as pd

# Load Data
countries = pd.read_csv('./resources/country_data.csv')
PANORAMAS = pd.read_csv('./resources/panoramas.csv')

# Drop alpha-3 column
countries.drop(columns=['alpha-3'], inplace=True)

# Create a dictionary of country data
COUNTRIES = {}
for index, row in countries.iterrows():
    COUNTRIES[row['alpha-2']] = row['name']
