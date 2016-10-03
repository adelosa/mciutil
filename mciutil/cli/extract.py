"""
mciutil.cli.extract

provides functionality for mideu sub-command extract
"""

from __future__ import print_function

import logging
import yaml

from mciutil import unblock, vbs_unpack, get_message_elements
from mciutil.cli.common import (
    get_config_filename,
    add_to_csv,
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

    # Unpack input
    if args.no_1014_blocking:
        input_file = vbs_unpack(input_file)
    else:
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

    # write to csv - utf-8 encoded
    if args.csvoutputfile:
        csv_output_filename = args.csvoutputfile
    else:
        csv_output_filename = args.input + ".csv"
    add_to_csv(
        output_list,
        config['output_data_elements'],
        csv_output_filename
    )
