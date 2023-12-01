import json
import os
import sys

def process_location(entry):
    """ Extracts specified fields from a location entry and validates them. """
    required_keys = ['latitudeE7', 'longitudeE7', 'timestamp']
    missing_keys = [key for key in required_keys if key not in entry]
    if missing_keys:
        raise KeyError(f"Missing keys in entry: {', '.join(missing_keys)}")

    # Convert E7 format to standard decimal degrees
    latitude = entry['latitudeE7'] / 1e7
    longitude = entry['longitudeE7'] / 1e7

    # Validate latitude and longitude ranges
    if not (-90 <= latitude <= 90):
        raise ValueError(f"Latitude {latitude} out of range. Must be between -90 and 90.")
    if not (-180 <= longitude <= 180):
        raise ValueError(f"Longitude {longitude} out of range. Must be between -180 and 180.")

    return {
        'latitudeE7': entry['latitudeE7'],
        'longitudeE7': entry['longitudeE7'],
        'timestamp': entry['timestamp']
    }

import sys
import json

def parse_and_save_large_json(input_file, output_file):
    """ Parses a large JSON file and extracts specific fields. """
    try:
        with open(input_file, 'r') as file:
            data = json.load(file)['locations']
    except FileNotFoundError:
        print(f"File not found: {input_file}")
        return
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {input_file}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    processed_data = []
    total_entries = len(data)
    for index, location in enumerate(data):
        try:
            processed_data.append(process_location(location))
        except KeyError:
            # Skip the entry if required fields are missing
            continue
        except Exception as e:
            print(f"Error processing data: {e}")
            return

        # Update the status on the same line in the terminal
        progress = (index + 1) / total_entries * 100
        sys.stdout.write(f"\rProcessing: {progress:.2f}%")
        sys.stdout.flush()

    print("\nFinished processing locations.")

    try:
        with open(output_file, 'w') as file:
            # Write the JSON file with indentation for readability
            json.dump({'locations': processed_data}, file, indent=4)
    except IOError as e:
        print(f"Error writing to output file: {output_file} - {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Usage
input_path = r"C:\Users\aaddr\Documents\location\source\Records.json"
output_path = r"C:\Users\aaddr\Documents\location\output\minimized.json"
parse_and_save_large_json(input_path, output_path)
