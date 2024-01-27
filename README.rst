Overview
========
The ``modelsandbox`` package and its core ``Model`` class allow for users to build intricate, multi-level, highly parameterized mathematical models without needing extensive knowledge of Python to design complex classes and analysis structures. Models are defined using a series of computational layers which can be created with the ``add_layer()`` class method and which are invoked sequentially when the model is called. These layers are populated with a series of processors which can be created in multiple ways and which are also invoked sequentially within each layer when the model is called.

Processors are the building blocks of a model, defining individual parameterized mathematical or computational processes within each layer. When the model is run, each layer is processed sequentially and each processor is processed sequentially within the layer. The parameters required by each processor are collected and exposed at the model level in the ``params`` property, requiring all to be input when running the model. These parameters are then passed as keyword arguments to each layer, and the outputs of each processor are collected and added to the ``dict`` of parameters based on the processor label or schema data and are then passed as keyword arguments to the next layer. In this way, processor outputs can be referenced and used in subsequent layers of the model. Outputs of each model component are also collected and exposed at the model level in the ``returns`` property.

Types of processors are represented by the following classes:

* ``FunctionProcessor`` This class is built around a single callable, most commonly a defined Python function, which takes a number of parameters and performs a single model task, returning a single output. Because these use callables which can be flexibly defined in Python, they are effective for performing the more mathematical processes of the model.

* ``SchemaProcessor`` This class is built around a schema ``dict`` or ``JSON`` file which contains information on a series of logical tests based on a number of parameters, returning a single output or a ``dict`` of output key: value pairs. Because these use static logical schemas, they are effective for performing more the more logical processes of the model or replacing table references.

Basic Implementation
====================
Creating a new model from scratch is easy. The ``Model`` class provides instant functionality with just a few lines of code::

    # example.py

    from modelsandbox import Model

    # Initialize the model class
    model = Model()

Adding Process Functions
------------------------
Once the ``Model`` class has been instantiated, we can begin building a basic model by adding a layer and a ``FunctionProcessor``::

    # example.py

    # Add a layer to the model
    model.add_layer('Compute expenses')

    # Add a processor to compute travel cost
    @model.add_wrapped()
    def travel_cost(number_of_travelers, ticket_cost):
        return number_of_travelers * ticket_cost

Inspecting the Model
--------------------
The ``add_wrapped`` method returns a decorator which can be placed in front of a function definition, adding that function to the model and exposing its features at the model level. If we save the model in ``example.py`` as a basic Python file or as a Python module, we can then import it and run it in a Jupyter Notebook or elsewhere, and using the ``structure`` and ``parameters`` properties, we can see that the ``travel_cost`` function is now built into the model::

    # example.ipynb

    # Load the built model
    from example import model

    # Inspect the model's structure
    model.structure

    [Output]:
    {'Compute expenses': ['travel_cost']}

    # Inspect the model's parameters
    model.parameters

    [Output]:
    ['number_of_travelers', 'ticket_cost']

Running the Model
-----------------
Now that we've determined the parameters needed for the model, we can pass these parameters to the model and run it using the ``analyze`` method, producing a ``dict`` of model parameters and returns along with their provided and computed values, respectively::

    # example.ipynb

    # Run the model
    model.analyze(number_of_travelers=3, ticket_cost=500)

    [Output]:
    {'number_of_travelers': 3,
     'ticket_cost': 500,
     'travel_cost': 1500}

Expanding the Model
-------------------
This basic model doesn't offer much benefit over a simple Python function which could do the same. However, once we begin to expand it, creating additional parameterization, interdependency of model features, and more, it begins to simplify the modelling process significantly. Here's some additional expansion for example::

    # example.py

    # Add processor to compute lodging cost
    @model.add_wrapped()
    def lodging_cost(number_of_travelers, nightly_cost, number_of_nights):
        return number_of_travelers * nightly_cost * number_of_nights

    # Add processor to compute per diem
    @model.add_wrapped()
    def per_diem_cost(number_of_travelers, number_of_nights, per_diem):
        return number_of_travelers * number_of_nights * per_diem

We've added a couple additional computations at the first level. If we want to then aggregate the results of each of these processors, we can add another layer and gain access to the outputs of each previous processor as a new input::

    # example.py

    # Add a second layer to the model
    model.add_layer('Aggregate expenses')

    # Add processor to compute total trip cost
    @model.add_wrapped()
    def total_trip_cost(travel_cost, lodging_cost, per_diem_cost):
        return travel_cost + lodging_cost + per_diem_cost

