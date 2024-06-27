import numpy as np
from typing import Tuple

class Boat:
    """
    The Boat class of Pytheas. 
    
    It represents a boat - a logboat, a plank canoe, a longship - you name it. In the Agent-Based Modelling framework, the Boat represents a basic Agent.
    
    """
    
    def __init__(self, craft: str, latitude: float, longitude: float, target: Tuple[float, float], polar_diagram: np.ndarray = None):
        """Creates a new boat.

        Args:
            craft (str): type of boat (e.g. "Hjortspring")
            longitude (float): current longitude of the boat. It gets updated when running move_step().
            latitude (float): current latitude of the boat. It gets updated when running move_step().
            target (Tuple[float, float]): tuple of lon/lat of the target.
            polar_diagram (np.ndarray): table representing the boat polar diagram. Defaults to None.
        """
        self.craft = craft
        self.latitude = latitude
        self.longitude = longitude
        self.target = target
        self.polar_diagram = polar_diagram
        
        self.trajectory = [(latitude, longitude)]
    
    @staticmethod     
    def calculate_displacement(polar_diagram: np.ndarray, local_winds: np.ndarray, local_currents: np.ndarray):
        # TODO write displacement function for a boat with polar diagram, given winds and currents
        return [0, 0]
    
    @staticmethod     
    def generic_displacement(local_winds: np.ndarray, local_currents: np.ndarray):
        # TODO write displacement function for a boat without polar diagram, given winds and currents
        return [0, 0]
    
    def move_boat(self, local_winds: np.ndarray,
                  local_currents: np.ndarray):
        
        if self.polar_diagram is not None:
            new_longitude, new_latitude = Boat.calculate_displacement(self.polar_diagram, local_winds, local_currents)
        else:
            new_longitude, new_latitude = Boat.generic_displacement(local_winds, local_currents)
            
        self.trajectory.append((new_longitude, new_latitude))
        self.longitude = new_longitude
        self.latitude = new_latitude