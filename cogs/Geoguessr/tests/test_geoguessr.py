import pytest
from ..panorama import Panorama
from ..streetview import get_closest_pano

KNOWN_PANO_LOCATION = (40.7128, -74.0060)

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