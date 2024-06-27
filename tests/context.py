# created from https://docs.python-guide.org/writing/structure/

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytheas

boat = pytheas.boat.Boat(
        craft = "Hjortspring",
        latitude = 0,
        longitude = 0,
        target = [1,1] 
    )
print(boat.craft)