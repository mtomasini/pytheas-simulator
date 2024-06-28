import numpy as np
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
    
    
def test_geographic_angle_to_xy():
    # a geographic angle of 0 corresponds to a trigonometric angle of 90
    # a geographic angle of 30 corresponds to a trigonometric angle of 60
    # a geographic angle of 100 corresponds to a trigonometric angle of 350
    # a geographic angle of 240 corresponds to a trigonometric angle of 210
    # a geogrephic angle of 330 corresponds to a trigonometric angle of 120
    
    for angle_geo, angle_tri in [(0, 90), (30, 60), (100, 350), (240, 210), (330, 120)]:
        angle_tri_rad = np.deg2rad(angle_tri)
        dxy_geo = utilities.geographic_angle_to_xy(angle_geo)
        dxy_rad = np.array([np.cos(angle_tri_rad), np.sin(angle_tri_rad)])
        assert np.allclose(dxy_geo, dxy_rad , rtol=1e-8, atol=1e-8)
        

def test_difference_between_geographic_angles():
    # if bearing is 50 and angle_wind is 60, difference is +10
    # if bearing is 60 and angle_wind is 50, difference is -10
    assert utilities.difference_between_geographic_angles(50.0, 60.0) == 10.0
    assert utilities.difference_between_geographic_angles(50.0, 60.0) == -utilities.difference_between_geographic_angles(60.0, 50.0)
    
    # if bearing is 190 and angle_wind is 200, difference is 10
    assert utilities.difference_between_geographic_angles(190.0, 200.0) == 10.0
    
    # if bearing is 30 and angle_wind is 350, difference is -40
    assert utilities.difference_between_geographic_angles(30.0, 350.0) == -40.0
    
    # if bearing is 190 and angle_wind is 30, difference is 160
    assert utilities.difference_between_geographic_angles(190.0, 30.0) == 160.0
    
    # if bearing is 150 and angle_wind is 300, difference is 150
    assert utilities.difference_between_geographic_angles(150.0, 300.0) == 150.0