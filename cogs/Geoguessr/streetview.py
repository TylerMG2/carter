import requests
from .panorama import Panorama
from shapely.geometry import Point
from shapely.geometry import Polygon, MultiPolygon
from geopandas import GeoDataFrame
from geopandas import GeoSeries
import os
from dotenv import load_dotenv
load_dotenv()

# Streetview API urls
STREETVIEW_SEARCH_URL = "https://maps.googleapis.com/maps/api/streetview/metadata?location={0:},{1:}&key={2:}&radius=1000"

# Load world_map
#world_map = GeoDataFrame.from_file('./world_map.shp')
#print(world_map)

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

# Function to check if a point is within a polygon
def point_in_polygon(point: Point, polygon: Polygon | MultiPolygon) -> bool:
    return point.within(polygon)

