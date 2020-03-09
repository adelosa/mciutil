"""
mciutil function library

Contains functions to work with MasterCard formatted files
"""
from __future__ import print_function

import binascii
import codecs
import datetime
import decimal
import logging
import re
import struct
import sys
from array import array

import hexdump

LOGGER = logging.getLogger(__name__)


class BitArray:
    """
    This is a minimal native python replacement for the bitarray module that was used to interpret
    the file bitmap. The bitarray module is written in c and does not provide binary wheels so
    forces users to have compilers installed just to install mciutil.
    This small class provides the required functions from that library.
    """
    endian = 'big'
    bytes = b''

    def __init__(self, endian='big'):
        self.endian = endian

    def frombytes(self, array_bytes):
        self.bytes = array_bytes

    def tolist(self):
        swap_bytes = array('B', self.bytes)
        if self.endian == 'little':
            for i, n in enumerate(swap_bytes):
                swap_bytes[i] = int('{:08b}'.format(n)[::-1], 2)
        width = len(self.bytes)*8
        try:
            swapped_bytes = swap_bytes.tobytes()
        except AttributeError:  # 2.7 does not recognise .tobytes method. 2.6 does!
            swapped_bytes = swap_bytes.tostring()
        bit_list = '{bytes:0{width}b}'.format(bytes=int(binascii.hexlify(swapped_bytes), 16), width=width)
        return [bit == '1' for bit in bit_list]


def unblock(blocked_data):
    """
    Unblocks a 1014 byte blocked string

    :param blocked_data: String containing 1014 blocked data or file
    :return: list of records in file
    """
    block_warning_triggered = False
    file_pointer = 0
    unblock_data = []

    while file_pointer <= len(blocked_data):
        unblock_data.append(blocked_data[file_pointer:file_pointer+1012])
        LOGGER.debug("Block chars [%s]", blocked_data[file_pointer+1012:file_pointer+1014])
        if not block_warning_triggered and (
                blocked_data[file_pointer+1012:file_pointer+1014] not in (b(''), b("\x40\x40"))):
            LOGGER.warn("File may not be in 1014 blocked format - found unusual EOB marker %s, usually x'40'x'40'\n"
                        "Consider using --no1014blocking option if file is VBS format",
                        blocked_data[file_pointer+1012:file_pointer+1014])
            block_warning_triggered = True
        file_pointer += 1014

    return vbs_unpack(b("").join(unblock_data))


def vbs_unpack(vbs_data):
    """
    Unpacks a variable blocked string into a list of records

    :param vbs_data: string containing repeating binary length(4) + data
        records in a single string.
    :return: list of unpacked records
    """

    vbs_pointer = 0     # position in file
    line_data = []      # output string

    while vbs_pointer < len(vbs_data):

        # get record length
        record_length_raw = vbs_data[vbs_pointer:vbs_pointer+4]

        # increment file pointer
        vbs_pointer += 4

        # get numerical record length
        record_length = struct.unpack(">i", record_length_raw)[0]
        LOGGER.debug("record_length=%s", record_length)

        # exit if last record (length=0)
        if record_length == 0:
            break

        # get record data
        record = vbs_data[vbs_pointer:vbs_pointer+record_length]

        # add record to output
        line_data.append(record)

        # increment file pointer
        vbs_pointer += record_length

    return line_data


def block(unblocked_data):
    """
    Blocks a list of records to 1014 byte blocked VBS records

    :param unblocked_data: list containing records
    :return: string containing repeating binary length(4) + data records in a
        single string including 1014 block markers
    """

    unblocked_data = vbs_pack(unblocked_data)

    pad_char = b("\x40")
    blocked_data = []
    block_count = 0

    while block_count <= len(unblocked_data):
        blocked_data.append(unblocked_data[block_count:block_count+1012])
        blocked_data.append(pad_char*2)
        block_count += 1012

    # add the pad characters
    pad_count = block_count - len(unblocked_data)
    print(str(pad_count) + " pad characters added")
    blocked_data.append(pad_char * pad_count)

    # return blocked_data
    return b("").join(blocked_data)


def vbs_pack(records):
    """
    Packs a list of records into a variable blocked string

    :param records: list containing records to be packed
    :return: string containing repeating binary length(4) + data
        records in a single string
    """

    vbs_data = []

    for record in records:
        # get the length of the record
        record_length = len(record)
        # convert length to binary
        record_length_raw = struct.pack(">i", record_length)
        # add length to output data
        vbs_data.append(record_length_raw)
        # add data to output
        vbs_data.append(record)

    # add zero length to end of record
    vbs_data.append(struct.pack(">i", 0))

    return b("").join(vbs_data)


