import numpy as np
import pandas as pd
from typing import Tuple

from .boat import Boat
from .map import Map
from .utilities import *

class Travel:
    """The Travel class of Pytheas. 
    
    It represents a travel from A to B. This class collects all the different components of the travel of a Boat from A to B on a Map. 
    In the Agent-Based Modelling framework, it represents the Model.
    
    Attr:
        boat (Boat): The boat that will travel.
        map (Map): The map over which the boat will travel.
        max_duration (int): The maximal duration of the trip (in hours).
        timestep (int): Time between each step (in minutes).
        launching_site (Tuple[float, float]): Departure site in lat/lon format, inherited from boat.
        start_time (pd.Timestamp): The day and time of departure for the trip.
        target (Tuple[float, float]): Target landing site in lat/lon format, inherited from boat.
        twilight_of_stops (str): Determines whether tips start and end at sunrise or twilight. Options are "sun" (sunrise), "civil", "nautical" and "astronomical".
        current_time (pd.Timestamp): Keeps track of the current time in the travel.
        is_completed (bool): Marks whether the travel is completed within tolerance. 
        tolerance (float): Tolerance distance from target to be considered "arrived" (in km). Defaults to 0.2 km.
    """
    
    def __init__(self, boat: Boat, map: Map,
                 start_day: str,
                 max_duration: int,
                 timestep: int,
                 tolerance_distance: float = 0.2,
                 twilights_of_stops: str = 'sun'):
        """
        Create a new travel.

        Args:
            boat (Boat): A boat that will accomplish the travel.
            map (Map): The map over which the travel is accomplished (includes temporal and spatial data).
            start_day (pd.Timestamp): Day in which the travel is started.
            max_duration (int): Maximal duration of the travel (in hours).
            timestep (int): Time between subsequent steps (in minutes).
            tolerance_distance (float, optional): Distance from target within which a travel is considered finished (in km). Defaults to 0.2.
            twilights_of_stops (str, optional): Determines whether tips start and end at sunrise or twilight. Options are "sun" (sunrise), "civil", "nautical" and "astronomical".. Defaults to 'sun'.
        """
        self.boat = boat
        self.map = map
        self.max_duration = max_duration
        self.timestep = timestep
        self.launching_site = [boat.latitude, boat.longitude]
        self.start_time = calculate_start_of_day(start_day, self.launching_site, type_of_twilight=twilights_of_stops)
        self.target = boat.target
        self.twilight_of_stops = twilights_of_stops
        
        self.current_time = self.start_time
        self.is_completed = False
        self.tolerance = tolerance_distance
        
    
    
    def step(self) -> None:
        """
        Advance the travel by one step.
        """
        current_location = [self.boat.latitude, self.boat.longitude]
        
        wind_here_and_now = self.map.return_local_winds(current_location, self.current_time)
        current_here_and_now = self.map.return_local_currents(current_location, self.current_time)
        
        if np.isnan(current_here_and_now[0]):
            self.boat.has_hit_land = True
            return
        
        self.boat.move_boat(wind_here_and_now, current_here_and_now, self.timestep)
        
        
    def run(self, verbose: bool = False) -> None:
        """
        Run the travel from the launching site to the target landing site or until it hits land.
        """
        max_date = self.start_time + pd.Timedelta(hours=self.max_duration)
        
        while self.current_time < max_date:
            if self.boat.has_hit_land:
                break
            
            # check how far one is from the target
            distance_from_target = distance_km(self.boat.trajectory[-1], self.boat.target)
            if distance_from_target < self.tolerance:
                self.is_completed = True
            
            self.step()
            self.current_time += pd.Timedelta(minutes=self.timestep)
        
        if verbose:
            print(f"Travel finished! \n Was land hit? {self.boat.has_hit_land}! \n Was the trip completed? {self.is_completed}! \n Distance from target: {distance_from_target} km")
    
    
    def output_geojson(self, output_path: str) -> None:
        
        # print out geojson based on boat data at the end of the trip
        pass