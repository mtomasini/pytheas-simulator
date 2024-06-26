from .boat import Boat

class Travel:
    """The Travel class of Pytheas. 
    
    It represents a travel from A to B. This class collects all the different components of the travel of a Boat from A to B on a Map. 
    In the Agent-Based Modelling framework, it represents the Model.
    """
    
    def __init__(self, boat: Boat):
        """Creates a new travel. 

        Args:
            boat (Boat): the boat that will travel.
        """
        self.boat = boat