import numpy as np
import pandas as pd
from pytheas import boat

def test_calculate_displacement():
    
    SPEED_POLAR_DIAGRAM_PATH = './configs/hjortspring_speeds_16pad_3000kg_44cad_75oars.txt'
    LEEWAY_POLAR_DIAGRAM_PATH = './configs/hjortspring_leeway_16pad_3000kg_44cad_75oars.txt'
    speed_polar_diagram = pd.read_csv(SPEED_POLAR_DIAGRAM_PATH, sep="\t", index_col=0)
    leeway_polar_diagram = pd.read_csv(LEEWAY_POLAR_DIAGRAM_PATH, sep="\t", index_col=0)
    
    test_boat = boat.Boat(
        craft = "Hjortspring",
        latitude = 58,
        longitude = -12,
        speed_polar_diagram=speed_polar_diagram,
        leeway_polar_diagram=leeway_polar_diagram,
        target = [57,-12]
    )
    
    # with no winds and no currents, if bearing = 0 (North), there is no displacement in dx and dy is positive
    winds = np.zeros(2)
    currents = np.zeros(2)
    bearing = 0
    displacement = test_boat.calculate_displacement(winds, currents, bearing)
    assert displacement[0] < 1e-10
    assert displacement[1] > 0
    
    # with no winds and no currents, if bearing = 90 (East), there is no displacement in dy and dx is positive
    winds = np.zeros(2)
    currents = np.zeros(2)
    bearing = 90
    displacement = test_boat.calculate_displacement(winds, currents, bearing)
    assert displacement[0] > 0
    assert displacement[1] < 1e-10
    
    # with no winds and no currents, if bearing = 180 (South), there is no displacement in dx and dy is negative
    winds = np.zeros(2)
    currents = np.zeros(2)
    bearing = 180
    displacement = test_boat.calculate_displacement(winds, currents, bearing)
    assert displacement[0] < 1e-10
    assert displacement[1] < 0
    
    # with no winds and no currents, if bearing = 270 (West), there is no displacement in dy and dx is negative
    winds = np.zeros(2)
    currents = np.zeros(2)
    bearing = 270
    displacement = test_boat.calculate_displacement(winds, currents, bearing)
    assert displacement[0] < 0
    assert displacement[1] < 1e-10
    

def test_generic_displacement():
    pass

# def test_move_boat():
#     test_boat = boat.Boat(
#         craft = "Hjortspring",
#         latitude = 58,
#         longitude = 12,
#         target = [1,1] 
#     )
    
#     assert len(test_boat.trajectory) == 1
#     assert test_boat.trajectory == [(58, 12)]
    
#     # if winds and currents are 0, there should be no movement, but still append a point
#     test_boat.move_boat([0, 0], [0, 0])
#     assert len(test_boat.trajectory)
#     assert test_boat.trajectory[-1] == (58, 12)
    
#     # test_boat.move_boat([])