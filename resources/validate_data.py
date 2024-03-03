import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon

# Load Panoramas
panoramas = pd.read_csv('./resources/panoramas.csv')

# Load map
world = gpd.read_file('./resources/country_shapes.geojson')

# Loop over each panorama and validate its within the country
for index, row in panoramas.iterrows():
    country = row['country']
    pano_point = Point(row['long'], row['lat'])
    country_poly : Polygon = world[world['iso3'] == country].geometry.iloc[0]
    
    # Check that the panorama is in the country
    if not country_poly.contains(pano_point):
        print(f'Panorama {row["pano_id"]} is not in {country}')
        
        # Remove the panorama from the dataframe
        panoramas.drop(index, inplace=True)

# Save the dataframe
panoramas.to_csv('./resources/panoramas.csv', index=False)