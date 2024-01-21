from modelsandbox.model.base import ModelComponentBase
from modelsandbox.model.layer import ModelLayer


class ModelPointer(object):
    """
    Class for referencing and adding model components relative to a given root.
    """

    def __init__(self, root: ModelComponentBase, loc: tuple=None) -> None:
        self.root = root
        self.loc = loc

    @property
    def root(self) -> ModelComponentBase:
        """
        Return the model root being referenced by the pointer.
        """
        return self._root
    
    @root.setter
    def root(self, root: ModelComponentBase) -> None:
        if not isinstance(root, ModelComponentBase):
            raise TypeError(
                f"ModelPointer root must be of type {ModelComponentBase}, "
                f"not {type(root)}."
            )
        self._root = root

    @property
    def loc(self) -> tuple:
        """
        Return the location of the model component being referenced by the 
        pointer relative to the root.
        """
        return self._loc
    
    @loc.setter
    def loc(self, loc: tuple) -> None:
        if loc is None:
            self._loc = ()
        elif isinstance(loc, int):
            self._loc = (loc,)
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
        
    def get_component(self, loc: tuple=None):
        """
        Return the model component being referenced by the pointer or at the 
        provided location.
        """
        loc = self._check_loc(loc)
        # Get root
        component = self._root
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
        return component