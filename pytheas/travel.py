import numpy as np
import pandas as pd
from typing import Tuple

from .boat import Boat
from .map import Map
import utilities

class Travel:
    """The Travel class of Pytheas. 
    
    It represents a travel from A to B. This class collects all the different components of the travel of a Boat from A to B on a Map. 
    In the Agent-Based Modelling framework, it represents the Model.
    """
    
    def __init__(self, boat: Boat, map: Map,
                 start_time: pd.Timestamp, max_duration: int,
                 timestep: int, target: np.ndarray):
        """Creates a new travel. 

        Args:
            boat (Boat): the boat that will travel.
            map (Map): the map over which the boat will travel.
            start_time (pd.Timestamp): the day and time of departure for the trip. 
            maximum_duration (int): the maximum duration of each trip (in hours). Explicits the number of hours after which the travel will be stopped.
            timestep (int): time between each step (in minutes)
            target (np.ndarray): lat/lon of the target of the travel
        """
        self.boat = boat
        self.map = map
        self.start_time = start_time
        self.max_duration = max_duration
        self.timestep = timestep
        self.target = target
        
        self.current_time = start_time
        
    def step(self):
        current_location = np.array([self.boat.latitude, self.boat.longitude])
        bearing = utilities.bearing_from_latlon()
        
        wind_here_and_now = self.map.measure_winds(current_location, self.current_time)
        current_here_and_now = self.map.measure_currents(current_location, self.current_time)
        
        self.boat.move_boat(wind_here_and_now, current_here_and_now, bearing)
        
    def run(self):
        max_date = self.start_time + pd.Timedelta(hours=self.max_duration)
        
        while self.current_time < max_date:
            self.step()
            self.current_time += pd.Timedelta(minutes=self.timestep)
    
    
    def output_geojson():
        # print out geojson based on boat data at the end of the trip
        pass