=========================
MasterCard file utilities
=========================

.. image:: https://img.shields.io/travis/adelosa/mciutil.svg
        :target: https://travis-ci.org/adelosa/mciutil

.. image:: https://img.shields.io/pypi/v/mciutil.svg
        :target: https://pypi.python.org/pypi/mciutil

.. image:: https://coveralls.io/repos/adelosa/mciutil/badge.svg?branch=develop&service=github
        :target: https://coveralls.io/github/adelosa/mciutil?branch=develop


Set of command line utilities to work with various MasterCard files.

* Free software: BSD license
* Documentation: https://mciutil.readthedocs.org.

Warning
=======

THIS PACKAGE HAS BEEN DEPRECATED AND WILL NOT BE UPDATED GOING FORWARD

This package was created when I first started learning python. I have learned a lot over the last 4 years
and I now see the error in my ways.

Some of the issues with this module that prompted me to rewrite it:

* memory efficiency - loads entire file into memory for processing. Very ineffient and not very scalable
* programming interface - mciutil did not consider the developer experience. You have to hack to use the logic elsewhere
* dependencies - Too many third party modules, with ones that required a compilation. New version is compile free
* bloat - I used a cookie cutter template when I started and it has stuff I don't like, value or use.
* just mastercard - The old module was for mastercard only but I think it makes sense to have a library for all card utils
* python 2 guff - mciutil works on py2 and 3. There is a lot of gunk in the code to make this work. We live in a py3 world now!

The replacement module is cardutil - see https://cardutil.readthedocs.io
It addresses all of the above issues.


why not just update mciutil?
----------------------------

Thats a good question. I think because the new codebase as developed from scratch rather than
via changes to the existing one (there is some borrowed code from mciutil).
If I just released a new version, anyone leaning on the internal API's would definetly be in trouble
as they are not the same.

Features
========

Provides the following command line utilities:

* paramconv: Utility for working with MasterCard MPE parameter extract files
* mideu: Utility for working with MasterCard IPM files
