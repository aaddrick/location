import json
from datetime import datetime, timezone
from haversine import haversine

# Configurable parameters
FILE_PATH = r'output\minimized.json'  # Path to your JSON file
TEMPORAL_AGGREGATION_SECONDS = 3600  # Aggregation by hours (3600 seconds), adjust as needed
DISTANCE_THRESHOLD_KM = 20  # Threshold for filtering locations in meters

def reduce_data(file_path, temporal_seconds, threshold_km):
    with open(file_path, 'r') as file:
        data = json.load(file)

    reduced_data = []
    last_valid_point = None
    total_locations = len(data['locations'])  # Get the total number of locations for progress calculation

    for index, entry in enumerate(data['locations']):
        # Progress indicator
        print(f'\rProcessing location {index + 1}/{total_locations}', end='')

        # Extracting latitude and longitude in E7 format
        lat_e7 = entry['latitudeE7']
        lon_e7 = entry['longitudeE7']

        # Temporal aggregation
        timestamp_str = entry['timestamp'].rstrip('Z')  # Remove the 'Z'
        timestamp = datetime.fromisoformat(timestamp_str)
        timestamp = timestamp.replace(tzinfo=timezone.utc)  # Set timezone to UTC

        if last_valid_point and (timestamp - last_valid_point['timestamp']).total_seconds() < temporal_seconds:
            continue

        point = (lat_e7 / 1e7, lon_e7 / 1e7)

        # Threshold-based filtering (using Haversine function directly with E7 format)
        if last_valid_point and haversine((last_valid_point['latitudeE7'] / 1e7, last_valid_point['longitudeE7'] / 1e7), point) < threshold_km:
            continue

        reduced_entry = {
            'latitudeE7': lat_e7,
            'longitudeE7': lon_e7,
            'timestamp': timestamp  # Keep the datetime object here
        }
        reduced_data.append({
            'latitudeE7': lat_e7,
            'longitudeE7': lon_e7,
            'timestamp': timestamp.isoformat()  # Convert datetime to string when appending to reduced_data
        })
        last_valid_point = reduced_entry  # Store the datetime object for comparison

    print()

    # Saving reduced data
    with open('minimized_reduced_data.json', 'w') as outfile:
        json.dump({'locations': reduced_data}, outfile, indent=4)

    return 'reduced_data.json'

# Call the function with the specified parameters
reduced_file = reduce_data(FILE_PATH, TEMPORAL_AGGREGATION_SECONDS, DISTANCE_THRESHOLD_KM)
