import pandas as pd

from pytheas.boat import Boat
from pytheas.map import Map
from pytheas.travel import Travel
from pytheas.utilities import calculate_start_of_day
from parameters import SPEED_POLAR_DIAGRAM_PATH, LEEWAY_POLAR_DIAGRAM_PATH
from varpelev_parameters import LAUNCHING, LANDING

# initiate parameters
WIND_DATA = "/run/media/mtomasini/LaCie/LIR/Full_data/winds_cerra/"
CURRENT_DATA = "/run/media/mtomasini/LaCie/LIR/Full_data/currents_baltic/"
WAVES_DATA = "/run/media/mtomasini/LaCie/LIR/Full_data/waves_baltic/"

speed_polar_diagram = pd.read_csv(SPEED_POLAR_DIAGRAM_PATH, sep=",", index_col=0)
leeway_polar_diagram = pd.read_csv(LEEWAY_POLAR_DIAGRAM_PATH, sep=",", index_col=0)

launching_site = LAUNCHING
landing_site = LANDING

bounding_box = [56.3, 5.8, 58.8, 13.1] #[49.806087, 0.840002, 54.935397, 7.904663]
start_day = calculate_start_of_day('1994-07-07', launching_site) #pd.Timestamp('1995-03-03')
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
hjortspring = Boat('hjortspring', latitude=launching_site_water[0], longitude=launching_site_water[1],
                   target=landing_site, land_radar_on=False, speed_polar_diagram=speed_polar_diagram, leeway_polar_diagram=leeway_polar_diagram)# , route_to_take = route)

# initiate travel
limfjorden_lista = Travel(boat = hjortspring, map = skagerrak_map, start_day = start_day, max_duration = max_duration_h, timestep = 15, night_travel=False)
limfjorden_lista.run(verbose=True)

output = limfjorden_lista.output_geojson('./Outputs/test_trajectory_2')
limfjorden_lista.boat.plot_trajectory(bounding_box)