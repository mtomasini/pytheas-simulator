import pandas as pd
import time

from pytheas.boat import Boat
from pytheas.map import Map
from pytheas.travel import Travel
from pytheas.utilities import calculate_start_of_day
from parameters import SPEED_POLAR_DIAGRAM_PATH, LEEWAY_POLAR_DIAGRAM_PATH
from varpelev_parameters import LAUNCHING, LANDING, OUTPUT_FOLDER

# initiate parameters
WIND_DATA = "/run/media/mtomasini/LaCie/LIR/Full_data/winds_cerra/"
CURRENT_DATA = "/run/media/mtomasini/LaCie/LIR/Full_data/currents_baltic/"
WAVES_DATA = "/run/media/mtomasini/LaCie/LIR/Full_data/waves_baltic/"

speed_polar_diagram = pd.read_csv(SPEED_POLAR_DIAGRAM_PATH, sep=",", index_col=0)
leeway_polar_diagram = pd.read_csv(LEEWAY_POLAR_DIAGRAM_PATH, sep=",", index_col=0)

launching_site = LAUNCHING
landing_site = LANDING
output = OUTPUT_FOLDER

bounding_box = [57.0, 10.3, 58.2, 12.3] #[49.806087, 0.840002, 54.935397, 7.904663]

start_year = 1993
end_year = 1993
frequency = 1

first_simulated_day = '01-02' if start_year==1993 else '01-01'
dates_to_simulate = ['1993-02-13'] #pd.date_range(f"{start_year}-{first_simulated_day}", f"{end_year}-12-31", freq=f"{frequency}D")

start_time = time.time()

for day in dates_to_simulate:
    start_day = calculate_start_of_day(day, launching_site, type_of_twilight='civil') #pd.Timestamp('1995-03-03')
    max_duration_h = 72
    end_day = start_day + pd.Timedelta(max_duration_h, unit="hours")

    # initiate map
    skagerrak_map = Map(bounding_box, earliest_time=start_day, latest_time=end_day, 
                        wind_data_path = WIND_DATA, current_data_path=CURRENT_DATA, waves_data_path=WAVES_DATA)

    # find closest water point to launching site
    launching_site_water = skagerrak_map.find_closest_water(launching_site)

    # create route
    # route = skagerrak_map.create_route(launching_site_water, landing_site, target_interval = 5, weights = [1, 10, 1, 100], iterations = [10, 5, 3, 1])

    # initiate boat
    varpelev = Boat('varpelev', latitude=launching_site_water[0], longitude=launching_site_water[1],
                    target=landing_site, land_radar_on=True, speed_polar_diagram=speed_polar_diagram, leeway_polar_diagram=leeway_polar_diagram)# , route_to_take = route)

    # initiate travel
    limfjorden_lista = Travel(boat = varpelev, map = skagerrak_map, start_day = start_day, max_duration = max_duration_h, timestep = 15, night_travel=False, twilights_of_stops='civil')
    limfjorden_lista.run(verbose=True)

    output = limfjorden_lista.output_geojson(f"/run/media/mtomasini/LaCie/LIR/Varpelev_Experiments/Outputs/{OUTPUT_FOLDER}/{day}")#{day.strftime('%Y-%m-%d')}") # ("./Outputs/test_trajectory")
   # limfjorden_lista.append_to_aggregates(f"/run/media/mtomasini/LaCie/LIR/Varpelev_Experiments/Aggregates/{OUTPUT_FOLDER}.csv")
    limfjorden_lista.boat.plot_trajectory(bounding_box)

end_time = time.time()
print(f"Process completed in about {round((end_time-start_time)/60, 2)} minutes.")