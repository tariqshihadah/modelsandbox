import json, os
from modelsandbox_old.helpers import _load_schema


class ProcessorBase(object):

    def __call__(self, **kwargs):
        return self.analyze(**kwargs)
    
    @property
    def __name__(self):
        return self._label

    @property
    def label(self):
        return self._label
    
    @label.setter
    def label(self, label):
        self._label = self._validate_label(label)

    @property
    def tags(self):
        return self._tags
    
    @tags.setter
    def tags(self, tags):
        if tags is None:
            tags = []
        self._tags = list(tags)


class ProcessFunction(ProcessorBase):
    """
    This class is built around a single callable, most commonly a defined 
    Python function, which takes a number of parameters and performs a single 
    model task, returning a single output. Because these use callables which 
    can be flexibly defined in Python, they are effective for performing the 
    more mathematical processes of the model.

    Parameters
    ----------
    obj : callable
        Callable object which will be the basis for the `ProcessFunction`.
    label : str, optional
        Label associated with the `ProcessFunction`. If not provided, will 
        default to the name of the input callable.
    tags : list, optional
        List of tags to be associated with the `ProcessFunction`. Tags may be 
        shared between multiple `ProcessFunction` instances, allowing them to 
        be referenced collectively.
    """

    def __init__(self, obj, label=None, tags=[]):
        self.callable_ = obj
        self.label = label
        self.tags = tags

    @property
    def parameters(self):
        num_args = self._callable_.__code__.co_argcount
        return list(self._callable_.__code__.co_varnames[:num_args])
    
    @property
    def returns(self):
        return [self._label]
    
    @property
    def callable_(self):
        return self._callable_
    
    @callable_.setter
    def callable_(self, obj):
        if not callable(obj):
            raise ValueError("Input `obj` must be callable.")
        self._callable_ = obj

    def _validate_label(self, label):
        if label is None:
            label = self._callable_.__name__
        return label

    def analyze(self, **kwargs):
        return {self._label: self._callable_(**kwargs)}
    

class ProcessSchema(ProcessorBase):
    """
    This class is built around a schema `dict` or `JSON` file which contains 
    information on a series of logical tests based on a number of parameters, 
    returning a single output or a `dict` of output key: value pairs. Because 
    these use static logical schemas, they are effective for performing more 
    the more logical processes of the model or replacing table references.

    Schema Structure
    ----------------
    doc = {
        # Label to be used with the `ProcessSchema` instance built from this 
        # data.
        "label": "schema_1",
        # List of parameter names which will be passed to the `ProcessSchema` 
        # as `**kwargs`.
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
    below:

    ```
    >>> ps = ProcessSchema(doc)
    >>> ps.analyze(lookup_param="b", numerical_param=5)
    {"x": 100, "y": 200}
    ```

    Parameters
    ----------
    schema : dict, str, or path
        Schema data following the required structure of the `ProcessSchema` 
        class. Can be input as a Python `dict`, an absolute path to a JSON 
        file, or a relative path to a JSON file within the default 
        `SCHEMA_PATH` directories.
    label : str, optional
        Label associated with the `ProcessFunction`. If not provided, will default 
        to the `label` parameter of the input schema.
    tags : list, optional
        List of tags to be associated with the `ProcessFunction`. Tags may be 
        shared between multiple `ProcessFunction` instances, allowing them to 
        be referenced collectively.
    """

    _valid_actions = ['get', 'lt', 'gt', 'lte', 'gte']

    def __init__(self, schema, label=None, tags=[]):
        self.schema = schema
        self.label = label
        self.tags = tags

    @property
    def parameters(self):
        return self._schema['parameters']
    
    @property
    def returns(self):
        # Traverse data to retrieve keys of first valid output data subset
        data = self._schema['data']
        for parameter in self.parameters:
            data = list(data.values())[0]
        # Check for return type of dict or value
        if isinstance(data, dict):
            return list(data.keys())
        else:
            return [self.label]

    @property
    def actions(self):
        return self._schema['actions']

    @property
    def data(self):
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
        self._label = obj['label']

    def _validate_label(self, label):
        if label is None:
            label = self._schema['label']
        return label

    def _validate_schema(self, obj):
        # Check for required structure
        try:
            keys = obj["parameters"]
        except KeyError:
            raise KeyError(
                "Input schema is missing the required `parameters` "
                "information."
            )
        try:
            actions = obj["actions"]
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
            assert all(action in self._valid_actions for action in actions)
        except:
            raise ValueError(
                f"Each input `action` must only be one of "
                f"{self._valid_actions}."
            )
        try:
            data = obj["data"]
        except KeyError:
            raise KeyError(
                "Input schema is missing the required `data` information."
            )
        try:
            obj["label"]
        except KeyError:
            raise KeyError(
                "Input schema is missing the required `label` information."
            )
        return obj

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
                    f"Missing required `ProcessSchema` parameter `{parameter}`."
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
