## Load country_data.csv
import pandas as pd
import geopandas as gpd
from ..streetview import get_pano_in_country
import asyncio
import pytest
import requests

# Load country data
country_data = pd.read_csv('./resources/country_data.csv')

# Load world map
world = gpd.read_file('./resources/country_shapes.geojson')

# Test that all the countries in the country_data.csv file are in the world map
def test_country_data():
    for country in country_data['alpha-3']:
        assert country in world['iso3'].values

# Test that get_pano_in_country returns a valid panorama for each country in under 5 seconds
@pytest.mark.asyncio
async def test_get_pano_in_country():
    for country in country_data['alpha-3']:
        try:
            pano = await asyncio.wait_for(get_pano_in_country(country), timeout=5)
            assert pano is not None

            # Check that pano.get_image_url() returns a valid image
            response = requests.get(pano.get_image_url())
            assert response.ok
            assert response.headers['Content-Type'] == 'image/jpeg'

        except asyncio.TimeoutError:
            print(f"Timeout for {country}")
            assert False