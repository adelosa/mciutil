============
Installation
============

mciutil is distributed as a python package.

You will need a version of python installed to run the tool.

Python version 2.7 or 3.4 and above are supported.
This will most likely work on Python 2.6 but no testing is done
and no 2.6 fixes will be considered. Its time to move to Py3.

See https://www.python.org/downloads for instructions on installing python on
your platform of choice.

Once you have Python available, at the command line enter::

    $ virtualenv mciutil
    $ source ./mciutil/bin/activate
    $ pip install mciutil

For Windows platforms::

    c:> virtualenv mciutil
    c:> ./mciutil/Scripts/activate
    c:> pip install mciutil

If you start another command prompt after installing, you can
make the commands available in the new session by activating the
python environment::

    $ source ./mciutil/bin/activate

or for windows::

    c:> ./mciutil/Scripts/activate
