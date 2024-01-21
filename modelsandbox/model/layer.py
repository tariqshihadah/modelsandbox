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
        layer = ModelLayer(label=label, tags=tags)
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
        processor = SchemaProcessor(schema, label=label, tags=tags)
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
        processor = FunctionProcessor(function, label=label, tags=tags)
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