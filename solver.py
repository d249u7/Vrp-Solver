from data_model import create_data_model
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

# I'll use a modified time_callback to calculate duration while parsing the routes
# routing.GetArcCostForVehicle returns 0 for everything for some reason


def get_duration(time_matrix, service_durations, from_node, to_node):
    print(from_node, to_node,
          time_matrix[from_node][to_node] + service_durations[to_node])
    return time_matrix[from_node][to_node] + service_durations[to_node]

# Get job id from location
# Returns -1 if location does not have a job


def location_to_job(delivery_location, jobs):
    for job in jobs:
        print(job)
        if job["location_index"] == delivery_location:
            return job["id"]

    return -1


def format_solution(routing, manager, solution, num_vehicles, time_matrix, service_durations, jobs):
    result = {"total_delivery_duration": 0, "routes": {
        i: {"jobs": [], "delivery_duration": 0} for i in range(1, num_vehicles+1)}}

    for vehicle_id in range(1, num_vehicles+1):
        index = routing.Start(vehicle_id-1)
        while not routing.IsEnd(index):
            job_id = location_to_job(manager.IndexToNode(index), jobs)

            if job_id == -1:
                continue

            result["routes"][vehicle_id]["jobs"].append(job_id)

            previous_index = index
            index = solution.Value(routing.NextVar(index))
            result["routes"][vehicle_id]["delivery_duration"] += get_duration(
                time_matrix, service_durations, manager.IndexToNode(previous_index), manager.IndexToNode(index))

        result["total_delivery_duration"] += result["routes"][vehicle_id]["delivery_duration"]
    return result


def vrp_solver(vehicles, time_matrix, jobs):
    number_of_vehicles, time_matrix, service_durations, demands, vehicle_capacities, start_locations, end_locations, time_constraint = create_data_model(
        vehicles, jobs, time_matrix)

    manager = pywrapcp.RoutingIndexManager(
        len(time_matrix), number_of_vehicles, start_locations, end_locations)
    routing = pywrapcp.RoutingModel(manager)

    # Set the arc cost to travel duration +
    # service duration of the destination node
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return time_matrix[from_node][to_node] + service_durations[to_index]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Time constraint
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        time_constraint,  # vehicle maximum travel time
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

    result = format_solution(routing, manager, solution, number_of_vehicles, time_matrix, service_durations, jobs) if solution else {
        'Error': 'Solution not found!'}

    return result
