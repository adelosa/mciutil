"""
mciutil.cli.mideu

provides functionality for cli tool mideu
"""
from __future__ import print_function

import os.path
import logging
import argparse

from mciutil.cli.common import add_logging_arg_group, add_source_format_arg
from mciutil.cli.extract import extract_command
from mciutil.cli.convert import convert_command

LOGGER = logging.getLogger(__name__)


def cli_entry():
    """
    mideu main cli entry

    :return: None
    """
    args = _get_cli_parser().parse_args()
    _main(args)


def _main(args):
    """
    mideu main processing

    :param args: argparse arguments
    :return: exit code
    """

    logging.basicConfig(
        level=args.loglevel,
        format="%(asctime)s:%(name)s:%(lineno)s:%(levelname)s:%(message)s"
    )

    # exit if input file does not exist
    if not os.path.isfile(args.input):
        print("Input file not found - {0}".format(args.input))
        exit(8)

    # do command level processing
    args.func(args)

    print("Done!")


def _get_cli_parser():
    """
    mideu argparse parser create

    :return: parser
    """
    parser = argparse.ArgumentParser(
        description="MasterCard IPM file formatter"
    )

    subparsers = parser.add_subparsers(help="Sub-command help")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract help")
    extract_parser.set_defaults(func=extract_command)
    _add_common_args(extract_parser)
    _add_extract_args(extract_parser)

    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert help")
    convert_parser.set_defaults(func=convert_command)
    _add_common_args(convert_parser)

    return parser


def _add_common_args(parser):
    """
    mideu add common cli arguments

    :param parser: the argparse parser
    :return: None
    """
    parser.add_argument("input", help="Input IPM file name")
    add_source_format_arg(parser)
    add_logging_arg_group(parser)


def _add_extract_args(parser):
    """
    mideu add extract subcommand arguments

    :param parser: the argparse parser
    :return: None
    """
    mongo_arg_group = parser.add_argument_group("mongo output options")
    mongo_arg_group.add_argument("--mongo",
                                 help="add to mongo",
                                 action="store_true")
    mongo_arg_group.add_argument("--mongohost", help="mongo hostname")
    mongo_arg_group.add_argument("--mongodb", help="mongo db")

    csv_arg_group = parser.add_argument_group("csv output options")
    csv_arg_group.add_argument("--csvoutputfile", help="Output filename")


if __name__ == "__main__":
    _main(_get_cli_parser().parse_args())
