import numpy as np
import pandas as pd
from typing import Tuple
import xarray as xr
import xoak

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
        
        
        # TODO measure data as averages of the boat with a radius of 0.02 around! 0.02 * 111km = ~2.2 km
        
    
    
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
                # the flag "MS" in pd.date_range creates an item for each beginning of the month, starting with the second month in the range (the first is calculated above0)
                further_path = f"{self.current_path}{date.year}/month_{date.month}.nc"
                further_dataset = xr.open_dataset(further_path)
                further_dataset_bounded = further_dataset.xoak.sel(latitude=xr.DataArray([self.bounding_box[0], self.bounding_box[2]]), 
                                                                   longitude=xr.DataArray([self.bounding_box[1], self.bounding_box[3]]))
                
                
                further_dataset.sel(latitude=slice(self.bounding_box[0], self.bounding_box[2]), 
                                                              longitude=slice(self.bounding_box[1], self.bounding_box[3]))
                dataset_bounded = dataset_bounded.combine_first(further_dataset_bounded)
                further_dataset.close()
                
        return dataset_bounded
    
    
    def load_dataset_winds(self, earliest_time: pd.Timestamp, latest_time: pd.Timestamp):
        # TODO re-consider that winds longitude is labelled from 0 to 360, instead of -180 to 180
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
                further_path = f"{self.current_path}{date.year}/{date.year}_{date.month}.nc"
                further_dataset = xr.open_dataset(further_path)
                further_dataset_bounded = further_dataset.where((dataset.latitude >= self.bounding_box[0]) & (dataset.latitude <= self.bounding_box[2]) & 
                                                                (dataset.longitude >= self.bounding_box[1]) & (dataset.longitude <= self.bounding_box[3]), drop=True)
                dataset_bounded = dataset_bounded.combine_first(further_dataset)
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
                further_path = f"{self.current_path}{date.year}/month_{date.month}.nc"
                further_dataset = xr.open_dataset(further_path)
                dataset_bounded = dataset_bounded.combine_first(further_dataset)
                further_dataset.close()
        
        return dataset_bounded
    
    
    
    def measure_winds(location: np.ndarray, time: pd.Timestamp, radius: float = 0.02):
        # TODO write wind measuring function
        
        pass
    
    def measure_currents(location: np.ndarray, time: pd.Timestamp, radius: float = 0.02):
        # TODO write wind measuring function
        pass
    
    def measure_waves (location: np.ndarray, time: pd.Timestamp, radius: float = 0.02):
        # TODO write waves measuring function
        pass