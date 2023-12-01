import geopandas as gpd
import json
import sys
import time
from tqdm import tqdm
from shapely.geometry import Point

max_level = 3

# Load the GADM geopackage layers with only necessary columns
gadm_gpkg_path = 'gadm-levels/gadm_410-levels.gpkg'

gadm_layers = ['ADM_0', 'ADM_1', 'ADM_2', 'ADM_3']
gadm_data = []

print("Loading GADM levels...")
for layer in tqdm(gadm_layers, desc="GADM Levels"):
    gadm_data.append(gpd.read_file(gadm_gpkg_path, layer=layer))

gadm_level_0, gadm_level_1, gadm_level_2, gadm_level_3 = gadm_data

# Function to perform spatial join and get administrative levels
def get_admin_levels(point, levels, max_level):
    admin_info = {}
    # Define the correct column names based on the GADM data
    column_names = ['COUNTRY', 'NAME_1', 'NAME_2', 'NAME_3']
    point_gdf = gpd.GeoDataFrame(geometry=[point], crs='EPSG:4326')
    for level, column_name in zip(levels[:max_level + 1], column_names[:max_level + 1]):
        result = gpd.sjoin(point_gdf, level, how='left', predicate='within')
        if not result.empty:
            # Use the correct column name from the GADM data
            admin_info[column_name] = result.iloc[0].get(column_name, '')
    return admin_info

# Load the minimized.json file
with open('output/minimized.json', 'r') as file:
    data = json.load(file)['locations']

# Calculate total_locations after loading the data
total_locations = len(data)

# Convert the locations to a GeoDataFrame
geometry = [Point(loc['longitudeE7'] / 1e7, loc['latitudeE7'] / 1e7) for loc in data]
locations_gdf = gpd.GeoDataFrame(data, geometry=geometry, crs='EPSG:4326')

# Add the administrative levels to each location with progress tracking
start_time = time.time()
def process_location(loc):
    point = loc.geometry
    admin_levels = get_admin_levels(point, [gadm_level_0, gadm_level_1, gadm_level_2, gadm_level_3], max_level)
    # Use the correct column names when setting the values
    loc['Country'] = admin_levels.get('COUNTRY', '')
    if max_level >= 1:
        loc['admin1'] = admin_levels.get('NAME_1', '')
    if max_level >= 2:
        loc['admin2'] = admin_levels.get('NAME_2', '')
    if max_level >= 3:
        loc['admin3'] = admin_levels.get('NAME_3', '')
    return loc

locations_gdf = locations_gdf.apply(process_location, axis=1)

# Progress and ETA
elapsed_time = time.time() - start_time
avg_time_per_location = elapsed_time / total_locations
estimated_total_time = avg_time_per_location * total_locations
remaining_time = estimated_total_time - elapsed_time
sys.stdout.write(f"\rProcessing complete - elapsed time: {elapsed_time/60:.2f} minutes, "
                 f"average time per location: {avg_time_per_location:.2f} seconds\n")
sys.stdout.flush()

# Convert the updated GeoDataFrame back to JSON
updated_data = json.loads(locations_gdf.to_json())
with open('output/minimized_with_admin.json', 'w') as file:
    json.dump(updated_data, file, indent=4)