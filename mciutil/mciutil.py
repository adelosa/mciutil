import logging
import codecs
import struct
import datetime
import decimal

import bitarray

logger = logging.getLogger(__name__)


def convert_text_eb2asc(value_to_convert):
    val = codecs.encode(codecs.decode(value_to_convert, "cp500"), "utf8")
    return val


def convert_text_asc2eb(value_to_convert):
    return codecs.encode(codecs.decode(value_to_convert, "utf8"), "cp500")


def unblock(blocked_data):
    """ This function will take a 1014 blocked file and remove the block
    characters """

    file_pointer = 0
    unblock_data = ""

    while file_pointer <= len(blocked_data):
        unblock_data += blocked_data[file_pointer:file_pointer+1012]
        file_pointer += 1014

    return _vbs_to_line(unblock_data)


def _vbs_to_line(vbs_data):
    """ Takes binary length(4) + Data organised data and returns Data records
    in array """

    record_count = 0
    vbs_pointer = 0     # position in file
    line_data = []      # output string

    while vbs_pointer < len(vbs_data):

        # increment record count
        record_count += 1

        # get record length
        record_length_raw = vbs_data[vbs_pointer:vbs_pointer+4]

        # increment file pointer
        vbs_pointer += 4

        # get numerical record length
        record_length = struct.unpack(">i", record_length_raw)[0]

        # exit if last record (length=0)
        if record_length == 0:
            vbs_pointer = len(vbs_data)
            break

        # get record data
        record = vbs_data[vbs_pointer:vbs_pointer+record_length]

        # add record to output
        line_data.append(record)

        # increment file pointer
        vbs_pointer += record_length

    return line_data


def block(unblocked_data):
    """This function will take an array of records and block it to 1014 format
    including adding record lengths
    """

    unblocked_data = _line_to_vbs(unblocked_data)

    pad_char = "\x40"
    blocked_data = ""
    block_count = 0

    while block_count <= len(unblocked_data):
        blocked_data += unblocked_data[block_count:block_count+1012]
        blocked_data += pad_char*2
        block_count += 1012

    # add the pad characters
    pad_count = block_count - len(unblocked_data)
    print pad_count, "pad characters added"
    blocked_data += pad_char * pad_count

    return blocked_data


def _line_to_vbs(records):
    """ take record array and convert to VBS format (length(4) + Data) """

    vbs_data = ""

    for record in records:
        # get the length of the record
        record_length = len(record)
        # convert length to binary
        record_length_raw = struct.pack(">i", record_length)
        # add length to output data
        vbs_data += record_length_raw
        # add data to output
        vbs_data += record

    # add zero length to end of record
    vbs_data += struct.pack(">i", 0)

    return vbs_data


