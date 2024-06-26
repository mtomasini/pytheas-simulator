"""
Script that contains utility functions that are not used within a particular class.
"""

import geopy.distance as gp
import numpy as np
from typing import Tuple


def distance(origin: Tuple[float, float], target: Tuple[float, float]) -> float:
    """Calculates distance in km between two lon/lat points, in km

    Args:
        origin (Tuple[float, float]): point of origin as [lon, lat]
        target (Tuple[float, float]): point of destination as [lon, lat]

    Returns:
        float: distance between origin and target
    """
    return gp.distance(gp.lonlat(*origin), gp.lonlat(*target)).km


def bearing_from_latlon(position: np.ndarray, target: np.ndarray) -> float:
    """Gives angle between a coordinate and a target (in degrees with respect to North). Taken from Voyager.

    Args:
        position (np.ndarray): current position (lat/lon)
        target (np.ndarray): target position (lat/lon)
    Returns:
        float: bearing (angle) between a position and a target in degrees
    """

    local_latitude = np.deg2rad(position[0])
    target_latitude = np.deg2rad(target[0])
    delta_longitude = np.deg2rad(position[1]-target[1])

    x = np.sin(delta_longitude) * np.cos(target_latitude)
    y = np.cos(local_latitude) * np.sin(target_latitude) - np.sin(local_latitude) * np.cos(target_latitude) * np.cos(delta_longitude)

    bearing = np.arctan2(x, y)

    bearing = (np.rad2deg(bearing) + 360) % 360

    return bearing