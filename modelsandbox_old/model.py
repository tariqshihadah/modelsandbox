import json, os, itertools
from modelsandbox_old.processors import ProcessFunction, ProcessSchema
from modelsandbox_old.validation import ExtendedValidator as Validator
from modelsandbox_old.helpers import _load_schema


class Model(object):
    """
    Flexible class for building intricate, multi-level, highly parameterized 
    mathematical models. Models are defined using a series of computational 
    layers which can be created with the `add_layer()` class method and which 
    are invoked sequentially when the model is called. These layers are 
    populated with a series of processors which can be created in multiple 
    ways and which are also invoked sequentially within each layer when the 
    model is called.

    Processors are the building blocks of a model, defining individual 
    parameterized mathematical or computational processes within each layer. 
    When the model is run, each layer is processed sequentially and each 
    processor is processed sequentially within the layer. The parameters 
    required by each processor are collected and exposed at the model level, 
    requiring all to be input when running the model. These parameters are 
    then passed as keyword arguments to each layer, and the outputs of each 
    processor are collected and added to the `dict` of parameters based on 
    the processor label or schema data and are then passed as keyword 
    arguments to the next layer. In this way, processor outputs can be 
    referenced and used in subsequent layers of the model.

    Types of processors are represented by the following classes:

    * `ProcessFunction` This class is built around a single callable, most 
    commonly a defined Python function, which takes a number of parameters 
    and performs a single model task, returning a single output. Because these 
    use callables which can be flexibly defined in Python, they are effective 
    for performing the more mathematical processes of the model.

    * `ProcessSchema` This class is built around a schema `dict` or `JSON` 
    file which contains information on a series of logical tests based on a 
    number of parameters, returning a single output or a `dict` of output key: 
    value pairs. Because these use static logical schemas, they are effective 
    for performing more the more logical processes of the model or replacing 
    table references.

    Parameters
    ----------
    label : label, optional
        Label associated with the model instance.
    """

    def __init__(self, label=None):
        # Initialize model structure
        self._layers = []
        self._validator = None
        self.label = label
                                         
    @property
    def model_path(self):
        return os.path.dirname(os.path.realpath(__file__))
    
    @property
    def layers(self):
        """
        List of all defined layers within the model.
        """
        return self._layers
    
    @property
    def processors(self):
        """
        List of lists of all defined processors within all defined layers 
        within the model.
        """
        return [layer.processors for layer in self.layers]

    @property
    def parameters(self):
        """
        List of all parameters required by all processors defined within the 
        model.
        """
        # Collect all unique parameters from all processors
        parameters = []
        for layer in self._layers:
            parameters.extend(layer.parameters)
        return sorted(set(parameters) - set(self.returns))
    
    @property
    def tags(self):
        """
        List of unique processor tags included within the defined model.
        """
        # Get list of all processors
        processors = list(itertools.chain.from_iterable(self.processors))
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
        processors = list(itertools.chain.from_iterable(self.processors))
        # Find tagged processors
        tagged = {}
        for tag in self.tags:
            tagged[tag] = [p for p in processors if tag in p.tags]
        return tagged

    @property
    def returns(self):
        """
        List of all returns created by all processors defined within the model.
        """
        # Collect all unique parameters from all processors
        returns = []
        for layer in self._layers:
            returns.extend(layer.returns)
        return sorted(set(returns))
    
    def validate(self, expand_dict=False, **params) -> dict:
        """
        Validate the input parameters, returning the output of the `cerberus` 
        validation API, aligned to the input parameters if requested.

        Parameters
        ----------
        expand_dict : bool, default False
            Whether to expand the validation results `dict` to include all 
            input parameters, producing an empty list for successfully 
            validated parameters.
        **params
            Keyword arguments for all required parameters in the defined 
            model. Use the `parameters` property to see which parameters are 
            required to be directly input when applying the model.
        """
        # Check for validator
        if self._validator is None:
            return {}
        # Validate the parameters
        self._validator.validate(params)
        if expand_dict:
            # Return dictionary of validation errors mapped to the inputs
            return {self._validator.errors.get(key, []) for key in params.keys()}
        else:
            return self._validator.errors

    def analyze(self, **params):
        """
        Apply the model to the input keyword argument parameters, running all 
        layers and returning a structured model output result.

        Parameters
        ----------
        **params
            Keyword arguments for all required parameters in the defined 
            model. Use the `parameters` property to see which parameters are 
            required to be directly input when applying the model.
        """
        # Validate inputs
        errors = self.validate(**params)
        if len(errors) > 0:
            raise ValueError(
                f"Input parameters caused validation errors:\n{errors}"
            )
        else:
            valid_params = {**params} # INPUT MODIFICATION NOT YET IMPLEMENTED

        # Iterate over layers
        layer_params = {**valid_params}
        for layer in self._layers:
            # Iterate over layer processors
            layer_results = {}
            for processor in layer._processors:
                # Group parameters by tags where applicable
                tagged = {}
                for tag, ps in self.tagged.items():
                    # Get list of unique return keys from all processors
                    return_keys = list(
                        itertools.chain.from_iterable(p.returns for p in ps)
                    )
                    tagged[f'__{tag}'] = {
                        key: layer_params[key] for key in return_keys \
                        if key in layer_params
                    }
                
                # Analyze current processor
                processor_params = {
                    key: val for key, val in \
                    {**layer_params, **tagged}.items() \
                    if key in processor.parameters
                }
                processor_results = processor.analyze(**processor_params)
                # Add processor results to current layer results
                layer_results = {**layer_results, **processor_results}
            
            # Log results from current layer as parameters for the next layer
            layer_params = {**layer_params, **layer_results}

        # Return structured model output
        return layer_params
    
    def add_validation(
            self, 
            schema, 
            require_all=True, 
            allow_unknown=True, 
            **kwargs
    ):
        """
        Add a validation schema to the model to validate input model 
        parameters. Validation is performed using an extension of the open-
        source `cerberus` package and validation schemas should follow their 
        standards and documentation. Additional provided keyword arguments 
        will be passed to the `cerberus.Validator` instantiation call.

        Parameters
        ----------
        schema : dict, str, or path
            Schema data following the required structure of the 
            `cerberus.Validator` class. Can be input as a python `dict`, a 
            stringified python `dict` or JSON file, or as a path to a valid 
            JSON file which will be loaded.
        require_all : bool, default True
            Whether all parameters defined in the validation schema should be 
            required for validation. Missing fields will produce a 
            `required_field` error.
        allow_unknown : bool, default True
            Whether parameters that aren't included in the validation schema 
            should produce an `unknown_field_error`. Should be `True` if not 
            all model parameters are being validated directly.
        """
        # Load the validation schema and create a cerberus Validator
        schema = _load_schema(schema)
        self._validator = Validator(
            schema, 
            require_all=require_all, 
            allow_unknown=allow_unknown, 
            **kwargs
        )

    def add_layer(self, label=None, **kwargs):
        """
        Add a `ProcessLayer` to the model to build additional processors into.
        """
        # Default label
        if label is None:
            label = f'Layer #{len(self._layers) + 1}'
        # Create and append the new layer
        layer = ProcessLayer(label=label, **kwargs)
        self._layers.append(layer)
        return layer

    def add_function(self, obj, tags=None, layer_index=None, **kwargs):
        """
        Add a `ProcessFunction` to the selected `ProcessLayer`.

        Parameters
        ----------
        obj : callable
            Callable object which will be the basis for the `ProcessFunction`.
        tags : list, optional
            List of tags to be associated with the `ProcessFunction`. Tags may 
            be shared between multiple `ProcessFunction` instances, allowing 
            them to be referenced collectively.
        layer_index : int, optional
            The integer index of the layer to which the `ProcessFunction` should be 
            appended.
        """
        # If no layers are currently defined, create a new one
        if len(self._layers) == 0:
            self.add_layer()
        # Create and append the new processor to the latest layer
        return self._layers[-1].add_function(obj, tags=tags)

    def add_schema(self, schema, tags=None, layer_index=None, **kwargs):
        """
        Add a process schema to the selected `ProcessLayer`.

        Parameters
        ----------
        schema : dict, str, or path
            Schema data following the required structure of the 
            `ProcessSchema` class. Can be input as a Python `dict`, an 
            absolute path to a JSON file, or a relative path to a JSON file 
            within the default `SCHEMA_PATH` directories.
        tags : list, optional
            List of tags to be associated with the `ProcessSchema`. Tags may be 
            shared between multiple `ProcessFunction` instances, allowing them to 
            be referenced collectively.
        layer_index : int, optional
            The integer index of the layer to which the `ProcessFunction` should be 
            appended.
        """
        # If no layers are currently defined, create a new one
        if len(self._layers) == 0:
            self.add_layer()
        # Create and append the new processor to the latest layer
        return self._layers[-1].add_schema(schema, tags=tags)

    def add_wrapped(self, tags=None, layer_index=None, **kwargs):
        """
        Returns a decorator which can be placed before a declared function 
        which takes that function and adds it as a processor to the selected 
        `ProcessLayer` similar to the `add_function` method.

        Parameters
        ----------
        tags : list, optional
            List of tags to be associated with the `ProcessFunction`. Tags may be 
            shared between multiple `ProcessFunction` instances, allowing them to 
            be referenced collectively.
        layer_index : int, optional
            The integer index of the layer to which the `ProcessFunction` should be 
            appended.
        """
        # Define the decorator
        def decorator(obj):
            # Add the processor using the provided parameters
            self.add_function(
                obj, tags=tags, layer_index=layer_index, **kwargs)
        return decorator

    @property
    def structure(self):
        structure = {
            layer.label: [processor.label for processor in layer._processors] 
            for layer in self._layers
        }
        return structure
    

class ProcessLayer(object):

    def __init__(self, label=None, **kwargs):
        self._processors = []
        self.label = label

    @property
    def processors(self):
        """
        List of all defined processors within the model layer.
        """
        return self._processors

    @property
    def parameters(self):
        # Collect all unique parameters from all processors
        parameters = []
        for processor in self._processors:
            parameters.extend(processor.parameters)
        return sorted(set(parameters))

    @property
    def returns(self):
        # Collect all unique parameters from all processors
        returns = []
        for processor in self._processors:
            returns.extend(processor.returns)
        return sorted(set(returns))

    def add_function(self, obj, **kwargs):
        """
        Add a callable `ProcessFunction` to the layer. Can be passed an actual 
        `ProcessFunction` instance or a callable which will be used to create a new 
        `ProcessFunction` instance.
        """
        # Check input type
        if isinstance(obj, ProcessFunction):
            pf = obj
        else:
            pf = ProcessFunction(obj, **kwargs)
        self._processors.append(pf)
        return pf

    def add_schema(self, schema, **kwargs):
        """
        """
        # Check input type
        if isinstance(schema, ProcessSchema):
            ps = schema
        else:
            ps = ProcessSchema(schema, **kwargs)
        self._processors.append(ps)
        return ps
        