def get_message_elements(message, bit_config, source_format):
    """
    Takes the ISO message, bit config (dict) and source format (ascii|ebcdic)
    Returns Dictionary of values
    - key MTI for message type indicator
    - key DEx for data elements
    - key PDSxxxx for private data
    """

    # split raw message into components MessageType(4B), Bitmap(16B),
    # Message(l=*)
    message_length = len(message)-20
    (message_type_indicator, binary_bitmap, message_data) \
        = struct.unpack("4s16s" + str(message_length) + "s", message)

    return_values = {}

    # add the message type
    if source_format == 'ebcdic':
        return_values["MTI"] = convert_text_eb2asc(message_type_indicator)
    else:
        return_values["MTI"] = message_type_indicator

    message_pointer = 0
    bitmap_array = _get_bitmap_array(binary_bitmap)

    for bit in range(2, 128):
        if bitmap_array[bit]:
            field_length = bit_config[bit]['field_length']

            if bit_config[bit]['field_type'] == "LLVAR":
                field_length_string = \
                    message_data[message_pointer:message_pointer+2]
                if source_format == 'ebcdic':
                    field_length_string = \
                        convert_text_eb2asc(field_length_string)
                field_length = int(field_length_string)
                message_pointer += 2

            if bit_config[bit]['field_type'] == "LLLVAR":
                field_length_string = \
                    message_data[message_pointer:message_pointer+3]
                if source_format == 'ebcdic':
                    field_length_string = \
                        convert_text_eb2asc(field_length_string)
                field_length = int(field_length_string)
                message_pointer += 3

            field_data = \
                message_data[message_pointer:message_pointer+field_length]

            if 'field_processor' in bit_config[bit]:
                field_processor = bit_config[bit]['field_processor']
            else:
                field_processor = ""

            # do ascii conversion except for ICC field
            if field_processor != 'ICC':
                if source_format == 'ebcdic':
                    field_data = convert_text_eb2asc(field_data)

            # if field is PAN type, mask the card value
            if field_processor == 'PAN':
                field_data = field_data[:6] \
                    + ("*" * (len(field_data)-9)) \
                    + field_data[len(field_data)-3:len(field_data)]

            # do field conversion to native python type
            if 'field_python_type' in bit_config[bit]:
                field_python_type = bit_config[bit]['field_python_type']
            else:
                field_python_type = ""

            if field_python_type == "int":
                field_data = int(field_data)
            if field_python_type == "decimal":
                field_data = decimal.Decimal(field_data)
            if field_python_type == "long":
                field_data = long(field_data)
            if field_python_type == "datetime":
                field_data = datetime.datetime.strptime(
                    field_data, "%y%m%d%H%M%S")

            # add value to return dictionary
            return_values["DE" + str(bit)] = field_data

            # if a PDS field, break it down again and add to results
            if field_processor == 'PDS':
                pds_values = _get_pds_fields(field_data)
                return_values = merge_two_dictionaries(
                    return_values, pds_values)

            # if a DE43 field, break in down again and add to results
            if field_processor == 'DE43':
                de43_values = _get_de43_elements(field_data)
                return_values = merge_two_dictionaries(
                    return_values, de43_values)

            # Increment the message pointer and process next field
            message_pointer += field_length

    return return_values


def _get_bitmap_array(binary_bitmap):
    """ Takes a binary bitmap and returns an array of bits. Element 0 is input
    binary bitmap. """

    working_bitmap_array = bitarray.bitarray(endian='big')
    working_bitmap_array.frombytes(binary_bitmap)

    # Add bit 0 -> original binary bitmap
    bitmap_array = [binary_bitmap]

    # add bits from bitmap
    bitmap_array.extend(working_bitmap_array.tolist())

    return bitmap_array


def _get_pds_fields(field_data):
    """ field processor for PDS fields
    # Takes Pds FieldData
    # Returns hash of PDS elements.
    # Key is PDS number, Value is value
    """

    field_pointer = 0
    return_values = {}

    while field_pointer < len(field_data):
        # get the pds tag id
        pds_field_tag = field_data[field_pointer:field_pointer+4]
        logger.debug("pds_field_tag=[" + pds_field_tag + "]")

        # get the pds length
        pds_field_length = int(field_data[field_pointer+4:field_pointer+7])
        logger.debug("pds_field_length=[" + str(pds_field_length) + "]")

        # get the pds data
        pds_field_data = \
            field_data[field_pointer+7:field_pointer+7+pds_field_length]
        logger.debug("pds_field_data=[" + str(pds_field_data) + "]")

        return_values["PDS" + pds_field_tag] = pds_field_data

        # increment the fieldPointer
        field_pointer += 7+pds_field_length

    return return_values


def _get_de43_elements(de43_field):
    """ Field processor for field 43 (Merchant name and address) """

    de43_elements = {}
    de43_split = de43_field.split('\\')
    de43_elements["DE43_NAME"] = de43_split[0].rstrip()
    de43_elements["DE43_ADDRESS"] = de43_split[1].rstrip()
    de43_elements["DE43_SUBURB"] = de43_split[2].rstrip()
    de43_elements["DE43_POSTCODE"] = de43_split[3][:4]
    de43_elements["DE43_STATE"] = \
        de43_split[3][len(de43_split[3])-6:len(de43_split[3])-3]
    de43_elements["DE43_COUNTRY"] = \
        de43_split[3][len(de43_split[3])-3:len(de43_split[3])]
    return de43_elements


def merge_two_dictionaries(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""

    z = x.copy()
    z.update(y)
    return z


def filter_dictionary(dictionary, field_list):
    """ Takes dictionary and list of elements and returns dictionary with just
    elements specified """

    filtered_dictionary = {}
    for item in dictionary:
        if item in field_list:
            filtered_dictionary[item] = dictionary[item]
    return filtered_dictionary
