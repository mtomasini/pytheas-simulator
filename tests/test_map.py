import pandas as pd
from pytheas.map import Map


def local_test_load_map_data():
    # WORKED FINE. CHANGED NAME OF TEST TO AVOID AUTOMATIC TEST INTEGRATION
    WIND_DATA = "/media/mtomasini/LaCie/LIR/Full_data/winds_cerra/"
    CURRENT_DATA = "/media/mtomasini/LaCie/LIR/Full_data/currents_northwest/"
    WAVES_DATA = "/media/mtomasini/LaCie/LIR/Full_data/waves_northwest/"
    
    bounding_box = [56.3, 5.8, 58.8, 13.1] # bounding_box for the Skagerrak strait
    testing_map = Map(bounding_box = bounding_box, 
                      earliest_time = pd.Timestamp('1995-12-15'),
                      latest_time = pd.Timestamp('1996-01-14'),
                      wind_data_path=WIND_DATA,
                      current_data_path=CURRENT_DATA,
                      waves_data_path=WAVES_DATA)
    
    assert testing_map.winds_data.latitude.max() > bounding_box[2]
    assert testing_map.currents_data.time.max() < pd.Timestamp('1996-01-15')
    assert testing_map.waves_data.time.min() > pd.Timestamp('1995-12-14')
    
    assert testing_map.return_local_winds([57.7, 9], pd.Timestamp('1995-12-31')) is not None
    assert testing_map.return_local_currents([57.7, 9], pd.Timestamp('1995-12-31')) is not None
    assert testing_map.return_local_waves([57.7, 9], pd.Timestamp('1995-12-31')) is not None
    
    
def local_test_find_closest_land():
    # WORKED FINE. CHANGED NAME OF TEST TO AVOID AUTOMATIC TEST INTEGRATION
    WIND_DATA = "/media/mtomasini/LaCie/LIR/Full_data/winds_cerra/"
    CURRENT_DATA = "/media/mtomasini/LaCie/LIR/Full_data/currents_northwest/"
    WAVES_DATA = "/media/mtomasini/LaCie/LIR/Full_data/waves_northwest/"
    
    bounding_box = [56.3, 5.0, 60.0, 13.1] # bounding_box for the Skagerrak strait
    testing_map = Map(bounding_box = bounding_box, 
                      earliest_time = pd.Timestamp('1995-12-15'),
                      latest_time = pd.Timestamp('1995-12-16'),
                      wind_data_path=WIND_DATA,
                      current_data_path=CURRENT_DATA,
                      waves_data_path=WAVES_DATA)
    
    distance, angle = testing_map.find_closest_land([58.7352, 5.4316])
    print(distance)
    assert angle < 180
    assert distance < 10