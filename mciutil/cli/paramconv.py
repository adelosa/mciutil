#!/usr/bin/env python

import argparse
import hexdump

from mciutil.mciutil import block, unblock, convert_text_eb2asc, \
    convert_text_asc2eb


def main():

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

    inputFilename = args.input
    outputFilename = args.output
    if not args.output:
        outputFilename = inputFilename + ".out"

    sourceFormat = args.sourceformat
    debug = args.debug

    # read file to string
    inputFile = file(inputFilename, 'rb').read()
    print "%s bytes read from %s" % (len(inputFile), inputFilename)

    # deblock the file
    inputFile = unblock(inputFile)

    # convert the file from source to target encoding
    outputArray = []     # output array

    # convert the file
    for recordCount, record in enumerate(inputFile, 1):
        # convert data
        if sourceFormat == "ebcdic":
            record = convert_text_eb2asc(record)
        else:
            record = convert_text_asc2eb(record)

        # add converted record data to output
        outputArray.append(record)

    # re-block the data
    outputFile = block(outputArray)

    # save to file
    with open(outputFilename, "wb") as outputCsv:
        outputCsv.write(outputFile)

    print "%s bytes written to %s" % (len(outputFile), outputFilename)
    print "%s records" % recordCount

    if debug:
        print "DEBUG:Input first 5000 bytes"
        hexdump.hexdump(inputFile[:5000])
        print "DEBUG:Output first 5000 bytes"
        hexdump.hexdump(outputFile[:5000])

        print "DEBUG:Input last 5000 bytes"
        hexdump.hexdump(inputFile[len(outputFile)-5000:len(inputFile)])
        print "DEBUG:Output last 5000 bytes"
        hexdump.hexdump(outputFile[len(outputFile)-5000:len(outputFile)])

    print "Done!"
    exit(0)

if __name__ == "__main__":
    main()
