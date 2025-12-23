import os
import json
import argparse
import jsonschema
import jsonschema.exceptions


def validate_trajectory_data(json_data, json_schema) -> bool:
    try:
        jsonschema.validate(instance=json_data, schema=json_schema)
        print("JSON is valid")
    except jsonschema.exceptions.ValidationError as err:
        print("JSON is invalid")
        print(err)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description='Process a trajectory JSON file.')

    parser.add_argument('trajectory_json', metavar='--trajectory-json', type=str,
                        help='Path to the trajectory JSON file')

    args = parser.parse_args()

    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    schema_path = os.path.join(this_file_dir, 'trajectory-schema.json')

    with open(schema_path, 'r') as schema_file:
        json_schema = json.load(schema_file)

    with open(args.trajectory_json, 'r') as json_file:
        json_data = json.load(json_file)

    return int(validate_trajectory_data(json_data, json_schema))


if __name__ == '__main__':
    main()
