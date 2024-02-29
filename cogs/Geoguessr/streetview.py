import requests
from .panorama import Panorama
from shapely.geometry import Point
from shapely.geometry import Polygon, MultiPolygon
from geopandas import GeoDataFrame
import asyncio
import os
import random
from dotenv import load_dotenv
load_dotenv()

# Streetview API urls
STREETVIEW_SEARCH_URL = "https://maps.googleapis.com/maps/api/streetview/metadata?location={0:},{1:}&key={2:}&radius=30000"

# Load world_map
world_map = GeoDataFrame.from_file('./resources/country_shapes.geojson')

# Function to get panos at a lat, long
async def get_closest_pano(lat, long) -> Panorama:

    # Make request
    url = STREETVIEW_SEARCH_URL.format(lat, long, os.getenv('STREETVIEW_API_KEY'))
    response = requests.get(url)

    # Check if request was successful
    if not response.ok:
        return None

    # Check status
    response = response.json()
    if response['status'] != 'OK':
        return None
    
    # Return pano
    location = response['location']
    return Panorama(response['pano_id'], location["lat"], location["lng"], response['date'])

# Generate a random point within a polygon
def random_point_in_polygon(polygon: Polygon | MultiPolygon) -> Point:
    minx, miny, maxx, maxy = polygon.bounds
    while True:
        point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(point):
            return point

# Function to get a panorama within a given country
async def get_pano_in_country(country: str) -> Panorama:

    # Check if country is in world_map
    if country not in world_map['iso3'].values:
        raise ValueError('Country not found in world_map')

    country = world_map[world_map['iso3'] == country]
    country_poly : Polygon | MultiPolygon = country.geometry.iloc[0]
    
    # Run until we find a pano
    pano = None
    while not pano:

        # Get point within the country
        point = random_point_in_polygon(country_poly)
        pano = await get_closest_pano(point.y, point.x)

        # Time out for a bit
        await asyncio.sleep(0.2)

        # Check that panorama is within the country
        if pano is not None:
            pano_point = Point(pano.long, pano.lat)
            if not pano_point.intersects(country_poly):
                pano = None
    
    return pano