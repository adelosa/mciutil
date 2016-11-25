from __future__ import absolute_import
import unittest
import os

from mciutil.cli.common import get_config_filename


class CliCommonTests(unittest.TestCase):
    def test_get_config_filename(self):
        """
        check that package default config exists, otherwise fail
        this will show up on remote build when package is installed
        rather than pointing to development environment
        """
        filename = get_config_filename('mideu.yml')
        self.assertTrue(os.path.exists(filename))

        print("config filename={0}".format(filename))
        if not os.path.isdir(".git"):
            print("Checking that config from site-packages")
            self.assertNotEqual(filename.find("site-packages"), -1)

if __name__ == '__main__':
    unittest.main()
