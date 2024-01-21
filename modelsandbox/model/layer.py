import itertools
from modelsandbox.model.base import ModelComponentBase
from modelsandbox.model.processors import FunctionProcessor, SchemaProcessor, EmptyProcessor


class ModelLayer(ModelComponentBase):
    """
    Main class for model Layers which may contain individual model 
    processors or additional model Layers.

    Parameters
    ----------
    label : str, optional
        Label associated with the model component.
    tags : list, optional
        List of tags to be associated with the model component. Tags may be 
        shared between multiple components, allowing them to be referenced 
        collectively.
    """

    def __init__(self, label: str=None, tags: list=[]) -> None:
        self._components = []
        self.label = label
        self.tags = tags

    def __len__(self) -> int:
        return len(self._components)

    def __getitem__(self, index):
        try:
            return self._components[index]
        except:
            raise IndexError(
                f"Index {index} is out of range of the {self.__class__} with "
                f"{len(self._components)} components."
            )
    
    @property
    def components(self) -> list:
        return self._components
    
    @property
    def params(self) -> list:
        """
        Return a list of parameters for all components in the model Layer.
        """
        params = []
        for component in self._components:
            params.extend(component.params)
        return list(set(params))
    
    @property
    def returns(self) -> list:
        """
        Return a list of return values for all components in the model Layer.
        """
        returns = []
        for component in self._components:
            returns.extend(component.returns)
        return list(set(returns))
    
    @property
    def processors(self) -> list:
        """
        Return a nested list processors of layer components.
        """
        processors = []
        for component in self._components:
            if isinstance(component, ModelLayer):
                processors.append(component.processors)
            else:
                processors.append(component)
        return processors
    
    @property
    def structure(self) -> dict:
        """
        Return a nested dictionary of the model structure.
        """
        structure = {}
        for component in self._components:
            if isinstance(component, ModelLayer):
                structure[component.label] = component.structure
            else:
                structure[component.label] = component
        return structure
    
    @property
    def all_tags(self):
        """
        List of unique processor tags included within the model.
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
        associated with each tag.
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

    def add_layer(self, label: str=None, tags: list=[]) -> None:
        """
        Add a new model Layer to the existing model Layer.

        Parameters
        ----------
        label : str, optional
            Label associated with the model component.
        tags : list, optional
            List of tags to be associated with the model component. Tags may be 
            shared between multiple components, allowing them to be referenced 
            collectively.
        """
        # Check label
        if label is None:
            # Use default label
            index = len([i for i in self._components if isinstance(i, ModelLayer)])
            label = f"Layer {index + 1}"
        # Create the model layer
        layer = ModelLayer(label=label, tags=self._tags + tags)
        self._components.append(layer)
        return layer
    
    def add_schema(self, schema: dict, label: str=None, tags: list=[]) -> None:
        """
        Add a new model schema to the existing model Layer.

        Parameters
        ----------
        schema : dict
            Dictionary containing the schema for the model component.
        label : str, optional
            Label associated with the model component.
        tags : list, optional
            List of tags to be associated with the model component. Tags may be 
            shared between multiple components, allowing them to be referenced 
            collectively.
        """
        # Create the model schema
        processor = SchemaProcessor(
            schema, label=label, tags=self._tags + tags
        )
        self._components.append(processor)
        return processor

    def add_function(self, function, label: str=None, tags: list=[]) -> None:
        """
        Add a new model function to the existing model Layer.

        Parameters
        ----------
        function : function
            Function containing the schema for the model component.
        label : str, optional
            Label associated with the model component.
        tags : list, optional
            List of tags to be associated with the model component. Tags may be 
            shared between multiple components, allowing them to be referenced 
            collectively.
        """
        # Create the model function
        processor = FunctionProcessor(
            function, label=label, tags=self._tags + tags
        )
        self._components.append(processor)
        return processor
    
    def add_wrapped(self, label: str=None, tags: list=[]) -> None:
        """
        Add a new model function to the existing model Layer by returning a 
        decorator to wrap the function.

        Parameters
        ----------
        label : str, optional
            Label associated with the model component.
        tags : list, optional
            List of tags to be associated with the model component. Tags may be 
            shared between multiple components, allowing them to be referenced 
            collectively.
        """
        # Define the wrapper
        def wrapper(function):
            return self.add_function(function, label=label, tags=tags)
        return wrapper
    
    def add_empty(self, label: str=None, tags: list=[]) -> None:
        """
        Add a new empty model component to the existing model Layer.

        Parameters
        ----------
        label : str, optional
            Label associated with the model component.
        tags : list, optional
            List of tags to be associated with the model component. Tags may be 
            shared between multiple components, allowing them to be referenced 
            collectively.
        """
        # Create the model component
        processor = EmptyProcessor(label=label, tags=self._tags + tags)
        self._components.append(processor)
        return processor
    
    def add_component(self, component: ModelComponentBase) -> None:
        """
        Add an existing model component to the existing model Layer.

        Parameters
        ----------
        component : ModelComponentBase
            Model component to be added to the model Layer.
        """
        # Add the model component
        self._components.append(component)
        return component
    
    def add_components(self, components: list) -> None:
        """
        Add multiple existing model components to the existing model Layer.

        Parameters
        ----------
        components : list
            List of model components to be added to the model Layer.
        """
        # Add the model components
        for component in components:
            self.add_component(component)
        return components
    
    def remove_component(self, index: int) -> None:
        """
        Remove an existing model component from the existing model Layer.

        Parameters
        ----------
        index : int
            Index of the model component to be removed from the model Layer.
        """
        # Remove the model component
        del self._components[index]
        return None
    
    def remove_components(self, indices: list) -> None:
        """
        Remove multiple existing model components from the existing model Layer.

        Parameters
        ----------
        indices : list
            List of indices of model components to be removed from the model 
            Layer.
        """
        # Remove the model components
        for index in sorted(indices, reverse=True):
            self.remove_component(index)
        return None
    
    def clear(self) -> None:
        """
        Clear all model components from the model Layer.
        """
        # Clear the model components
        self._components = []
        return None
    
    def analyze(self, **params) -> dict:
        """
        Execute the model component.

        Parameters
        ----------
        params : dict
            Dictionary of parameters to be passed to the model component.

        Returns
        -------
        dict
            Dictionary of return values from the model component.
        """
        # Initialize the return values
        returns = {}
        # Execute the model components
        print(f'\n{self.label} layer parameters: ', self.params)
        for component in self._components:
            # Filter parameters
            print(f'\n{component.label} component parameters: ', component.params)
            print(f'\nAvailable parameters: ', params)
            params_i = {k: v for k, v in params.items() if k in component.params}
            returns_i = component.analyze(**params_i)
            returns.update(returns_i)
            print(f'\nProduced returns: ', returns_i)

        # Update tagged returns
        for tag, processors in self.tagged.items():
            if tag in returns:
                returns[tag].update({p.label: returns[p.label] for p in processors})
            else:
                returns[tag] = {p.label: returns[p.label] for p in processors}

        # Update parameters with returns and return
        params.update(returns)
        return params