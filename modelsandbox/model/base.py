from __future__ import annotations
from typing import Union
from keyword import iskeyword


class BaseComponent(object):

    # Default order value
    _default_order = 0

    def __init__(self, *args, **kwargs) -> None:
        try:
            self.order = kwargs.pop('order')
        except KeyError:
            pass
        try:
            self.label = kwargs.pop('label')
        except KeyError:
            pass
        super().__init__(*args, **kwargs)

    def __init_subclass__(cls, *args, **kwargs) -> None:
        # Set class-level values
        cls._order = kwargs.pop('order', cls._default_order)
        # Call super
        super().__init_subclass__(*args, **kwargs)

    @property
    def order(self):
        return self._order
    
    @order.setter
    def order(self, value):
        if value is None:
            self._order = self._default_order
        elif isinstance(value, int):
            self._order = value
        else:
            raise TypeError("Value must be of type int")
    
    @property
    def default_label(self):
        return self.__class__.__name__

    @property
    def label(self):
        try:
            return self._label
        except AttributeError:
            return self.default_label
        
    @label.setter
    def label(self, value):
        if value is None:
            return
        else:
            self._label = self._validate_label(value)

    @classmethod
    def _validate_label(cls, label: str) -> str:
        """
        Validate a label for the model component.
        """
        if not isinstance(label, str):
            raise TypeError("Label must be a string.")
        elif not label.isidentifier():
            raise ValueError("Label must be a valid Python identifier string.")
        elif iskeyword(label):
            raise ValueError("Label cannot be a Python keyword.")
        return label


class BaseTaggable(object):
    """
    Base class for taggable model components.
    """

    def __init__(self, tags: list=[], *args, **kwargs) -> None:
        self.tags = tags
        super().__init__(*args, **kwargs)

    @property
    def tags(self) -> list:
        """
        Return a list of tags for the model component.
        """
        return self._tags
    
    @tags.setter
    def tags(self, tags: list) -> None:
        self._tags = self._validate_tags(tags)

    @classmethod
    def _validate_tag(cls, tag: str) -> str:
        """
        Validate a tag for the model component.
        """
        if not isinstance(tag, str):
            raise TypeError("Tag must be a string.")
        elif not tag.isidentifier():
            raise ValueError("Tag must be a valid Python identifier string.")
        elif iskeyword(tag):
            raise ValueError("Tag cannot be a Python keyword.")
        return tag
    
    @classmethod
    def _validate_tags(cls, tags: list) -> list:
        """
        Validate tags for the model component.
        """
        # Validate input
        if tags is None:
            tags = []
        elif isinstance(tags, str):
            tags = [tags]
        else:
            tags = list(tags)
        # Format tags
        return [cls._validate_tag(tag) for tag in set(tags)]
    
    def set_tags(self, tags: list) -> None:
        """
        Set the tags for the model component.
        """
        self.tags = tags

    def add_tags(self, tags: list) -> None:
        """
        Add tags to the model component.
        """
        self.tags.extend(tags)

    def remove_tags(self, tags: list) -> None:
        """
        Remove tags from the model component.
        """
        for tag in tags:
            self.tags.remove(tag)


class BaseCallable(object):
    """
    Base class for callable model components.
    """

    def __init__(self, hidden: Union[bool, list]=False, *args, **kwargs) -> None:
        self.hidden_param = hidden
        super().__init__(*args, **kwargs)

    def __call__(self, **params) -> dict:
        return self.analyze(**params)
    
    @property
    def hidden_param(self) -> Union[bool, list]:
        return self._hidden_param
    
    @hidden_param.setter
    def hidden_param(self, hidden: Union[bool, list]) -> None:
        if not isinstance(hidden, (bool, list)):
            raise ValueError(
                "Input hidden must be a boolean or a list of parameters to "
                "hide."
            )
        self._hidden_param = hidden
    
    @property
    def params(self) -> list:
        """
        Return a list of parameters for the model component.
        """
        raise NotImplementedError
    
    @property
    def returns(self) -> list:
        """
        Return a list of parameters for the model component.
        """
        raise NotImplementedError
    
    @property
    def hidden(self) -> list:
        """
        Return a list of hidden return values for the model component.
        """
        # Check hidden parameter for additions
        if self._hidden_param==True:
            return self.returns
        elif self._hidden_param==False:
            return []
        else:
            return self._hidden_param
        
    def _filter_params(self, **params) -> dict:
        """
        Filter parameters for the model component.
        """
        return {k: v for k, v in params.items() if k in self.params}

    def analyze(self, **params) -> dict:
        """
        Execute the model component.
        """
        raise NotImplementedError
    

class BaseProcessor(BaseComponent, BaseCallable, BaseTaggable):
    """
    Base class for model processors.
    """
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
