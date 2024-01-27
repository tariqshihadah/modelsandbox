from modelsandbox.model.structure import ModelSequence, ModelLayer


class Model(object):
    """
    Top-level class for defining and executing models.
    """

    def __init__(self, **kwargs):
        self._root = ModelSequence(**kwargs)

    def __getitem__(self, index):
        return self._root[index]
    
    def __setitem__(self, index, value):
        raise NotImplementedError(
            "Directly setting model components is not yet supported."
        )

    @property
    def root(self):
        """
        Return the root model Layer.
        """
        return self._root
    
    @property
    def params(self):
        """
        Return a list of parameters for the model.
        """
        return self._root.params
    
    @property
    def returns(self):
        """
        Return a list of return values for the model.
        """
        return self._root.returns

    @property
    def processors(self):
        """
        Return a nested list processors of model components.
        """
        return self._root.processors
    
    @property
    def structure(self):
        """
        Return a nested dictionary of the model structure.
        """
        return self._root.structure

    @property
    def tags(self):
        """
        List of unique processor tags included within the model.
        """
        return self._root.tags

    @property
    def all_tags(self):
        """
        List of unique processor tags included within the model.
        """
        return self._root.all_tags

    @property
    def tagged(self):
        """
        Dictionary of unique processor tags and lists of all processors 
        associated with each tag.
        """
        return self._root.tagged

    def analyze(self, **params):
        """
        Execute the model.
        """
        return self._root.analyze(**params)