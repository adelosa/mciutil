"""
mciutil.cli.extract

provides functionality for mideu sub-command extract
"""

from __future__ import print_function

import logging
import yaml
import pymongo

from mciutil import unblock, get_message_elements
from mciutil.cli.common import (
    get_config_filename,
    add_to_csv,
    filter_data_list,
)

LOGGER = logging.getLogger(__name__)


def extract_command(args):
    """
    extract command
    :param args: arg object
    :return:
    """

    # Read input file
    with open(args.input, 'rb') as infile:
        input_file = infile.read()
    LOGGER.info("%s bytes read from %s", len(input_file), args.input)

    # Unblock input
    input_file = unblock(input_file)

    # get config filename
    config_filename = get_config_filename("mideu.yml")
    LOGGER.info("Config file: %s", config_filename)

    # load the config from yaml file
    with open(config_filename, 'r') as config_file:
        config = yaml.load(config_file)

    # parse the records
    output_list = [
        get_message_elements(
            record,
            config["bit_config"],
            args.sourceformat
        ) for record in input_file
    ]

    print("\nCompleted processing {0} records".format(len(input_file)))

    # write to output
    if args.mongo or args.mongohost or args.mongodb:
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
        if args.csvoutputfile:
            csv_output_filename = args.csvoutputfile
        else:
            csv_output_filename = args.input + ".csv"
        add_to_csv(
            output_list,
            config['output_data_elements'],
            csv_output_filename
        )


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
    filtered_data_list = filter_data_list(data_list, field_list)

    LOGGER.info("Loading %s items", len(filtered_data_list))
    return db_client.mastercardtransactions.insert_many(filtered_data_list)
