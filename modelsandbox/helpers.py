import json, os


def _load_schema(obj, search_paths=[]):
    """
    Helper function for loading dict/JSON schema data from a provided object 
    and potential search paths.
    """
    # If dictionary, return
    if isinstance(obj, dict):
        return obj
    
    # If string, try to load JSON file
    elif isinstance(obj, str):
        # Define possible search paths
        paths = [obj]
        paths.extend([os.path.join(path, obj) for path in search_paths])
        # Try to load file
        for path in paths:
            if os.path.isfile(path):
                try:
                    with open(obj) as f:
                        schema = json.load(f)
                    return schema
                except:
                    continue
        raise ValueError(
            f"Unable to load JSON schema file at provided path "
            f"({obj})"
        )
    else:
        raise TypeError(
            "Input schema must be a `dict`, a path to a valid JSON file, "
            "or a loadable JSON-structured `str`."
        )
    return schema
