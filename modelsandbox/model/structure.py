from __future__ import annotations
from modelsandbox.model.base import ModelComponentBase
from modelsandbox.model.processors import ModelProcessorBase, FunctionProcessor, SchemaProcessor, EmptyProcessor


class ModelSequence(ModelComponentBase):
    """
    Main class for model Sequences which contain individual model layers 
    which will be executed sequentially.

    Parameters
    ----------
    label : str, optional
        Label associated with the model component.
    tags : list, optional
        List of tags to be associated with the model component. Tags may be 
        shared between multiple components, allowing them to be referenced 
        collectively.
    """

    _member_type = "layer"
    _member_types = "layers"

    def __init__(self, label: str=None, tags: list=[]) -> None:
        super().__init__(label=label, tags=tags)

    @property
    def layers(self) -> list:
        return self._members
    
    def add_layer(self, label: str=None, tags: list=[]) -> ModelLayer:
        """
        Add a new model Layer to the existing model Sequence.

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
            index = len([i for i in self._members if isinstance(i, ModelLayer)])
            label = f"Layer {index + 1}"
        # Create the model layer
        layer = ModelLayer(label=label, tags=self._tags + tags)
        self._members.append(layer)
        return layer


class ModelLayer(ModelComponentBase):
    """
    Main class for model Layers which may contain individual model 
    processors or additional model sequences.

    Parameters
    ----------
    label : str, optional
        Label associated with the model component.
    tags : list, optional
        List of tags to be associated with the model component. Tags may be 
        shared between multiple components, allowing them to be referenced 
        collectively.
    """

    _member_type = "component"
    _member_types = "components"

    def __init__(self, label: str=None, tags: list=[]) -> None:
        super().__init__(label=label, tags=tags)

    @property
    def components(self) -> list:
        return self._members
    
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