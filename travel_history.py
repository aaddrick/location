import json
import csv

def format_location(feature):
    country = feature['properties']['Country']
    admin1 = feature['properties']['admin1'] or ''  # Replace None with an empty string
    return f"{country} {admin1}".strip()

def find_country_changes(file_path, output_file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    with open(output_file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Date', 'From', 'To'])  # Header row

        previous_feature = None
        for feature in data['features']:
            if previous_feature and previous_feature['properties']['Country'] != feature['properties']['Country']:
                prev_location = format_location(previous_feature)
                current_location = format_location(feature)
                csvwriter.writerow([
                    feature['properties']['timestamp'],
                    prev_location,
                    current_location
                ])
            previous_feature = feature

# Replace 'path_to_your_json_file.json' with the actual file path
# The output will be written to 'changes.csv'
find_country_changes('output\minimized_with_admin.json', 'changes.csv')