# -*- coding: utf-8 -*-
"""
mciutil
=======
Shared functions for working with MasterCard files
"""
from .mciutil import (
    block, unblock, vbs_pack, vbs_unpack, get_message_elements,
    flip_message_encoding, b,
)

import warnings
warnings.warn("mciutil project is now deprecated. Please use python module cardutil instead. "
              "See https://cardutil.readthedocs.io", DeprecationWarning)

__author__ = 'Anthony Delosa'
__email__ = 'adelosa@gmail.com'

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
