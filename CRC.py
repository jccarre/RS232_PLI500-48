# import ctypes  # Pour l'appel de la fonction C permettant de calculer le CRC des messages.

def calculate_crc(msg):
    crc_ta = [
        0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
        0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef
    ]
    crc = 0
    for c in msg.encode():
        da = (crc >> 8) >> 4
        crc = (crc << 4) & 0b000000001111111111111111
        b = c >> 4
        d = da ^ (c >> 4)
        crc ^= crc_ta[da ^ (c >> 4)]
        da = (crc >> 8) >> 4
        crc = (crc << 4) & 0b000000001111111111111111
        e = (c & 0x0f)
        f = da ^ (c & 0x0f)
        crc ^= crc_ta[da ^ (c & 0x0f)]
    bCRCLow = crc & 0xff
    bCRCHign = (crc >> 8) & 0xff
    if bCRCLow == 0x28 or bCRCLow == 0x0d or bCRCLow == 0x0a:
        bCRCLow += 1
    if bCRCHign == 0x28 or bCRCHign == 0x0d or bCRCHign == 0x0a:
        bCRCHign += 1
    crc = (bCRCHign << 8) | bCRCLow
    return crc


# Ceci était l'ancienne façon de calculer le CRC, qui faisait appel au code C. Désormais, cette fonction a été écrite en python.
#
# Load the shared library containing the cal_crc_half function
# lib = ctypes.cdll.LoadLibrary("./calcul_CRC.so")
# Define the argument and return types of the cal_crc_half function
# lib.cal_crc_half.argtypes = (ctypes.POINTER(ctypes.c_char), ctypes.c_uint)
# lib.cal_crc_half.restype = ctypes.c_uint16
#
# def calculate_crc(string):
#    # Convert the Python string to a C-style char array
#    c_string = ctypes.create_string_buffer(string.encode())
#
#    # Call the cal_crc_half function and return the result
#    return lib.cal_crc_half(c_string, len(string)+1)