import geopandas as gpd
import json
import sys
from shapely.geometry import Point

# Load the GADM geopackage layers
gadm_gpkg_path = 'gadm-levels/gadm_410-levels.gpkg'
gadm_level_0 = gpd.read_file(gadm_gpkg_path, layer='ADM_0')  # Countries
gadm_level_1 = gpd.read_file(gadm_gpkg_path, layer='ADM_1')  # States/Provinces
gadm_level_2 = gpd.read_file(gadm_gpkg_path, layer='ADM_2')  # Counties/Districts
gadm_level_3 = gpd.read_file(gadm_gpkg_path, layer='ADM_3')  # Communes/Municipalities

# Function to perform spatial join and get administrative levels
def get_admin_levels(point, levels):
    admin_info = {}
    # Create a GeoDataFrame for the point with the correct CRS
    point_gdf = gpd.GeoDataFrame(geometry=[point], crs='EPSG:4326')
    for level, level_name in zip(levels, ['Country', 'admin1', 'admin2', 'admin3']):
        result = gpd.sjoin(point_gdf, level, how='left', predicate='within')
        if not result.empty:
            if level_name == 'Country':
                admin_info[level_name] = result.iloc[0].get('COUNTRY', '')
            else:
                admin_info[level_name] = result.iloc[0].get(f'NAME_{level_name[-1]}', '')
    return admin_info

# Load the minimized.json file
with open('output/minimized.json', 'r') as file:
    data = json.load(file)['locations']

# Convert the locations to a GeoDataFrame
geometry = [Point(loc['longitudeE7'] / 1e7, loc['latitudeE7'] / 1e7) for loc in data]
locations_gdf = gpd.GeoDataFrame(data, geometry=geometry)
locations_gdf = locations_gdf.set_crs(epsg=4326)  # Set CRS to WGS 84

# Add the administrative levels to each location with progress tracking
total_locations = len(locations_gdf)
for index, loc in locations_gdf.iterrows():
    point = loc.geometry
    admin_levels = get_admin_levels(point, [gadm_level_0, gadm_level_1, gadm_level_2, gadm_level_3])
    for level_name in ['Country', 'admin1', 'admin2', 'admin3']:
        locations_gdf.at[index, level_name] = admin_levels.get(level_name, '')

    # Update progress
    progress = (index + 1) / total_locations * 100
    sys.stdout.write(f"\rProcessing location {index + 1}/{total_locations} ({progress:.2f}%)")
    sys.stdout.flush()

print("\nFinished populating administrative levels.")

# Convert the updated GeoDataFrame back to JSON
updated_data = json.loads(locations_gdf.to_json())
with open('output/minimized_with_admin.json', 'w') as file:
    json.dump(updated_data, file, indent=4)