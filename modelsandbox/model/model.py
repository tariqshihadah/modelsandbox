from typing import Any
from modelsandbox.model.layer import ModelLayer
from modelsandbox.model.processors import FunctionProcessor, SchemaProcessor, EmptyProcessor


class Model(object):
    """
    Top-level class for defining and executing models.
    """

    def __init__(self):
        self._root = ModelLayer()

    def __getitem__(self, index):
        return ModelPointer(self, index)
    
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
        return self._model.params

    @property
    def processors(self):
        """
        Return a nested list processors of model components.
        """
        processors = []
        for component in self._root._components:
            if isinstance(component, ModelLayer):
                processors.append(component.processors)
            else:
                processors.append(component)
        return processors

    def analyze(**params):
        """
        Execute the model.
        """
        pass


class ModelPointer(object):
    """
    Class for referencing and adding model components.
    """

    def __init__(self, model: Model, loc: tuple=None) -> None:
        self.model = model
        self.loc = loc

    @property
    def model(self) -> Model:
        """
        Return the model being referenced by the pointer.
        """
        return self._model
    
    @model.setter
    def model(self, model: Model) -> None:
        if not isinstance(model, Model):
            raise TypeError(
                f"ModelPointer model must be of type {Model}, "
                f"not {type(model)}."
            )
        self._model = model

    @property
    def loc(self) -> tuple:
        """
        Return the location of the model component being referenced by the 
        pointer.
        """
        return self._loc
    
    @loc.setter
    def loc(self, loc: tuple) -> None:
        if loc is None:
            self._loc = ()
        elif isinstance(loc, tuple):
            self._loc = loc
        else:
            raise TypeError(
                f"ModelPointer loc must be of type {tuple}, "
                f"not {type(loc)}."
            )
        
    def _check_loc(self, loc: tuple) -> tuple:
        """
        Check if a location is provided. If not, return the pointer's location.
        """
        if loc is None:
            loc = self._loc
        elif not isinstance(loc, tuple):
            raise TypeError(
                f"ModelPointer loc must be of type {tuple}, "
                f"not {type(loc)}."
            )
        return loc
        
    def get_component(self, loc: tuple=None) -> Any:
        """
        Return the model component being referenced by the pointer or at the 
        provided location.
        """
        loc = self._check_loc(loc)
        # Get model root
        component = self._model._root
        for i, position in enumerate(loc):
            if isinstance(component, ModelLayer):
                try:
                    component = component[position]
                except IndexError:
                    raise IndexError(
                        f"ModelPointer loc contains an invalid index "
                        f"at position {i}: {position}. Index is out of range."
                    )
            else:
                raise IndexError(
                    f"ModelPointer loc contains an invalid index "
                    f"at position {i}: {position}. Cannot index a "
                    f"{type(component)}."
                )
