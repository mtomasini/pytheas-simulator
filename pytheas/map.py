import numpy as np
import pandas as pd

class Map:
    """
    The map object of Pytheas.
    
    It represents the space over which the Boat will travel. It is a continuous space where we super impose three distinct layers of data: winds, currents and waves.
    The wind and current layers directly affect the movement of the boat, while the wave layer is necessary to record encountered waves. 
    In the Agent-Based Modelling framework, the Map corresponds to the Space. 
    """
    
    def __init__(self, wind_data_path: str, current_data_path: str, waves_data_path: str):
        """Creates new map.

        Args:
            wind_data_path (str): folder where the wind data are stored
            current_data_path (str): folder where the current data are stored
            waves_data_path (str): folder where the waves data are stored
        """
        self.wind = wind_data_path
        self.current = current_data_path
        self.waves = waves_data_path
        
    def measure_winds(location: np.ndarray, time: pd.Timestamp):
        # TODO write wind measuring function
        pass
    
    def measure_currents(location: np.ndarray, time: pd.Timestamp):
        # TODO write current measuring function
        pass
    
    def measure_waves (location: np.ndarray, time: pd.Timestamp):
        # TODO write waves measuring function
        pass