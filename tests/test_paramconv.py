import os
from unittest import TestCase
from mciutil import b, block
from mciutil.cli.paramconv import _get_cli_parser, _main

TEST_ASCII_MPE_PARAM_FILENAME = "build/test/test_ascii_mpe.in"


class CommandLineTestCase(TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    def setUp(self):
        self.parser = _get_cli_parser()
        write_test_file(create_test_mpe_parameter_extract(),
                        TEST_ASCII_MPE_PARAM_FILENAME)


class ParamConvTestCase(CommandLineTestCase):

    def test_with_empty_args(self):
        # with self.assertRaises(SystemExit):
        #     self.parser.parse_args([])
        self.assertRaises(SystemExit,
                          lambda: self.parser.parse_args([]))

    def test_with_bad_filename(self):
        test_file = 'abc.txt'
        args = self.parser.parse_args([test_file])
        # with self.assertRaises(SystemExit) as stat:
        #     _main(args)
        # self.assertEquals(stat.exception.code, 8)
        self.assertRaises(SystemExit,
                          lambda: _main(args))

    def test_with_ascii_file(self):
        # convert to ebcdic
        args = self.parser.parse_args(["-s", "ascii",
                                       TEST_ASCII_MPE_PARAM_FILENAME])
        _main(args)
        # convert back to ascii
        args = self.parser.parse_args([TEST_ASCII_MPE_PARAM_FILENAME + ".out"])
        _main(args)

        # check that double converted file == original file
        with open(TEST_ASCII_MPE_PARAM_FILENAME + ".out.out", 'rb') as outfile:
            output_data = outfile.read()

        self.assertEqual(output_data, create_test_mpe_parameter_extract())


def create_test_mpe_parameter_extract():
    """
    Create a test extract file to perform cli testing with
    Contents do no matter..
    """
    message_raw = b("12345678901ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    # add 5 records to a list
    message_list = [message_raw for x in range(5)]
    return block(message_list)

    #  block_and_write_list(message_list, TEST_ASCII_MPE_PARAM_FILENAME)


def write_test_file(message, file_name):
    # block and write to file
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    with open(file_name, 'wb') as output_file:
        output_file.write(message)
