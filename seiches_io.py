import pickle
import os


def save(obj, filename, verbose: bool = False):
    """
    Save any Python object to a file using pickle.

    Args:
        obj: Any Python object (variables, lists, dicts, custom objects)
        filename: File path to save to (e.g., 'data.pkl')
    """

    with open(filename, "wb") as f:
        pickle.dump(obj, f)
    if verbose:
        print(f"Saved object to {filename}")


def load(filename):
    """
    Load a Python object previously saved with `save`.

    Args:
        filename: File path to load from

    Returns:
        The Python object stored in the file
    """

    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} does not exist")
    with open(filename, "rb") as f:
        obj = pickle.load(f)
    return obj
