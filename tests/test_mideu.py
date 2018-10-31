# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os.path
import sys
import hexdump

from unittest import TestCase

from mciutil.mciutil import block, vbs_pack, _convert_text_asc2eb, b
from mciutil.cli.mideu import _get_cli_parser, _main
from mciutil.cli.common import get_config_filename, filter_dictionary

TEST_ASCII_IPM_FILENAME = "build/test/test_ascii_ipm"
TEST_EBCDIC_IPM_FILENAME = "build/test/test_ebcdic_ipm"

HEADER_LINE = (
    "MTI,DE2,DE3,DE4,DE12,DE14,DE22,DE23,DE24,DE25,DE26,DE30,DE31,DE33,"
    "DE37,DE38,DE40,DE41,DE42,DE48,DE49,DE50,DE63,DE71,DE73,DE93,DE94,"
    "DE95,DE100,PDS0023,PDS0052,PDS0122,PDS0148,PDS0158,PDS0165,DE43_NAME,"
    "DE43_SUBURB,DE43_POSTCODE,ICC_DATA\n"
)

DETAIL_LINE = (
    "1144,444455*******555,111111,000000009999,201508151715,,123456789012,"
    ",333,,1234,,57995799120000001230612,123456,,123456,,,579942111111111,"
    "0001001Y,999,,0000000000000001,12345678,,,999999,,,,,,,,,BIG BOBS,"
    "ANNERLEY,4103,\n"
)


