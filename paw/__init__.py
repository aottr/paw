from django import get_version

PAW_VERSION = (0, 5, 8, "final", 0)
FBL_ITERATION = 2

__version__ = f"{get_version(PAW_VERSION)}-fbl{FBL_ITERATION}"
