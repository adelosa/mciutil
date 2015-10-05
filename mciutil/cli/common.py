import os
import sys
import logging
import csv

LOGGER = logging.getLogger(__name__)


def update_cli_progress(current_val, end_val, bar_length=20):
    percent = float(current_val) / end_val
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write(
        "\rProcessing: [{0}] {1}%".format(
            hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()


def get_config_filename(config_filename):
    """
    Determines the config file to use.
    Starts with current directory, then user home directory and
    finally module installed default config
    :return:
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
    return [filter_dictionary(item, field_list) for item in data_list]


# if sys.version_info[0] == 2 and sys.version_info[1] == 6:
def filter_dictionary(dictionary, field_list):
    return_dictionary = {}
    for item in dictionary:
        if item in field_list:
            return_dictionary[item] = dictionary[item].decode()

    return return_dictionary
# else:
#     def filter_dictionary(dictionary, field_list):
#         """
#         Takes dictionary and list of elements and returns dictionary with just
#         elements specified. Also decodes the items to unicode
#         """
#         print("{},{}".format(sys.version_info.major, sys.version_info.minor))
#         return {item: dictionary[item].decode() for item in dictionary
#                 if item in field_list}
