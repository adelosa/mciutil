"""
mciutil.cli.convert

provides functionality for mideu subcommand convert
"""

from __future__ import print_function

import logging
import yaml

from mciutil import flip_message_encoding, unblock, block
from mciutil.cli.common import get_config_filename

LOGGER = logging.getLogger(__name__)


def convert_command(args):
    """
    convert command
    :param args: arg object
    :return:
    """

    # Read input file
    with open(args.input, 'rb') as input_file:
        input_data = input_file.read()
    LOGGER.info("%s bytes read from %s", len(input_data), args.input)

    # Unblock input
    input_data = unblock(input_data)

    # get config filename
    config_filename = get_config_filename("mideu.yml")
    LOGGER.info("Config file: %s", config_filename)

    # load the config from yaml file
    with open(config_filename, 'r') as config_file:
        config = yaml.load(config_file)

    output_records = [
        flip_message_encoding(
            record,
            config["bit_config"],
            args.sourceformat
        ) for record in input_data
    ]

    output_data = block(output_records)

    print("\nCompleted processing {0} records".format(len(input_data)))

    # save to file
    output_filename = args.input + ".out"
    with open(output_filename, "wb") as output_file:
        output_file.write(output_data)
