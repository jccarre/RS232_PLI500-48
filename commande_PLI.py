import ctypes #Pour l'appel de la fonction C permettant de calculer le CRC des messages.
import serial #Importation de la bibliothèque « pySerial »

# Load the shared library containing the cal_crc_half function
lib = ctypes.cdll.LoadLibrary("./calcul_CRC.so")

# Define the argument and return types of the cal_crc_half function
lib.cal_crc_half.argtypes = (ctypes.POINTER(ctypes.c_char), ctypes.c_uint)
lib.cal_crc_half.restype = ctypes.c_uint16

def calculate_crc(string):
    # Convert the Python string to a C-style char array
    c_string = ctypes.create_string_buffer(string.encode())

    # Call the cal_crc_half function and return the result
    return lib.cal_crc_half(c_string, len(string))  #TODO : essayer avec d'autres valeurs de len (en décalant de +/- 1)

def envoyerCommande(commande):
    """Envoie la commande (en ajoutant la parenthèse, le CRC et le retour à la ligne.
    Renvoie La réponse de la part du PLI"""
    with serial.serial_for_url(port= "COM6", baudrate=2400,timeout=1) as s:
        print(s.name + 'is open…')
        print(s.get_settings())  # Grace a ces 3 lignes lorsque le Port est ouvert c’est indiqué dans le LOG
        crc = calculate_crc(commande)
        s.write(commande.encode('utf-8'))
        s.write(crc)
        s.write('\n')
        return s.readline()

def requete_statuts():
    reponse = envoyerCommande("QFLAG")
    