Re-running the ``parameters`` property and the ``analyze`` method, we can see that the new processor paramters have been added to the model::

    # example.ipynb

    # Inspect the model's parameters
    model.parameters

    [Output]:
    ['nightly_cost',
     'number_of_nights',
     'number_of_travelers',
     'per_diem',
     'ticket_cost']

    # Run the model
    model.analyze(
        nightly_cost=185,
        number_of_nights=4,
        number_of_travelers=3,
        per_diem=72,
        ticket_cost=500
    )

    [Output]:
    {'nightly_cost': 185,
     'number_of_nights': 4,
     'number_of_travelers': 3,
     'per_diem': 72,
     'ticket_cost': 500,
     'travel_cost': 1500,
     'lodging_cost': 2220,
     'per_diem_cost': 864,
     'total_trip_cost': 4584}

Note that though some parameters, such as the ``number_of_travelers`` parameter, get used in multiple functions, they only appear once and only need to be passed to the model a single time. Additionally, though we use the output of the ``travel_cost`` function as a parameter in the ``total_trip_cost`` function, we are not required to pass it on its own to the model.

Process Schemas
---------------
For models which require references or logical patterns such as lookup tables, we can also employ the ``SchemaProcessor`` class in addition to the ``FunctionProcessor`` class we've been using with the ``add_wrapped`` method/decorator. To add such a feature to our model, we can do the following::

    # example.py

    # Define a process schema according to documentation
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

If we make this addition to a new layer before our initial layer, this will allow us to input the ``destination`` and ``airline_class`` parameters instead of the ``ticket_cost`` parameter directly, which will instead be automatically computed for us. Note that this could also be done by creating a separate ``.py`` or ``.json`` file and loading it into the model file or passing the path of the separate file to the ``add_process_schema`` method. Let's take another look at the model's ``structure`` and ``parameters`` properties with the newly-defined model::

    # example.ipynb

    # Inspect the model's structure
    model.structure

    [Output]:
    {'Compute ticket cost': ['ticket_cost'],
     'Compute expenses': ['travel_cost', 'lodging_cost', 'per_diem_cost'],
     'Aggregate expenses': ['total_trip_cost']}

    # Inspect the model's parameters
    model.parameters

    [Output]:
    ['airline_class',
     'destination',
     'nightly_cost',
     'number_of_nights',
     'number_of_travelers',
     'per_diem']

Now let's analyze the model using some example inputs to see our new results::

    # example.ipynb

    # Run the model
    model.analyze(
        airline_class="Business",
        destination="Chicago",
        nightly_cost=185,
        number_of_nights=4,
        number_of_travelers=3,
        per_diem=72,
        ticket_cost=500
    )

    [Output]:
    {'airline_class': 'Business',
     'destination': 'Chicago',
     'nightly_cost': 185,
     'number_of_nights': 4,
     'number_of_travelers': 3,
     'per_diem': 72,
     'ticket_cost': 450,
     'travel_cost': 1350,
     'lodging_cost': 2220,
     'per_diem_cost': 864,
     'total_trip_cost': 4434}

Final Example
-------------
The final ``example.py`` model file is shown below::

    # example.py

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

    # Add a layer to the model to compute additional costs
    model.add_layer('Compute expenses')

    # Add a processor to compute travel cost
    @model.add_wrapped()
    def travel_cost(number_of_travelers, ticket_cost):
        return number_of_travelers * ticket_cost

    # Add processor to compute lodging cost
    @model.add_wrapped()
    def lodging_cost(number_of_travelers, nightly_cost, number_of_nights):
        return number_of_travelers * nightly_cost * number_of_nights

    # Add processor to compute per diem
    @model.add_wrapped()
    def per_diem_cost(number_of_travelers, number_of_nights, per_diem):
        return number_of_travelers * number_of_nights * per_diem

    # Add a layer to the model to aggregate costs
    model.add_layer('Aggregate expenses')

    # Add processor to compute total trip cost
    @model.add_wrapped()
    def total_trip_cost(travel_cost, lodging_cost, per_diem_cost):
        return travel_cost + lodging_cost + per_diem_cost