from pytheas import boat

def test_calculate_displacement():
    pass

def test_generic_displacement():
    pass

def test_move_boat():
    test_boat = boat.Boat(
        craft = "Hjortspring",
        latitude = 0,
        longitude = 0,
        target = [1,1] 
    )
    
    assert len(test_boat.trajectory) == 1
    assert test_boat.trajectory == [(0, 0)]
    
    # if winds and currents are 0, there should be no movement, but still append a point
    test_boat.move_boat([0, 0], [0, 0])
    assert len(test_boat.trajectory)
    assert test_boat.trajectory[-1] == (0, 0)