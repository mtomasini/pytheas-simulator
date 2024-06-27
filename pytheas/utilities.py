"""
Script that contains utility functions that are not used within a particular class.
"""

import geopy.distance as gp
import numpy as np
from typing import Tuple


def distance_km(origin: Tuple[float, float], target: Tuple[float, float]) -> float:
    """Calculates distance in km between two lon/lat points, in km

    Args:
        origin (Tuple[float, float]): point of origin as [lon, lat]
        target (Tuple[float, float]): point of destination as [lon, lat]

    Returns:
        float: distance between origin and target
    """
    return gp.distance(gp.lonlat(*origin), gp.lonlat(*target)).km


def bearing_from_latlon(position: Tuple[float, float], target: Tuple[float, float]) -> float:
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

def knots_to_si(knots: float) -> float:
    """Converts knots to SI units (m/s)

    Args:
        knots (float): Speed in knots

    Returns:
        float: Speed in metres/second
    """

    return knots / 1.94


def si_to_knots(si: float) -> float:
    """Converts SI units (m/s) to knots

    Args:
        si (float): Speed in m/s

    Returns:
        float: Speed in knots
    """

    return si * 1.94


def angle_uncertainty(sigma=0) -> float:
    """Returns an angle error in radiants. 
    """
    angle_error = np.random.normal(0, sigma)
    
    return angle_error