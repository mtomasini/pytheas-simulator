import math
import numpy as np
import pandas as pd
from typing import Tuple

import pytheas.utilities

class Boat:
    """
    The Boat class of Pytheas. 
    
    It represents a boat - a logboat, a plank canoe, a longship - you name it. In the Agent-Based Modelling framework, the Boat represents a basic Agent.
    
    """
    
    def __init__(self, craft: str, 
                 latitude: float, longitude: float, 
                 target: Tuple[float, float], 
                 speed_polar_diagram: pd.DataFrame = None, 
                 leeway_polar_diagram: pd.DataFrame = None):
        """Creates a new boat.

        Args:
            craft (str): type of boat (e.g. "Hjortspring")
            longitude (float): current longitude of the boat. It gets updated when running move_step().
            latitude (float): current latitude of the boat. It gets updated when running move_step().
            target (Tuple[float, float]): tuple of lon/lat of the target.
            speed_polar_diagram (pd.DataFrame): table representing the boat speed polar diagram. Defaults to None.
            leeway_polar_diagram (pd.DataFrame): table representing the boat leeway polar diagram. Defaults to None.
        """
        self.craft = craft
        self.latitude = latitude
        self.longitude = longitude
        self.target = target
        self.speed_polar_diagram = speed_polar_diagram
        self.leeway_polar_diagram = leeway_polar_diagram
        
        self.trajectory = [(latitude, longitude)]
        self.bearing = pytheas.utilities.bearing_from_latlon([(self.longitude, self.latitude)], self.target)
    
    
    def speed_due_to_wind(self, local_winds: np.ndarray, bearing_xy: np.ndarray):
        """Calculates the combined speed of paddling with the effect of the wind according to a polar diagram, when existing.

        Args:
            current_winds (np.ndarray): Wind velocity (two components)
            bearing_xy (np.ndarray): bearing of the boat split in x, y components

        Raises:
            ValueError: Raised if the angle between the bearing and reference is a non-positive number
            ValueError: Raised if the speed of the wind is higher than 30
            
        Returns:
            speed (float): speed in m/s of the paddling crew
        """

        true_wind_angle = np.arctan2(np.linalg.det([bearing_xy, local_winds]), np.dot(bearing_xy, local_winds))
        true_wind_angle = np.abs(np.rad2deg(true_wind_angle))

        true_wind_speed = np.linalg.norm(local_winds)
        true_wind_speed_knots = pytheas.utilities.si_to_knots(true_wind_speed)

        # round angle to next 10 and speed to next 5
        if 0 <= true_wind_angle <= 180:
            rounded_angle = math.ceil(true_wind_angle/10)*10
        else:
            raise ValueError(f"Wind angle is not between 0 and 180 ({true_wind_angle} deg)")
        if 0 <= true_wind_speed_knots <= 30:
            rounded_speed = math.ceil(true_wind_speed_knots/5)*5
        elif true_wind_speed_knots > 30:
            # OPEN what if speed is too high? Set final speed of boat to zero, possibly
            rounded_speed = 30
        else:
            raise ValueError(f"Wind speed is negative ({true_wind_speed} m/s)")

        speed_in_knots = self.speed_polar_diagram[str(rounded_speed)][rounded_angle]
        speed = pytheas.utilities.knots_to_si(speed_in_knots)

        return speed
    
    
    def leeway_due_to_wind(self, current_winds: np.ndarray, bearing_xy: np.ndarray):
        """Calculates the leeway due to wind according to a polar diagram, when existing.

        Args:
            current_winds (np.ndarray): Wind velocity (two components)
            bearing_xy (np.ndarray): bearing of the boat split in x, y components

        Raises:
            ValueError: Raised if the angle between the bearing and reference is a non-positive number
            ValueError: Raised if the speed of the wind is higher than 30
            
        Returns:
            leeway_angle: angle of leeway due to the wind to be added to the bearing to obtain the real angle
                            at which the boat travels, in degrees
        """

        # find angle of wind compared to bearing of boat
        true_wind_angle = np.arctan2(np.linalg.det([bearing_xy, current_winds]), np.dot(bearing_xy, current_winds))

        # find the wind_sign, will be used in leeway_angle to apply the correct angle to leeway.
        wind_sign = np.sign(true_wind_angle)
        # then adapt to the polar diagram (symmetric, only reported for positive angles, with negative angles having opposite sign results)
        true_wind_angle = np.abs(np.rad2deg(true_wind_angle))

        true_wind_speed = np.linalg.norm(current_winds)
        true_wind_speed_knots = pytheas.utilities.si_to_knots(true_wind_speed)

        # round angle to next 10 and speed to next 5
        if 0 <= true_wind_angle <= 180:
            rounded_angle = math.ceil(true_wind_angle/10)*10
        else:
            raise ValueError(f"Wind angle is not between 0 and 180 ({true_wind_angle} deg)")
        if 0 <= true_wind_speed_knots <= 30:
            rounded_speed = math.ceil(true_wind_speed_knots/5)*5
        elif true_wind_speed_knots > 30:
            # OPEN what if speed is too high? Set final speed of boat to zero, possibly
            rounded_speed = 30
        else:
            raise ValueError(f"Wind speed is negative ({true_wind_speed} m/s)")

        leeway_angle = -wind_sign*self.leeway_polar_diagram[str(rounded_speed)][rounded_angle]

        return leeway_angle
    
    
    def calculate_displacement(self, local_winds: np.ndarray, local_currents: np.ndarray,
                               bearing_xy: np.ndarray):
        # TODO write displacement function for a boat with polar diagram, given winds and currents
        
        paddling_speed = self.speed_due_to_wind(local_winds, bearing_xy)
        leeway_angle = self.leeway_due_to_wind(local_winds, bearing_xy)
        
        
        
        # 1) calculate dx, dy due to wind
        # 2) calculate dy, dy due to current
        # 3) 
        
        
        
        return [0, 0]
    
    
    def generic_displacement(self, local_winds: np.ndarray, local_currents: np.ndarray,
                               bearing_xy: np.ndarray):
        # TODO write displacement function for a boat without polar diagram, given winds and currents
        return [0, 0]
    
    def move_boat(self, local_winds: np.ndarray, local_currents: np.ndarray, uncertainty_sigma: float = 0.0):
        # first, update the bearing based on the local position
        self.bearing = pytheas.utilities.bearing_from_latlon([(self.longitude, self.latitude)], self.target)
        bearing_radiants = np.deg2rad(self.bearing + pytheas.utilities.angle_uncertainty(uncertainty_sigma))
        bearing_xy = np.array[np.cos(bearing_radiants), np.sin(bearing_radiants)]
        
        if self.polar_diagram is not None:
            moved_horizontal, moved_vertical = Boat.calculate_displacement(local_winds, local_currents, bearing_xy)
            new_longitude, new_latitude
        else:
            new_longitude, new_latitude = Boat.generic_displacement(local_winds, local_currents, bearing_xy)
            
        self.trajectory.append((new_longitude, new_latitude))
        self.longitude = new_longitude
        self.latitude = new_latitude