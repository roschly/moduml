def test_module_interface():
    assert True

    import_cases = [
        "import numpy",
        "import numpy as np",
        "import numpy, astroid",
        "import astroid, numpy as np",
    ]

    import_from_cases = [
        "from numpy import array",
        "from .core import some_module",
        "from . import filtering",
    ]

    """ special cases:

    importing a folder --> should point to folder's __init__ file instead
    importing from within a package
    
    """
