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


def geographic_angle_to_xy(angle: float) -> np.ndarray:
    """From a geographic angle (with 0 degrees signifying North, 90 East, 180 South and 270 W) return x and y.

    Args:
        angle (float): geographic angle in degrees

    Returns:
        np.ndarray: array with dx (horizontal Eastward) and dy (vertical Northward)
    """
    angle_radians = np.deg2rad(angle)
    dx = np.sin(np.pi - angle_radians)
    dy = np.cos(angle_radians)
    
    return np.array([dx, dy])


def difference_between_geographic_angles(bearing: float, angle_wind: float) -> float:
    # first, turn angle into the range -180, 180
    if bearing > 180:
        bearing -= 360
    if angle_wind > 180:
        angle_wind -= 360
    
    effective_wind_angle = angle_wind - bearing
    
    if effective_wind_angle > 180:
        effective_wind_angle = 360 - effective_wind_angle
    if effective_wind_angle < -180:
        effective_wind_angle = 360 + effective_wind_angle
    
    # # if both angles are in the same half (both left of N or both right of N)
    # if (bearing <= 180 and angle_wind <= 180) or (bearing > 180 and angle_wind > 180): 
    #         effective_wind_angle = angle_wind - bearing
    # # second, if winds are from the left and bearing is to the right: 
    # elif (bearing <= 180 and angle_wind > 180):
    #     difference_between_angles = angle_wind - bearing
    #     effective_wind_angle = difference_between_angles - 360
    # # third, if winds are from the right and bearing is to the left
    # elif (bearing > 180 and angle_wind <= 180):
    #     difference_between_angles = angle_wind - bearing
    #     effective_wind_angle = 360 + difference_between_angles
        
    return effective_wind_angle