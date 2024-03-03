
# Url for panorama image
PANORAMA_URL = "https://streetviewpixels-pa.googleapis.com/v1/thumbnail?panoid={0:}&cb_client=maps_sv.tactile.gps&w=1280&h=720&yaw={1:}&pitch=0&thumbfov=120"
UNOFFICIAL_PANORAMA_URL = "https://lh5.googleusercontent.com/p/{0:}=w1280-h720-k-no-pi0-ya{1:}-ro9.544053-fo120"

# Class for storing and handling panorama images
class Panorama:

    def __init__(self, pano_id: str, lat: float, long: float, date: str, official: bool) -> None:
        self.pano_id = pano_id
        self.lat = lat
        self.long = long
        self.date = date
        self.official = official

    # Method to get the panorama image url
    def get_image_url(self, yaw: int = 0) -> str:
        if self.official:
            return PANORAMA_URL.format(self.pano_id, yaw)
        else:
            return UNOFFICIAL_PANORAMA_URL.format(self.pano_id, yaw)