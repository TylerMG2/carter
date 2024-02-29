import requests
from .panorama import Panorama
import os
from dotenv import load_dotenv
load_dotenv()

# Streetview API urls
STREETVIEW_SEARCH_URL = "https://maps.googleapis.com/maps/api/streetview/metadata?location={0:},{1:}&key={2:}&radius=1000"

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

