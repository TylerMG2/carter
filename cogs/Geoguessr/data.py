# data.py
import pandas as pd
import random
from .panorama import Panorama

# Load Data
countries = pd.read_csv('./resources/country_data.csv')
PANORAMAS = pd.read_csv('./resources/panoramas.csv')

# Drop alpha-3 column
countries.drop(columns=['alpha-3'], inplace=True)

# Create a dictionary of country data
COUNTRIES = {}
for index, row in countries.iterrows():
    COUNTRIES[row['alpha-2']] = row['name']

# Function to pick a random country and panorama
def get_random_pano() -> Panorama:
    country_iso2 = random.choice(list(COUNTRIES.keys()))
    pano_info = PANORAMAS[PANORAMAS['country'] == country_iso2].sample().iloc[0]
    return Panorama(pano_info['pano_id'], pano_info['lat'], pano_info['long'], pano_info['date'], COUNTRIES[country_iso2], country_iso2)