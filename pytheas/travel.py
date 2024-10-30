"""
    The Travel class of Pytheas. 
     
    It represents a travel from A to B. This class collects all the different components of the travel of a Boat from A to B on a Map. 
    In the Agent-Based Modelling framework, it represents the Model.
"""

import geopy.distance
import json
import numpy as np
import os
import pandas as pd
from typing import Tuple

from .boat import Boat
from .map import Map
from .utilities import *

class Travel:
    """
    Base class for a Travel in Pytheas. 
    
    Attr:
        boat (Boat): The boat that will travel.
        map (Map): The map over which the boat will travel.
        max_duration (int): The maximal duration of the trip (in hours).
        timestep (int): Time between each step (in minutes).
        launching_site (Tuple[float, float]): Departure site in lat/lon format, inherited from boat.
        start_time (pd.Timestamp): The day and time of departure for the trip.
        target (Tuple[float, float]): Target landing site in lat/lon format, inherited from boat.
        night_travel (bool): Whether the boat is stops for night or not.
        twilight_of_stops (str): Determines whether tips start and end at sunrise or twilight. Options are "sun" (sunrise), "civil", "nautical" and "astronomical".
        current_time (pd.Timestamp): Keeps track of the current time in the travel.
        is_completed (bool): Marks whether the travel is completed within tolerance. 
        tolerance (float): Tolerance distance from target to be considered "arrived" (in km). Defaults to 3 km, a distance within which a boat travelling at 3 m/s can travel in 15 minutes.
        encountered_currents (List): List of tuples (x, y) of currents encountered on the travel.
        encountered_winds (List): List of tuples (speed, angle) of winds encountered on the travel.
        encountered_waves (List[float]): List of wave heights encountered on the travel.
        times_of_stops (List[pd.Timestamp]): List of times at which stops for night were initiated. It gets populated only if night_travel = True.
        stop_coords (List): List of lat/lon points at which the boat stopped for night. 
    """
    
    def __init__(self, boat: Boat, map: Map,
                 start_day: str,
                 max_duration: int,
                 timestep: int,
                 night_travel: bool = False,
                 tolerance_distance: float = 3,
                 twilights_of_stops: str = 'sun'):
        """
        Create a new travel.

        Args:
            boat (Boat): A boat that will accomplish the travel.
            map (Map): The map over which the travel is accomplished (includes temporal and spatial data).
            start_day (pd.Timestamp): Day in which the travel is started.
            max_duration (int): Maximal duration of the travel (in hours).
            timestep (int): Time between subsequent steps (in minutes).
            tolerance_distance (float, optional): Distance from target within which a travel is considered finished (in km). Defaults to 3 km.
            twilights_of_stops (str, optional): Determines whether tips start and end at sunrise or twilight. Options are "sun" (sunrise), "civil", "nautical" and "astronomical".. Defaults to 'sun'.
        """
        self.boat = boat
        self.map = map
        self.max_duration = max_duration
        self.timestep = timestep
        self.launching_site = [boat.latitude, boat.longitude]
        self.start_time = calculate_start_of_day(start_day, self.launching_site, type_of_twilight=twilights_of_stops)
        self.target = boat.target
        self.night_travel = night_travel
        self.twilight_of_stops = twilights_of_stops
        
        self.current_time = self.start_time
        self.is_completed = False
        self.tolerance = tolerance_distance
        
        self.encountered_currents = []
        self.encountered_winds = []
        self.encountered_waves = []
        
        self.times_of_stops = []
        self.stop_coords = []
        
    
    
    def step(self) -> None:
        """
        Advance the travel by one step.
        """
        current_location = [self.boat.latitude, self.boat.longitude]
        
        # Check if land was hit
        local_point_current = self.map.return_local_currents(current_location, self.current_time, average=False)
        if np.isnan(local_point_current[0]):
            self.boat.has_hit_land = True
            return

        wind_here_and_now = self.map.return_local_winds(current_location, self.current_time)
        current_here_and_now = self.map.return_local_currents(current_location, self.current_time)
        waves_here_and_now = self.map.return_local_waves(current_location, self.current_time)
        
        self.encountered_winds.append(wind_here_and_now.tolist())
        self.encountered_currents.append(current_here_and_now.tolist())
        self.encountered_waves.append(waves_here_and_now.tolist())
        
        if self.night_travel:
            sunrise = calculate_start_of_day(self.current_time.strftime('%Y-%m-%d'), current_location, type_of_twilight=self.twilight_of_stops)
            sunset = calculate_end_of_day(self.current_time.strftime('%Y-%m-%d'), current_location, type_of_twilight=self.twilight_of_stops)
            
            if sunrise <= self.current_time < sunset:
                if self.boat.land_radar_on:
                    landmarks = self.map.find_closest_land(current_location)
                else:
                    landmarks = [None, None]
                
                # TODO consider putting parameter `move_target` in function move_boat() to allow following either the final target or the route
                self.boat.move_boat(landmarks, wind_here_and_now, current_here_and_now, self.timestep, self.tolerance)
            else:
                # save stop position and time if this was not already saved last loop
                if len(self.stop_coords) > 0:
                    if self.stop_coords[-1] != current_location:
                        self.stop_coords.append(current_location)
                        self.times_of_stops.append(self.current_time)
                else:
                    self.stop_coords.append(current_location)    
                    self.times_of_stops.append(self.current_time)
                        
                
        else:
            if self.boat.land_radar_on:
                landmarks = self.map.find_closest_land(current_location)
            else:
                landmarks = [None, None]
            # landmarks = self.map.find_closest_land(current_location)
            
            self.boat.move_boat(landmarks, wind_here_and_now, current_here_and_now, self.timestep, self.tolerance)
        
        
    def run(self, verbose: bool = False) -> None:
        """
        Run the travel from the launching site to the target landing site or until it hits land.
        
        Args:
            verbose (bool): Boolean determining whether to print a final short summary of the trip.
        """
        max_date = self.start_time + pd.Timedelta(hours=self.max_duration)
        
        while self.current_time < max_date:
            
            
            # check how far one is from the target
            distance_from_target = distance_km(self.boat.trajectory[-1], self.boat.target)
            if distance_from_target < self.tolerance:
                self.is_completed = True
                break
            
            self.step()
            if self.boat.has_hit_land:
                break
            
            self.current_time += pd.Timedelta(minutes=self.timestep)
        
        if verbose:
            duration = round((self.current_time - self.start_time).total_seconds() / 3600, 2)
            print(f"Travel finished after {duration} hours! \n Was land hit? {self.boat.has_hit_land}! \n Was the trip completed? {self.is_completed}! \n Distance from target: {distance_from_target} km")
    
    
    def output_geojson(self, output_path: str) -> dict:
        """
        Save GeoJSON file of the travel and return it.

        Args:
            output_path (str): filepath for output.

        Returns:
            dict: GeoJSON of the travel containing various data.
        """
        
        duration_in_seconds = (self.current_time - self.start_time).total_seconds()
        
        # print out geojson based on boat data at the end of the trip
        GeoJSON_format = {
            "type": "FeatureCollection",
            "features": []
        }
        
        GeoJSON_format["features"].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": self.boat.trajectory,
                },
                "properties": {
                    "start_date": self.start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "stop_date": self.current_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "timestep (m)": self.timestep,
                    "distance (km)": self.boat.distance, 
                    "duration (h)": duration_in_seconds / 3600, # duration in hours
                    "mean_speed (km/h)": self.boat.distance / (duration_in_seconds / 3600),
                    "mean_speed (m/s)": self.boat.distance*1000 / duration_in_seconds,
                    "crew_bearings": self.boat.nominal_bearings,
                    "actual_bearings": self.boat.modified_bearings,
                    "launching_site": self.launching_site,
                    "landing_site": self.target,
                    "night_travel": self.night_travel,
                    "route": self.boat.route_to_take,
                    "trip_winds": self.encountered_winds,
                    "trip_currents": self.encountered_currents,
                    "trip_waves": self.encountered_waves,
                    "twilight_convention": self.twilight_of_stops,
                    "stop_times": [(lambda x: x.strftime('%Y-%m-%dT%H:%M:%S'))(x) for x in self.times_of_stops],
                    "stop_coords": self.stop_coords,
                    "hit_land": self.boat.has_hit_land,
                    "is_completed": self.is_completed,
                }
            }
        )
        
        with open(f'{output_path}.json','w') as file:
            json.dump(GeoJSON_format, file, indent=4)
        
        return GeoJSON_format

    def append_to_aggregates(self, output_path: str, radius_for_success: float = 5) -> None:
        if not os.path.exists(output_path):
            with open(output_path, 'w') as f:
                f.write(f"Date,Duration,Distance,MeanSpeed,Success10K,WavesAvg,WavesMax,HoursAbove2m,WindAvgSpeed,WindAvgDir,CurrentsAvgX,CurrentsAvgY\n")

        date = self.start_time.strftime("%Y-%m-%d")
        duration_in_seconds = (self.current_time - self.start_time).total_seconds()
        duration = duration_in_seconds / 3600
        distance = self.boat.distance
        speed = self.boat.distance / duration
        success = 1 if geopy.distance.distance((self.boat.latitude, self.boat.longitude), self.target) <= radius_for_success else 0
        mean_wave = np.nanmean(self.encountered_waves)
        max_wave = np.nanmax(self.encountered_waves)
        hours_above = sum(np.array(self.encountered_waves) > 2)*self.timestep / 60
        avg_wind_speed = np.nanmean(np.array(self.encountered_winds)[:,0])
        avg_wind_direction = np.nanmean(np.array(self.encountered_winds)[:,1])
        avg_currents_x = np.nanmean(np.array(self.encountered_currents)[:,0])
        avg_currents_y = np.nanmean(np.array(self.encountered_currents)[:,1])

        with open(output_path, 'a') as f:
            f.write(f"{date},{duration},{distance},{speed},{success},{mean_wave},{max_wave},{hours_above},{avg_wind_speed},{avg_wind_direction},{avg_currents_x},{avg_currents_y}\n")
