
# Url for panorama image
PANORAMA_URL = "https://streetviewpixels-pa.googleapis.com/v1/thumbnail?panoid={0:}&cb_client=maps_sv.tactile.gps&w=1280&h=720&yaw={1:}&pitch=0&thumbfov=120"
STREETVIEW_URL = "http://maps.google.com/maps?q=&layer=c&cbll={0:},{1:}&cbp=11,{2:},0,0,0"

# Class for storing and handling panorama images
class Panorama:

    def __init__(self, pano_id: str, lat: float, long: float, date: str, country: str, iso2: str) -> None:
        self.pano_id = pano_id
        self.lat = lat
        self.long = long
        self.date = date
        self.country = country
        self.iso2 = iso2

    # Method to get the panorama image url
    def get_image_url(self, yaw: int = 0) -> str:
        return PANORAMA_URL.format(self.pano_id, yaw)

    # Method to get the streetview url
    def get_streetview_url(self, yaw: int = 0) -> str:
        return STREETVIEW_URL.format(self.lat, self.long, yaw)