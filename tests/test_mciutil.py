from unittest import TestCase
import hexdump

# Public import
import mciutil
# Private functions
from mciutil.mciutil import (
    _convert_text_asc2eb, _get_de43_fields, _mask_pan, b, flip_message_encoding
)

CONFIG = {
    'data_elements':
        {1: {'field_type': 'FIXED',
             'field_name': 'Bitmap secondary', 'field_length': 8},
         2: {'field_type': 'LLVAR',
             'field_name': 'PAN', 'field_processor': 'PAN', 'field_length': 0},
         3: {'field_type': 'FIXED',
             'field_name': 'Processing code', 'field_length': 6},
         4: {'field_type': 'FIXED',
             'field_name': 'Amount transaction', 'field_length': 12},
         71: {'field_type': 'FIXED',
              'field_name': 'Message number', 'field_length': 8},
         73: {'field_type': 'FIXED',
              'field_name': 'Date, Action', 'field_length': 6},
         12: {'field_type': 'FIXED',
              'field_name': 'Date/Time local transaction', 'field_length': 12},
         22: {'field_type': 'FIXED',
              'field_name': 'Point of service data code', 'field_length': 12},
         23: {'field_type': 'FIXED',
              'field_name': 'Card sequence number', 'field_length': 3},
         24: {'field_type': 'FIXED',
              'field_name': 'Function code', 'field_length': 3},
         26: {'field_type': 'FIXED',
              'field_name': 'Card acceptor business code', 'field_length': 4},
         94: {'field_type': 'LLVAR',
              'field_name': 'Transaction originator institution ID',
              'field_length': 0},
         31: {'field_type': 'LLVAR',
              'field_name': 'Acquirer reference data', 'field_length': 23},
         33: {'field_type': 'LLVAR',
              'field_name': 'Forwarding inst id', 'field_length': 0},
         38: {'field_type': 'FIXED',
              'field_name': 'Approval code', 'field_length': 6},
         40: {'field_type': 'FIXED',
              'field_name': 'Service code', 'field_length': 3},
         42: {'field_type': 'FIXED',
              'field_name': 'Card acceptor Id', 'field_length': 15},
         43: {'field_type': 'LLVAR',
              'field_name': 'Card acceptor name/location',
              'field_processor': 'DE43',
              'field_length': 0},
         48: {'field_type': 'LLLVAR',
              'field_name': 'Additional data', 'field_processor': 'PDS',
              'field_length': 0},
         49: {'field_type': 'FIXED',
              'field_name': 'Currency code', 'field_length': 3},
         55: {'field_type': 'LLLVAR',
              'field_name': 'ICC system related data',
              'field_processor': 'ICC',
              'field_length': 255},
         63: {'field_type': 'LLLVAR',
              'field_name': 'Transaction lifecycle Id', 'field_length': 16}},
    'default_output_elements':
        ['MTI', 'DE2', 'DE3', 'DE4', 'DE12', 'DE22', 'DE24', 'DE26', 'DE31',
         'DE33', 'DE38', 'DE42', 'DE49', 'DE71', 'DE94', 'DE73', 'DE23',
         'DE40', 'DE63', 'PDS0023', 'PDS0052', 'PDS0148', 'PDS0158', 'PDS0165',
         'DE43_NAME', 'DE43_SUBURB', 'DE43_POSTCODE']
    }


