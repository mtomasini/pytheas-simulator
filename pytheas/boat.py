"""
The Boat class of Pytheas. 
    
It represents a boat - a logboat, a plank canoe, a longship - you name it. In the Agent-Based Modelling framework, the Boat represents a basic Agent.
"""
import cartopy
import geopy.distance as gp
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Tuple, List

import pytheas.utilities

class Boat:
    """
    Base class for a Boat in Pytheas.
    
    Attributes:
        craft (str): Name or type of boat.
        latitude (float): Latitude at which the boat is.
        longitude (float): Longitude at which the boat is.
        target (Tuple[float, float]): Lat/Lon of the target landing site.
        land_radar_on (bool): Whether the land radar algorithm acts or not.
        uncertainty_sigma (float): standard deviation of the navigation error.
        speed_polar_diagram (pd.DataFrame): Table representing the boat speed polar diagram.
        leeway_polar_diagram (pd.DataFrame): Table representing the boat leeway polar diagram. 
        route_to_take (List[float]): List of lat/lon coordinates that the boat has to follow to get to target.
        trajectory (List[float]): List of lat/lon keeping track of the trajectory of the boat.
        distance (float): Distance (in km) covered by the boat so far.
        bearing (float)): Current angle between launching site and target.
        nominal_bearings (List[float]): list of all the direction that the crew takes to reach the target.
        modified_bearings (List[float]): list of the actual bearings that the boat takes during the trip, after accounting for currents and land avoidance.
        has_hit_land (bool): Boolean to record if the boat hits land before the end of the trip. 
    """
    
    def __init__(self, craft: str, 
                 latitude: float, longitude: float, 
                 target: Tuple[float, float], 
                 land_radar_on: bool = True,
                 uncertainty_sigma: float = 0.0,
                 speed_polar_diagram: pd.DataFrame = None, 
                 leeway_polar_diagram: pd.DataFrame = None, 
                 route_to_take: List[float] = None):
        """Create a new boat.

        Args:
            craft (str): Type of boat (e.g. "Hjortspring").
            longitude (float): Current longitude of the boat. It gets updated when running move_step().
            latitude (float): Current latitude of the boat. It gets updated when running move_step().
            target (Tuple[float, float]): Tuple of lat/lon of the target.
            land_radar_on (bool): Whether the land radar is on. Defaults to True.
            uncertainty_sigma (float): standard deviation of the navigation error. Defaults to zero
            speed_polar_diagram (pd.DataFrame): Table representing the boat speed polar diagram. Defaults to None.
            leeway_polar_diagram (pd.DataFrame): Table representing the boat leeway polar diagram. Defaults to None.
            route_to_take (List[float]): List of lat/lon coordinates that the boat has to follow to get to target.
        """
        self.craft = craft
        self.latitude = latitude
        self.longitude = longitude
        self.target = target
        self.land_radar_on = land_radar_on
        self.uncertainty_sigma = uncertainty_sigma
        self.speed_polar_diagram = speed_polar_diagram
        self.leeway_polar_diagram = leeway_polar_diagram
        self.route_to_take = route_to_take # TODO implement routing
        
        self.trajectory = [(latitude, longitude)]
        self.distance = 0
        self.bearing = pytheas.utilities.bearing_from_latlon([self.latitude, self.longitude], self.target)
        self.nominal_bearings = [self.bearing]
        self.modified_bearings = []
        
        self.has_hit_land = False
    
    
    def speed_due_to_wind(self, current_winds: np.ndarray, bearing: float):
        """
        Calculate the combined speed of paddling with the effect of the wind according to a polar diagram, when existing.

        Args:
            current_winds (np.ndarray): Wind velocity (two components), 0-element is speed in m/s, 1-element is direction in degrees.
            bearing_xy (np.ndarray): Bearing of the boat split in x, y components.

        Raises:
            ValueError: Raised if the angle between the bearing and reference is a non-positive number.
            ValueError: Raised if the speed of the wind is higher than 30.
            
        Returns:
            speed (float): Speed in m/s of the paddling crew.
        """

        # find angle of wind compared to bearing of boat. 
        effective_wind_angle = pytheas.utilities.difference_between_geographic_angles(bearing, current_winds[1])
        # wind_sign = np.sign(effective_wind_angle)

        # then adapt to the polar diagram (symmetric, only reported for positive angles, with negative angles having opposite sign results)
        abs_wind_angle = np.abs(effective_wind_angle)

        wind_speed = current_winds[0]
        wind_speed_knots = pytheas.utilities.si_to_knots(wind_speed)

        # round angle to next 10 and speed to next 5
        if 0 <= abs_wind_angle <= 180:
            rounded_angle = math.ceil(abs_wind_angle/10)*10
        else:
            raise ValueError(f"Absolute wind angle is not between 0 and 180 ({abs_wind_angle} deg)")
        if 0 <= wind_speed_knots <= 30:
            rounded_speed = math.ceil(wind_speed_knots/5)*5
        elif wind_speed_knots > 30:
            # OPEN what if speed is too high? Set final speed of boat to zero, possibly
            rounded_speed = 30
        else:
            raise ValueError(f"Wind speed is negative ({wind_speed} m/s)")

        speed_in_knots = self.speed_polar_diagram[str(rounded_speed)][rounded_angle]
        speed = pytheas.utilities.knots_to_si(speed_in_knots)

        return speed
    
    
    def leeway_due_to_wind(self, current_winds: np.ndarray, bearing: float):
        """Calculates the leeway due to wind according to a polar diagram, when existing.

        Args:
            current_winds (np.ndarray): Wind velocity (two components)
            bearing_xy (np.ndarray): bearing of the boat split in x, y components

        Raises:
            ValueError: Raised if the angle between the bearing and reference is a non-positive number
            ValueError: Raised if the speed of the wind is higher than 30
            
        Returns:
            leeway_angle: geographic angle of leeway due to the wind to be added to the bearing to obtain the real angle
                            at which the boat travels, in degrees
        """

        # find angle of wind compared to bearing of boat. 
        effective_wind_angle = pytheas.utilities.difference_between_geographic_angles(bearing, current_winds[1])
        wind_sign = np.sign(effective_wind_angle)

        # then adapt to the polar diagram (symmetric, only reported for positive angles, with negative angles having opposite sign results)
        abs_wind_angle = np.abs(effective_wind_angle)

        wind_speed = current_winds[0]
        wind_speed_knots = pytheas.utilities.si_to_knots(wind_speed)

        # round angle to next 10 and speed to next 5
        if 0 <= abs_wind_angle <= 180:
            rounded_angle = math.ceil(abs_wind_angle/10)*10
        else:
            raise ValueError(f"Absolute wind angle is not between 0 and 180 ({abs_wind_angle} deg)")
        if 0 <= wind_speed_knots <= 30:
            rounded_speed = math.ceil(wind_speed_knots/5)*5
        elif wind_speed_knots > 30:
            # OPEN what if speed is too high? Set final speed of boat to zero, possibly
            rounded_speed = 30
        else:
            raise ValueError(f"Wind speed is negative ({wind_speed} m/s)")

        leeway_angle = wind_sign*self.leeway_polar_diagram[str(rounded_speed)][rounded_angle]

        return leeway_angle
    
    
    def calculate_displacement(self, local_winds: np.ndarray, local_currents: np.ndarray,
                               bearing: float, timestep: int) -> np.ndarray:
        """Function to calculate the displacement in km of a boat from its current position given winds, currents and bearing.

        Args:
            local_winds (np.ndarray): array containing speed and direction of the wind in the local position.
            local_currents (np.ndarray): array containing Eastward (x) and Northward (y) speed of currents in the local position.
            bearing (float): bearing taken by the boat.

        Returns:
            np.ndarray: array containing Eastward and Northward displacement of the boat from current position. 
        """
        
        paddling_speed = self.speed_due_to_wind(local_winds, bearing)
        leeway_angle = self.leeway_due_to_wind(local_winds, bearing)
        effective_direction = bearing - leeway_angle
        movement_angle_dxy = pytheas.utilities.geographic_angle_to_xy(effective_direction)
        
        # paddling_speed is in m/s, timestep is in minutes
        timestep_seconds = timestep * 60.
        wind_dxy = paddling_speed*movement_angle_dxy*timestep_seconds # wind_dxy in meters
        currents_dxy = local_currents*timestep_seconds
        displacement_dxy = (wind_dxy + currents_dxy) / 1000 # displacement_dxy in km.
        
        return displacement_dxy
    
    
    def generic_displacement(self, local_winds: np.ndarray, local_currents: np.ndarray,
                               bearing_xy: np.ndarray):
        # TODO write displacement function for a boat without polar diagram, given winds and currents
        return [0, 0]
    
    
    def move_boat(self, landmarks: Tuple[float, float], 
                  local_winds: np.ndarray, local_currents: np.ndarray, 
                  timestep: int, accepted_distance_from_target: float = 1):
        """Function tha determines the movement of a boat at each time step. It runs from Travel.

        Args:
            landmarks (Tuple[float, float]: List containing the distance to the closest land (in km) and the direction to the closest land (in degrees)).
            local_winds (np.ndarray): Array containing the speed and geographic angle of the wind.
            local_currents (np.ndarray): Array containing Northward and Eastward components of sea currents speed.
            timestep (int): Time step between steps of movement, in minutes.
            acceted_distance_from_target (float): Distance from target that does not trigger stirring away from land (if target is not distant, the boat should keep going towards it, not stir away.)
        """
        # first, update the bearing based on the local position
        self.bearing = pytheas.utilities.bearing_from_latlon([self.latitude, self.longitude], self.target)
        self.nominal_bearings.append(self.bearing)
        
        # if there is land ahead stir away, but only if we're not close to the target! If we're less than 20 km away from the target, let hit either target or land.
        if landmarks[0] is not None and landmarks[0] < 20:
            land_angle = landmarks[1]
            # we need to define "ahead", this would be within +/- 45 degrees from the bearing. 
            left_limit = (self.bearing - 45) % 360
            right_limit = (self.bearing + 45) % 360
            
            # the bearing is given as a number between 0 and 360, we need to split here. is_ahead is True if:
            if 45 <= self.bearing <= 315:
                is_ahead = (left_limit <= land_angle <= right_limit)
            else:
                is_ahead = (0 <= land_angle <= right_limit) or (left_limit <= land_angle <= 360)
                
            if is_ahead:
                # in general, if (bearing - land_angle) > 0 , then land is on the left (steering to the right - positive - is necessary). And viceversa.
                sign_of_steering = np.sign(self.bearing - land_angle)
                if sign_of_steering != 0:
                    self.bearing = self.bearing + sign_of_steering * 90
                else:
                    # the case where (bearing - land_angle) = 0 represent land right ahead. In this (hopefully rare) case we just move in the 
                    # opposite direction and try again...
                    self.bearing = self.bearing + 180 
            else:
                pass
            
            self.bearing = self.bearing % 360
        else:
            pass
        
        # next, add uncertainty to the bearing and split the bearing into x and y
        bearing_with_uncertainty = self.bearing + pytheas.utilities.angle_uncertainty(self.uncertainty_sigma)

        self.modified_bearings.append(bearing_with_uncertainty)
        
        if self.speed_polar_diagram is not None:
            displacement_xy = self.calculate_displacement(local_winds, local_currents, bearing_with_uncertainty, timestep)
            direction_of_displacement = pytheas.utilities.direction_from_displacement(displacement_xy)
            distance_of_displacement = np.linalg.norm(displacement_xy)
            
            new_coordinates = gp.distance(distance_of_displacement).destination((self.latitude, self.longitude), bearing = direction_of_displacement)
            
        else:
            raise ValueError('There is no polar diagram attached!')
            # TODO write logic for generic displacement without polar diagram
            
        self.latitude = new_coordinates.latitude
        self.longitude = new_coordinates.longitude
        self.trajectory.append((new_coordinates.latitude, new_coordinates.longitude))
        self.distance += distance_of_displacement
        
    
    def plot_trajectory(self, bbox: Tuple[float, float, float, float], show_route: bool = False) -> None:
        """
        Quick trajectory plot utility, to show a simulated trajectory. 

        Args:
            bbox (Tuple[float, float, float, float]): list containing [min latitude, min longitude, max latitude, max longitude] for map plotting.
        """
        fig, ax = plt.subplots(subplot_kw={'projection': cartopy.crs.PlateCarree()}, )
        ax.set_extent([bbox[1], bbox[3], bbox[0], bbox[2]], cartopy.crs.PlateCarree())
        ax.add_feature(cartopy.feature.OCEAN, zorder=0)
        ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor='black')
        ax.gridlines(crs=cartopy.crs.PlateCarree(), draw_labels=True,
                     linewidth=1, color='gray', alpha=0.2, linestyle='--')
        
        trajectory = pd.DataFrame(self.trajectory) 
        ax.plot(trajectory[1], trajectory[0], zorder=10)
        ax.scatter(self.trajectory[0][1], self.trajectory[0][0], s = 50, marker="<", color="tab:red")
        ax.scatter(self.target[1], self.target[0], s = 50, marker="X", color="tab:green")

        if show_route == True:
            route = pd.DataFrame(self.route_to_take)
            ax.scatter(route[1], route[0], color="tab:blue")
        
        plt.show()