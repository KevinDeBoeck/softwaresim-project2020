import math
from math import sin, cos, sqrt, atan2, radians

import model.GlobalVars as Config


def get_distance(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def convert_and_normalize_coordinates(longitude, latitude):
    """Return geocentric (Cartesian) Coordinates x, y, z corresponding to
    the geodetic coordinates given by latitude and longitude (in
    degrees) and height above ellipsoid. The ellipsoid must be
    specified by a pair (semi-major axis, reciprocal flattening).
    """

    # Ellipsoid parameters: semi major axis in metres, reciprocal flattening.
    GRS80 = 6378137, 298.257222100882711
    WGS84 = 6378137, 298.257223563
    height = 0

    ellipsoid = WGS84

    phi = radians(latitude)
    lambdaa = radians(longitude)
    sin_phi = sin(phi)
    a, rf = ellipsoid  # semi-major axis, reciprocal flattening
    e2 = 1 - (1 - 1 / rf) ** 2  # eccentricity squared
    n = a / sqrt(1 - e2 * sin_phi ** 2)  # prime vertical radius
    r = (n + height) * cos(phi)  # perpendicular distance from z axis
    x = r * cos(lambdaa)
    y = r * sin(lambdaa)
    z = (n * (1 - e2) + height) * sin_phi

    return x, y


def normalize(x, y):
    """ Normalize the coordinates to fit in the pane"""
    nodes_width = Config.node_x_max - Config.node_x_min
    nodes_height = Config.node_y_max - Config.node_y_min

    x_coordinate_unit = Config.screen_x_width / nodes_width
    y_coordinate_unit = Config.screen_y_width / nodes_height

    # Determine real x and y pos
    x_norm = (x - Config.node_x_min) * x_coordinate_unit + Config.screen_x_min
    y_norm = (y - Config.node_y_min) * y_coordinate_unit + Config.screen_y_min

    return x_norm, y_norm
