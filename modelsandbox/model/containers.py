from __future__ import annotations
from typing import Union
from keyword import iskeyword
import itertools, inspect

from modelsandbox.model.base import BaseComponent, BaseCallable, BaseTaggable, BaseProcessor


class Container(BaseComponent, BaseCallable, BaseTaggable):
    """
    Base class for container model components.
    """

    _valid_member_types = ()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._init_members()

    def __len__(self) -> int:
        return len(self._members)
    
    def __iter__(self):
        return iter(self._members.items())
    
    def __getattr__(self, name):
        try:
            members = object.__getattribute__(self, '_members')
            self._members[[m.label for m in members].index(name)]
        except ValueError:
            object.__getattribute__(self, name)
    
    def _init_members(self) -> None:
        """
        Initialize model component members.
        """
        # Initialize member classes
        self._init_classes()
        # Collect all members
        members = []
        for k, v in inspect.getmembers(self):
            if isinstance(v, BaseComponent):
                members.append(v)
        # Sort members by order
        members = sorted(members, key=lambda x: x.order)
        self._members = members
    
    def _init_classes(self) -> None:
        """
        Initialize model component member classes.
        """
        # Initialize inner classes as members
        for k, v in self.__class__.__dict__.items():
            # Select only valid members
            if inspect.isclass(v):
                if issubclass(v, BaseComponent):
                    setattr(self, k, v())

    @property
    def members(self) -> list:
        """
        Return a list of model component members.
        """
        return self._members
    
    @property
    def params(self) -> list:
        """
        Return a list of all parameters for the model container.
        """
        params = []
        returns = []
        for index, members in self.ordered.items():
            for member in members:
                params.extend(member.params)
                returns.extend(member.returns)
        return sorted(set(params) - set(returns))
    
    @property
    def hidden(self) -> list:
        """
        Return a list of hidden return values for the model container.
        """
        # Check hidden parameter for additions
        if self._hidden_param==True:
            return self.returns
        elif self._hidden_param==False:
            hidden = []
        else:
            hidden = self._hidden_param
        
        # Add hidden returns from members
        for index, members in self.ordered.items():
            for member in members:
                hidden.extend(member.hidden)
        return sorted(set(hidden))
    
    @property
    def returns(self) -> list:
        """
        Return a list of all return values for the model container.
        """
        returns = []
        hidden = []
        for index, members in self.ordered.items():
            for member in members:
                returns.extend(member.returns)
                hidden.extend(member.hidden)
        return sorted(set(returns) - set(hidden))

    @property
    def processors(self) -> list:
        """
        Return a nested list processors in the model structure.
        """
        processors = []
        for member in self._members:
            if isinstance(member, Container):
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
            if isinstance(member, Container):
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
            if isinstance(member, Container):
                processors.extend(member.processors_flat)
            elif isinstance(member, BaseProcessor):
                processors.append(member)
            else:
                raise TypeError(f"Invalid member type: {member}.")
        return processors
    
    @property
    def ordered(self) -> dict:
        """
        Return a dictionary of order indices and lists of model components at 
        each order index.
        """
        ordered = {}
        for member in self._members:
            if member.order not in ordered:
                ordered[member.order] = []
            ordered[member.order].append(member)
        return ordered
    
    @property
    def all_tags(self):
        """
        List of unique processor tags included within the model structure.
        """
        tags = list(itertools.chain.from_iterable(
            p.tags for p in self.processors_flat))
        return sorted(set(tags))

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
    
    def analyze(self, **params) -> dict:
        """
        Step through model structure and execute processors.
        """
        # Initialize results
        results = {}
        # Step through order indices
        for index, members in self.ordered.items():
            # Update parameters with results
            params.update(results)
            # Step through members at order index
            for member in members:
                # Filter parameters
                filtered_params = member._filter_params(**params)
                # Execute processor
                result = member.analyze(**filtered_params)
                # Add result to results
                results.update(result)
        
        # Remove hidden returns
        for hidden in self.hidden:
            results.pop(hidden, None)
        return results