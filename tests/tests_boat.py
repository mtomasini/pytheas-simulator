from .context import pytheas

def test_calculate_displacement():
    pass

def test_generic_displacement():
    pass

def test_move_boat():
    boat = pytheas.boat.Boat(
        craft = "Hjortspring",
        latitude = 0,
        longitude = 0,
        target = [1,1] 
    )
    
    assert len(boat.trajectory) == 1
    assert boat.trajectory == [(0, 0)]
    
    # if winds and currents are 0, there should be no movement, but still append a point
    boat.move_boat([0, 0], [0, 0])
    assert len(boat.trajectory)
    assert boat.trajectory[-1] == [0, 0]