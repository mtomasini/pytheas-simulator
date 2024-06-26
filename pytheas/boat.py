class Boat:
    """
    The Boat class of Pytheas. 
    
    It represents a boat - a logboat, a plank canoe, a longship - you name it. In the Agent-Based Modelling framework, the Boat represents a basic Agent.
    
    """
    
    def __init__(self, craft: str):
        """Creates a new boat.

        Args:
            craft (str): type of boat (e.g. "Hjortspring")
        """
        self.craft = craft