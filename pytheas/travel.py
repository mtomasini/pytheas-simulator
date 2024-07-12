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
        launching_site (Tuple[float, float]): departure site in lat/lon format, inherited from boat.
        start_time (pd.Timestamp): The day and time of departure for the trip.
        target (Tuple[float, float]): target landing site in lat/lon format, inherited from boat.
        twilight_of_stops (str): determines whether tips start and end at sunrise or twilight. Options are "sun" (sunrise), "civil", "nautical" and "astronomical".
        current_time (pd.Timestamp): keeps track of the current time in the travel.
        is_completed (bool): marks whether the travel is completed within tolerance. 
        tolerance (float): tolerance distance from target to be considered "arrived" (in km). Defaults to 0.2 km.
    """
    
    def __init__(self, boat: Boat, map: Map,
                 start_day: str,
                 max_duration: int,
                 timestep: int,
                 tolerance_distance: float = 0.2,
                 twilights_of_stops: str = 'sun'):
        """
        Create a new travel. 
        
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
        current_location = [self.boat.latitude, self.boat.longitude]
        
        wind_here_and_now = self.map.return_local_winds(current_location, self.current_time)
        current_here_and_now = self.map.return_local_currents(current_location, self.current_time)
        
        if current_here_and_now[0] is None:
            self.boat.has_hit_land = True
            return
        
        self.boat.move_boat(wind_here_and_now, current_here_and_now, self.timestep)
        
        
    def run(self) -> None:
        max_date = self.start_time + pd.Timedelta(hours=self.max_duration)
        
        while self.current_time < max_date:
            if self.boat.has_hit_land:
                break
            
            # check how far one is from the target
            distance_from_target = distance_km([self.boat.latitude, self.boat.longitude], self.boat.target)
            if distance_from_target < self.tolerance:
                self.is_completed = True
            
            self.step()
            self.current_time += pd.Timedelta(minutes=self.timestep)
    
    
    def output_geojson():
        # print out geojson based on boat data at the end of the trip
        pass