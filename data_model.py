from random import randint

# Add a node that has 0 travel time to any node
# Which is equivalent to not having a depot


def add_nonexistent_depot(matrix):
    matrix_with_depot = [[0 for _ in range(len(matrix)+1)]]
    for distances in matrix:
        matrix_with_depot.append([0] + distances)
    return matrix_with_depot

# Map several required data to arrays whose indexes represent
# the objects
# Alternatively merge these mapping to loop over once
# I will seperate them for readability and maintanibility


def map_service_to_location(jobs, number_of_nodes):
    # This will ensure each node exists in the final list
    # But with an insignificant value if there's no service required
    service_durations = {i: 0 for i in range(1, number_of_nodes+1)}

    for job in jobs:
        service_durations[job["location_index"]] = job["service"]

    return list(service_durations.values())


def map_demand_to_location(jobs, number_of_nodes):
    demands = {i: 0 for i in range(1, number_of_nodes+1)}

    for job in jobs:
        # Delivery is a list but I am not sure what multiple
        # entries mean so I am treating it as a number
        demands[job["location_index"]] += job["delivery"][0]

    return list(demands.values())


def map_capacity_to_vehicles(vehicles, number_of_vehicles):
    vehicle_capacities = {i: 0 for i in range(1, number_of_vehicles+1)}

    for vehicle in vehicles:
        # Same as delivery, I'm treating this as a number
        vehicle_capacities[vehicle["id"]] = vehicle["capacity"][0]

    return list(vehicle_capacities.values())


def map_start_locations_to_vehicles(vehicles, number_of_vehicles):
    start_locations = {i: 0 for i in range(1, number_of_vehicles+1)}

    for vehicle in vehicles:
        start_locations[vehicle["id"]] = vehicle["start_index"] + 1

    return list(start_locations.values())


def map_end_locations_to_vehicles(number_of_vehicles):
    return [0 for _ in range(number_of_vehicles)]


def create_data_model(vehicles, jobs):

    number_of_vehicles = len(vehicles)
    time_matrix = add_nonexistent_depot(time_matrix)
    service_durations = map_service_to_location(vehicles, len(time_matrix[0]))
    demands = map_demand_to_location(jobs, len(time_matrix[0]))
    vehicle_capacities = map_capacity_to_vehicles(
        vehicles, number_of_vehicles)
    start_locations = map_start_locations_to_vehicles(
        vehicles, number_of_vehicles)
    end_locations = map_end_locations_to_vehicles(number_of_vehicles)

    # Define an arbitrary duration constraint for each vehicle
    time_constraint = randint(3000, 5000)

    return number_of_vehicles, time_matrix, service_durations, demands, vehicle_capacities, start_locations, end_locations, time_constraint