def flip_message_encoding(message, bit_config, source_format):
    """
    Flip the encoding of an ISO8583 style file between ASCII and EBCDIC

    :param message: The data to be flipped
    :param bit_config: dictionary of bit mapping configuration
    :param source_format: The encoding of the source {ebcdic, ascii}
    :return: message encoded
    """
    message_length = len(message)-20
    (message_type_indicator, binary_bitmap, message_data) \
        = struct.unpack("4s16s" + str(message_length) + "s", message)

    flipped_message = b("")

    # add the message type
    if source_format == 'ebcdic':
        flipped_message += _convert_text_eb2asc(message_type_indicator)
    else:
        flipped_message += _convert_text_asc2eb(message_type_indicator)

    message_pointer = 0
    bitmap_list = _get_bitmap_list(binary_bitmap)

    # add back the bitmap - no encoding
    flipped_message += binary_bitmap

    for bit in range(2, 128):   # cycle each bit
        if bitmap_list[bit]:    # if bit is on for message
            if bit in bit_config:   # if config available for bit
                return_message, message_increment = \
                    _flip_element_encoding(
                        bit_config[bit],
                        message_data[message_pointer:],
                        source_format)
            else:
                print("No config found for bit {0}".format(bit))
                raise Exception("Config missing for bit {0}".format(bit))

            # Increment the message pointer and process next field
            message_pointer += message_increment
            flipped_message += return_message

    # check that all of message has been consumed, otherwise raise exception
    if message_pointer != len(message_data):
        raise Exception(
            "Message data not correct length. Bitmap indicates len={0}, message is len={1}\n{2}".format(
                message_pointer,
                len(message_data),
                hexdump.hexdump(message_data, result="return")
            )
        )
    return flipped_message


def _flip_element_encoding(bit_config, message_data, source_format):
    """
    Converts a field in an iso8583 style message from ascii to ebcdic

    :param bit_config: dict of field iso8583 bits mapping
    :param message_data: the message containing the field
    :param source_format: encoding of source -- ebcdic or ascii
    :returns: converted string
    :returns: pointer to next field in message

    """

    flipped_element = b("")

    field_length = bit_config['field_length']
    LOGGER.debug("processing field %s", bit_config["field_name"])

    length_size = _get_field_length(bit_config)

    if length_size > 0:
        field_length_string = message_data[:length_size]
        LOGGER.debug("field_length_string %s, %s", length_size, field_length_string)
        if source_format == 'ebcdic':
            field_length_string = _convert_text_eb2asc(field_length_string)
            field_length = int(field_length_string)
        else:
            field_length = int(field_length_string)
            field_length_string = _convert_text_asc2eb(field_length_string)

        flipped_element += field_length_string

    field_data = message_data[length_size:length_size+field_length]

    field_processor = _set_parameter(bit_config,
                                     'field_processor')
    # flip except for ICC field
    if field_processor != 'ICC':
        if source_format == 'ebcdic':
            converted_data = _convert_text_eb2asc(field_data)
        else:
            converted_data = _convert_text_asc2eb(field_data)
        if len(field_data) != len(converted_data):
            raise Exception(
                "Conversion returned different lengths\n{0}\n{1}".format(
                    hexdump.hexdump(field_data, result="return"),
                    hexdump.hexdump(converted_data, result='return')
                )
            )
        flipped_element += converted_data
    else:  # Add ICC data as is
        flipped_element += field_data

    return flipped_element, field_length + length_size


def get_message_elements(message, bit_config, source_format):
    """
    Convert ISO8583 style message to dictionary

    :param message: The message in ISO8583 based format

    * Message Type indicator - 4 bytes
    * Binary bitmap - 16 bytes (Reads DE1 and DE2)
    * Message data - Remainder of record

    :param bit_config: dictionary of bit mapping configuration
    :param source_format: string indicating encoding of data (ascii|ebcdic)
    :return: dictionary of message elements

    * key = 'MTI' message type indicator
    * key = 'DEx' data elements
    * key = 'PDSxxxx' private data fields
    * key = 'TAGxxxx' icc fields

    """
    LOGGER.debug("Processing message: len=%s contents:\n%s", len(message), hexdump.hexdump(message, result="return"))
    # split raw message into components MessageType(4B), Bitmap(16B),
    # Message(l=*)
    message_length = len(message)-20
    (message_type_indicator, binary_bitmap, message_data) \
        = struct.unpack("4s16s" + str(message_length) + "s", message)

    return_values = dict()

    # add the message type
    if source_format == 'ebcdic':
        return_values["MTI"] = _convert_text_eb2asc(message_type_indicator)
    else:
        return_values["MTI"] = message_type_indicator

    message_pointer = 0
    bitmap_list = _get_bitmap_list(binary_bitmap)

    for bit in range(2, 128):
        if bitmap_list[bit]:
            LOGGER.debug("processing bit %s", bit)
            return_message, message_increment = \
                _process_element(bit,
                                 bit_config[bit],
                                 message_data[message_pointer:],
                                 source_format)

            # Increment the message pointer and process next field
            message_pointer += message_increment
            return_values.update(return_message)

    # check that all of message has been consumed, otherwise raise exception
    if message_pointer != len(message_data):
        raise Exception(
            "Message data not correct length. Bitmap indicates len={0}, message is len={1}\n{2}".format(
                message_pointer,
                len(message_data),
                hexdump.hexdump(message_data, result="return")
            )
        )

    return return_values


