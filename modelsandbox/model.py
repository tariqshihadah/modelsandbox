from typing import Any
from modelsandbox.globals import _VALID_SCHEMA_ACTIONS


class Model(object):
    """
    Top-level class for defining and executing models.
    """

    def __init__(self):
        self._model = ModelContainer()

    @property
    def params(self):
        """
        Return a list of parameters for the model.
        """
        return self._model.params

    def analyze(**params):
        """
        Execute the model.
        """
        pass


class ModelComponent(object):
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
        self._label = label
    
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

    def analyze(self, **params) -> dict:
        """
        Execute the model component.
        """
        raise NotImplementedError


class ModelContainer(ModelComponent):
    """
    Main class for model containers which may contain individual model 
    processors or additional model containers.
    """

    def __init__(self) -> None:
        self._contents = []

    def __len__(self) -> int:
        return len(self._contents)

    def __getitem__(self, index):
        try:
            return self._contents[index]
        except:
            raise IndexError(
                f"Index {index} is out of range of the {self.__class__} with "
                f"content length of {len(self._contents)}."
            )
    
    @property
    def contents(self) -> list:
        return self._contents
    
    @property
    def params(self) -> list:
        """
        Return a list of parameters for all contents in the model container.
        """
        params = []
        for content in self._contents:
            params.extend(content.params)
        return list(set(params))
    
    @property
    def returns(self) -> list:
        """
        Return a list of return values for all contents in the model container.
        """
        returns = []
        for content in self._contents:
            returns.extend(content.returns)
        return list(set(returns))


class ModelProcessor(ModelComponent):
    """
    Base class for model processors.

    Model processors are the lowest level of model definition. They include 
    the following subclasses:

    ProcessSchema
    ProcessFunction
    """
    
    def __init__(self):
        pass

    def __call__(self, **kwargs) -> dict:
        return self.anlayze(**kwargs)
    
    def analyze(self, **kwargs) -> dict:
        """
        Execute the model processor.
        """
        pass

    
class SchemaProcessor(ModelProcessor):
    """
    Class for defining a model processor using a schema.
    """
    
    def __init__(self, schema: dict) -> None:
        self.schema = schema

    def analyze(self, **params) -> dict:
        """
        Execute the model processor.
        """
        # Pull the schema data
        schema_data = self.data.copy()




def _validate_schema_processor(schema):
        # Check for required structure
        try:
            keys = schema["parameters"]
        except KeyError:
            raise KeyError(
                "Input schema is missing the required `parameters` "
                "information."
            )
        try:
            actions = schema["actions"]
            assert len(actions) == len(keys)
        except KeyError:
            raise KeyError(
                "Input schema is missing the required `actions` information."
            )
        except AssertionError:
            raise ValueError(
                "Number of `actions` must be equal to the number of "
                "`parameters` in the provided schema."
            )
        try:
            assert all(action in self._valid_actions for action in actions)
        except:
            raise ValueError(
                f"Each input `action` must only be one of "
                f"{self._valid_actions}."
            )
        try:
            data = schema["data"]
        except KeyError:
            raise KeyError(
                "Input schema is missing the required `data` information."
            )
        try:
            schema["label"]
        except KeyError:
            raise KeyError(
                "Input schema is missing the required `label` information."
            )
        return schema