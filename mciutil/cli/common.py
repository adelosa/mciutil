"""
mciutil.cli.common

provides common functions for cli tools
"""

import os
import sys
import logging
import csv

LOGGER = logging.getLogger(__name__)


def update_cli_progress(current_val, end_val, bar_length=20):
    """
    Provides cli based progress meter

    :param current_val: the current counter
    :param end_val: the total
    :param bar_length: How long is the progress bar
    :return: None
    """
    percent = float(current_val) / end_val
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write(
        "\rProcessing: [{0}] {1}%".format(
            hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()


def add_source_format_arg(parser):
    """
    Adds source format option to parser

    :param parser: the parser to add the source format option to
    :return: None
    """
    parser.add_argument(
        "-s", "--sourceformat",
        help="encoding format of source file",
        choices=["ebcdic", "ascii"],
        default="ebcdic"
    )


def add_logging_arg_group(parser):
    """
    Adds logging options to parser
    :param parser: the argparse parser to add logging options to
    :return: None
    """
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


def get_config_filename(config_filename):
    """
    Determines the config file to use.

    Starts with current directory, then user home directory and
    finally module installed default config

    :param config_filename: the config filename to use
    :return: the full path and filename of config
    """
    current_dir = os.getcwd()
    user_home_dir = os.path.expanduser("~")

    if os.path.isfile(current_dir + "/" + config_filename):
        return current_dir + "/" + config_filename
    elif os.path.isfile(user_home_dir + "/." + config_filename):
        return user_home_dir + "/." + config_filename
    else:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        return module_dir + "/" + config_filename


def add_to_csv(data_list, field_list, output_filename):
    """
    Writes data to CSV file

    :param data_list: list of dictionaries that contain the data to be loaded
    :param field_list: list of fields in the dictionary to be loaded
    :param output_filename: filename for output CSV file
    :return: None
    """
    filtered_data_list = filter_data_list(data_list, field_list)

    with open(output_filename, "w") as output_file:
        writer = csv.DictWriter(output_file,
                                fieldnames=field_list,
                                extrasaction="ignore",
                                lineterminator="\n")
        # python 2.6 does not support writeheader() so skip
        if sys.version_info[0] == 2 and sys.version_info[1] == 6:
            pass
        else:
            writer.writeheader()

        writer.writerows(filtered_data_list)
    LOGGER.info("%s records written", len(data_list))


def filter_data_list(data_list, field_list):
    """
    Takes list of dictionaries and returns new list filtered to only
    return the field keys provided in field_list and the values
    decoded to unicode.

    :param data_list: the list of dictionaries
    :param field_list: the list of string keys to return
    :return: filtered data list
    """
    return [filter_dictionary(item, field_list) for item in data_list]


def filter_dictionary(dictionary, field_list):
    """
    Takes dictionary and list of elements and returns dictionary with just
    elements specified. Also decodes the items to unicode

    :param dictionary: the dictionary to filter
    :param field_list: list containing keys to keep
    :return: dictionary with just keys from list. All values decoded
    """
    return_dictionary = {}
    for item in dictionary:
        if item in field_list:
            return_dictionary[item] = dictionary[item].decode()

    return return_dictionary


# The following code works in py2.7 and up.. just not 2.6
#     def filter_dictionary(dictionary, field_list):
#         """
#         Takes dictionary and list of elements and returns dictionary with
#         just elements specified. Also decodes the items to unicode
#         """
#         print("{},{}".format(sys.version_info.major, sys.version_info.minor))
#         return {item: dictionary[item].decode() for item in dictionary
#                 if item in field_list}