def _process_element(bit, bit_config, message_data, source_format):
    """
    Processes a message bit element

    :param bit: DE bit
    :param bit_config: message bit configuration
    :param message_data: the data to be processed
    :param source_format: EBCDIC or ASCII
    :returns:
        dictionary: field values
        message incrementer: position of next message
    """

    field_length = bit_config['field_length']

    length_size = _get_field_length(bit_config)

    if length_size > 0:
        field_length_string = message_data[:length_size]
        if source_format == 'ebcdic':
            field_length_string = _convert_text_eb2asc(field_length_string)
        field_length = int(field_length_string)

    field_data = message_data[length_size:length_size+field_length]

    field_processor = _set_parameter(bit_config,
                                     'field_processor')

    # do ascii conversion except for ICC field
    if field_processor != 'ICC':
        if source_format == 'ebcdic':
            field_data = _convert_text_eb2asc(field_data)

    # if field is PAN type, mask the card value
    if field_processor == 'PAN':
        field_data = _mask_pan(field_data)

    # if field is PAN type, mask the card value
    if field_processor == 'PAN-PREFIX':
        field_data = _mask_pan(field_data, prefix_only=True)

    # do field conversion to native python type
    field_data = _convert_to_type(field_data, bit_config)

    return_values = dict()

    # add value to return dictionary
    return_values["DE" + str(bit)] = field_data

    # if a PDS field, break it down again and add to results
    if field_processor == 'PDS':
        return_values.update(_get_pds_fields(field_data))

    # if a DE43 field, break in down again and add to results
    if field_processor == 'DE43':
        return_values.update(_get_de43_fields(field_data))

    # if ICC field, break into tags
    if field_processor == 'ICC':
        return_values.update(_get_icc_fields(field_data))

    return return_values, field_length + length_size


def _set_parameter(config, parameter):
    """
    Checks for parameter value and sets if present

    :param config: bit configuration list
    :param parameter: the configuration item to set
    :return: string with value of parameter
    """
    if parameter in config:
        return config[parameter]
    else:
        return ""


def _mask_pan(field_data, prefix_only=False):
    """
    Mask a pan number string

    :param field_data: unmasked pan
    :return: masked pan
    """
    # if field is PAN type, mask the card value
    if prefix_only:
        return field_data[:9]
    else:
        return field_data[:6] + (b("*") * (len(field_data)-9)) + field_data[len(field_data)-3:len(field_data)]


def _convert_to_type(field_data, bit_config):
    """
    Field conversion to native python type

    :param field_data: Data to be converted
    :param bit_config: Configuration for bit
    :return: data in required type
    """
    field_python_type = _set_parameter(bit_config, 'python_field_type')

    if field_python_type == "int":
        field_data = int(field_data)
    if field_python_type == "decimal":
        field_data = decimal.Decimal(field_data)
    if field_python_type == "long":
        field_data = int(field_data)
    if field_python_type == "datetime":
        field_data = datetime.datetime.strptime(
            field_data, "%y%m%d%H%M%S")
    return field_data


def _get_field_length(bit_config):
    """
    Determine length of iso8583 style field

    :param bit_config: dictionary of bit config data
    :return: length of field
    """
    length_size = 0

    if bit_config['field_type'] == "LLVAR":
        length_size = 2
    elif bit_config['field_type'] == "LLLVAR":
        length_size = 3

    return length_size


def _convert_text_eb2asc(value_to_convert):
    """
    Converts a string from ebcdic to ascii

    :param value_to_convert: The ebcdic value to convert
    :return: converted ascii text
    """

    val = codecs.encode(codecs.decode(value_to_convert, "cp500"), "latin-1")
    return val


def _convert_text_asc2eb(value_to_convert):
    """
    Converts a string from ebcdic to ascii

    :param value_to_convert: The ascii value to convert
    :return: converted ebcdic text
    """

    return codecs.encode(codecs.decode(value_to_convert, "latin-1"), "cp500")


