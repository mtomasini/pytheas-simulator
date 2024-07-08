
import pandas as pd

from pytheas.boat import Boat
from pytheas.map import Map
from pytheas.travel import Travel
import pytheas.utilities 
from parameters import SPEED_POLAR_DIAGRAM_PATH, LEEWAY_POLAR_DIAGRAM_PATH

# initiate parameters
WIND_DATA = "/media/mtomasini/LaCie/LIR/Full_data/winds_cerra/"
CURRENT_DATA = "/media/mtomasini/LaCie/LIR/Full_data/currents_northwest/"
WAVES_DATA = "/media/mtomasini/LaCie/LIR/Full_data/waves_northwest/"

speed_polar_diagram = pd.read_csv(SPEED_POLAR_DIAGRAM_PATH, sep="\t", index_col=0)
leeway_polar_diagram = pd.read_csv(LEEWAY_POLAR_DIAGRAM_PATH, sep="\t", index_col=0)

launching_site = [57.1224, 8.4475] # Limfjorden
landing_site = [58.0487, 6.6845] # Listafjorden

bounding_box = [56.3, 5.8, 58.8, 13.1]
start_day = pd.Timestamp('1995-03-03')
max_duration_h = 72
end_day = start_day + pd.Timedelta(max_duration_h, unit="hours")


# initiate boat
hjortspring = Boat('hjortspring', latitude=launching_site[0], longitude=launching_site[1],
                   target=landing_site, speed_polar_diagram=speed_polar_diagram, leeway_polar_diagram=leeway_polar_diagram)

# initiate map
skagerrak_map = Map(bounding_box, earliest_time=start_day, latest_time=end_day, 
                    wind_data_path = WIND_DATA, current_data_path=CURRENT_DATA, waves_data_path=WAVES_DATA)

print(skagerrak_map.currents_data.uo.sel(time=start_day, latitude=slice(57.8, 58.9), longitude=slice(6.8, 6.9)).mean(skipna=True).values)

# initiate travel
# limfjorden_lista = Travel(boat = hjortspring, map = skagerrak_map, start_day=start_day, max_duration = 72, timestep = 15)