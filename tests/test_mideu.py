import os.path
import hexdump
from unittest import TestCase
from mciutil.cli.mideu import main, _get_cli_parser
from mciutil.mciutil import block, _convert_text_asc2eb

TEST_ASCII_IPM_FILENAME = "build/test/test_ascii_ipm.in"
TEST_EBCDIC_IPM_FILENAME = "build/test/test_ebcdic_ipm.in"


class CommandLineTestCase(TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    def setUp(self):
        self.parser = _get_cli_parser()
        create_test_ascii_ipm_file()
        create_test_ebcdic_ipm_file()


class MideuTestCase(CommandLineTestCase):

    def test_with_empty_args(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])

    def test_with_bad_filename(self):
        test_file = 'abc.txt'
        args = self.parser.parse_args([test_file])
        with self.assertRaises(SystemExit) as stat:
            main(args)
        self.assertEquals(stat.exception.code, 8)

    def test_with_ascii_file_only(self):
        args = self.parser.parse_args(['-s', 'ascii', TEST_ASCII_IPM_FILENAME])
        main(args)

    def test_with_ebcdic_file_only(self):
        args = self.parser.parse_args(['-d', TEST_EBCDIC_IPM_FILENAME])
        main(args)

class CsvOutputTest(TestCase):
    def test_csv_output(self):
        pass


class MongoOutputTest(TestCase):
    def test_mongo_output(self):
        pass


def create_test_ebcdic_ipm_file():
    message_raw = _convert_text_asc2eb("1144") + \
        "\xF0\x10\x05\x42\x84\x61\x80\x02\x02\x00\x00\x04" + \
        "\x00\x00\x00\x00" + \
        _convert_text_asc2eb("164444555544445555111111000000009999201508"
                             "151715123456789012333123423579957991200000"
                             "012306120612345612345657994211111111145BIG"
                             " BOBS\\70 FERNDALE ST\\ANNERLEY\\4103  QLD"
                             "AUS0080001001Y9990160000000000000001123456"
                             "7806999999")
    # add 5 records to a list
    message_list = [message_raw for x in range(5)]
    block_and_write_list(message_list, TEST_EBCDIC_IPM_FILENAME)


def create_test_ascii_ipm_file():
    """
    Create a test IPM file to perform cli testing with
    """
    message_raw = "1144\xF0\x10\x05\x42\x84\x61\x80\x02\x02\x00\x00\x04" \
                  "\x00\x00\x00\x00" + \
                  "1644445555444455551111110000000099992015081517151234" \
                  "5678901233312342357995799120000001230612061234561234" \
                  "5657994211111111145BIG BOBS\\70 FERNDALE ST\\ANNERLE" \
                  "Y\\4103  QLDAUS0080001001Y99901600000000000000011234" \
                  "567806999999"
    # add 5 records to a list
    message_list = [message_raw for x in range(5)]
    block_and_write_list(message_list, TEST_ASCII_IPM_FILENAME)

def block_and_write_list(message_list, file_name):
    # block and write to file
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    with open(file_name, 'wb') as output_file:
        output_file.write(block(message_list))

    # show the file for debugging
    hexdump.hexdump(block(message_list))
