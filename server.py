from flask import Flask, request
from waitress import serve
from solver import vrp_solver

app = Flask(__name__)


@app.route("/get_routes", methods=["POST"])
def calculate_routes():
    params = request.get_json()
    required_params = ["vehicles", "matrix", "jobs"]

    # Check if the input has the expected minimum keys
    if not all(key in params for key in required_params):
        return {"Error": "Missing required paramaters"}, 422

    vehicles = params["vehicles"]
    matrix = params["matrix"]
    jobs = params["jobs"]

    routes, cost = vrp_solver(vehicles, matrix, jobs)
