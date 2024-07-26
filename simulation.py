import pandas as pd

from pytheas.boat import Boat
from pytheas.map import Map
from pytheas.travel import Travel
from pytheas.utilities import calculate_start_of_day, distance_km
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
start_day = calculate_start_of_day('1995-03-03', launching_site) #pd.Timestamp('1995-03-03')
max_duration_h = 100
end_day = start_day + pd.Timedelta(max_duration_h, unit="hours")


# initiate boat
hjortspring = Boat('hjortspring', latitude=launching_site[0], longitude=launching_site[1],
                   target=landing_site, speed_polar_diagram=speed_polar_diagram, leeway_polar_diagram=leeway_polar_diagram)

# initiate map
skagerrak_map = Map(bounding_box, earliest_time=start_day, latest_time=end_day, 
                    wind_data_path = WIND_DATA, current_data_path=CURRENT_DATA, waves_data_path=WAVES_DATA)

# dataset = skagerrak_map.winds_data.sel(time=start_day + pd.Timedelta(6, unit="hours"), method="nearest")

# point = [57.3, 7.1]

# wind_mean = dataset.where((dataset.latitude >= point[0] - 0.05) & (dataset.latitude <= point[0] + 0.05) & (dataset.longitude >= point[1] - 0.05) & (dataset.longitude <= point[1] + 0.05), drop=True)

# initiate travel
limfjorden_lista = Travel(boat = hjortspring, map = skagerrak_map, start_day=start_day, max_duration = max_duration_h, timestep = 15)
limfjorden_lista.run(verbose=True)

output = limfjorden_lista.output_geojson('./Outputs/test_trajectory')
limfjorden_lista.boat.plot_trajectory(bounding_box)
