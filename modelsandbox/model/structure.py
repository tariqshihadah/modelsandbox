from __future__ import annotations
from modelsandbox.model.base import BaseContainer, BaseProcessor
from modelsandbox.model.processors import FunctionProcessor, SchemaProcessor, EmptyProcessor


class ContainerAdder(object):
    """
    Class for adding model components to a container.
    """

    def add_layer(self, *args, **kwargs) -> Layer:
        """
        Add a new model layer to the existing model container.
        """
        return self.add_member(Layer(*args, **kwargs))

    def add_sequence(self, *args, **kwargs) -> Sequence:
        """
        Add a new model sequence to the existing model layer.
        """
        return self.add_member(Sequence(*args, **kwargs))
    
    def add_function(self, *args, **kwargs) -> FunctionProcessor:
        """
        Add a new model function to the existing model layer.
        """
        return self.add_member(FunctionProcessor(*args, **kwargs))
    
    def add_schema(self, *args, **kwargs) -> SchemaProcessor:
        """
        Add a new model schema to the existing model layer.
        """
        return self.add_member(SchemaProcessor(*args, **kwargs))
    
    def add_wrapped(self, *args, **kwargs) -> callable:
        """
        Add a new model function to the existing model layer by returning a 
        decorator to wrap the function.
        """
        def wrapper(func) -> FunctionProcessor:
            return self.add_function(func=func, *args, **kwargs)
        return wrapper


class Layer(BaseContainer, ContainerAdder):
    """
    Model layer which processes members concurrently.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class Sequence(BaseContainer, ContainerAdder):
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





class ModelSequence(ModelStructureBase):
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

    def __getitem__(self, index):
        # Return the layer if it exists
        try:
            return self._members[index]
        # Create the layer if it does not exist
        except:
            # Build earlier layers if required
            for i in range(len(self._members), index + 1):
                layer = self.add_layer()
            return layer

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
        tags = self._validate_tags(tags)
        layer = ModelLayer(label=label, tags=self._tags + tags)
        self._members.append(layer)
        return layer
    
    def analyze(self, **params) -> dict:
        """
        Execute the model sequence.

        Parameters
        ----------
        params : dict
            Dictionary of parameters to be passed to the first layer in the 
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


class ModelLayer(ModelStructureBase):
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
    
    def add_sequence(self, label: str=None, tags: list=[]) -> ModelSequence:
        """
        Add a new model Sequence to the existing model Layer.
        
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
            index = len([i for i in self._members if isinstance(i, ModelSequence)])
            label = f"Sequence {index + 1}"
        # Create the model sequence
        tags = self._validate_tags(tags)
        sequence = ModelSequence(label=label, tags=self._tags + tags)
        self._members.append(sequence)
        return sequence
    
    def add_processor(self, processor: ModelProcessorBase) -> ModelProcessorBase:
        """
        Add an existing model processor to the existing model Layer.

        Parameters
        ----------
        processor : ModelProcessorBase
            Model processor to be added to the model Layer.
        """
        # Validate type
        if not isinstance(processor, ModelProcessorBase):
            raise TypeError(
                f"Processor must be of type {ModelProcessorBase}."
            )
        # Add the model processor to the model layer
        self._members.append(processor)
        return processor
    
    def add_schema(
            self, schema: dict, label: str=None, tags: list=[]
        ) -> SchemaProcessor:
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
        tags = self._validate_tags(tags)
        processor = SchemaProcessor(
            schema, label=label, tags=self._tags + tags
        )
        # Add the model processor to the model layer
        self._members.append(processor)
        return processor

    def add_function(
            self, function, label: str=None, tags: list=[]
        ) -> FunctionProcessor:
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
        tags = self._validate_tags(tags)
        processor = FunctionProcessor(
            function, label=label, tags=self._tags + tags
        )
        # Add the model processor to the model layer
        self._members.append(processor)
        return processor
    
    def add_wrapped(self, label: str=None, tags: list=[]) -> callable:
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
        def wrapper(function) -> FunctionProcessor:
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
        tags = self._validate_tags(tags)
        processor = EmptyProcessor(label=label, tags=self._tags + tags)
        # Add the model processor to the model layer
        self._members.append(processor)
        return processor
    
    def add_component(self, component: ModelComponentBase) -> ModelComponentBase:
        """
        Add an existing model component to the existing model Layer.

        Parameters
        ----------
        component : ModelComponentBase
            Model component to be added to the model Layer.
        """
        # Add the model component to the model layer
        self._members.append(component)
        return component
    
    def remove_component(self, index: int) -> None:
        """
        Remove an existing model component from the existing model Layer.

        Parameters
        ----------
        index : int
            Index of the model component to be removed from the model Layer.
        """
        # Remove the model component
        del self._members[index]
        return None
    
    def clear(self) -> None:
        """
        Clear all model components from the model Layer.
        """
        # Clear all model components
        self._members = []
        return None
    
    def analyze(self, **params) -> dict:
        """
        Execute the model layer.

        Parameters
        ----------
        params : dict
            Dictionary of parameters to be passed to the model component.

        Returns
        -------
        returns : dict
            Dictionary of return values from the model component.
        """
        # Initialize the return values
        returns = {}
        # Execute the model components
        for component in self._members:
            # Filter input parameters based on member parameter requirements
            params_i = {k: v for k, v in params.items() if k in component.params}
            returns_i = component.analyze(**params_i)
            returns.update(returns_i)

        # Update tagged returns
        for tag, processors in self.tagged.items():
            if tag in returns:
                returns[tag].update({p.label: returns[p.label] for p in processors})
            else:
                returns[tag] = {p.label: returns[p.label] for p in processors}

        # Update parameters with returns and return
        params.update(returns)
        return params