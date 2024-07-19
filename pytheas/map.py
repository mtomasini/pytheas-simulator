import numpy as np
import pandas as pd
from typing import Tuple
import xarray as xr

from pytheas import utilities

class Map:
    """
    The map object of Pytheas.
    
    It represents the space over which the Boat will travel. It is a continuous space where we super impose three distinct layers of data: winds, currents and waves.
    The wind and current layers directly affect the movement of the boat, while the wave layer is necessary to record encountered waves. 
    In the Agent-Based Modelling framework, the Map corresponds to the Space. 
    """
    
    def __init__(self, bounding_box: Tuple[float, float, float, float], earliest_time: pd.Timestamp, latest_time: pd.Timestamp,
                 wind_data_path: str, current_data_path: str, waves_data_path: str):
        """Creates new map.

        Args:
            bounding_box (List[float, float, float, float]): [min_latitude, min_longitude, max_latitude, max_longitude]
            wind_data_path (str): folder where the wind data are stored
            current_data_path (str): folder where the current data are stored
            waves_data_path (str): folder where the waves data are stored
        """
        self.bounding_box = bounding_box
        self.wind_path = wind_data_path
        self.current_path = current_data_path
        self.waves_path = waves_data_path
        self.earliest_time = earliest_time
        self.latest_time = latest_time
        
        # to initialize the map, one needs to cut out the winds, currents and waves to the bounding box
        # this happens once at the beginning of the simulation, when the map is initiated.
        
        self.winds_data = self.load_dataset_winds(earliest_time, latest_time)
        self.currents_data = self.load_dataset_currents(earliest_time, latest_time)
        self.waves_data = self.load_dataset_waves(earliest_time, latest_time)
    
    
    def load_dataset_currents(self, earliest_time: pd.Timestamp, latest_time: pd.Timestamp):
        
        earliest_year = earliest_time.year
        earliest_month = earliest_time.month
        latest_year = latest_time.year
        latest_month = latest_time.month
        
        path = f"{self.current_path}{earliest_year}/month_{earliest_month}.nc"
        
        dataset = xr.open_dataset(path)
        dataset.close()
        
        if latest_month == earliest_month and latest_year == earliest_year:
            dataset_bounded = dataset.sel(time=slice(earliest_time, latest_time), 
                                          latitude=slice(self.bounding_box[0], self.bounding_box[2]),
                                          longitude=slice(self.bounding_box[1], self.bounding_box[3]))
        else:
            dataset_bounded = dataset.sel(time=slice(earliest_time, None), 
                                          latitude=slice(self.bounding_box[0], self.bounding_box[2]), 
                                          longitude=slice(self.bounding_box[1], self.bounding_box[3]))
        
        if earliest_month != latest_month or earliest_year != latest_year:
            for date in pd.date_range(earliest_time, latest_time, freq="MS"):
                # the flag "MS" in pd.date_range creates an item for each beginning of the month, thus NOT including the first
                further_path = f"{self.current_path}{date.year}/month_{date.month}.nc"
                further_dataset = xr.open_dataset(further_path)
                if (latest_month == date.month) and (latest_year == date.year):
                    # if year-month of the last date calculated are the same as the latest_time, just select up to latest_time.
                    further_dataset_bounded = further_dataset.sel(time=slice(None, latest_time),
                                                                  latitude=slice(self.bounding_box[0], self.bounding_box[2]), 
                                                                  longitude=slice(self.bounding_box[1], self.bounding_box[3]))
                else:
                    # in every other case, it means that we want to take the whole month in our map.
                    further_dataset_bounded = further_dataset.sel(latitude=slice(self.bounding_box[0], self.bounding_box[2]), 
                                                                  longitude=slice(self.bounding_box[1], self.bounding_box[3]))
                
                dataset_bounded = dataset_bounded.combine_first(further_dataset_bounded)
                further_dataset.close()
                
        return dataset_bounded
    
    
    def load_dataset_winds(self, earliest_time: pd.Timestamp, latest_time: pd.Timestamp):
        earliest_year = earliest_time.year
        earliest_month = earliest_time.month
        latest_year = latest_time.year
        latest_month = latest_time.month
        
        path = f"{self.wind_path}{earliest_year}/{earliest_year}_{earliest_month}.nc"
        
        dataset = xr.open_dataset(path)
        dataset.close()
        if latest_month == earliest_month and latest_year == earliest_year:
            dataset_bounded = dataset.where((dataset.latitude >= self.bounding_box[0]) & (dataset.latitude <= self.bounding_box[2]) & 
                                            (dataset.longitude >= self.bounding_box[1]) & (dataset.longitude <= self.bounding_box[3]), drop=True)
            dataset_bounded = dataset_bounded.sel(time=slice(earliest_time, latest_time))
            
        else:
            dataset_bounded = dataset.where((dataset.latitude >= self.bounding_box[0]) & (dataset.latitude <= self.bounding_box[2]) & 
                                            (dataset.longitude >= self.bounding_box[1]) & (dataset.longitude <= self.bounding_box[3]), drop=True)
            dataset_bounded = dataset_bounded.sel(time=slice(earliest_time, None))
        
        if earliest_month != latest_month or earliest_year != latest_year:
            for date in pd.date_range(earliest_time, latest_time, freq="MS"):
                # the flag "MS" in pd.date_range creates an item for each beginning of the month, starting with the second month in the range (the first is calculated above0)
                further_path = f"{self.wind_path}{date.year}/{date.year}_{date.month}.nc"
                further_dataset = xr.open_dataset(further_path)
                further_dataset_bounded = further_dataset.where((dataset.latitude >= self.bounding_box[0]) & (dataset.latitude <= self.bounding_box[2]) & 
                                                                (dataset.longitude >= self.bounding_box[1]) & (dataset.longitude <= self.bounding_box[3]), drop=True)
                dataset_bounded = dataset_bounded.combine_first(further_dataset_bounded)
                further_dataset.close()
                
        return dataset_bounded
    
    
    def load_dataset_waves(self, earliest_time: pd.Timestamp, latest_time: pd.Timestamp):
          
        earliest_year = earliest_time.year
        earliest_month = earliest_time.month
        latest_year = latest_time.year
        latest_month = latest_time.month
        
        path = f"{self.waves_path}{earliest_year}/month_{earliest_month}.nc"
        
        dataset = xr.open_dataset(path)
        dataset.close()
        if latest_month == earliest_month and latest_year == earliest_year:
            dataset_bounded = dataset.sel(time=slice(earliest_time, latest_time), 
                                          latitude=slice(self.bounding_box[0], self.bounding_box[2]), 
                                          longitude=slice(self.bounding_box[1], self.bounding_box[3]))
        else:
            dataset_bounded = dataset.sel(time=slice(earliest_time, None), 
                                          latitude=slice(self.bounding_box[0], self.bounding_box[2]), 
                                          longitude=slice(self.bounding_box[1], self.bounding_box[3]))
        
        if earliest_month != latest_month or earliest_year != latest_year:
            for date in pd.date_range(earliest_time, latest_time, freq="MS"):
                # the flag "MS" in pd.date_range creates an item for each beginning of the month, starting with the second month in the range (the first is calculated above0)
                further_path = f"{self.waves_path}{date.year}/month_{date.month}.nc"
                further_dataset = xr.open_dataset(further_path)
                if (latest_month == date.month) and (latest_year == date.year):
                    # if year-month of the last date calculated are the same as the latest_time, just select up to latest_time.
                    further_dataset_bounded = further_dataset.sel(time=slice(None, latest_time),
                                                                  latitude=slice(self.bounding_box[0], self.bounding_box[2]), 
                                                                  longitude=slice(self.bounding_box[1], self.bounding_box[3]))
                else:
                    # in every other case, it means that we want to take the whole month in our map.
                    further_dataset_bounded = further_dataset.sel(latitude=slice(self.bounding_box[0], self.bounding_box[2]), 
                                                                  longitude=slice(self.bounding_box[1], self.bounding_box[3]))
                
                dataset_bounded = dataset_bounded.combine_first(further_dataset_bounded)
                further_dataset.close()
        
        return dataset_bounded
    
    
    
    def return_local_winds(self, location: np.ndarray, time: pd.Timestamp, radius: float = 0.05) -> np.ndarray:
        """
        Return wind speed and direction given a location and a time. Winds are measured in a square of +/-0.02 degrees around the location, and an average of all the values found
        in that radius is output. The radius is chosen based on the grid size for the CERRA dataset (~2 x 2 km).

        Args:
            location (np.ndarray): Array of latitude and longitude of a location.
            time (pd.Timestamp): Timestamp of time at which one wants the measure.
            radius (float, optional): "Square" radius around which the measure of wind datapoints is performed. Defaults to 0.02.

        Returns:
            np.ndarray: An array containing wind speed (m/s) and wind direction (degrees).
        """
        # The winds dataset longitude is expressed in degrees from 0 to 360, instead of -180 to 180 like the rest of the dataset. Thus:
        latitude_minus = location[0] - radius
        latitude_plus = location[0] + radius
        if location[1] < 0:
            # transform number between -180 and 0 into one between 180 and 360
            longitude_minus = 360 + location[1] - radius
            longitude_plus = 360 + location[1] + radius
        elif location[1] >= 0: 
            longitude_minus = location[1] - radius
            longitude_plus = location[1] + radius
        
        winds_now = self.winds_data.sel(time=time, method="nearest")
        
        if (longitude_minus <= 180 and longitude_plus <= 180) or (longitude_minus > 180 and longitude_plus > 180):
            # if both longitude_minus and longitude_plus are in the same half quadrant, there is no problem in slicing the database
            winds_here_and_now = winds_now.where((winds_now.latitude >= latitude_minus) & (winds_now.latitude <= latitude_plus) &
                                                 (winds_now.longitude >= longitude_minus) & (winds_now.longitude <= longitude_plus), drop = True)
            wind_speed_si = np.nanmean(winds_here_and_now.si10.values)
            wind_direction = np.nanmean(winds_here_and_now.wdir10.values)
            
        elif (longitude_minus > 180 and longitude_plus <= 180):
            # this is the situation where the longitude_plus is in the right quadrant (0 to 180), and longitude_minus in the left quadrant (-180 to 0, transformed into 180 to 360). 
            # in this situation, because of how xarray works, we need to calculate the average quantities for the quadrant < 0 and average them with the avg quantities of the quadrant > 0:
            winds_here_and_now_pos = winds_now.where((winds_now.latitude >= latitude_minus) & (winds_now.latitude <= latitude_plus) &
                                                     (winds_now.longitude >= 0) & (winds_now.longitude <= longitude_plus), drop = True)
            winds_here_and_now_neg = winds_now.where((winds_now.latitude >= latitude_minus) & (winds_now.latitude <= latitude_plus) &
                                                     (winds_now.longitude >= longitude_minus) & (winds_now.longitude < 360), drop = True)
            
            wind_speed_si = (np.nanmean(winds_here_and_now_pos.si10.values) + np.nanmean(winds_here_and_now_neg.si10.values)) / 2
            wind_direction = (np.nanmean(winds_here_and_now_pos.wdir10.values) + np.nanmean(winds_here_and_now_neg.wdir10.values)) / 2
        
        return np.array([wind_speed_si, wind_direction])
        
            
    def return_local_currents(self, location: np.ndarray, time: pd.Timestamp, radius: float = 0.07):
        """
        Return horizontal and vertical components of current speed at a location and a time. Currents are measured in a square of +/-0.05 degrees around the location, 
        and an average of all the values found in that "radius" is output. The radius is chosen based on the grid size for the ECMWF dataset (~5.5 x 5.5 km).

        Args:
            location (np.ndarray): Array of latitude and longitude of a location.
            time (pd.Timestamp): Timestamp of time at which one wants the measure.
            radius (float, optional): "Square" radius around which the measure of wind datapoints is performed. Defaults to 0.02.

        Returns:
            np.ndarray: An array containing horizontal (Eastward) and vertical (Northward) component of the currents speed.
        """
        
        latitude_minus = location[0] - radius
        latitude_plus = location[0] + radius
        longitude_minus = location[1] - radius
        longitude_plus = location[1] + radius
        
        data_now = self.currents_data.sel(time=time, method="nearest")
        
        u = np.nanmean(data_now.uo.sel(latitude=slice(latitude_minus, latitude_plus), 
                            longitude=slice(longitude_minus, longitude_plus)).values)
        v = np.nanmean(data_now.vo.sel(latitude=slice(latitude_minus, latitude_plus), 
                            longitude=slice(longitude_minus, longitude_plus)).values)
        
        return np.array([u, v])
    
    
    def return_local_waves(self, location: np.ndarray, time: pd.Timestamp, radius: float = 0.05) -> float:
        """
        Return wave height at a location and a time. Waves are measured in a square of +/-0.05 degrees around the location, 
        and an average of all the values found in that "radius" is output. The radius is chosen based on the grid size for the ECMWF dataset (~5.5 x 5.5 km).

        Args:
            location (np.ndarray): Array of latitude and longitude of a location.
            time (pd.Timestamp): Timestamp of time at which one wants the measure.
            radius (float, optional): "Square" radius around which the measure of wind datapoints is performed. Defaults to 0.02.

        Returns:
            float: A wave height.
        """
        latitude_minus = location[0] - radius
        latitude_plus = location[0] + radius
        longitude_minus = location[1] - radius
        longitude_plus = location[1] + radius
        
        data_now = self.waves_data.sel(time=time, method="nearest")
        wave_height = np.nanmean(data_now.VHM0.sel(latitude=slice(latitude_minus, latitude_plus), 
                                 longitude=slice(longitude_minus, longitude_plus)).values)
        
        return wave_height
    
    
    def find_closest_land(self, position_on_water: Tuple[float, float], radar_radius: float = 0.2):
        r_earth = 6371 # km

        # select only currents_data, since if u is None, then v is None too.
        # selected_radius = self.currents_data.sel(, method = "nearest")
        selected_radius = self.currents_data.sel(time=self.earliest_time, 
                                              latitude=slice(position_on_water[0] - radar_radius, position_on_water[0] + radar_radius),
                                              longitude=slice(position_on_water[1] - radar_radius, position_on_water[1] + radar_radius))
        # calculate whether there is land anywhere
        nan_count = sum(sum(np.isnan(selected_radius.uo.values)))
        isThereLand = False if nan_count == 0 else True
        
        if isThereLand:
            # selected_radius = selected_radius.to_dataset()
            # calculate matrix of distances
            distances = selected_radius.assign(distance = lambda x: 
                (r_earth*np.pi/180)*np.sqrt((x.uo.latitude - position_on_water[0])**2 + (x.uo.longitude - position_on_water[1])**2)*np.cos(position_on_water[0]*np.pi/180))
            idx_lat_closest = distances.where(distances.uo.isnull()).distance.argmin(dim=['latitude', 'longitude'])['latitude'].values
            idx_lon_closest = distances.where(distances.uo.isnull()).distance.argmin(dim=['latitude', 'longitude'])['longitude'].values
            lat_closest = distances.latitude[idx_lat_closest].values
            lon_closest = distances.longitude[idx_lon_closest].values
            
            # print(lat_closest, lon_closest)

            distance_to_land = distances.distance[idx_lon_closest][idx_lat_closest].values
            angle_to_land = utilities.bearing_from_latlon(position_on_water, [lat_closest, lon_closest])

            return [distance_to_land, angle_to_land]
        
        else:
            return [None, None]
        