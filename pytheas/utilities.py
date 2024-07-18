"""
Module containing utility functions that are not used within a particular class. These are generally functions that deal with geography, measurements 
and distances, or time functions, such as ephemeris functions.
"""

import ephem
import geopy.distance as gp
import numpy as np
import pandas as pd
from typing import Tuple


def distance_km(origin: Tuple[float, float], target: Tuple[float, float]) -> float:
    """Calculates distance in km between two lat/lon points, in km

    Args:
        origin (Tuple[float, float]): point of origin as [lon, lat]
        target (Tuple[float, float]): point of destination as [lon, lat]

    Returns:
        float: distance between origin and target
    """
    return gp.distance(origin, target).km


def bearing_from_latlon(position: Tuple[float, float], target: Tuple[float, float]) -> float:
    """Gives angle between a coordinate and a target (in degrees with respect to North). Taken from Voyager.

    Args:
        position (np.ndarray): current position (lat/lon)
        target (np.ndarray): target position (lat/lon)
    Returns:
        float: bearing (angle) between a position and a target in degrees
    """

    local_latitude = np.deg2rad(position[0])
    local_longitude = np.deg2rad(position[1])
    target_latitude = np.deg2rad(target[0])
    target_longitude = np.deg2rad(target[1])
    # delta_longitude = np.deg2rad(position[1]-target[1])
    delta_longitude = target_longitude - local_longitude

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

    return knots / 1.94384


def si_to_knots(si: float) -> float:
    """Converts SI units (m/s) to knots

    Args:
        si (float): Speed in m/s

    Returns:
        float: Speed in knots
    """

    return si * 1.94384


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
        
    return effective_wind_angle


def direction_from_displacement(displacement: np.ndarray) -> float:
    
    bearing_rad = np.arctan(displacement[1]/displacement[0])
    
    bearing = np.rad2deg(bearing_rad)
    
    return bearing


def calculate_start_of_day(day : str, position: Tuple[float, float], type_of_twilight: str = 'sun') -> pd.Timestamp:
    """Function to calculate at what time the sun rises (or twilight).

    Args:
        day (str): date in format 'yyyy-mm-dd'
        position (Tuple[float, float]): position at which you want to calculate the start of the day, in format lon / lat
        type_of_twilight (str, optional): whether you want to calculate sunrise, civil, nautical or astronomical twilight. Defaults to 'sun'.

    Raises:
        ValueError: If 'type_of_twilight' is not one  of 'civil', 'nautical', 'astronomical' or 'sun'.

    Returns:
        pd.Timestamp: timestamp of date and time of end of the day.
    """
    earth = ephem.Observer()
    earth.lat = str(position[0])
    earth.lon = str(position[1])
    earth.date = pd.Timestamp(day)

    sun = ephem.Sun()
    sun.compute()

    if type_of_twilight == "civil":
        earth.horizon = "-6"
    elif type_of_twilight == "nautical":
        earth.horizon = "-12"
    elif type_of_twilight == "astronomical":
        earth.horizon = "-18"
    elif type_of_twilight == "sun":
        pass
    else:
        raise ValueError("type_of_twilight needs to be among 'civil', 'nautical', 'astronomical' or 'sun'")

    morning_twilight = ephem.localtime(earth.next_rising(sun))

    return pd.Timestamp(morning_twilight)


def calculate_end_of_day(day : str, position: Tuple[float, float], type_of_twilight: str = 'sun') -> pd.Timestamp:
    """Function to calculate at what time the sun goes down (or twilight).

    Args:
        day (str): date in format 'yyyy-mm-dd'
        position (Tuple[float, float]): position at which you want to calculate the end of the day
        type_of_twilight (str, optional): whether you want to calculate sunset, civil, nautical or astronomical twilight. Defaults to 'sun'.

    Raises:
        ValueError: If 'type_of_twilight' is not one  of 'civil', 'nautical', 'astronomical' or 'sun'.

    Returns:
        pd.Timestamp: timestamp of date and time of end of the day.
    """
    earth = ephem.Observer()
    earth.lat = str(position[0])
    earth.lon = str(position[1])
    earth.date = day

    sun = ephem.Sun()
    sun.compute()

    if type_of_twilight == "civil":
        earth.horizon = "-6"
    elif type_of_twilight == "nautical":
        earth.horizon = "-12"
    elif type_of_twilight == "astronomical":
        earth.horizon = "-18"
    elif type_of_twilight == "sun":
        pass
    else:
        raise ValueError("type_of_twilight needs to be among 'civil', 'nautical', 'astronomical' or 'sun'")

    evening_twilight = ephem.localtime(earth.next_setting(sun))

    return pd.Timestamp(evening_twilight)


def is_it_night(date_and_time: pd.Timestamp, position: Tuple[float, float], type_of_twilight="sun") -> bool:
    # TODO test this function
    """Calculates whether a set of coordinates refer to a moment in the day or in the night. We consider sunrise time as day, and sunset time as night.

    Args:
        date_and_time (pd.Timestamp): day of the year
        position (Tuple[float, float]): place in format [longitude, latitude]
        type_of_twilight (str): type of twilight, "civil", "nautical" or "astronomical". Defaults to "sun".

    Returns:
        bool: returns whether the point is during the night or not
    """
    what_day = date_and_time.date()
    sunrise = calculate_start_of_day(what_day, position, type_of_twilight)
    sunset = calculate_end_of_day(what_day, position, type_of_twilight)
    
    is_night = (date_and_time < sunrise) or (sunset <= date_and_time)
    return is_night