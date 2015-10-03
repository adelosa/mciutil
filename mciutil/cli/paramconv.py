#!/usr/bin/env python
"""
paramconv
---------

Command line interface functions
"""
import argparse
import hexdump

from ..mciutil import (
    block, unblock, _convert_text_eb2asc, _convert_text_asc2eb
)


def main():
    """
    main cli runner

    :return: exit code
    """

    parser = argparse.ArgumentParser(
        description="MasterCard parameter file conversion utility"
    )
    parser.add_argument("input", help="MasterCard parameter file name")
    parser.add_argument("-o", "--output", help="Converted parameter file name")
    parser.add_argument("-s", "--sourceformat",
                        help="encoding format of source file",
                        choices=["ebcdic", "ascii"],
                        default="ebcdic")
    parser.add_argument("-d", "--debug",
                        help="turn debugging output on",
                        action="store_true")

    args = parser.parse_args()

    input_filename = args.input
    output_filename = args.output
    if not args.output:
        output_filename = input_filename + ".out"

    source_format = args.sourceformat
    debug = args.debug

    # read file to string
    input_file = open(input_filename, 'rb').read()
    print("%s bytes read from %s".format(len(input_file), input_filename))

    # deblock the fil   e
    input_file = unblock(input_file)

    # convert the file from source to target encoding
    output_list = []     # output array
    record_count = 0

    # convert the file
    for record_count, record in enumerate(input_file, 1):
        # convert data
        if source_format == "ebcdic":
            record = _convert_text_eb2asc(record)
        else:
            record = _convert_text_asc2eb(record)

        # add converted record data to output
        output_list.append(record)

    # re-block the data
    output_data = block(output_list)

    # save to file
    with open(output_filename, "wb") as output_file:
        output_file.write(output_data)

    print("%s bytes written to %s".format(len(output_data), output_filename))
    print("%s records".format(record_count))

    if debug:
        print("DEBUG:Input first 5000 bytes")
        hexdump.hexdump(input_file[:5000])
        print("DEBUG:Output first 5000 bytes")
        hexdump.hexdump(output_data[:5000])

        print("DEBUG:Input last 5000 bytes")
        hexdump.hexdump(input_file[len(output_data)-5000:len(input_file)])
        print("DEBUG:Output last 5000 bytes")
        hexdump.hexdump(output_data[len(output_data)-5000:len(output_data)])

    print("Done!")


if __name__ == "__main__":
    main()
