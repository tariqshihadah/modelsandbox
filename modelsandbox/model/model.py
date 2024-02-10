from __future__ import annotations
from modelsandbox.model.containers import Sequence, Layer
from modelsandbox.model.processors import FunctionProcessor, SchemaProcessor, EmptyProcessor
from modelsandbox.model.base import BaseContainer


class Model(object):
    """
    Top-level class for defining and executing models.
    """

    def __init__(self, **kwargs):
        self._root = Sequence(**kwargs)
        self._cursor = Cursor(self)

    def __getitem__(self, index):
        return self._root[index]
    
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
    def cursor(self):
        """
        Return the cursor for the model.
        """
        return self._cursor
    
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

    @property
    def tags(self):
        """
        List of unique processor tags included within the model.
        """
        return self._root.tags

    @property
    def all_tags(self):
        """
        List of unique processor tags included within the model.
        """
        return self._root.all_tags

    @property
    def tagged(self):
        """
        Dictionary of unique processor tags and lists of all processors 
        associated with each tag.
        """
        return self._root.tagged

    def analyze(self, **params):
        """
        Execute the model.
        """
        return self._root.analyze(**params)
    

class Cursor(object):
    """
    Class for managing and accessing indexed positions within a model.
    """

    def __init__(self, model: Model):
        self.model = model
        self.reset()

    def __getitem__(self, index):
        """
        Return the model component at the specified index.
        """
        return self.get_index(index)
    
    def __enter__(self):
        # Get the currently indexed component
        component = self.get_current()
        # If the component is a container, attempt to enter it
        if isinstance(component, BaseContainer):
            if len(component) == 0:
                raise IndexError(
                    "Cannot enter an empty container. Add a new sub-container "
                    "with the 'add_layer' or 'add_sequence' methods.")
            self._index.append(len(component) - 1)
        else:
            raise TypeError("Cannot enter a non-container component.")
        return self.get_current()
    
    def __exit__(self, exc_type, exc_value, traceback):
        # Move down one level in the model cursor
        self._index.pop()

    @property
    def model(self):
        """
        Return the model associated with the cursor.
        """
        return self._model
    
    @model.setter
    def model(self, obj: Model):
        """
        Set the model associated with the cursor.
        """
        if not isinstance(obj, Model):
            raise TypeError("Model must be an instance of 'Model'.")
        self._model = obj

    @property
    def root(self):
        """
        Return the root of the model.
        """
        return self.model.root
    
    def _validate_index(self, index: tuple[list, tuple]):
        """
        Validate the index to ensure it is a valid path within the model.
        """
        if not isinstance(index, (list, tuple, int)):
            raise TypeError("Index must be a list, tuple, or integer.")
        if isinstance(index, int):
            return [index]
        if not all(isinstance(i, int) for i in index):
            raise TypeError("Index must contain only integers.")
        return list(index)

    def reset(self):
        """
        Reset the cursor to the root of the model.
        """
        self._index = [] # Point to the root of the model

    def _get_from_root(self, index: tuple[list, tuple]):
        """
        Traverse the model root to get the indexed component.
        """
        # Start at the model root
        container = self._model.root
        return self._get_from_container(container, index)
    
    @classmethod
    def _get_from_container(cls, container: BaseContainer, index: tuple[list, tuple]):
        # Iterate over indices to traverse components
        component = container
        for i, j in enumerate(index):
            try:
                component = component[j]
            except:
                raise IndexError(f"Index {j} at position {i} is out of range.")
        return component

    def get_current(self):
        """
        Return the current model component.
        """
        return self._get_from_root(self._index)
    
    def get_index(self, index: tuple[list, tuple]):
        """
        Return the model component at the specified index relative to the 
        current cursor position.
        """
        return self._get_from_root(self._index + self._validate_index(index))
    
    def add_layer(self, *args, **kwargs) -> Cursor:
        """
        Add a new model layer to the indexed model container.

        Returns
        -------
        This method returns itself to allow for chaining and the use of the 
        with statement syntax.
        """
        # Get current component
        container = self.get_current()
        # Confirm valid container
        if not isinstance(container, BaseContainer):
            raise TypeError("Cannot add component to a non-container component.")
        # Add member
        container.add_layer(*args, **kwargs)
        return self
    
    def add_sequence(self, *args, **kwargs) -> Cursor:
        """
        Add a new model sequence to the indexed model layer.

        Returns
        -------
        This method returns itself to allow for chaining and the use of the
        with statement syntax.
        """
        # Get current component
        container = self.get_current()
        # Confirm valid container
        if not isinstance(container, BaseContainer):
            raise TypeError("Cannot add component to a non-container component.")
        # Add member
        container.add_sequence(*args, **kwargs)
        return self
    
    def add_function(self, *args, **kwargs) -> Cursor:
        """
        Add a new model function to the indexed model layer.

        Returns
        -------
        This method returns itself to allow for chaining and the use of the
        with statement syntax.
        """
        # Get current component
        container = self.get_current()
        # Confirm valid container
        if not isinstance(container, BaseContainer):
            raise TypeError("Cannot add component to a non-container component.")
        # Add member
        container.add_function(*args, **kwargs)
        return self
    
    def add_schema(self, *args, **kwargs) -> Cursor:
        """
        Add a new model schema to the indexed model layer.

        Returns
        -------
        This method returns itself to allow for chaining and the use of the
        with statement syntax.
        """
        # Get current component
        container = self.get_current()
        # Confirm valid container
        if not isinstance(container, BaseContainer):
            raise TypeError("Cannot add component to a non-container component.")
        # Add member
        container.add_schema(*args, **kwargs)
        return self
    
    def add_wrapped(self, *args, **kwargs) -> callable:
        """
        Add a new model function to the indexed model layer by returning a 
        decorator to wrap the function.

        Returns
        -------
        This method returns a decorator to wrap the function.
        """
        # Get current component
        container = self.get_current()
        # Confirm valid container
        if not isinstance(container, BaseContainer):
            raise TypeError("Cannot add component to a non-container component.")
        # Add member
        return container.add_wrapped(*args, **kwargs)