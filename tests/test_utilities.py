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
    # numbers used as benchmark
    gothenburg = [58, 12]
    locarno = [46, 9]
    
    should_be = 170
    calculated_bearing = utilities.bearing_from_latlon(gothenburg, locarno)
    
    assert  round(calculated_bearing, 0) == should_be