from modelsandbox.model.base import BaseContainer

class ModelCursor(object):
    """
    Cursor for navigating and manipulating model components.
    """

    def __init__(self, root):
        self.root = root

    def __enter__(self):
        pass

    @property
    def root(self):
        """
        The root of the model cursor instance.
        """
        return self._root
    
    @root.setter
    def root(self, container):
        if not isinstance(container, BaseContainer):
            raise TypeError(
                "ModelCursor root must be a BaseContainer instance."
            )
        self._root = container

    def reset(self):
        """
        Reset the cursor to the root of the model.
        """
        self.loc = ()

    def add_layer():
        """
        Add a new layer to the model at the current cursor location.
        """
        pass

    def add_sequence():
        """
        Add a new sequence to the model at the current cursor location.
        """
        pass

    def add_wrapped():
        """
        Add a new wrapped function processor to the model at the current cursor location.
        """
        pass

    def add_function():
        """
        Add a new function processor to the model at the current cursor location.
        """
        pass

    def add_schema():
        """
        Add a new schema processor to the model at the current cursor location.
        """
        pass