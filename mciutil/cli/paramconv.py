#!/usr/bin/env python
"""
paramconv
---------

Convert MasterCard Parameter Extract files between ASCII and EBCDIC encoding
"""
import os.path
import argparse
import logging

from hexdump import hexdump

from ..mciutil import (
    block, unblock, _convert_text_eb2asc, _convert_text_asc2eb
)


def cli_entry():
    args = _get_cli_parser().parse_args()
    _main(args)


def _get_cli_parser():

    parser = argparse.ArgumentParser(
        description="MasterCard parameter file conversion utility"
    )
    parser.add_argument("input", help="MasterCard parameter file name")
    parser.add_argument("-o", "--output", help="Converted parameter file name")
    parser.add_argument("-s", "--sourceformat",
                        help="encoding format of source file",
                        choices=["ebcdic", "ascii"],
                        default="ebcdic")
    logging_arg_group = parser.add_argument_group("logging options")
    logging_arg_group.add_argument("-d", "--debug",
                                   help="turn debugging output on",
                                   action="store_const",
                                   dest="loglevel",
                                   const=logging.DEBUG,
                                   default=logging.WARNING)
    logging_arg_group.add_argument("-v", "--verbose",
                                   help="turn information output on",
                                   action="store_const",
                                   dest="loglevel",
                                   const=logging.INFO)

    return parser


def _main(args):

    logging.basicConfig(
        level=args.loglevel,
        format='%(asctime)s:%(name)s:%(lineno)s:%(levelname)s:%(message)s'
    )

    # exit if input file does not exist
    if not os.path.isfile(args.input):
        print("Input file not found - {0}".format(args.input))
        exit(8)

    input_filename = args.input
    output_filename = args.output
    if not args.output:
        output_filename = input_filename + ".out"

    # read file to string
    with open(input_filename, 'rb') as infile:
        input_file = infile.read()

    print("{0} bytes read from {1}".format(len(input_file), input_filename))

    # deblock the file
    input_file = unblock(input_file)

    # convert the file
    output_list = [
        _convert(record, args.sourceformat) for record in input_file
    ]

    # re-block the data
    output_data = block(output_list)

    # save to file
    with open(output_filename, "wb") as output_file:
        output_file.write(output_data)

    print("{0} bytes written to {1}".format(len(output_data), output_filename))
    print("{0} records".format(len(output_list)))

    if args.loglevel == logging.DEBUG:
        print("DEBUG:Input first 5000 bytes")
        hexdump(input_file[:5000])
        print("DEBUG:Output first 5000 bytes")
        hexdump(output_data[:5000])

        print("DEBUG:Input last 5000 bytes")
        hexdump(input_file[len(output_data)-5000:len(input_file)])
        print("DEBUG:Output last 5000 bytes")
        hexdump(output_data[len(output_data)-5000:len(output_data)])

    print("Done!")


def _convert(record, source_format):
    # convert data
    if source_format == "ebcdic":
        record = _convert_text_eb2asc(record)
    else:
        record = _convert_text_asc2eb(record)
    return record


if __name__ == "__main__":
    main_args = _get_cli_parser().parse_args()
    _main(main_args)
