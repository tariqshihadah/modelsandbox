from __future__ import annotations
from itertools import count
from modelsandbox.model.base import BaseContainer, BaseProcessor
from modelsandbox.model.processors import FunctionProcessor, SchemaProcessor, EmptyProcessor


class ContainerAdder(object):
    """
    Class for adding model components to a container.
    """

    def add_layer(self, *args, **kwargs) -> Layer:
        """
        Add a new model layer to the existing model container.
        """
        return self.add_member(Layer(*args, **kwargs))

    def add_sequence(self, *args, **kwargs) -> Sequence:
        """
        Add a new model sequence to the existing model layer.
        """
        return self.add_member(Sequence(*args, **kwargs))
    
    def add_function(self, *args, **kwargs) -> FunctionProcessor:
        """
        Add a new model function to the existing model layer.
        """
        return self.add_member(FunctionProcessor(*args, **kwargs))
    
    def add_schema(self, *args, **kwargs) -> SchemaProcessor:
        """
        Add a new model schema to the existing model layer.
        """
        return self.add_member(SchemaProcessor(*args, **kwargs))
    
    def add_wrapped(self, *args, **kwargs) -> callable:
        """
        Add a new model function to the existing model layer by returning a 
        decorator to wrap the function.
        """
        def wrapper(func) -> FunctionProcessor:
            return self.add_function(func=func, *args, **kwargs)
        return wrapper


class Layer(BaseContainer, ContainerAdder):
    """
    Model layer which processes members concurrently.
    """
    _ids = count(0)

    def __init__(self, *args, **kwargs) -> None:
        self._id = next(self._ids)
        super().__init__(*args, **kwargs)

    def _prepare_label(self) -> str:
        return f"layer_{self._id}"

    def analyze(self, **params) -> dict:
        """
        Execute the model layer.

        Parameters
        ----------
        params : dict
            Dictionary of parameters to be passed to the first member in the 
            layer.

        Returns
        -------
        returns : dict
            Dictionary of return values from the model layer.
        """
        # Initialize the return values
        returns = {}
        returns.update(params)
        # Execute the model layers
        for layer in self._members:
            returns_i = layer.analyze(**params) # Input params
            returns.update(returns_i)

        # Remove hidden return values
        for hidden in self.hidden:
            returns.pop(hidden, None)

        # Return the results of analyzing all layers
        return returns


class Sequence(BaseContainer, ContainerAdder):
    """
    Model sequence which processes members sequentially.
    """
    _ids = count(0)

    def __init__(self, *args, **kwargs) -> None:
        self._id = next(self._ids)
        super().__init__(*args, **kwargs)

    def _prepare_label(self) -> str:
        return f"sequence_{self._id}"

    def analyze(self, **params) -> dict:
        """
        Execute the model sequence.

        Parameters
        ----------
        params : dict
            Dictionary of parameters to be passed to the first member in the 
            sequence.

        Returns
        -------
        returns : dict
            Dictionary of return values from the model sequence.
        """
        # Initialize the return values
        returns = {}
        returns.update(params)
        # Execute the model layers
        for layer in self._members:
            returns_i = layer.analyze(**returns) # Input returns
            returns.update(returns_i)

        # Remove hidden return values
        for hidden in self.hidden:
            returns.pop(hidden, None)

        # Return the results of analyzing all layers
        return returns


Layer._valid_member_types = (Sequence, BaseProcessor)
Sequence._valid_member_types = (Layer, BaseProcessor)
