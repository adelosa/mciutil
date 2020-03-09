"""
mciutil.cli.common

provides common functions for cli tools
"""

import os
import sys
import logging
import csv
from pkg_resources import resource_filename

LOGGER = logging.getLogger(__name__)
# this module gets loaded by all the CLI programs so will emit message
# for all cli programs.
print("""!!! WARINING !!!
mciutil module has been deprecated
Please consider using module cardutil instead
see https://cardutil.readthedocs.io
""")


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

    parser.add_argument(
        "--no1014blocking",
        help="do not use 1014 block format. Just vbs type record",
        dest="no_1014_blocking",
        action="store_true"
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
        config_filename = current_dir + "/" + config_filename
    elif os.path.isfile(user_home_dir + "/." + config_filename):
        config_filename = user_home_dir + "/." + config_filename
    else:
        module_dir = resource_filename("mciutil", "cli")
        config_filename = module_dir + "/" + config_filename
    LOGGER.info("Using {0} config file".format(config_filename))
    return config_filename


def add_to_csv(data_list, field_list, output_filename):
    """
    Writes data to CSV file

    :param data_list: list of dictionaries that contain the data to be loaded
    :param field_list: list of fields in the dictionary to be loaded
    :param output_filename: filename for output CSV file
    :return: None
    """
    try:
        instance_type = unicode
        file_mode = "wb"
    except NameError:
        instance_type = str
        file_mode = "w"

    filtered_data_list = filter_data_list(data_list, field_list)

    with open(output_filename, file_mode) as output_file:
        writer = csv.DictWriter(output_file,
                                fieldnames=field_list,
                                extrasaction="ignore",
                                lineterminator="\n")

        # python 2.6 does not support writeheader() so skip
        if sys.version_info[0] == 2 and sys.version_info[1] == 6:
            pass
        else:
            writer.writeheader()

        for item in filtered_data_list:
            if file_mode == "w":
                row = dict(
                    (k, v.decode('latin1') if not isinstance(v, instance_type) else v)
                    for k, v in item.items()
                )
            else:
                row = dict(
                    (k, v.encode('utf-8') if isinstance(v, instance_type) else v)
                    for k, v in item.items()
                )
            writer.writerow(row)

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
            return_dictionary[item] = dictionary[item]

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
