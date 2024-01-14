Overview
========
The ``modelsandbox`` and its core ``Model`` class allow for users to build intricate, multi-level, highly parameterized mathematical models. Models are defined using a series of computational layers which can be created with the `add_layer()` class method and which are invoked sequentially when the model is called. These layers are populated with a series of processors which can be created in multiple ways and which are also invoked sequentially within each layer when the model is called.

Processors are the building blocks of a model, defining individual parameterized mathematical or computational processes within each layer. When the model is run, each layer is processed sequentially and each processor is processed sequentially within the layer. The parameters required by each processor are collected and exposed at the model level, requiring all to be input when running the model. These parameters are then passed as keyword arguments to each layer, and the outputs of each processor are collected and added to the `dict` of parameters based on the processor label or schema data and are then passed as keyword arguments to the next layer. In this way, processor outputs can be referenced and used in subsequent layers of the model.

Types of processors are represented by the following classes:

* ``ProcessFunction`` This class is built around a single callable, most commonly a defined Python function, which takes a number of parameters and performs a single model task, returning a single output. Because these use callables which can be flexibly defined in Python, they are effective for performing the more mathematical processes of the model.

* ``ProcessSchema`` This class is built around a schema ``dict`` or ``JSON`` file which contains information on a series of logical tests based on a number of parameters, returning a single output or a ``dict`` of output key: value pairs. Because these use static logical schemas, they are effective for performing more the more logical processes of the model or replacing table references.
