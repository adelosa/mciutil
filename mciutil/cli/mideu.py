#!/usr/bin/env python

import os.path
import argparse
import csv
import yaml
import hexdump
import pymongo
import logging

from mciutil.mciutil import unblock, get_message_elements, filter_dictionary

logger = logging.getLogger(__name__)


def main():

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

    # load command line arguements
    args = parser.parse_args()
    input_filename = args.input
    csv_output_filename = input_filename + ".out"
    source_format = args.sourceformat
    logging.basicConfig(
        level=args.loglevel,
        format='%(asctime)s:%(name)s:%(lineno)s:%(levelname)s:%(message)s'
    )

    config_filename = __file__ + ".yaml"

    # load the default config from YAML
    os.path.isfile(config_filename)
    with open(config_filename, 'r') as configFile:
        config = yaml.load(configFile)

    # set config dictionaries
    bit_config = config['data_elements']
    output_elements = config['default_output_elements']
    mongo_config = config['mongodb']

    # override with mongo command line parameters if provided
    if args.mongohost:
        mongo_config["host"] = args.mongohost
    if args.mongodb:
        mongo_config["db"] = args.mongodb

    # Read input file : 1014 Block format
    input_file = file(input_filename, 'rb').read()
    logger.info("%s bytes read from %s" % (len(input_file), input_filename))

    # Unblock input
    input_file = unblock(input_file)

    # Output array for record dictionaries
    output_array = []

    # parse the records
    for record_count, record in enumerate(input_file, 1):

        # Print data out in Debug mode
        logger.debug(record_count)
        logger.debug(hexdump.hexdump(record, result="return"))

        # get message elements from the raw message data
        record_values = get_message_elements(record, bit_config, source_format)

        # add the row to the output array
        output_array.append(record_values)

    logger.info("Completed processing records")

    # write to output
    if args.mongo:
        add_to_mongo(output_array, output_elements, mongo_config)
    if csv_output_filename and not args.mongo:
        add_to_csv(output_array, output_elements, csv_output_filename)

    print "Done!"
    exit(0)


def add_to_csv(data_list, field_list, output_filename):
    """ Writes data to CSV file
    :param data_list: List of dictionaries that contain the data to be loaded
    :param field_list: The fields in the dictionary to be loaded
    :param output_filename: Filename for output CSV file
    :return: None
    """
    with open(output_filename, 'wb') as outputFile:
        writer = csv.DictWriter(outputFile,
                                fieldnames=field_list,
                                extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data_list)
    logger.info("%s records written" % len(data_list))


def add_to_mongo(data_list, field_list, mongo_config):
    """ Loads data into a mongo db collection
    :param data_list: List of dictionaries that contain the data to be loaded
    :param field_list: The fields in the dictionary to be loaded
    :param mongo_config: Config required to connect to mongo
    :return: result from mongo insert
    """
    logger.info("Connecting to mongo at %s" % mongo_config["host"])
    client = pymongo.MongoClient("mongodb://" + mongo_config["host"])
    db = client[mongo_config["db"]]

    logger.info("Deleting existing items")
    db.mastercardtransactions.delete_many({})  # delete records in collection

    logger.info("Filtering %s items" % len(data_list))
    filtered_data_list = []
    for item in data_list:
        filtered_data_list.append(filter_dictionary(item, field_list))

    logger.info("Loading %s items" % len(filtered_data_list))
    return db.mastercardtransactions.insert_many(filtered_data_list)


if __name__ == "__main__":
    main()
