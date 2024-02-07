from timezonefinder import TimezoneFinder

def lat_lon_to_timezone(coords: list[float, float]) -> str:
    tf = TimezoneFinder()
    tz: str = tf.timezone_at(lat=coords[0], lng=coords[1])
    return tz