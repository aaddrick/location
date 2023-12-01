import geopandas as gpd
import json
import sys
import time
from shapely.geometry import Point

max_level = 3

# Load the GADM geopackage layers with only necessary columns
gadm_gpkg_path = 'gadm-levels/gadm_410-levels.gpkg'
gadm_level_0 = gpd.read_file(gadm_gpkg_path, layer='ADM_0', columns=['GID_0', 'COUNTRY'])
gadm_level_1 = gpd.read_file(gadm_gpkg_path, layer='ADM_1', columns=['GID_1', 'NAME_1'])
gadm_level_2 = gpd.read_file(gadm_gpkg_path, layer='ADM_2', columns=['GID_2', 'NAME_2'])
gadm_level_3 = gpd.read_file(gadm_gpkg_path, layer='ADM_3', columns=['GID_3', 'NAME_3'])

# Function to perform spatial join and get administrative levels
def get_admin_levels(point, levels, max_level):
    admin_info = {}
    level_names = ['Country', 'admin1', 'admin2', 'admin3']
    point_gdf = gpd.GeoDataFrame(geometry=[point], crs='EPSG:4326')
    for level, level_name in zip(levels[:max_level + 1], level_names[:max_level + 1]):
        result = gpd.sjoin(point_gdf, level, how='left', predicate='within')
        if not result.empty:
            admin_info[level_name] = result.iloc[0][level_name]
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
    for level_name in ['Country', 'admin1', 'admin2', 'admin3'][:max_level + 1]:
        loc[level_name] = admin_levels.get(level_name, '')
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