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
The app currently works with 1014 blocked file and VBS format which is
used for communications between MasterCard and the member.

Most simple usage, just provide a MasterCard MPE file to convert::

    paramconv <inputfile>

This runs with the following assumptions

* Input file format is EBCDIC with 1014 blocking
* Output file name is the input file name plus a '.out' extension

If you have an ASCII file and want to convert it to EBCDIC, you need to provide
the source format type::

    paramconv -s ascii <inputfile>

If you are working with VBS format, just add the --no1014blocking flag to the command::

    paramconv -s ascii --no1014blocking <inputfile>

You can change the output file location::

    paramconv -o <outputfile> <inputfile>

To get all the usage details::

    paramconv --help

mideu - MasterCard IPM file tool
--------------------------------
This utility is for working with MasterCard IPM clearing files.
Currently the utility provides the following functions:

* extract - provide IPM transaction data in usable format
* convert - convert IPM files between ASCII and EBCDIC encoding

Extract command
^^^^^^^^^^^^^^^
Use this command to extract transactions from a MasterCard
IPM format file into usable formats like csv. The app currently works
with 1014 blocked file format and VBS format which is used for communications
between MasterCard and the member.

Get a csv file from an IPM file::

    mideu extract <filename>

This runs with the following assumptions

* Input file is EBCDIC and 1014 blocked format
* Output file name is the input file name plus a '.csv' extension

.. attention::
   Currently python 2.6 does not print a header row as the csv library only
   added this support in python 2.7. This function may be added in a future
   release.

If you need to process an ASCII encoded 1014 blocked file::

    mideu extract -s ascii <filename>

If you are working with VBS format, just add the --no1014blocking flag to the command::

    mideu extract -s ascii --no1014blocking <filename>

You can change the CSV output file name and location::

    mideu extract <inputfile> --csvoutputfile <outputfile>

To get all the usage details::

    mideu extract --help

Convert command
^^^^^^^^^^^^^^^
Use this command to convert a MasterCard IPM format file into another encoding
scheme (ASCII or EBCDIC). The app currently works exclusively with 1014 blocked
file format which is used for communications between MasterCard and the member.

Most simple usage, just provide a MasterCard IPM file to convert::

    mideu convert <inputfile>

This runs with the following assumptions

* Input file is EBCDIC and 1014 blocked format
* Output file name is the input file name plus a '.out' extension

If you have a ASCII file and want to convert it to EBCDIC, you need to provide
the source format type::

    mideu convert -s ascii <inputfile>

If you are working with VBS format, just add the --no1014blocking flag to the command::

    mideu convert -s ascii --no1014blocking <filename>

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

MasterCard file formats
-----------------------
VBS file format
^^^^^^^^^^^^^^^
*added 0.4.6*

This format is a basic variable record format.
To process this format, add the ``--no1014blocking`` option.

There are no carriage returns or line feeds in the file.
A file consists of records. Each record is prefixed with a 4 byte binary
length.

Say you had a file with the following 2 records::

    "This is first record 1234567"  <- length 28
    "This is second record AAAABBBBB123"  <- length 34

Add binary length to the start of each record. (x'1C' = 28, x'22' = 34)
with the file finishing with a zero length record length::

    00000000: 00 00 00 1C 54 68 69 73  20 69 73 20 66 69 72 73  ....This is firs
    00000010: 74 20 72 65 63 6F 72 64  20 31 32 33 34 35 36 37  t record 1234567
    00000020: 00 00 00 22 54 68 69 73  20 69 73 20 73 65 63 6F  ..."This is seco
    00000030: 6E 64 20 72 65 63 6F 72  64 20 41 41 41 41 42 42  nd record AAAABB
    00000040: 42 42 42 31 32 33 00 00  00 00                    BBB123....

1014 blocked file format
^^^^^^^^^^^^^^^^^^^^^^^^
This is the default format used by mciutil

This is the same as VBS format with 1014 blocking applied.

The VBS data is blocked into lengths of 1012, and an additional
2 x'40' characters are appended at each block.

Finally, the total file length is made a multiple of 1014 with the final
incomplete record being filled with the x'40' character

Taking the above VBS example ::

    00000000: 00 00 00 1C 54 68 69 73  20 69 73 20 66 69 72 73  ....This is firs
    00000010: 74 20 72 65 63 6F 72 64  20 31 32 33 34 35 36 37  t record 1234567
    00000020: 00 00 00 22 54 68 69 73  20 69 73 20 73 65 63 6F  ..."This is seco
    00000030: 6E 64 20 72 65 63 6F 72  64 20 41 41 41 41 42 42  nd record AAAABB
    00000040: 42 42 42 31 32 33 00 00  00 00                    BBB123....

Block to 1014 by adding 2 * x'40' characters every 1012 characters in the data.
Finally fill with x'40' characters to next 1014 increment.
In this case, there is only one increment::

    00000000: 00 00 00 1C 54 68 69 73  20 69 73 20 66 69 72 73  ....This is firs
    00000010: 74 20 72 65 63 6F 72 64  20 31 32 33 34 35 36 37  t record 1234567
    00000020: 00 00 00 22 54 68 69 73  20 69 73 20 73 65 63 6F  ..."This is seco
    00000030: 6E 64 20 72 65 63 6F 72  64 20 41 41 41 41 42 42  nd record AAAABB
    00000040: 42 42 42 31 32 33 00 00  00 00 40 40 40 40 40 40  BBB123....@@@@@@
    00000050: 40 40 40 40 40 40 40 40  40 40 40 40 40 40 40 40  @@@@@@@@@@@@@@@@
    ... all X'40' characters
    000003E0: 40 40 40 40 40 40 40 40  40 40 40 40 40 40 40 40  @@@@@@@@@@@@@@@@
    000003F0: 40 40 40 40 40 40                                 @@@@@@


mciutil package
---------------
To use Mastercard file utilities in a project::

    import mciutil

There are some useful functions for working with bitmap, variable length files.
Will document in a future version.
