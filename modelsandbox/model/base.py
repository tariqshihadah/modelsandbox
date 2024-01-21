class ModelComponentBase(object):
    """
    Base class for model components.
    """

    def __call__(self, **params) -> dict:
        return self.analyze(**params)
    
    def __name__(self) -> str:
        return self._label
    
    @property
    def label(self) -> str:
        """
        Return the label for the model component.
        """
        return self._label
    
    @label.setter
    def label(self, label: str) -> None:
        self._label = self._validate_label(label)
    
    @property
    def tags(self) -> list:
        """
        Return a list of tags for the model component.
        """
        return self._tags
    
    @tags.setter
    def tags(self, tags: list) -> None:
        if tags is None:
            self._tags = []
        elif isinstance(tags, str):
            self._tags = [tags]
        else:
            self._tags = list(tags)

    def _validate_label(self, label: str) -> str:
        """
        Validate the label for the model component.
        """
        return label

    def analyze(self, **params) -> dict:
        """
        Execute the model component.
        """
        raise NotImplementedError
    

class EmptyComponent(ModelComponentBase):
    """
    Class for empty model components.
    """

    def __init__(self, label: str=None, tags: list=[]) -> None:
        self._components = None
        self.label = label
        self.tags = tags

    def analyze(self, **params) -> dict:
        return {}