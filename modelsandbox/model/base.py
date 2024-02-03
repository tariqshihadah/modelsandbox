from __future__ import annotations
import re
from keyword import iskeyword
import itertools


class BaseCallable(object):
    """
    Base class for callable model components.
    """

    def __init__(self, *args, **kwargs) -> None:
        pass

    def __call__(self, **params) -> dict:
        return self.analyze(**params)
    
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
    
    def analyze(self, **params) -> dict:
        """
        Execute the model component.
        """
        raise NotImplementedError
    

class BaseTaggable(object):
    """
    Base class for taggable model components.
    """

    def __init__(self, tags: list=[], *args, **kwargs) -> None:
        pass

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
        if not isinstance(label, str):
            raise TypeError("Label must be a string.")
        elif not label.isidentifier():
            raise ValueError("Label must be a valid Python identifier string.")
        elif iskeyword(label):
            raise ValueError("Label cannot be a Python keyword.")
        return label
    
    def set_label(self, label: str) -> None:
        """
        Set the label for the model component.
        """
        self.label = label


class BaseContainer(object):
    """
    Base class for container model components.
    """

    _member_type = "member"
    _member_types = "members"
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


class BaseLayer(BaseCallable, BaseTaggable, BaseLabeled, BaseContainer): pass


class BaseSequence(BaseCallable, BaseTaggable, BaseLabeled, BaseContainer): pass


class BaseProcessor(BaseCallable, BaseTaggable, BaseLabeled): pass


BaseLayer._valid_member_types = [BaseSequence, BaseProcessor]
BaseSequence._valid_member_types = [BaseLayer, BaseProcessor]


class ModelComponentBase(object):
    """
    Base class for model components.
    """
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(label='{self.label}', tags={self.tags})"
    

class ModelStructureBase(ModelComponentBase):
    """
    Base class for model structures.
    """

    _member_type = "member"
    _member_types = "members"
    
    def __init__(self, label: str=None, tags: list=[]) -> None:
        self._members = []
        self.label = label
        self.tags = tags

    def __len__(self) -> int:
        return len(self._members)
    
    def __getitem__(self, index):
        try:
            return self._members[index]
        except:
            raise IndexError(
                f"Index {index} is out of range of the {self.__class__} with "
                f"{len(self._members)} {self._member_types}."
            )
        
    @property
    def layers(self) -> list:
        return self._layers

    @property
    def params(self) -> list:
        """
        Return a list of parameters for all members in the model structure.
        """
        params = []
        for member in self._members:
            params.extend(member.params)
        return list(set(params))
    
    @property
    def returns(self) -> list:
        """
        Return a list of return values for all members in the model structure.
        """
        returns = []
        for member in self._members:
            returns.extend(member.returns)
        return list(set(returns))
    
    @property
    def members(self) -> list:
        """
        Return a list of model structure members.
        """
        return self._members
        
    @property
    def processors(self) -> list:
        """
        Return a nested list processors in the model structure.
        """
        processors = []
        for member in self._members:
            if isinstance(member, ModelStructureBase):
                processors.append(member.processors)
            elif isinstance(member, ModelProcessorBase):
                processors.append(member)
            else:
                raise TypeError(
                    f"Members of {self.__class__} must be instances of "
                    f"ModelStructureBase or ModelProcessorBase."
                )
        return processors
    
    @property
    def structure(self) -> dict:
        """
        Return a nested dictionary of the model structure.
        """
        structure = {}
        for member in self._members:
            if isinstance(member, ModelStructureBase):
                structure[member.label] = member.structure
            elif isinstance(member, ModelProcessorBase):
                structure[member.label] = member
            else:
                raise TypeError(
                    f"Members of {self.__class__} must be instances of "
                    f"ModelStructureBase or ModelProcessorBase."
                )
        return structure
    
    @property
    def all_tags(self):
        """
        List of unique processor tags included within the model structure.
        """
        # Get list of all processors
        try:
            processors = list(itertools.chain.from_iterable(self.processors))
        except TypeError:
            processors = self.processors
        # Get tags
        tags = list(itertools.chain.from_iterable(p.tags for p in processors))
        return list(set(tags))

    @property
    def tagged(self):
        """
        Dictionary of unique processor tags and lists of all processors 
        associated with each tag within the model structure.
        """
        # Get list of all processors
        try:
            processors = list(itertools.chain.from_iterable(self.processors))
        except TypeError:
            processors = self.processors
        # Find tagged processors
        tagged = {}
        for tag in self.all_tags:
            tagged[tag] = [p for p in processors if tag in p.tags]
        return tagged


class ModelProcessorBase(ModelComponentBase):
    """
    Base class for model processors.

    Model processors are the lowest level of model definition. They include 
    the following subclasses:

    - FunctionProcessor
    - SchemaProcessor
    - EmptyProcessor
    """
    pass