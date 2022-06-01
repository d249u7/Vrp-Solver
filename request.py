import json
import requests


def get_routes(file_path="./input.json"):
    # Read the given file, raise exception in case of error
    try:
        with open(file_path) as input_file:
            inputs = json.load(input_file)
    except (OSError, IOError) as e:
        raise Exception(f"File could not be read. \n\n{e}")

    URL = "http://localhost:3000/get_routes"
    response = requests.post(URL, json=inputs)

    return response


result = get_routes()
print(result.json())

# write the response to a file
with open("./routes.json", "w") as output_file:
    json.dump(result.json(), output_file, ensure_ascii=False, indent=4)
