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

    paramconv -s ebcdic <inputfile>

You can change the output file location::

    paramconv -o <outputfile> <inputfile>

To get all the usage details::

    paramconv --help

mideu - Extract transaction data from IPM files
-----------------------------------------------
Use this tool to extract transactions into usable formats from a MasterCard
IPM format file. The app currently works exclusively with 1014 blocked file
format which is used for communications between MasterCard and the member.

Get a csv file from an IPM file::

    mideu <filename>

This runs with the following assumptions

* Input file format is EBCDIC
* Output file is the input file plus a '.csv' extension

If you need to process an ASCII file::

    mideu -s ascii <filename>

You can change the output file location for the CSV file::

    mideu <inputfile> --csvoutputfile <outputfile>

You can also load the transactions into a MongoDB collection::

    mideu <inputfile> --mongohost localhost --mongodb testdb

The transactions will be added to a collection called ``mastercardtransactions``
Currently the existing collection is deleted prior to the load.
You should consider this functionality to be beta and subject to change in the
future. Feel free to suggest changes.

To get all the usage details::

    mideu --help


mideu.yaml configuration
^^^^^^^^^^^^^^^^^^^^^^^^
The package provides a common configuration, but you can provide your own if
you wish to change it. You have 2 options for providing your own configuration.

* mideu.yaml file in the current directory
* .mideu.yaml file in the users home directory

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

