from typing import Any
from modelsandbox.globals import _VALID_SCHEMA_ACTIONS
from modelsandbox.helpers import _load_schema
from modelsandbox.model.base import ModelComponentBase


class ModelProcessorBase(ModelComponentBase):
    """
    Base class for model processors.

    Model processors are the lowest level of model definition. They include 
    the following subclasses:

    - FunctionProcessor
    - SchemaProcessor
    - EmptyProcessor
    """
    pass


class EmptyProcessor(ModelProcessorBase):
    """
    Class for defining an empty model processor.
    """

    def __init__(self, *args, **kwargs):
        self.label = label
        self.tags = tags

    @property
    def params(self):
        """
        Return a list of parameters for the empty processor.
        """
        return []
    
    @property
    def returns(self):
        """
        Return a list of return values for the empty processor.
        """
        return []
    
    def analyze(self, **params):
        return {}
    

class FunctionProcessor(ModelProcessorBase):
    """
    Class for defining a model processor using a function.
    
    This class is built around a single callable, most commonly a defined 
    Python function, which takes a number of parameters and performs a single 
    model task, returning a single output. Because these use callables which 
    can be flexibly defined in Python, they are effective for performing the 
    more mathematical processes of the model.

    Parameters
    ----------
    function : callable
        Callable object which will be the basis for the `FunctionProcessor`.
    label : str, optional
        Label associated with the model component.
    tags : list, optional
        List of tags to be associated with the model component. Tags may be 
        shared between multiple components, allowing them to be referenced 
        collectively.
    """

    def __init__(self, function, label: str=None, tags: list=[]):
        self.callable_ = function
        self.label = label
        self.tags = tags

    @property
    def params(self) -> list:
        """
        Return a list of parameters for the function processor.
        """
        num_args = self._callable_.__code__.co_argcount
        return list(self._callable_.__code__.co_varnames[:num_args])
    
    @property
    def returns(self) -> list:
        """
        Return a list of return values for the function processor.
        """
        return [self._label]
    
    @property
    def callable_(self) -> callable:
        """
        Return the callable for the function processor.
        """
        return self._callable_
    
    @callable_.setter
    def callable_(self, obj) -> None:
        if not callable(obj):
            raise ValueError("Input `obj` must be callable.")
        self._callable_ = obj

    def _validate_label(self, label):
        if label is None:
            label = self._callable_.__name__
        return label

    def analyze(self, **params):
        return {self._label: self._callable_(**params)}
    

