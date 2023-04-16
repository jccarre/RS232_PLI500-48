import ctypes #Pour l'appel de la fonction C permettant de calculer le CRC des messages.
import serial #Importation de la bibliothèque « pySerial »
from datetime import datetime
from datetime import date
from os import path
from time import sleep

COM_port_name = '/dev/ttyACM0'
#COM_port_name = '/dev/ttyUSB0'  #Sur le raspberry

# Load the shared library containing the cal_crc_half function
lib = ctypes.cdll.LoadLibrary("./calcul_CRC.so")

# Define the argument and return types of the cal_crc_half function
lib.cal_crc_half.argtypes = (ctypes.POINTER(ctypes.c_char), ctypes.c_uint)
lib.cal_crc_half.restype = ctypes.c_uint16

def log(message, dossier = "log"):
    nom_fichier = date.today().strftime("%Y-%m-%d")
    nom_fichier = path.join(dossier, nom_fichier)
    with open(nom_fichier, 'a', encoding='utf-8') as f:
        now = datetime.now()
        dt_string = now.strftime("%H:%M:%S")
        f.write(dt_string + ";" + message + "\n")

def calculate_crc(string):
    # Convert the Python string to a C-style char array
    c_string = ctypes.create_string_buffer(string.encode())

    # Call the cal_crc_half function and return the result
    return lib.cal_crc_half(c_string, len(string))  #TODO : essayer avec d'autres valeurs de len (en décalant de +/- 1)

def envoyerCommande(commande):
    """Envoie la commande (en ajoutant la parenthèse, le CRC et le retour à la ligne.
    Renvoie La réponse de la part du PLI"""
    with serial.Serial(COM_port_name, baudrate=2400, timeout=1) as s:
        sleep(2)#nécessaire pour laisser le temps à la communication série de s'ouvrir.
        print(s.name + ' is open…')
        print("Paramètres de la communication : ", s.get_settings())  # Grace a ces 3 lignes lorsque le Port est ouvert c’est indiqué dans le LOG
        crc = calculate_crc(commande)
        print("CRC : ", crc)
        s.write(bytes(commande, 'utf-8'))
        bytes_crc = crc.to_bytes(2, 'big')  #La méthode de calcul du crc proposé par Steca renvoie un CRC sur 16 bit.
        values = bytearray(bytes_crc)
        s.write(values)
        #for b in bytes_crc:                 #Si jamais on est obligé d'envoyer chaque bit séparément, on peut faire comme ça.
        #    s.write(b)
        #s.write(crc)
        s.write(bytes('\n', 'utf-8'))
        sleep(0.5)
        retour = s.readline()
        log("commande : " + commande + "; resultat = " + str(retour) + ";")
        return retour
    
def requete_statuts():
    reponse = envoyerCommande("QFLAG")
    return reponse

r = requete_statuts()
print(r)
print("fin d'exécution")