def _get_bitmap_list(binary_bitmap):
    """
    Get list of bits from binary bitmap

    :param binary_bitmap: the binary bitmap to be returned
    :return: the list containing bit values. Bit 0 contains original binary
             bitmap
    """

    # working_bitmap_list = bitarray.bitarray(endian='big')
    working_bitmap_list = BitArray(endian='big')
    working_bitmap_list.frombytes(binary_bitmap)

    # Add bit 0 -> original binary bitmap
    bitmap_list = [binary_bitmap]

    # add bits from bitmap
    bitmap_list.extend(working_bitmap_list.tolist())

    return bitmap_list


def _get_pds_fields(field_data):
    """
    Get MasterCard pds fields from iso field

    :param field_data: the field containing pds fields
    :return: dictionary of pds key values
             key in the form PDSxxxx where x is zero filled number of pds
    """

    field_pointer = 0
    return_values = {}

    while field_pointer < len(field_data):
        # get the pds tag id
        pds_field_tag = field_data[field_pointer:field_pointer+4]
        LOGGER.debug("pds_field_tag=[%s]", pds_field_tag)

        # get the pds length
        pds_field_length = int(field_data[field_pointer+4:field_pointer+7])
        LOGGER.debug("pds_field_length=[%i]", pds_field_length)

        # get the pds data
        pds_field_data = \
            field_data[field_pointer+7:field_pointer+7+pds_field_length]
        LOGGER.debug("pds_field_data=[%s]", str(pds_field_data))
        return_values["PDS" + pds_field_tag.decode()] = pds_field_data

        # increment the fieldPointer
        field_pointer += 7+pds_field_length

    return return_values


def _get_icc_fields(field_data):
    """
    Get de55 fields from message

    :param field_data: the field containing de55
    :return: dictionary of de55 key values
             key is tag+tagid
    """
    TWO_BYTE_TAG_PREFIXES = [b("\x9f"), b("\x5f")]

    field_pointer = 0
    return_values = {"ICC_DATA": binascii.b2a_hex(field_data)}

    while field_pointer < len(field_data):
        # get the tag id (one byte)
        field_tag = field_data[field_pointer:field_pointer+1]
        # set to 2 bytes if 2 byte tag
        if field_tag in TWO_BYTE_TAG_PREFIXES:
            field_tag = field_data[field_pointer:field_pointer+2]
            field_pointer += 2
        else:
            field_pointer += 1

        field_tag_display = binascii.b2a_hex(field_tag)
        LOGGER.debug("field_tag_display=%s", field_tag_display)
        # stop processing de55 if low values tag found
        if field_tag_display == b('00'):
            break
        field_length_raw = field_data[field_pointer:field_pointer+1]
        field_length = struct.unpack(">B", field_length_raw)[0]

        LOGGER.debug("%s", format(field_tag_display))
        LOGGER.debug(field_length)

        # get the pds data
        de_field_data = field_data[field_pointer+1:field_pointer+field_length+1]
        de_field_data_display = binascii.b2a_hex(de_field_data)
        LOGGER.debug("%s", de_field_data_display)
        return_values["TAG" + field_tag_display.upper().decode()] = de_field_data_display

        # increment the fieldPointer
        field_pointer += 1+field_length

    return return_values


def _get_de43_fields(de43_field):
    """
    get pds 43 field breakdown
    :param de43_field: data of pds 43
    :return: dictionary of pds 43 sub elements
    """
    LOGGER.debug("de43_field=%s", de43_field)
    de43_regex = (
        r"(?P<DE43_NAME>.+?) *\\(?P<DE43_ADDRESS>.+?) *\\(?P<DE43_SUBURB>.+?) *\\"
        r"(?P<DE43_POSTCODE>\S{4,10}) *(?P<DE43_STATE>.{3})(?P<DE43_COUNTRY>.{3})"
    )

    field_match = re.match(de43_regex, de43_field.decode('latin-1'))
    if not field_match:
        return dict()

    # get the dict
    field_dict = field_match.groupdict()

    # set fields in dict to bytes (no effect for py2)
    for field in field_dict:
        field_dict[field] = b(field_dict[field])

    return field_dict


if sys.version_info < (3,):
    def b(string):
        """
        Create a byte string field - Python 2.x

        :param string: input string
        :return: a byte array containing the string
        """
        return string
else:
    def b(string):
        """
        Create a byte string field - Python 3.x

        :param string: input string
        :return: a byte array containing the string
        """
        return codecs.latin_1_encode(string)[0]
