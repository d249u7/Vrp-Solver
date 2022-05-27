from numpy import number
from ortools.constraint_solver import pywrapcp
from random import randint
from ortools.constraint_solver import routing_enums_pb2


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
        service_durations[job["id"]] = job["service"]

    return service_durations


def map_demand_to_location(jobs, number_of_nodes):
    demands = {i: 0 for i in range(1, number_of_nodes+1)}

    for job in jobs:
        # Delivery is a list but I am not sure what multiple
        # entries mean so I am treating it as a number
        demands[job["location_index"]] += job["delivery"][0]

    return demands


def map_capacity_to_vehicles(vehicles, number_of_vehicles):
    vehicle_capacities = {i: 0 for i in range(1, number_of_vehicles+1)}

    for vehicle in vehicles:
        # Same as delivery, I'm treating this as a number
        vehicle_capacities[vehicle["id"]] = vehicle["capacity"][0]

    return vehicle_capacities


# Solution parser from Google OR Tools site
def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
    max_route_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print('Maximum of the route distances: {}m'.format(max_route_distance))


def vrp_solver(vehicles, time_matrix, jobs):
    number_of_vehicles = len(vehicles)
    depot = 0
    time_matrix = add_nonexistent_depot(time_matrix)
    service_durations = map_service_to_location(jobs, len(time_matrix[0]))
    demands = map_demand_to_location(jobs, len(time_matrix[0]))
    vehicle_capacities = map_capacity_to_vehicles(vehicles, number_of_vehicles)
    print(service_durations, demands, vehicle_capacities)
    # Define an arbitrary duration constraint for each vehicle
    time_constraint = randint(3000, 5000)

    manager = pywrapcp.RoutingIndexManager(
        len(time_matrix), number_of_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    # Set the arc cost to travel duration +
    # service duration of the destination node
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        print(time_matrix[from_node][to_node], service_durations[to_index])
        return time_matrix[from_node][to_node] + service_durations[to_index]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Time constraint
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        time_constraint,  # vehicle maximum travel distance
        True,  # start cumul to zero
        "Time")

    time_dimension = routing.GetDimensionOrDie("Time")
    time_dimension.SetGlobalSpanCostCoefficient(100)

    # Capacity constraint
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        vehicle_capacities,  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        print_solution({"distance_matrix": time_matrix, "num_vehicles": number_of_vehicles,
                       "depot": depot}, manager, routing, solution)
    else:
        print('No solution found !')

    return "heheh"
