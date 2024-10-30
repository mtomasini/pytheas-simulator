"""
    The map object of Pytheas.
    
    It represents the space over which the Boat will travel. It is a continuous space where we super impose three distinct layers of data: winds, currents and waves.
    The wind and current layers directly affect the movement of the boat, while the wave layer is necessary to record encountered waves. 
    In the Agent-Based Modelling framework, the Map corresponds to the Space. 
"""
    
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import xarray as xr

from pytheas import search
from pytheas import utilities


class Map:
    """
    The base Map object in Pytheas.
    
    Attributes:
        bounding_box (List[float, float, float, float]): Bounding box including [min_latitude, min_longitude, max_latitude, max_longitude].
        earliest_time (pd.Timestamp): Earliest time included in the Map dataset.
        latest_time (pd.Timestamp): Latest time included in the Map dataset.
        wind_path (str): Folder where the wind data are stored.
        current_path (str): Folder where the current data are stored.
        waves_path (str): Folder where the waves data are stored.
        winds_data (xr.DataArray): Data array containing winds data (each point is speed/angle).
        currents_data (xr.DataArray): Data array containing currents data (each point is speed in x/y).
        waves_data (xr.DataArray): Data array containing waves height data (each point is wave height).
    """
    
    def __init__(self, 
                 bounding_box: Tuple[float, float, float, float], 
                 earliest_time: pd.Timestamp, 
                 latest_time: pd.Timestamp,
                 wind_data_path: str, 
                 current_data_path: str, 
                 waves_data_path: str):
        """Creates new map.

        Args:
            bounding_box (List[float, float, float, float]): Bounding box including [min_latitude, min_longitude, max_latitude, max_longitude].
            earliest_time (pd.Timestamp): Earliest time included in the Map dataset.
            latest_time (pd.Timestamp): Latest time included in the Map dataset.
            wind_data_path (str): Folder where the wind data are stored.
            current_data_path (str): Folder where the current data are stored.
            waves_data_path (str): Folder where the waves data are stored.
        """
        self.bounding_box = bounding_box
        self.earliest_time = earliest_time
        self.latest_time = latest_time
        self.wind_path = wind_data_path
        self.current_path = current_data_path
        self.waves_path = waves_data_path

        # to initialize the map, one needs to cut out the winds, currents and waves to the bounding box
        # this happens once at the beginning of the simulation, when the map is initiated.
        
        self.winds_data = self.load_dataset_winds()
        self.currents_data = self.load_dataset_currents()
        self.waves_data = self.load_dataset_waves()
    
    
    def load_dataset_currents(self) -> xr.DataArray:
        """
        Load the dataset for currents in xarray's DataArray format.

        Returns:
            xr.DataArray: Data array containing the currents data.
        """
        
        earliest_year = self.earliest_time.year
        earliest_month = self.earliest_time.month
        latest_year = self.latest_time.year
        latest_month = self.latest_time.month
        
        path = f"{self.current_path}{earliest_year}/month_{earliest_month}.nc"
        
        dataset = xr.open_dataset(path)
        dataset.close()
        
        if latest_month == earliest_month and latest_year == earliest_year:
            dataset_bounded = dataset.sel(time=slice(self.earliest_time, self.latest_time), 
                                          latitude=slice(self.bounding_box[0], self.bounding_box[2]),
                                          longitude=slice(self.bounding_box[1], self.bounding_box[3]))
        else:
            dataset_bounded = dataset.sel(time=slice(self.earliest_time, None), 
                                          latitude=slice(self.bounding_box[0], self.bounding_box[2]), 
                                          longitude=slice(self.bounding_box[1], self.bounding_box[3]))
        
        if earliest_month != latest_month or earliest_year != latest_year:
            for date in pd.date_range(self.earliest_time, self.latest_time, freq="MS"):
                # the flag "MS" in pd.date_range creates an item for each beginning of the month, thus NOT including the first
                further_path = f"{self.current_path}{date.year}/month_{date.month}.nc"
                further_dataset = xr.open_dataset(further_path)
                if (latest_month == date.month) and (latest_year == date.year):
                    # if year-month of the last date calculated are the same as the latest_time, just select up to latest_time.
                    further_dataset_bounded = further_dataset.sel(time=slice(None, self.latest_time),
                                                                  latitude=slice(self.bounding_box[0], self.bounding_box[2]), 
                                                                  longitude=slice(self.bounding_box[1], self.bounding_box[3]))
                else:
                    # in every other case, it means that we want to take the whole month in our map.
                    further_dataset_bounded = further_dataset.sel(latitude=slice(self.bounding_box[0], self.bounding_box[2]), 
                                                                  longitude=slice(self.bounding_box[1], self.bounding_box[3]))
                
                dataset_bounded = dataset_bounded.combine_first(further_dataset_bounded)
                further_dataset.close()
                
        return dataset_bounded
    
    
    def load_dataset_winds(self) -> xr.DataArray:
        """
        Load the dataset for winds in xarray's DataArray format.

        Returns:
            xr.DataArray: Data array containing the winds data.
        """
        earliest_year = self.earliest_time.year
        earliest_month = self.earliest_time.month
        latest_year = self.latest_time.year
        latest_month = self.latest_time.month
        
        path = f"{self.wind_path}{earliest_year}/{earliest_year}_{earliest_month}.nc"
        
        dataset = xr.open_dataset(path)
        dataset.close()
        if latest_month == earliest_month and latest_year == earliest_year:
            dataset_bounded = dataset.where((dataset.latitude >= self.bounding_box[0]) & (dataset.latitude <= self.bounding_box[2]) & 
                                            (dataset.longitude >= self.bounding_box[1]) & (dataset.longitude <= self.bounding_box[3]), drop=True)
            dataset_bounded = dataset_bounded.sel(time=slice(self.earliest_time, self.latest_time))
            
        else:
            dataset_bounded = dataset.where((dataset.latitude >= self.bounding_box[0]) & (dataset.latitude <= self.bounding_box[2]) & 
                                            (dataset.longitude >= self.bounding_box[1]) & (dataset.longitude <= self.bounding_box[3]), drop=True)
            dataset_bounded = dataset_bounded.sel(time=slice(self.earliest_time, None))
        
        if earliest_month != latest_month or earliest_year != latest_year:
            for date in pd.date_range(self.earliest_time, self.latest_time, freq="MS"):
                # the flag "MS" in pd.date_range creates an item for each beginning of the month, starting with the second month in the range (the first is calculated above0)
                further_path = f"{self.wind_path}{date.year}/{date.year}_{date.month}.nc"
                further_dataset = xr.open_dataset(further_path)
                further_dataset_bounded = further_dataset.where((dataset.latitude >= self.bounding_box[0]) & (dataset.latitude <= self.bounding_box[2]) & 
                                                                (dataset.longitude >= self.bounding_box[1]) & (dataset.longitude <= self.bounding_box[3]), drop=True)
                dataset_bounded = dataset_bounded.combine_first(further_dataset_bounded)
                further_dataset.close()
                
        return dataset_bounded
    
    
    def load_dataset_waves(self):
        """
        Load the dataset for waves in xarray's DataArray format.

        Returns:
            xr.DataArray: Data array containing the waves data.
        """
        earliest_year = self.earliest_time.year
        earliest_month = self.earliest_time.month
        latest_year = self.latest_time.year
        latest_month = self.latest_time.month
        
        path = f"{self.waves_path}{earliest_year}/month_{earliest_month}.nc"
        
        dataset = xr.open_dataset(path)
        dataset.close()
        if latest_month == earliest_month and latest_year == earliest_year:
            dataset_bounded = dataset.sel(time=slice(self.earliest_time, self.latest_time), 
                                          latitude=slice(self.bounding_box[0], self.bounding_box[2]), 
                                          longitude=slice(self.bounding_box[1], self.bounding_box[3]))
        else:
            dataset_bounded = dataset.sel(time=slice(self.earliest_time, None), 
                                          latitude=slice(self.bounding_box[0], self.bounding_box[2]), 
                                          longitude=slice(self.bounding_box[1], self.bounding_box[3]))
        
        if earliest_month != latest_month or earliest_year != latest_year:
            for date in pd.date_range(self.earliest_time, self.latest_time, freq="MS"):
                # the flag "MS" in pd.date_range creates an item for each beginning of the month, starting with the second month in the range (the first is calculated above0)
                further_path = f"{self.waves_path}{date.year}/month_{date.month}.nc"
                further_dataset = xr.open_dataset(further_path)
                if (latest_month == date.month) and (latest_year == date.year):
                    # if year-month of the last date calculated are the same as the latest_time, just select up to latest_time.
                    further_dataset_bounded = further_dataset.sel(time=slice(None, self.latest_time),
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
        Return wind speed and direction given a location and a time. Winds are measured in a square of +/-0.05 degrees around the location, and an average of all the values found
        in that radius is output. The radius is chosen based on the grid size for the CERRA dataset (~2 x 2 km).

        Args:
            location (np.ndarray): Array of latitude and longitude of a location.
            time (pd.Timestamp): Timestamp of time at which one wants the measure.
            radius (float, optional): "Square" radius around which the measure of wind datapoints is performed. Defaults to 0.05.

        Returns:
            np.ndarray: An array containing wind speed (m/s) and wind direction (degrees).
        """
        winds_now = self.winds_data.sel(time=time, method="nearest")

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
        
            
    def return_local_currents(self, location: np.ndarray, time: pd.Timestamp, average: bool = True, radius: float = 0.07) -> np.ndarray:
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
        
        # TOFIX this function returns a mean ignoring nan. It's good when trying to find an average speed, but it's not good when detecting whethere one is on land or not!
        if average:
            u = np.nanmean(data_now.uo.sel(latitude=slice(latitude_minus, latitude_plus), 
                                longitude=slice(longitude_minus, longitude_plus)).values)
            v = np.nanmean(data_now.vo.sel(latitude=slice(latitude_minus, latitude_plus), 
                                longitude=slice(longitude_minus, longitude_plus)).values)
        else:
            u = data_now.uo.sel(latitude=location[0], longitude=location[1], method="nearest").values
            v = data_now.vo.sel(latitude=location[0], longitude=location[1], method="nearest").values
        
        return np.array([u, v])
    
    
    def return_local_waves(self, location: np.ndarray, time: pd.Timestamp, radius: float = 0.07) -> float:
        """
        Return wave height at a location and a time. Waves are measured in a square of +/-0.07 degrees around the location, 
        and an average of all the values found in that "radius" is output. The radius is chosen based on the grid size for the ECMWF dataset (~5.5 x 5.5 km).

        Args:
            location (np.ndarray): Array of latitude and longitude of a location.
            time (pd.Timestamp): Timestamp of time at which one wants the measure.
            radius (float, optional): "Square" radius around which the measure of wind datapoints is performed. Defaults to 0.05.

        Returns:
            float: A wave height.
        """
        latitude_minus = location[0] - radius
        latitude_plus = location[0] + radius
        longitude_minus = location[1] - radius
        longitude_plus = location[1] + radius
        
        data_now = self.waves_data.sel(time=time, method="nearest")
        data_to_average = data_now.VHM0.sel(latitude=slice(latitude_minus, latitude_plus), longitude=slice(longitude_minus, longitude_plus)).values
        if data_to_average.size > 0:
            wave_height = np.nanmean(data_to_average)
        else:
            wave_height = None

        return wave_height
    
    
    def find_closest_land(self, position_on_water: Tuple[float, float], radar_radius: float = 0.2) -> Tuple[float, float]:
        """
        Find land closest to a point in water. 

        Args:
            position_on_water (Tuple[float, float]): Position on the water in latitude / longitude.
            radar_radius (float, optional): Radius within which to look for land, in degrees. Defaults to 0.2 degrees.

        Returns:
            Tuple[float, float]: Distance from closest land and angle to closest land.
        """
        r_earth = 6371 # km

        # select only currents_data, since if u is None, then v is None too.
        data_now = self.currents_data.sel(time=self.earliest_time, method = "nearest")
        selected_radius = data_now.sel(latitude=slice(position_on_water[0] - radar_radius, position_on_water[0] + radar_radius),
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

            distance_to_land = distances.distance[idx_lat_closest][idx_lon_closest].values
            angle_to_land = utilities.bearing_from_latlon(position_on_water, [lat_closest, lon_closest])

            return [distance_to_land, angle_to_land]
        
        else:
            return [None, None]
       
        
    def find_closest_water(self, position_on_land: Tuple[float, float], radar_radius: float = 10) -> Tuple[float, float]:
        """
        Find coordinates in water closest to a point on land.

        Args:
            position_on_land (Tuple[float, float]): Position on land in lon/lat format.
            radar_radius (float, optional): Radius within which to look for water, in degrees. Defaults to 10 degrees.

        Returns:
            Tuple[float, float]: Lat/lon of closest point.
        """
        r_earth = 6371 # km

        # select only currents_data, since if u is None, then v is None too.
        data_now = self.currents_data.sel(time=self.earliest_time, method = "nearest")
        selected_radius = data_now.sel(latitude=slice(position_on_land[0] - radar_radius, position_on_land[0] + radar_radius),
                                        longitude=slice(position_on_land[1] - radar_radius, position_on_land[1] + radar_radius))
        # calculate whether there is land anywhere
        values_count = sum(sum(selected_radius.uo.notnull().values))
        isThereWater = False if values_count == 0 else True
            
        if isThereWater:
            distances = selected_radius.assign(distance = lambda x: 
                (r_earth*np.pi/180)*np.sqrt((x.uo.latitude - position_on_land[0])**2 + 
                                            (x.uo.longitude - position_on_land[1])**2)*np.cos(position_on_land[0]*np.pi/180))
            idx_lat_closest = distances.where(distances.uo.notnull()).distance.argmin(dim=['latitude', 'longitude'])['latitude'].values
            idx_lon_closest = distances.where(distances.uo.notnull()).distance.argmin(dim=['latitude', 'longitude'])['longitude'].values
                
            lat_closest = distances.latitude[idx_lat_closest].values
            lon_closest = distances.longitude[idx_lon_closest].values

            return [lat_closest.item(), lon_closest.item()]
            
        else:
            return [None, None]

    
    def find_nearest_index_to_point(self, point: Tuple[float, float]) -> Tuple[int, int]:
        """
        Find the index of the latitude/longitude in the data closest to a given point.

        Args:
            point (Tuple[float, float]): A geographical point in lat/lon format.

        Returns:
            Tuple[int, int]: x index and y index of closest coordinate in the data to a given point.
        """
        id_lat = min(enumerate(self.currents_data.latitude.values), key=lambda x: abs(x[1] - point[0]))
        id_lon = min(enumerate(self.currents_data.longitude.values), key=lambda x: abs(x[1] - point[1]))
    
        return id_lat[0], id_lon[0]
    

    def create_route(self, launching_site: Tuple[float, float], landing_site: Tuple[float, float], target_interval: int = 5, **kwargs):
        """
        Create a route that hugs the coast from a launching site to a landing site. The kwargs need to be `weights` (a list) 
        and `iterations` (also a list, of the same length as `weights`) to modify the creation of different "weight corridors" 
        along the shoreline.

        Args:
            launching_site (Tuple[float, float]): Launching site in lat/lon format.
            landing_site (Tuple[float, float]): Landing site in in lat/lon format.
            target_interval (int): Interval between the nodes in the route. Defaults to 5.

        Raises:
            RuntimeError: Raised if the algorithm was unable to find a route.

        Returns:
            List[Tuple[float, float]]: List of coordinates through which the routes goes.
        """
        grid = search.WeightedGrid.from_map(self.currents_data.uo.sel(time=self.earliest_time, method="nearest"), **kwargs)
        astar = search.Astar(grid)

        (i,j) = self.find_nearest_index_to_point(launching_site)
        (i_goal, j_goal) = self.find_nearest_index_to_point(landing_site)

        came_from, cost_so_far = astar.search(start=(i,j), goal=(i_goal,j_goal))

        # Chart the route
        try:
            route = astar.reconstruct_path(came_from, start=(i,j), goal=(i_goal,j_goal))
            route = [(self.currents_data.latitude[i].values.item(), self.currents_data.longitude[j].values.item()) for i, j in route]
            route = [route[0], *route[1:-2:target_interval], route[-1]]
            route.reverse()
            return route

        except Exception as e:
            raise RuntimeError("No possible route") from e
        
        