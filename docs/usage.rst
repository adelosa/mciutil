=====
Usage
=====

The mciutil package provides command line tools and python functions you can
use when working with MasterCard files.

.. note:: Make sure set binary transfers when moving MasterCard files. For
          example, if using FTP, use the ``binary`` command before starting the
          transfer

paramconv - Convert MPE parameter extract files
-----------------------------------------------
Use this tool if you are moving between a mainframe and PC based clearing
application and need the parameter files available on both platforms.
The app currently works exclusively with 1014 blocked file format which is
used for communications between MasterCard and the member.

Most simple usage, just provide a MasterCard MPE file to convert::

    paramconv <inputfile>

This runs with the following assumptions

* Input file format is EBCDIC
* Output file is the input file plus a '.out' extension

If you have a ASCII file and want to convert it to EBCDIC, you need to provide
the source format type::

    paramconv -s ascii <inputfile>

You can change the output file location::

    paramconv -o <outputfile> <inputfile>

To get all the usage details::

    paramconv --help

mideu - MasterCard IPM file tool
--------------------------------
This utility is for working with MasterCard IPM clearing files.
Currently the utility provides the following functions::

* extract - provide IPM transaction data in usable format
* convert - convert IPM files between ASCII and EBCDIC encoding

Extract command
^^^^^^^^^^^^^^^
Use this tool to extract transactions from a MasterCard
IPM format file into usable formats. The app currently works exclusively with
1014 blocked file format which is used for communications between MasterCard
and the member.

Get a csv file from an IPM file::

    mideu extract <filename>

This runs with the following assumptions

* Input file format is EBCDIC
* Output file is the input file plus a '.csv' extension

If you need to process an ASCII file::

    mideu extract -s ascii <filename>

You can change the output file location for the CSV file::

    mideu extract <inputfile> --csvoutputfile <outputfile>

You can also load the transactions into a MongoDB collection::

    mideu extract <inputfile> --mongohost localhost --mongodb testdb

The transactions will be added to a collection called ``mastercardtransactions``
Currently the existing collection is deleted prior to the load.
You should consider this functionality to be beta and subject to change in the
future. Feel free to suggest changes.

To get all the usage details::

    mideu extract --help

Convert command
^^^^^^^^^^^^^^^
Most simple usage, just provide a MasterCard IPM file to convert::

    mideu convert <inputfile>

This runs with the following assumptions

* Input file format is EBCDIC
* Output file is the input file plus a '.out' extension

If you have a ASCII file and want to convert it to EBCDIC, you need to provide
the source format type::

    mideu convert -s ascii <inputfile>

To get all the usage details::

    mideu convert --help

mideu.yml configuration
^^^^^^^^^^^^^^^^^^^^^^^
The package provides a common configuration, but you can provide your own if
you wish to change it. You have 2 options for providing your own configuration.

* mideu.yml file in the current directory
* .mideu.yml file in the users home directory

The file is a basic yaml file with the following sections

**output_data_elements**
    Specify fields to output. Set the order and fields to be output.
Structure::

    output_data_elements:
        - MTI
        - DE1
        - DE10
        - PDS0023
        - DE43_NAME

**bit_config**
    Define the bitmap fields. You should not need to change this but if you
    think you need to, have a look at the source to see what the options mean.
    Will document this in more details at some point.
Structure::

    bit_config:
        1:
            field_name: Bitmap secondary
            field_type: FIXED
            field_length: 8
        2:
            field_name: PAN
            field_type: LLVAR
            field_length: 0
            field_processor: PAN

**mongo_config**
    Specify mongo host and port details. Command line options will override
    options provided in a config file
Structure::

    mongo_config:
        host: 192.168.99.100:27017
        db: test

mciutil package
---------------
To use Mastercard file utilities in a project::

    import mciutil

There are some useful functions for working with bitmap, variable length files.
Will document in a future version.
