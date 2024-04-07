from django import get_version

PAW_VERSION = (0, 5, 9, "final", 0)
FBL_ITERATION = 4

__version__ = f"{get_version(PAW_VERSION)}-fbl{FBL_ITERATION}"
