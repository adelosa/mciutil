#!/usr/bin/env python
"""
mideu
-----
Utility for processing MasterCard IPM files
"""
import os.path
import logging

import argparse
import csv
import yaml
import hexdump
import pymongo

from mciutil import unblock, get_message_elements

LOGGER = logging.getLogger(__name__)


def cli_entry():
    args = _get_cli_parser().parse_args()
    main(args)


def main(args):
    """
    main cli runner
    :param args: arg object
    :return: exit code
    """

    logging.basicConfig(
        level=args.loglevel,
        format='%(asctime)s:%(name)s:%(lineno)s:%(levelname)s:%(message)s'
    )

    # set config filename
    config_filename = os.path.dirname(
        os.path.abspath(__file__)) + "/mideu.yaml"
    LOGGER.info("Config file: %s", config_filename)

    # load the default config from YAML
    os.path.isfile(config_filename)
    with open(config_filename, 'r') as config_file:
        config = yaml.load(config_file)

    # exit if input file does not exist
    if not os.path.isfile(args.input):
        print "File not found {}".format(args.input)
        exit(8)

    # Read input file
    input_file = file(args.input, 'rb').read()
    LOGGER.info("%s bytes read from %s", len(input_file), args.input)

    # Unblock input
    input_file = unblock(input_file)

    # Output list for record dictionaries
    output_list = []

    # parse the records
    for record_count, record in enumerate(input_file, 1):

        # Print data out in debug mode
        LOGGER.debug(record_count)
        LOGGER.debug(hexdump.hexdump(record, result="return"))

        # get message elements from the raw message data
        record_values = get_message_elements(
            record,
            config['bit_config'],
            args.sourceformat
        )

        # add the row to the output array
        output_list.append(record_values)

    LOGGER.info("Completed processing records")

    # write to output
    if args.mongo:
        mongo_config = config["mongo_config"]
        if args.mongohost:
            mongo_config["host"] = args.mongohost
        if args.mongodb:
            mongo_config["db"] = args.mongodb

        add_to_mongo(
            output_list,
            config['output_data_elements'],
            mongo_config)

    else:  # default write to csv
        csv_output_filename = args.input + ".out"
        add_to_csv(
            output_list,
            config['output_data_elements'],
            csv_output_filename
        )

    print "Done!"


def _get_cli_parser():
    """
    Setup the command line parsing using argparse
    :return: parser
    """
    parser = argparse.ArgumentParser(
        description="MasterCard IPM file formatter"
    )
    parser.add_argument("input", help="MasterCard IPM file name")
    parser.add_argument("-s", "--sourceformat",
                        help="encoding format of source file",
                        choices=["ebcdic", "ascii"],
                        default="ebcdic")
    mongo_arg_group = parser.add_argument_group("mongo output options")
    mongo_arg_group.add_argument("--mongo",
                                 help="add to mongo",
                                 action="store_true")
    mongo_arg_group.add_argument("--mongohost", help="mongo hostname")
    mongo_arg_group.add_argument("--mongodb", help="mongo db")

    csv_arg_group = parser.add_argument_group("csv output options")
    csv_arg_group.add_argument("--csvoutputfile", help="Output filename")

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


def add_to_csv(data_list, field_list, output_filename):
    """
    Writes data to CSV file

    :param data_list: list of dictionaries that contain the data to be loaded
    :param field_list: list of fields in the dictionary to be loaded
    :param output_filename: filename for output CSV file
    :return: None
    """
    with open(output_filename, 'wb') as output_file:
        writer = csv.DictWriter(output_file,
                                fieldnames=field_list,
                                extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data_list)
    LOGGER.info("%s records written", len(data_list))


def add_to_mongo(data_list, field_list, mongo_config):
    """
    Loads data into a mongo db collection

    :param data_list: list of dictionaries that contain the data to be loaded
    :param field_list: list of fields in the dictionary to be loaded
    :param mongo_config: config dictionary required to connect to mongo
    :return: result from mongo insert
    """
    LOGGER.info("Connecting to mongo at %s", mongo_config["host"])
    client = pymongo.MongoClient("mongodb://" + mongo_config["host"])
    db_client = client[mongo_config["db"]]

    LOGGER.info("Deleting existing items")
    db_client.mastercardtransactions.delete_many({})

    LOGGER.info("Filtering %s items", len(data_list))
    filtered_data_list = []
    for item in data_list:
        filtered_data_list.append(_filter_dictionary(item, field_list))

    LOGGER.info("Loading %s items", len(filtered_data_list))
    return db_client.mastercardtransactions.insert_many(filtered_data_list)


def _filter_dictionary(dictionary, field_list):
    """
    Takes dictionary and list of elements and returns dictionary with just
    elements specified
    """

    filtered_dictionary = dict()
    for item in dictionary:
        if item in field_list:
            filtered_dictionary[item] = dictionary[item]
    return filtered_dictionary


if __name__ == "__main__":
    main_args = _get_cli_parser().parse_args()
    main(main_args)
