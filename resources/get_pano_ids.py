import requests
from shapely.geometry import Point
from shapely.geometry import Polygon
from geopandas import GeoDataFrame
import pandas as pd
import numpy as np
from math import pi as PI
from math import cos
import os
import random
from dotenv import load_dotenv
from time import sleep
import asyncio
load_dotenv()

# Streetview API urls
STREETVIEW_SEARCH_URL = "https://maps.googleapis.com/maps/api/streetview/metadata?location={0:},{1:}&key={2:}&radius={3:}&source=outdoor"
SEARCH_RADIUS = 5000
PANORAMAS = 100

# Load world_map
world_map = GeoDataFrame.from_file('./resources/country_shapes.geojson')
country_data = pd.read_csv('./resources/country_data.csv')

# Load panos csv
panos = pd.read_csv('./resources/panoramas.csv')

# Function to get panos at a lat, long
async def get_closest_pano(lat: float, long: float, radius: int = SEARCH_RADIUS) -> dict:

    # Make request
    url = STREETVIEW_SEARCH_URL.format(lat, long, os.getenv('STREETVIEW_API_KEY'), radius)
    response = requests.get(url)

    # Check if request was successful
    if not response.ok:
        return None

    # Check status
    response = response.json()
    if response['status'] != 'OK':
        return None
    
    return response

# Generate a random point within a polygon
async def random_point_in_polygon(polygon: Polygon) -> Point:
    minx, miny, maxx, maxy = polygon.bounds
    while True:
        point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(point):
            return point

# Function to get adjacent lat, long
async def adjacent_lat_long(lat: float, long: float, direction: tuple, step: float) -> (float, float):
    earth_radius = 6378137
    new_lat = lat + (direction[0] * step / earth_radius) * (180 / PI)
    new_long = long + (direction[1] * step / earth_radius) * (180 / PI) / cos(lat * PI)
    return new_lat, new_long

# Function to get next possible directions
async def get_next_directions(prev_direction: tuple) -> set:

    all_directions = {(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)}
    if prev_direction == (0, 0):
        return all_directions

    next_directions = set()
    next_directions.add(prev_direction) 

    # If its a diagonal
    dx, dy = prev_direction
    if dx != 0 and dy != 0:
        next_directions.update({(dx, -dy), (-dx, dy), (0, dy), (dx, 0)})
    elif dx == 0:
        next_directions.update({(1, dy), (-1, dy)})
    else:
        next_directions.update({(dx, 1), (dx, -1)})
    return next_directions

# Function to search in a grid
async def search_grid(lat: float, long: float, direction: tuple, step: float, found: set) -> dict:

    # Current lat long
    lat, long = await adjacent_lat_long(lat, long, direction, step)

    # Get pano at this location
    pano = await get_closest_pano(lat, long, radius=15)

    # Base cases
    # No pano found
    if not pano:
        return
    
    # Check if pano already found
    if pano['pano_id'] in found:
        return

    # Add to found
    found.add(pano['pano_id'])
    next_directions = await get_next_directions(direction)
    print(f"Found: {len(found)} panoramas")

    # Search in all directions
    for next_direction in next_directions:
        await search_grid(lat, long, next_direction, step, found)

found = set()
asyncio.run(search_grid(18.33838677387596,-64.9444448532636, (0, 0), 20, found))

# Function to get a panorama within a given country
def get_pano_in_country(country: str) -> dict:

    country = world_map[world_map['iso3'] == country]
    country_poly : Polygon = country.geometry.iloc[0]

    # Get country bounds
    minx, miny, maxx, maxy = country_poly.bounds
    max_size = max(maxx - minx, maxy - miny)

    # Set search radius scale
    search_scale = max(max_size / 5, 0.1)

    # Generate random points until one is found within the country
    point = random_point_in_polygon(country_poly)
    pano = get_closest_pano(point.y, point.x, radius=int(SEARCH_RADIUS*search_scale))

    # If we found a pano
    if pano:

        # Check if panorama is in the country
        pano_point = Point(pano['location']['lng'], pano['location']['lat'])
        if country_poly.contains(pano_point):
            return pano

    return None



# Loop through all the countries and get 10 panos for each
# for country in country_data['alpha-3']:
#     print(f"Getting panos for {country}")
    
#     count = 0
#     while count < PANORAMAS:
#         try:
#             pano = get_pano_in_country(country)
#         except:
#             sleep(10)
#         if pano is not None:

#             # Check if pano already exists
#             if pano['pano_id'] in panos['pano_id'].values:
#                 print(f"Panorama {pano['pano_id']} already exists")
#                 continue

#             # Build new row
#             new_pano = {
#                 'pano_id': pano['pano_id'],
#                 'lat': pano['location']['lat'],
#                 'long': pano['location']['lng'],
#                 'date': pano['date'],
#                 'copyright': pano['copyright'],
#                 'country': country
#             }

#             # Add to panos
#             panos = pd.concat([panos, pd.DataFrame([new_pano])], ignore_index=True)
#             count += 1
#         sleep(0.02)

#     # Save panos
#     panos.to_csv('./resources/panoramas.csv', index=False)