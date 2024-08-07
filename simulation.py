import pandas as pd

from pytheas.boat import Boat
from pytheas.map import Map
from pytheas.travel import Travel
from pytheas.utilities import calculate_start_of_day
from parameters import SPEED_POLAR_DIAGRAM_PATH, LEEWAY_POLAR_DIAGRAM_PATH

# initiate parameters
WIND_DATA = "/media/mtomasini/LaCie/LIR/Full_data/winds_cerra/"
CURRENT_DATA = "/media/mtomasini/LaCie/LIR/Full_data/currents_northwest/"
WAVES_DATA = "/media/mtomasini/LaCie/LIR/Full_data/waves_northwest/"

speed_polar_diagram = pd.read_csv(SPEED_POLAR_DIAGRAM_PATH, sep="\t", index_col=0)
leeway_polar_diagram = pd.read_csv(LEEWAY_POLAR_DIAGRAM_PATH, sep="\t", index_col=0)

launching_site = [57.1224, 8.4475]# [51.566722, 3.261733] # Limfjorden
landing_site = [58.0487, 6.6845] #[52.055910, 1.555690] # Listafjorden [58.0236, 7.4554] #

bounding_box = [56.3, 5.8, 58.8, 13.1] #[49.806087, 0.840002, 54.935397, 7.904663]
start_day = calculate_start_of_day('1995-07-10', launching_site) #pd.Timestamp('1995-03-03')
max_duration_h = 72
end_day = start_day + pd.Timedelta(max_duration_h, unit="hours")

# initiate map
skagerrak_map = Map(bounding_box, earliest_time=start_day, latest_time=end_day, 
                    wind_data_path = WIND_DATA, current_data_path=CURRENT_DATA, waves_data_path=WAVES_DATA)

# find closest water point to launching site
launching_site_water = skagerrak_map.find_closest_water(launching_site)

# create route
route = skagerrak_map.create_route(launching_site_water, landing_site, target_interval = 5, weights = [1, 10, 1, 100], iterations = [10, 5, 3, 1])

# initiate boat
# hjortspring = Boat('hjortspring', latitude=launching_site_water[0], longitude=launching_site_water[1],
#                    target=landing_site, land_radar_on=False, speed_polar_diagram=speed_polar_diagram, leeway_polar_diagram=leeway_polar_diagram, route_to_take = route)

# initiate travel
# limfjorden_lista = Travel(boat = hjortspring, map = skagerrak_map, start_day = start_day, max_duration = max_duration_h, timestep = 15, night_travel=False)
# limfjorden_lista.run(verbose=True)

# output = limfjorden_lista.output_geojson('./Outputs/test_trajectory')
# limfjorden_lista.boat.plot_trajectory(bounding_box)

print(route)