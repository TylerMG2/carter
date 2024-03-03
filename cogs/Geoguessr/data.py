# data.py
import pandas as pd

# Load Data
countries = pd.read_csv('./resources/country_data.csv')
PANORAMAS = pd.read_csv('./resources/panoramas.csv')

# Drop alpha-3 column
countries.drop(columns=['alpha-3'], inplace=True)

# Create a dictionary of country data
COUNTRIES = countries.set_index('alpha-2').T.to_dict()