class TestGetMessageElements(TestCase):

    def test_get_message_elements_ascii(self):
        message_raw = b(
                      "1144\xF0\x10\x05\x42\x84\x61\x80\x02\x02\x00\x00\x04"
                      "\x00\x00\x00\x00" +
                      "1644445555444455551111110000000099992015081517151234"
                      "5678901233312342357995799120000001230612061234561234"
                      "5657994211111111145BIG BOBS\\70 FERNDALE ST\\ANNERLE"
                      "Y\\4103  QLDAUS0080001001Y99901600000000000000011234"
                      "567806999999")

        message_elements = mciutil.get_message_elements(
            message_raw, CONFIG['data_elements'], 'ascii')

        print(message_elements)

        # print message_elements
        self.assertEqual(message_elements["DE2"], b"444455*******555")
        self.assertEqual(message_elements["DE3"], b"111111")
        self.assertEqual(message_elements["DE4"], b"000000009999")
        self.assertEqual(message_elements["PDS0001"], b"Y")

    def test_get_message_elements_ebcdic(self):
        message_raw = (
            _convert_text_asc2eb(b("1144")) +
            b("\xF0\x10\x05\x42\x84\x61\x80\x02\x02\x00\x00\x04") +
            b("\x00\x00\x00\x00") +
            _convert_text_asc2eb(b("164444555544445555111111000000009999201508"
                                   "151715123456789012333123423579957991200000"
                                   "012306120612345612345657994211111111145BIG"
                                   " BOBS\\70 FERNDALE ST\\ANNERLEY\\4103  QLD"
                                   "AUS0080001001Y9990160000000000000001123456"
                                   "7806999999"))
        )
        message_elements = mciutil.get_message_elements(
            message_raw, CONFIG['data_elements'], 'ebcdic')

        # print message_elements
        self.assertEqual(message_elements["DE2"], b"444455*******555")
        self.assertEqual(message_elements["DE3"], b"111111")
        self.assertEqual(message_elements["DE4"], b"000000009999")

    def test_get_de43_elements(self):
        de43_raw = b("AAMI                  \\36 WICKHAM TERRACE             "
                     "              \\BRISBANE     \\4000      QLDAUS")
        de43_elements = _get_de43_fields(de43_raw)
        self.assertEqual(de43_elements["DE43_NAME"], b"AAMI")
        self.assertEqual(de43_elements["DE43_ADDRESS"], b"36 WICKHAM TERRACE")
        self.assertEqual(de43_elements["DE43_SUBURB"], b"BRISBANE")
        self.assertEqual(de43_elements["DE43_POSTCODE"], b"4000")
        self.assertEqual(de43_elements["DE43_STATE"], b"QLD")
        self.assertEqual(de43_elements["DE43_COUNTRY"], b"AUS")

    def test_vbs_to_line(self):
        vbs_record = b("\x00\x00\x00\x0A1234567890\x00\x00\x00\x0A1234567890")
        records = mciutil.vbs_unpack(vbs_record)
        print("Length of output =", len(records))
        print(records)

    def test_line_to_vbs(self):
        linebreakdata = [b('1234567890'), b('1234567890')]
        vbsdata = mciutil.vbs_pack(linebreakdata)
        hexdump.hexdump(vbsdata)
        self.assertEqual(vbsdata,
                         b"\x00\x00\x00\x0A1234567890\x00\x00\x00\x0A123456"
                         b"7890\x00\x00\x00\x00",
                         )

    def test_unblock(self):
        umodedata = ((b("\x00\x00\x00\x0A1234567890") * 72) +
                     b("\x00\x00\x00\x0A\x40\x401234567890"))
        records = mciutil.unblock(umodedata)
        print(len(records))
        print(records[0])
        print(records[72])

    def test_block(self):
        linebreakdata = []
        for x in range(0, 73):
            linebreakdata.append(b("1234567890"))
        output = mciutil.block(linebreakdata)
        hexdump.hexdump(output)
        input = mciutil.unblock(output)
        print(len(input))
        print(input)

    def test_mask_pan(self):
        card_number = b("1234567890123456")
        self.assertEqual(_mask_pan(card_number), b"123456*******456")

    def test_flip_message_elements_ascii(self):
        message_raw = b(
                      "1144\xF0\x10\x05\x42\x84\x61\x80\x02\x02\x00\x00\x04"
                      "\x00\x00\x00\x00" +
                      "1644445555444455551111110000000099992015081517151234"
                      "5678901233312342357995799120000001230612061234561234"
                      "5657994211111111145BIG BOBS\\70 FERNDALE ST\\ANNERLE"
                      "Y\\4103  QLDAUS0080001001Y99901600000000000000011234"
                      "567806999999")

        message_elements = flip_message_encoding(
            message_raw, CONFIG['data_elements'], 'ascii')
        print("************* E B C D I C ******************")
        hexdump.hexdump(message_elements)
        message_elements = flip_message_encoding(
            message_elements, CONFIG['data_elements'], 'ebcdic')
        print("************* A S C I I ********************")
        hexdump.hexdump(message_elements)
        print("********************************************")
        self.assertEqual(message_raw, message_elements)