class CommandLineTestCase(TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    def setUp(self):
        self.parser = _get_cli_parser()
        create_test_ascii_ipm_file()
        create_test_ebcdic_ipm_file()
        create_test_ascii_de55_ipm_file()
        create_bad_ascii_ipm_file()


class MideuCommonTestCase(CommandLineTestCase):
    def test_enter_with_no_subcommand(self):
        """
        try calling standard entry without sub command.. should return help text
        :return:
        """
        _main(None)


class MideuExtractTestCase(CommandLineTestCase):

    def test_with_empty_args(self):
        # with self.assertRaises(SystemExit):
        #    self.parser.parse_args(["extract"])
        self.assertRaises(SystemExit,
                          lambda: self.parser.parse_args(["extract"]))

    def test_with_bad_filename(self):
        test_file = 'abc.txt'
        args = self.parser.parse_args(["extract", test_file])
        self.assertRaises(SystemExit, lambda: _main(args))
        # with self.assertRaises(SystemExit) as stat:
        #     _main(args)
        # self.assertEqual(stat.exception.code, 8)

    def test_with_ascii_file_only(self):
        args = self.parser.parse_args(["extract", "-s", "ascii",
                                       ".".join([TEST_ASCII_IPM_FILENAME, "1014block"])])
        _main(args)
        with open(".".join([TEST_ASCII_IPM_FILENAME, "1014block"]) + ".csv", 'r') as csv_file:
            csv_file_lines = csv_file.readlines()
            print(csv_file_lines)

        # check there are the right number of lines
        # Py26 does not support getheader so will have one less line
        if sys.version_info[0] == 2 and sys.version_info[1] == 6:
            self.assertEqual(len(csv_file_lines), 5)
        else:
            self.assertEqual(len(csv_file_lines), 6)

        # same issue here - 2.6 has no header
        start_line = 1
        if sys.version_info[0] == 2 and sys.version_info[1] == 6:
            start_line = 0
        else:
            self.assertEqual(csv_file_lines[0], HEADER_LINE)

        for line in range(start_line, start_line+5):
            self.assertEqual(csv_file_lines[line], DETAIL_LINE)

    def test_with_ebcdic_file_only(self):
        args = self.parser.parse_args(["extract", "-d",
                                       ".".join([TEST_EBCDIC_IPM_FILENAME, "1014block"])])
        _main(args)
        with open(".".join([TEST_EBCDIC_IPM_FILENAME, "1014block"]) + ".csv", 'r') as csv_file:
            csv_file_lines = csv_file.readlines()
            print(csv_file_lines)

        # check there are the right number of lines
        # Py26 does not support getheader so will have one less line
        if sys.version_info[0] == 2 and sys.version_info[1] == 6:
            self.assertEqual(len(csv_file_lines), 5)
        else:
            self.assertEqual(len(csv_file_lines), 6)

        # same issue here - 2.6 has no header
        start_line = 1
        if sys.version_info[0] == 2 and sys.version_info[1] == 6:
            start_line = 0
        else:
            self.assertEqual(csv_file_lines[0], HEADER_LINE)

        for line in range(start_line, start_line+5):
            self.assertEqual(csv_file_lines[line], DETAIL_LINE)

    def test_with_ascii_de55_values(self):
        args = self.parser.parse_args(["extract", "-s", "ascii",
                                       "build/test/test_ascii_de55_ipm.in"])
        _main(args)

    def test_with_bad_ascii_file(self):
        args = self.parser.parse_args(["extract", "-s", "ascii",
                                       "build/test/test_bad_ascii_ipm.in"])
        self.assertRaises(Exception, lambda: _main(args))


class CsvOutputTest(TestCase):
    def test_output_byte_field(self):
        field = b"this is some text"
        self.assertEqual(field.decode(), 'this is some text')


class FilteredDictionaryTest(TestCase):
    def test_filter_dict(self):
        dict = {"a": b("123"), "b": b("456"), "c": b("789")}
        field_list = ["a", "c"]
        expected_dict = {"a": b("123"), "c": b("789")}
        actual_dict = filter_dictionary(dict, field_list)
        self.assertEqual(len(actual_dict), 2)
        self.assertEqual(actual_dict, expected_dict)

    def test_filter_dict_with_latin1(self):
        dict = {
            "a": b("123\xc9"),
            "b": b("456\xc9"),
            "c": b("789\xc9")
        }
        field_list = ["a", "c"]
        expected_dict = {"a": b("123\xc9"), "c": b("789\xc9")}
        actual_dict = filter_dictionary(dict, field_list)
        self.assertEqual(len(actual_dict), 2)
        self.assertEqual(actual_dict, expected_dict)


class GetConfigFilenameTest(TestCase):
    def test_module_default(self):
        filename = get_config_filename("test.conf")
        print(filename)


class MideuConvertTestCases(CommandLineTestCase):
    def test_de55_file(self):
        # Convert file with DE55 in it
        args = self.parser.parse_args(["convert", "-s", "ascii",
                                       "build/test/test_ascii_de55_ipm.in"])
        _main(args)

    def test_with_ascii_file_1014_block(self):
        self.run_file_both_directions("1014block", "-v")

    def test_with_ascii_file_vbs(self):
        self.run_file_both_directions("vbs", "--no1014blocking")

    def run_file_both_directions(self, file_postfix, option):
        print("************ ASCII IN ****************")
        with open(".".join([TEST_ASCII_IPM_FILENAME, file_postfix]), "rb") as ascii_file:
            ascii_data = ascii_file.read()
            hexdump.hexdump(ascii_data)

        args = self.parser.parse_args(["convert", "-s", "ascii", option,
                                       ".".join([TEST_ASCII_IPM_FILENAME, file_postfix])])
        _main(args)

        print("************ EBCDIC IN ****************")
        with open(".".join([TEST_ASCII_IPM_FILENAME, file_postfix]) + ".out", "rb") as ebcdic_file:
            ebcdic_data = ebcdic_file.read()
            hexdump.hexdump(ebcdic_data)

        args = self.parser.parse_args(["convert", option,
                                       ".".join([TEST_ASCII_IPM_FILENAME, file_postfix]) + ".out"])
        _main(args)

        with open(".".join([TEST_ASCII_IPM_FILENAME, file_postfix]) + ".out.out", "rb") as ascii2_file:
            ascii2_data = ascii2_file.read()

        self.assertEqual(ascii2_data, ascii_data)


def create_test_ebcdic_ipm_file():
    message_raw = _convert_text_asc2eb(b("1144")) + \
        b("\xF0\x10\x05\x42\x84\x61\x80\x02\x02\x00\x00\x04"
          "\x00\x00\x00\x00") + \
        _convert_text_asc2eb(b(
            "164444555544445555111111000000009999201508"
            "151715123456789012333123423579957991200000"
            "012306120612345612345657994211111111145BIG"
            " BOBS\\70 FERNDALE ST\\ANNERLEY\\4103  QLD"
            "AUS0080001001Y9990160000000000000001123456"
            "7806999999")
        )
    # add 5 records to a list
    message_list = [message_raw for x in range(5)]
    block_and_write_list(message_list, ".".join([TEST_EBCDIC_IPM_FILENAME, "1014block"]))


def create_test_ascii_ipm_file():
    """
    Create a test IPM file to perform cli testing with
    """
    message_raw = b(
        "1144\xF0\x10\x05\x42\x84\x61\x80\x02\x02\x00\x00\x04"
        "\x00\x00\x00\x00"
        "1644445555444455551111110000000099992015081517151234"
        "5678901233312342357995799120000001230612061234561234"
        "5657994211111111145BIG BOBS\\70 FERNDALE ST\\ANNERLE"
        "Y\\4103  QLDAUS0080001001Y99901600000000000000011234"
        "567806999999"
    )
    # add 5 records to a list
    message_list = [message_raw for x in range(5)]
    block_and_write_list(message_list, ".".join([TEST_ASCII_IPM_FILENAME, "1014block"]))
    write_vbs_list(message_list, ".".join([TEST_ASCII_IPM_FILENAME, "vbs"]))


def create_bad_ascii_ipm_file():
    """
    Create a test IPM file with length greater than bitmap data.
    This record has additional byte added
    """
    message_raw = b(
        "\x00\x00\x00\xee1144\xF0\x10\x05\x42\x84\x61\x80\x02\x02\x00\x00\x04"
        "\x00\x00\x00\x00"
        "1644445555444455551111110000000099992015081517151234"
        "5678901233312342357995799120000001230612061234561234"
        "5657994211111111145BIG BOBS\\70 FERNDALE ST\\ANNERLE"
        "Y\\4103  QLDAUS0080001001Y99901600000000000000011234"
        "567806999999^"
    )
    filename = "build/test/test_bad_ascii_ipm.in"
    with open(filename, 'wb') as output_file:
        output_file.write(message_raw)


def block_and_write_list(message_list, file_name):
    # block and write to file
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    with open(file_name, 'wb') as output_file:
        output_file.write(block(message_list))


def write_vbs_list(message_list, file_name):
    # write to file
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    with open(file_name, 'wb') as output_file:
        output_file.write(vbs_pack(message_list))


def create_test_ascii_de55_ipm_file():
    message_raw = b(
        "1240" + "\xf0"
        "\x10\x07\xc2\x8d\xe1\x82\x02\x02\x00\x00\x04\x00\x00\x00\x00" + "1"
        "65204230010000012000000000000063"
        "20015102901120601010109014C00120"
        "01401599423752309053030010113511"
        "09110000000988503314801120609054"
        "9120000000290000010364     65MER"
        "CH TERMINAL SETT1\\152 Edward Str"
        "eetq\\BRISBANE\\4000      QLDAUS04"
        "80023003NA 014800403620158012   "
        "       750165001M036052"
        "\x9f\x26\x08\x3e\x24\x24\xed\xa3\x69"
        "\xaa\x47\x9f\x36\x02\x04\xdd\x82\x02\x20\x00\x9f\x02\x06\x00\x00"
        "\x00\x00\x14\x50\x9f\x03\x06\x00\x00\x00\x00\x00\x00\x9f\x27\x01"
        "\x80\x9f\x34\x03\x1f\x00\x00\x9f\x53\x01\xb5"
        "016 M"
        "DP388S6Q1015  000000921100000009"
        "885"
    )

    filename = "build/test/test_ascii_de55_ipm.in"

    message_list = [message_raw for _ in range(5)]
    block_and_write_list(message_list, filename)
