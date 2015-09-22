from unittest import TestCase
from mciutil.cli.mideu import main, _get_cli_parser


class CommandLineTestCase(TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    @classmethod
    def setUpClass(cls):
        parser = _get_cli_parser()
        cls.parser = parser


class MideuTestCase(CommandLineTestCase):
    def test_with_empty_args(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])

    def test_with_filename(self):
        test_file = 'abc.txt'
        args = self.parser.parse_args([test_file])
        with self.assertRaises(SystemExit) as stat:
            main(args)
        self.assertEquals(stat.exception.code, 8)

class CsvOutputTest(TestCase):
    def test_csv_output(self):
        pass


class MongoOutputTest(TestCase):
    def test_mongo_output(self):
        pass