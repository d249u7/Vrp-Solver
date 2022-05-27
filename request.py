import json
import requests


def get_routes(file_path="./input.json"):
    # Read the given file, raise exception in case of error
    try:
        with open(file_path) as input_file:
            inputs = json.load(input_file)
    except (OSError, IOError) as e:
        raise Exception(f"File could not be read. \n\n{e}")

    URL = "http://localhost:3000"
    response = requests.post(URL, data=inputs)

    print(response)
