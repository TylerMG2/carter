## Load country_data.csv
import pandas as pd
import geopandas as gpd
import pytest
from ..data import COUNTRIES, PANORAMAS

# Load world map
world = gpd.read_file('./resources/country_shapes.geojson')

# Test that all the countries in the country_data.csv file are in the world map
def test_country_data():
    for country in COUNTRIES['alpha-3']:
        assert country in world['iso3'].values

# Test that all countries have at least one panorama
def test_country_panos():
    for country in COUNTRIES['alpha-2']:
        assert PANORAMAS[PANORAMAS['country'] == country].shape[0] > 0

# Test get_pano_in_country for each country
# @pytest.mark.asyncio
# async def test_get_pano_in_country():
#     for country in country_data['alpha-3']:
#         pano = await get_pano_in_country(country)
#         assert pano
#         assert pano.lat
#         assert pano.long

#         # Check that the panorama is in the country
#         country_poly:Polygon = world[world['iso3'] == country].geometry.iloc[0]
#         pano_point = Point(pano.long, pano.lat)
#         assert country_poly.contains(pano_point)

# # Test get_pano_in_country for a country that doesn't exist
# @pytest.mark.asyncio
# async def test_get_pano_in_country_bad_country():
#     with pytest.raises(ValueError):
#         await get_pano_in_country('AAA')

# Test 