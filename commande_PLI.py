import ctypes #Pour l'appel de la fonction C permettant de calculer le CRC des messages.
import serial #Importation de la bibliothèque « pySerial »
from datetime import datetime
from datetime import date
from os import path
from time import sleep

#COM_port_name = '/dev/ttyACM0'
COM_port_name = '/dev/ttyUSB0'  #Sur le raspberry

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
    return lib.cal_crc_half(c_string, len(string)+1)

def envoyerCommande(commande):
    """Envoie la commande (en ajoutant la parenthèse, le CRC et le retour à la ligne.
    Renvoie La réponse de la part du PLI"""
    with serial.Serial(COM_port_name, baudrate=2400, timeout=1) as s:
        sleep(0.5)#nécessaire pour laisser le temps à la communication série de s'ouvrir.
        #print(s.name + ' is open…')
        #print("Paramètres de la communication : ", s.get_settings())  # Grace a ces 3 lignes lorsque le Port est ouvert c’est indiqué dans le LOG
        crc = calculate_crc(commande)
        print("CRC : ", crc)
        s.write(bytes(commande, 'utf-8'))
        bytes_crc = crc.to_bytes(2, 'big')  #La méthode de calcul du crc proposé par Steca renvoie un CRC sur 16 bit.
        values = bytearray(bytes_crc)
        s.write(values)
        s.write(bytes('\r', 'utf-8'))
        sleep(0.5)
        retour = str(s.readline())[3:-5] #les premiers bits sont simplement la guillemet et le caractère "b" pour dire que c'est en binaire. Les derniers bits sont le crc et le retour à la ligne. On enlève tout ça.
        #log("commande : " + commande + "; resultat = " + retour + ";")
        return retour
    
def requete_statuts():
    reponse = envoyerCommande("QFLAG")
    return str(reponse)

def request_rating_informations():
    reponse = envoyerCommande("QPIRI")
    #data = reponse.split(" ")
    dictionnaire = {}
    noms = ["Grid rating voltage",
            "Grid rating current",
            "AC output rating voltage",
            "AC output rating frequency",
            "AC output rating current",
            "AC output rating apparent power",
            "AC output rating active power",
            "Battery rating voltage",
            "Battery re-charge voltage",
            "Battery under voltage",
            "Battery bulk voltage",
            "Battery float voltage",
            "Battery type",
            "Current max AC charging",
            "Current max charging current",
            "Input voltage range",
            "Output source priority",
            "Charger source priority",
            "Parallel max number",
            "Machine type",
            "Topology",
            "Output mode",
            "Battery re-discharge voltage",
            "PV 'OK' condition for parallel devices",
            "PV power balance",
            "Max charging time at boost stage"]
    #units = ["V", "A", "V", "Hz", "A", "VA", "W", "V", "V", "V", "V", "V", "", "A", "A", "", "", "", "", "", "", "", "", "", "", ""]
    #for i in range(len(data)):
        #dictionnaire[noms[i]] = (data[i], [units[i]])
        #print(noms[i] + " : " + data[i] + " " + units[i])
    return reponse, dictionnaire

def request_general_status_parameter():
    reponse = envoyerCommande("QPIGS")
    #data = reponse.split(" ")
    dictionnaire = {}
    noms = ["Grid voltage",
            "Grid frequency",
            "AC output voltage",
            "AC output frequency",
            "AC output apparent power",
            "AC output active power",
            "Output load percent",
            "Internal bus voltage",
            "Battery voltage measured by inverter",
            "Battery charging current",
            "Battery capacity (approximate SOC)",
            "Inverter heat sink temperature",
            "PV battery charging current (measured on battery side)",
            "PV input voltage",
            "Battery voltage measured by solar charge controller",
            "Battery discharge current",
            "device status",
            "Battery voltage offset for fans on",
            "EEPROM version",
            "PV charging power",
            "Device status"]
    #units = ["V", "Hz", "V", "Hz", "VA", "W", "%", "V", "V", "A", "%", "°C", "A", "V", "V", "A", "", "10mV", "", "W", ""]
    #for i in range(len(data)):
    #    dictionnaire[noms[i]] = (data[i], [units[i]])
    #    print(noms[i] + " : " + data[i] + " " + units[i])
    return reponse, dictionnaire

def request_mode():
    return envoyerCommande("QMOD")


def request_warning_and_faults():
    return envoyerCommande("QPIWS")

for i in range(10):
    print("Passage n°" + str(i))
    statuts = requete_statuts()
    #r = request_rating_informations()
    status_param = request_general_status_parameter()
    mode = request_mode()
    warnings_faults = request_warning_and_faults()
    msg = statuts + ";" + status_param[0] + ";" + mode  + ";" + warnings_faults
    log(msg, "log")
    sleep(10)

#print(r)
#print("fin d'exécution")

