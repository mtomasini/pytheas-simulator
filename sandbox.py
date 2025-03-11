import pandas as pd
import time

from pytheas.boat import Boat
from pytheas.map import Map
from pytheas.travel import Travel
from pytheas.utilities import calculate_start_of_day
from parameters import WIND_DATA, CURRENT_DATA, WAVES_DATA, SPEED_POLAR_DIAGRAM_PATH, LEEWAY_POLAR_DIAGRAM_PATH, BOULOGNE_SUR_MER, ABER_ILDUT, BOUNDING_BOX_BRETAGNE

# load polar diagrams
speed_polar_diagram = pd.read_csv(SPEED_POLAR_DIAGRAM_PATH, sep=",", index_col=0)
leeway_polar_diagram = pd.read_csv(LEEWAY_POLAR_DIAGRAM_PATH, sep=",", index_col=0)

# prepare geographical parameters
launching_site = BOULOGNE_SUR_MER
landing_site = ABER_ILDUT

bounding_box = BOUNDING_BOX_BRETAGNE

# prepare time parameters
max_duration_h = 720

start_day = pd.Timestamp('1995-03-03T00:00')
end_day = calculate_start_of_day(start_day, launching_site, type_of_twilight='civil') + pd.Timedelta(max_duration_h, unit="hours")

# load map
bretagne_map = Map(bounding_box, earliest_time=start_day, latest_time=end_day, 
                   wind_data_path = WIND_DATA, current_data_path=CURRENT_DATA, waves_data_path=WAVES_DATA)
launching_site_water = bretagne_map.find_closest_water(launching_site)
landing_site_water = bretagne_map.find_closest_water(landing_site)

route = bretagne_map.create_route(launching_site_water, landing_site_water, target_interval = 2, weights = [1, 1000, 1, 1000], iterations = [10, 5, 3, 1])

# initiate boat
hjortspring = Boat('Hjortspring', latitude=launching_site_water[0], longitude=launching_site_water[1],
                   target=landing_site, land_radar_on=True, speed_polar_diagram=speed_polar_diagram, leeway_polar_diagram=leeway_polar_diagram, route_to_take = route)

# load and run travel
travel = Travel(boat = hjortspring, map = bretagne_map, start_day = start_day, max_duration = max_duration_h, timestep = 15, night_travel=False, twilights_of_stops='civil')
travel.run(verbose=True)

travel.output_geojson(f"./Outputs/{start_day.strftime('%Y-%m-%d')}.json") 
hjortspring.plot_trajectory(bounding_box, show_route=True)