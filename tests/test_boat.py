import numpy as np
import pandas as pd
from pytheas import boat

def test_calculate_displacement():
    
    SPEED_POLAR_DIAGRAM_PATH = './configs/hjortspring_speeds_16pad_3000kg_44cad_75oars.txt'
    LEEWAY_POLAR_DIAGRAM_PATH = './configs/hjortspring_leeway_16pad_3000kg_44cad_75oars.txt'
    speed_polar_diagram = pd.read_csv(SPEED_POLAR_DIAGRAM_PATH, sep="\t", index_col=0)
    leeway_polar_diagram = pd.read_csv(LEEWAY_POLAR_DIAGRAM_PATH, sep="\t", index_col=0)
    timestep = 15
    
    test_boat = boat.Boat(
        craft = "Hjortspring",
        latitude = 58,
        longitude = 12,
        speed_polar_diagram=speed_polar_diagram,
        leeway_polar_diagram=leeway_polar_diagram,
        target = [59, 12]
    )
    
    # with no winds and no currents, if bearing = 0 (North), there is no displacement in dx and dy is positive
    winds = np.zeros(2)
    currents = np.zeros(2)
    bearing = 0
    displacement = test_boat.calculate_displacement(winds, currents, bearing, timestep)
    assert displacement[0] - 0 < 1e-10
    assert displacement[1] > 0
    
    # with no winds and no currents, if bearing = 90 (East), there is no displacement in dy and dx is positive
    winds = np.zeros(2)
    currents = np.zeros(2)
    bearing = 90
    displacement = test_boat.calculate_displacement(winds, currents, bearing, timestep)
    assert displacement[0] > 0
    assert displacement[1] - 0 < 1e-10
    
    # with no winds and no currents, if bearing = 180 (South), there is no displacement in dx and dy is negative
    winds = np.zeros(2)
    currents = np.zeros(2)
    bearing = 180
    displacement = test_boat.calculate_displacement(winds, currents, bearing, timestep)
    assert displacement[0] - 0 < 1e-10
    assert displacement[1] < 0
    
    # with no winds and no currents, if bearing = 270 (West), there is no displacement in dy and dx is negative
    winds = np.zeros(2)
    currents = np.zeros(2)
    bearing = 270
    displacement = test_boat.calculate_displacement(winds, currents, bearing, timestep)
    assert displacement[0] < 0
    assert displacement[1] - 0 < 1e-10
    
    # with slight Northern winds, bearing N, and currents at 45 degrees, the boat should move towards NNE (= positive dx, positive dy)
    winds = np.array([0.05, 0])
    currents = np.array([0.5, 0.5])
    bearing = 0
    displacement = test_boat.calculate_displacement(winds, currents, bearing, timestep)
    assert displacement[0] > 0
    assert displacement[1] > 0
    
    # with slight Eastern winds, bearing N, and currents at 315 degrees, the boat should move towards NW (= negative dx, positive dy)
    winds = np.array([0.05, 90])
    currents = np.array([-0.5, 0.5])
    bearing = 0
    displacement = test_boat.calculate_displacement(winds, currents, bearing, timestep)
    assert displacement[0] < 0
    assert displacement[1] > 0
    
    # No winds, no currents, bearing 0 should cause a northerly displacement of 3.402 km
    winds = np.array([0.0, 0.0])
    currents = np.array([0.0, 0.0])
    bearing = 0
    displacement = test_boat.calculate_displacement(winds, currents, bearing, timestep)
    assert displacement[1] - 3.402 < 1e-8
    
    # Example calculated by hand!
    winds = np.array([10.0, 90.0])
    currents = np.array([-0.5, 0.5])
    bearing = 0
    displacement = test_boat.calculate_displacement(winds, currents, bearing, timestep)   
    assert displacement[0] - (-0.6083) < 1e-3
    assert displacement[1] - 0.8850 < 1e-3
    

def test_generic_displacement():
    pass

def test_move_boat():
    SPEED_POLAR_DIAGRAM_PATH = './configs/hjortspring_speeds_16pad_3000kg_44cad_75oars.txt'
    LEEWAY_POLAR_DIAGRAM_PATH = './configs/hjortspring_leeway_16pad_3000kg_44cad_75oars.txt'
    speed_polar_diagram = pd.read_csv(SPEED_POLAR_DIAGRAM_PATH, sep="\t", index_col=0)
    leeway_polar_diagram = pd.read_csv(LEEWAY_POLAR_DIAGRAM_PATH, sep="\t", index_col=0)
    timestep = 15
    
    test_boat = boat.Boat(
        craft = "Hjortspring",
        latitude = 58,
        longitude = 12,
        speed_polar_diagram=speed_polar_diagram,
        leeway_polar_diagram=leeway_polar_diagram,
        target = [59, 12]
    )
    
    old_latitude = test_boat.latitude
    old_longitude = test_boat.longitude
    
    # with slight Northern winds, bearing N, and currents at 45 degrees, the boat should move towards NNE
    winds = np.array([0.05, 0])
    currents = np.array([0.5, 0.5])
    test_boat.move_boat(winds, currents, timestep)
    assert len(test_boat.trajectory) == 2
    assert test_boat.trajectory[-1][0] > old_latitude
    assert test_boat.trajectory[-1][1] > old_longitude
    
    # with slight Eastern winds, bearing N, and currents at 315 degrees, the boat should move towards NW
    winds = np.array([0.05, 90])
    currents = np.array([-0.5, 0.5])
    old_latitude = test_boat.latitude
    old_longitude = test_boat.longitude
    test_boat.move_boat(winds, currents, timestep)
    assert len(test_boat.trajectory) == 3
    assert test_boat.trajectory[-1][0] > old_latitude
    assert test_boat.trajectory[-1][1] < old_longitude