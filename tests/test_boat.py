from pytheas import boat

def test_calculate_displacement():
    pass

def test_generic_displacement():
    pass

def test_move_boat():
    test_boat = boat.Boat(
        craft = "Hjortspring",
        latitude = 58,
        longitude = 12,
        target = [1,1] 
    )
    
    assert len(test_boat.trajectory) == 1
    assert test_boat.trajectory == [(58, 12)]
    
    # if winds and currents are 0, there should be no movement, but still append a point
    test_boat.move_boat([0, 0], [0, 0])
    assert len(test_boat.trajectory)
    assert test_boat.trajectory[-1] == (58, 12)
    # test_boat.move_boat([])