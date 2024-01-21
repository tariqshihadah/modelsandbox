from typing import Any
from modelsandbox.model.base import ModelComponentBase
from modelsandbox.model.layer import ModelLayer
from modelsandbox.model.processors import FunctionProcessor, SchemaProcessor, EmptyProcessor
from modelsandbox.model.pointer import ModelPointer


class Model(object):
    """
    Top-level class for defining and executing models.
    """

    def __init__(self):
        self._root = ModelLayer()

    def __getitem__(self, index):
        return ModelPointer(self._root, index).get_component()
    
    def __setitem__(self, index, value):
        raise NotImplementedError(
            "Directly setting model components is not yet supported."
        )

    @property
    def root(self):
        """
        Return the root model Layer.
        """
        return self._root
    
    @property
    def params(self):
        """
        Return a list of parameters for the model.
        """
        return self._root.params
    
    @property
    def returns(self):
        """
        Return a list of return values for the model.
        """
        return self._root.returns

    @property
    def processors(self):
        """
        Return a nested list processors of model components.
        """

        return self._root.processors
    
    @property
    def structure(self):
        """
        Return a nested dictionary of the model structure.
        """
        return self._root.structure

    def analyze(**params):
        """
        Execute the model.
        """
        pass