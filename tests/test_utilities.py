from pytheas import utilities

def test_distance_km():
    # numbers used as benchmark
    gothenburg = [58, 12]
    locarno = [46, 9]
    
    distance_between_1 = utilities.distance_km(gothenburg, locarno)
    distance_between_2 = utilities.distance_km(locarno, gothenburg)
    
    assert round(distance_between_1, 0) == 1355.0
    assert distance_between_1 == distance_between_2
    

def test_bearing_from_latlon():
    # create two positions that should have between 0 and 90 bearing.
    position_0 = [58, -12]
    position_1 = [59, -13]
    
    calculated_bearing = utilities.bearing_from_latlon(position_0, position_1)
    
    assert 0 < round(calculated_bearing, 0) < 90 
    
    # create positions that should have between 180 and 270
    position_2 = [58, 12]
    position_3 = [57, 13]
    
    calculated_bearing = utilities.bearing_from_latlon(position_2, position_3)
    
    # assert round(calculated_bearing, 0) > 0
    assert 180 < round(calculated_bearing, 0) < 270