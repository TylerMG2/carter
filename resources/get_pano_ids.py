import random
from shapely.geometry import Point
from shapely.geometry import Polygon
from geopandas import GeoDataFrame
import pandas as pd
import numpy as np
from math import pi as PI
from math import cos, radians
import os
from aiohttp import ClientSession
from dotenv import load_dotenv
from time import sleep
import asyncio
from asyncio import Queue
load_dotenv()

# Constants
STREETVIEW_SEARCH_URL = "https://maps.googleapis.com/maps/api/streetview/metadata?location={1:},{0:}&key={2:}&radius={3:}&source=outdoor"
SEARCH_RADIUS = 5000
PANORAMAS = 500
METRES_PER_DEGREE = 111000
MIN_STEP = 20
STARTING_COUNTRY = 'PRI'

# Load data
world_map = GeoDataFrame.from_file('./resources/country_shapes.geojson')
country_data = pd.read_csv('./resources/country_data.csv')
panos = pd.read_csv('./resources/panoramas.csv')

# Function to get panos at a lat, long
async def get_closest_pano(session: ClientSession, point: Point, radius: int = SEARCH_RADIUS) -> dict:
    url = STREETVIEW_SEARCH_URL.format(point.x, point.y, os.getenv('STREETVIEW_API_KEY'), radius)
    async with session.get(url) as response:
        if response.status != 200:
            return None
        response = await response.json()
        if response['status'] != 'OK':
            return None
        return response

# Takes a country polygon and bbox and returns a grid of points, their distance from others and step in metres
async def get_grid_points(polygon: Polygon, bbox: tuple, cells: int = 10) -> tuple[list[tuple[Point, Point]], int]:
    minx, miny, maxx, maxy = bbox

    # Calculate the longitude distance in metres
    size_x = maxx - minx # Calculate the longitude distance in degrees
    size_y = maxy - miny # Calculate the latitude distance in degrees
    size_y_metres = size_y * METRES_PER_DEGREE
    step = size_y_metres / cells
    
    # Generate points on grid
    points = []
    for y in range(cells):

        # Loop through the latitude
        lat = miny + (size_y * (y/cells))
        size_x_metres = size_x * METRES_PER_DEGREE * cos(radians(lat))
        long_cells = int(size_x_metres / step)
        for x in range(long_cells):
            
            # Calculate the latitude
            long = minx + (size_x * (x/long_cells))
            point = Point(long, lat)
            if polygon.contains(point):
                points.append((point, Point(size_x/long_cells, size_y/cells)))

    return points, int(step)

# Function to process a specific point
async def process_point(session: ClientSession, point_info: tuple[Point, Point], polygon: Polygon, panos: dict, step):
    point, distances = point_info
    pano = None
    radius = step/2

    # Loop until either no pano is found or a valid pano is found
    while not pano:
        pano = await get_closest_pano(session, point, radius=int(radius))
        if not pano:
            return None
        
        # Check if pano is in the country
        pano_point = Point(pano['location']['lng'], pano['location']['lat'])
        if not polygon.contains(pano_point):
            radius /= 2
            pano = None
        
        # Check if pano is already in the list
        elif pano['pano_id'] in panos:
            return None
    
    # If we found a pano
    if pano:
        panos[pano['pano_id']] = pano
        #print(f"Found {len(panos.keys())} panos")
        return (point.x-distances.x/2, point.y-distances.y/2, point.x+distances.x/2, point.y+distances.y/2)

# Takes a country polygon, bbox and panorama dictionary
async def get_panos_in_country(polygon: Polygon, bbox: tuple, panos: dict) -> None:
    queue = Queue()
    current_depth = 0
    await queue.put((bbox, current_depth))
    
    async with ClientSession() as session:
        while not queue.empty():

            # Get grid points
            bbox, depth = await queue.get()
            points, step = await get_grid_points(polygon, bbox)
            print(step, len(points))

            if depth > 1 and len(panos.keys()) >= PANORAMAS:
                break
            
            if depth > current_depth:

                # Randomize queue
                queue_list = list(queue._queue)
                random.shuffle(queue_list)
                for item in queue_list:
                    await queue.put(item)


                # If we have enough panos
                if len(panos.keys()) >= PANORAMAS or step <= MIN_STEP:
                    break
                
                current_depth = depth
            
            # Process each point
            batch = []
            tasks = []
            for point in points:
                #print(f'Point in queue: {point}')
                task = asyncio.create_task(process_point(session, point, polygon, panos, step))
                tasks.append(task)
                if len(tasks) >= 4:
                    # Wait for the first batch of 4 tasks to complete before continuing
                    batch += await asyncio.gather(*tasks)
                    tasks = []
            
            # Wait for the last batch of tasks to complete
            batch += await asyncio.gather(*tasks)

            # Queue the next set of points
            for new_bbox in batch:
                if new_bbox:
                    await queue.put((new_bbox, depth+1))

# Get panos in all countries
async def get_panos_in_all_countries(panos: pd.DataFrame, starting_country: str = None) -> None:
    for country in country_data['alpha-3']:

        # Skip until we get to the starting country
        if starting_country and country != starting_country:
            continue

        starting_country = None
        print(f"Getting panos in {country}")
        
        # Get the country poly
        country_poly = world_map[world_map['iso3'] == country].geometry.values[0]

        # Get panos in the country
        country_panos = {}
        await get_panos_in_country(country_poly, country_poly.bounds, country_panos)
        
        # Add to panos
        for pano in country_panos.values():
            new_pano = pd.DataFrame([[
                pano['pano_id'],
                pano['location']['lat'],
                pano['location']['lng'],
                pano['date'],
                pano['copyright'],
                country
            ]], columns=['pano_id', 'lat', 'long', 'date', 'copyright', 'country'])
            panos = pd.concat([panos, new_pano])
        
        # Remove duplicates
        panos.drop_duplicates(subset='pano_id', inplace=True)

        # Save
        panos.to_csv('./resources/panoramas.csv', index=False)

# Run the function
asyncio.run(get_panos_in_all_countries(panos, starting_country=STARTING_COUNTRY))
