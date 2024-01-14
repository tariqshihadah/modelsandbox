from modelsandbox import Model

# Initialize the model class
model = Model()

# Add a layer to the model to compute airline ticket cost
model.add_layer('Compute ticket cost')

# Define a process schema for computing ticket cost
schema = {
    "label": "ticket_cost",
    "parameters": ["destination", "airline_class"],
    "actions": ["get", "get"],
    "data": {
        "Chicago": {
            "Economy": 220,
            "Business": 450,
            "First": 785
        },
        "Los Angeles": {
            "Economy": 365,
            "Business": 520,
            "First": 965
        }
    }
}
# Add the process schema to the model
model.add_process_schema(schema)

# Add a layer to the model
model.add_layer('Compute expenses')

# Add a processor to compute travel cost
@model.include_process_function()
def travel_cost(number_of_travelers, ticket_cost):
    return number_of_travelers * ticket_cost

# Add processor to compute lodging cost
@model.include_process_function()
def lodging_cost(number_of_travelers, nightly_cost, number_of_nights):
    return number_of_travelers * nightly_cost * number_of_nights

# Add processor to compute per diem
@model.include_process_function()
def per_diem_cost(number_of_travelers, number_of_nights, per_diem):
    return number_of_travelers * number_of_nights * per_diem

# Add a second layer to the model
model.add_layer('Aggregate expenses')
# Add processor to compute total trip cost
@model.include_process_function()
def total_trip_cost(travel_cost, lodging_cost, per_diem_cost):
    return travel_cost + lodging_cost + per_diem_cost