class SchemaProcessor(ModelProcessorBase):
    """
    Class for defining a model processor using a schema.

    Parameters
    ----------
    schema : dict, str, or path
        Schema data following the required structure of the `SchemaProcessor` 
        class. Can be input as a Python `dict`, an absolute path to a JSON 
        file, or a relative path to a JSON file within the default 
        `SCHEMA_PATH` directories.
    label : str, optional
        Label associated with the model component.
    tags : list, optional
        List of tags to be associated with the model component. Tags may be 
        shared between multiple components, allowing them to be referenced 
        collectively.

    Schema Structure
    ----------------
    doc = {
        # Label to be used with the `SchemaProcessor` instance built from this 
        # data.
        "label": "schema_1",
        # List of parameter names which will be passed to the `SchemaProcessor` 
        # as `**params`.
        "parameters": ["lookup_param", "numerical_param"],

        # List of actions of equal length to `parameters`. These actions will 
        # indicate how each parameter will be tested against the schema data. 
        # Note that associated schema data will always be tested with the 
        # requested action in chronological order, returning the first success.
        "actions": ["get", "gte"],

        # Nested `dict` of data which will be traversed during analysis based 
        # on the input parameters and their associated actions
        "data": {
            # First level will be associated with the first parameter and 
            # action
            "a": {
                0: {
                    "x": 1,
                    "y": 2
                },
                10: {
                    "x": 10,
                    "y": 20
                }
            "b": {
                0: {
                    "x": 100,
                    "y": 200
                },
                10: {
                    "x": 1000,
                    "y": 2000
                }
            }
        }
    }

    Based on this schema, running the following code will produce the result 
    below::

    >>> ps = SchemaProcessor(doc)
    >>> ps.analyze(lookup_param="b", numerical_param=5)
    {"x": 100, "y": 200}
    """
    
    def __init__(self, schema: dict, label: str=None, tags: list=[]) -> None:
        self.schema = schema
        self.label = label
        self.tags = tags

    @property
    def params(self):
        """
        Return a list of parameters for the schema processor.
        """
        return self._schema['params']
    
    @property
    def returns(self):
        """
        Return a list of return values for the schema processor.
        """
        # Traverse data to retrieve keys of first valid output data subset
        data = self._schema['data']
        for param in self.params:
            data = list(data.values())[0]
        # Check for return type of dict or value
        if isinstance(data, dict):
            return list(data.keys())
        else:
            return [self.label]

    @property
    def actions(self):
        """
        Return a list of actions for the schema processor.
        """
        return self._schema['actions']

    @property
    def data(self):
        """
        Return the logical data for the schema processor.
        """
        return self._schema['data']

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, obj):
        # Load, validate the schema
        obj = self._validate_schema(
            _load_schema(obj)
        )
        self._schema = obj
        self._label = getattr(obj, 'label', None)

    def _validate_label(self, label):
        if label is None:
            label = self._schema['label']
        return label

    @classmethod
    def _validate_schema(cls, schema):
            # Check for required structure
            try:
                keys = schema["params"]
            except KeyError:
                raise KeyError(
                    "Input schema is missing the required `parameters` "
                    "information."
                )
            try:
                actions = schema["actions"]
                assert len(actions) == len(keys)
            except KeyError:
                raise KeyError(
                    "Input schema is missing the required `actions` information."
                )
            except AssertionError:
                raise ValueError(
                    "Number of `actions` must be equal to the number of "
                    "`parameters` in the provided schema."
                )
            try:
                assert all(action in _VALID_SCHEMA_ACTIONS for action in actions)
            except:
                raise ValueError(
                    f"Each input `action` must only be one of "
                    f"{_VALID_SCHEMA_ACTIONS}."
                )
            try:
                data = schema["data"]
            except KeyError:
                raise KeyError(
                    "Input schema is missing the required `data` information."
                )
            try:
                schema["label"]
            except KeyError:
                raise KeyError(
                    "Input schema is missing the required `label` information."
                )
            return schema
    
    def analyze(self, **params):
        """
        Analyze the schema using the input parameters which must align with 
        the schema's `parameters` and `actions`.
        """
        # Pull schema data
        data = self.data.copy()
        # Iterate through keys and actions in schema
        for parameter, action in zip(self.parameters, self.actions):
            SUCCESS = False
            # Pull parameter value
            try:
                parameter_value = params[parameter]
            except KeyError:
                raise KeyError(
                    f"Missing required `SchemaProcessor` parameter `{parameter}`."
                )
            # Check action with the appropriate test
            try:
                if action in ['get']:
                    data = data[parameter_value]
                    SUCCESS = True
                elif action in ['lt', 'gt', 'lte', 'gte']:
                    # Select the appropriate test
                    if action in ['lt']:
                        tester = lambda a, b: a < b
                    elif action in ['gt']:
                        tester = lambda a, b: a > b
                    elif action in ['lte']:
                        tester = lambda a, b: a <= b
                    elif action in ['gte']:
                        tester = lambda a, b: a >= b
                    # Iterate over data keys
                    for key, val in data.items():
                        if tester(parameter_value, float(key)):
                            data = val
                            SUCCESS = True
                            break
                    assert SUCCESS
            except:
                raise ValueError(
                    f"Unable to satisfy test for schema parameter "
                    f"`{parameter}: {action}` with value {parameter_value}."
                )
        
        # Return final retrieved data set
        if isinstance(data, dict):
            return data
        else:
            return {self.label: data}