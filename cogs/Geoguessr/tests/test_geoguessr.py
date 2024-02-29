import pytest
from shapely.geometry import Point, Polygon, MultiPolygon
from geopandas import GeoSeries
from ..panorama import Panorama
from ..streetview import get_closest_pano, point_in_polygon

KNOWN_PANO_LOCATION = (40.7128, -74.0060)
POLYGON = Polygon(((0, 0), (1, 0), (1, 1), (0, 1)))

# Test that the get_closest_pano function returns a Panorama object
@pytest.mark.asyncio
async def test_get_closest_pano():
    pano = await get_closest_pano(*KNOWN_PANO_LOCATION)
    assert pano is not None
    assert isinstance(pano, Panorama)
    assert pano.pano_id is not None
    assert pano.lat is not None
    assert pano.long is not None
    assert pano.date is not None

# Test that the get_closest_pano function returns None when given invalid lat, long
@pytest.mark.asyncio
async def test_get_closest_pano_invalid():
    pano = await get_closest_pano(0.0, 0.0)
    assert pano is None

# Test that get_closet_pano function returns a panorama object close to the given lat, long
@pytest.mark.asyncio
async def test_get_closest_pano_close():
    pano = await get_closest_pano(*KNOWN_PANO_LOCATION)
    assert pano is not None
    assert abs(pano.lat - KNOWN_PANO_LOCATION[0]) < 0.1
    assert abs(pano.long - KNOWN_PANO_LOCATION[1]) < 0.1

## Tests for point_in_polygon(point: Point, polygon: Polygon | MultiPolygon)
    
# Test that point_in_polygon returns True when a point is within a polygon
def test_point_in_polygon_valid():
    point = Point(0, 0)
    assert point_in_polygon(point, POLYGON)

# Test that point_in_polygon returns False when a point is not within a polygon
def test_point_in_polygon_invalid():
    point = Point(2, 2)
    assert not point_in_polygon(point, POLYGON)

# Test with a MultiPolygon
def test_point_in_multipolygon():
    point = Point(0, 0)
    multipolygon = MultiPolygon([POLYGON])
    assert point_in_polygon(point, multipolygon)

## Tests for get_point_in_polygon(polygon: Polygon | MultiPolygon)

# Test that get_point_in_polygon returns a Point object
def test_get_point_in_polygon():
    point = get_point_in_polygon(POLYGON)
    assert point is not None
    assert isinstance(point, Point)
    assert point.x is not None
    assert point.y is not None

# Test that get_point_in_polygon returns a point within the polygon
def test_get_point_in_polygon_valid():
    point = get_point_in_polygon(POLYGON)
    assert point_in_polygon(point, POLYGON)

## Tests for get_pano(country: str)
    
# Test that get_pano returns a Panorama object
@pytest.mark.asyncio
async def test_get_pano():
    pano = await get_pano("us")
    assert pano is not None
    assert isinstance(pano, Panorama)
    assert pano.pano_id is not None
    assert pano.lat is not None
    assert pano.long is not None
    assert pano.date is not None