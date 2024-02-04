from __future__ import annotations
from typing import Union
from keyword import iskeyword
import itertools


class BaseLabeled(object):
    """
    Base class for labeled model components.
    """

    def __init__(self, label: str, *args, **kwargs) -> None:
        self.label = label

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
    
    def _validate_label(self, label: str) -> str:
        """
        Validate the label for the model component.
        """
        if label is None:
            label = self._prepare_label()
        if not isinstance(label, str):
            raise TypeError("Label must be a string.")
        elif not label.isidentifier():
            raise ValueError("Label must be a valid Python identifier string.")
        elif iskeyword(label):
            raise ValueError("Label cannot be a Python keyword.")
        return label
    
    def _prepare_label(self, label) -> str:
        """
        Get the label for the model component if possible. Fallback method 
        if no label is provided. Subclass-dependent.
        """
        raise ValueError("No label provided.")
    
    def set_label(self, label: str) -> None:
        """
        Set the label for the model component.
        """
        self.label = label


class BaseTaggable(object):
    """
    Base class for taggable model components.
    """

    def __init__(self, tags: list=[], *args, **kwargs) -> None:
        self.tags = tags

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

    def analyze(self, **params) -> dict:
        """
        Execute the model component.
        """
        raise NotImplementedError
    

class BaseProcessor(BaseCallable, BaseTaggable, BaseLabeled):
    """
    Base class for model processors.
    """
    pass


class BaseContainer(BaseCallable, BaseTaggable, BaseLabeled):
    """
    Base class for container model components.
    """

    _valid_member_types = []

    def __init__(self, members: list=[], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._members = self._validate_members(members)

    def __len__(self) -> int:
        return len(self._members)
    
    def __getitem__(self, index):
        try:
            return self._members[index]
        except:
            raise IndexError(
                f"Index {index} is out of range of the {self.__class__} with "
                f"{len(self._members)} members."
            )
    
    def __iter__(self):
        return iter(self._members)
    
    def __contains__(self, member):
        return member in self._members
    
    def _validate_member(self, member) -> object:
        """
        Validate a member for the model component.
        """
        if not isinstance(member, self._valid_member_types):
            raise TypeError(
                f"Members of {self.__class__} must be instances of "
                f"{self._valid_member_types}."
            )
        return member
    
    def _validate_members(self, members: list) -> list:
        """
        Validate members for the model component.
        """
        return [self._validate_member(member) for member in members]
    
    @property
    def members(self) -> list:
        """
        Return a list of model component members.
        """
        return self._members
    
    @members.setter
    def members(self, members: list) -> None:
        self._members = self._validate_members(members)

    @property
    def all_params(self) -> list:
        """
        Return a list of all parameters for the model component, including 
        those covered by hidden returns.
        """
        params = []
        for member in self._members:
            params.extend(member.params)
        return list(set(params))
    
    @property
    def params(self) -> list:
        """
        Return a list of parameters for the model component.
        """
        return self.all_params
    
    @property
    def hidden(self) -> list:
        """
        Return a list of hidden return values for the model component.
        """
        # Check hidden parameter for additions
        if self._hidden_param==True:
            return self.all_returns
        elif self._hidden_param==False:
            hidden = []
        else:
            hidden = self._hidden_param
        # Add hidden returns from members
        for member in self._members:
            hidden.extend(member.hidden)
        return list(set(hidden))
    
    @property
    def all_returns(self) -> list:
        """
        Return a list of all return values for the model component, including
        hidden returns.
        """
        returns = []
        for member in self._members:
            returns.extend(member.returns)
        return list(set(returns))

    @property
    def returns(self) -> list:
        """
        Return a list of return values for the model component.
        """
        return self.all_returns
    
    @property
    def processors(self) -> list:
        """
        Return a nested list processors in the model structure.
        """
        processors = []
        for member in self._members:
            if isinstance(member, BaseContainer):
                processors.append(member.processors)
            elif isinstance(member, BaseProcessor):
                processors.append(member)
            else:
                raise TypeError("Invalid member type.")
        return processors
    
    @property
    def structure(self) -> dict:
        """
        Return a nested dictionary of the model structure.
        """
        structure = {}
        for member in self._members:
            if isinstance(member, BaseContainer):
                structure[member.label] = member.structure
            elif isinstance(member, BaseProcessor):
                structure[member.label] = member
            else:
                raise TypeError("Invalid member type.")
        return structure
    
    @property
    def processors_flat(self) -> list:
        """
        Return a flat list of processors in the model structure.
        """
        processors = []
        for member in self._members:
            if isinstance(member, BaseContainer):
                processors.extend(member.processors_flat)
            elif isinstance(member, BaseProcessor):
                processors.append(member)
            else:
                raise TypeError("Invalid member type.")
        return processors
    
    @property
    def all_tags(self):
        """
        List of unique processor tags included within the model structure.
        """
        tags = list(itertools.chain.from_iterable(
            p.tags for p in self.processors_flat))
        return list(set(tags))

    @property
    def tagged(self):
        """
        Dictionary of unique processor tags and lists of all processors 
        associated with each tag within the model structure.
        """
        tagged = {}
        for tag in self.all_tags:
            tagged[tag] = [p for p in self.processors_flat if tag in p.tags]
        return tagged
    
    def add_member(self, member) -> None:
        """
        Add a member to the model component.
        """
        member = self._validate_member(member)
        self._members.append(member)


class Layer(BaseContainer):
    """
    Model layer which processes members concurrently.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class Sequence(BaseContainer):
    """
    Model sequence which processes members sequentially.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def params(self) -> list:
        """
        Return a list of parameters for the model component.
        """
        return list(set(self.all_params) - set(self.hidden))

    @property
    def returns(self) -> list:
        """
        Return a list of return values for the model component.
        """
        return list(set(self.all_returns) - set(self.hidden))
    
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
            returns_i = layer.analyze(**returns)
            returns.update(returns_i)

        # Return the results of analyzing all layers
        return returns


Layer._valid_member_types = [Sequence, BaseProcessor]
Sequence._valid_member_types = [Layer, BaseProcessor]
