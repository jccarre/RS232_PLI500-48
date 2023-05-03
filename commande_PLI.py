import ctypes  # Pour l'appel de la fonction C permettant de calculer le CRC des messages.
import serial  # Importation de la bibliothèque « pySerial »
from datetime import datetime
from datetime import date
from os import path
from time import sleep
from serial.tools.list_ports import comports as list_COM_ports
from random import randint

COM_port_name = ""
#COM_port_name = '/dev/ttyACM0'
# COM_port_name = '/dev/ttyUSB0'  # Sur le raspberry

current_output_priority_mode = -1  # entre 0 et 3. Inconnu par défaut (d'où le -1)


# Load the shared library containing the cal_crc_half function
# lib = ctypes.cdll.LoadLibrary("./calcul_CRC.so")
# Define the argument and return types of the cal_crc_half function
# lib.cal_crc_half.argtypes = (ctypes.POINTER(ctypes.c_char), ctypes.c_uint)
# lib.cal_crc_half.restype = ctypes.c_uint16

def log(message, dossier="log"):
    nom_fichier = date.today().strftime("%Y-%m-%d")
    nom_fichier = path.join(dossier, nom_fichier)
    with open(nom_fichier, 'a', encoding='utf-8') as f:
        now = datetime.now()
        dt_string = now.strftime("%H:%M:%S")
        f.write(dt_string + ";" + message + "\n")


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
# def calculate_crc(string):
#    # Convert the Python string to a C-style char array
#    c_string = ctypes.create_string_buffer(string.encode())
#
#    # Call the cal_crc_half function and return the result
#    return lib.cal_crc_half(c_string, len(string)+1)

def envoyerCommande(commande, crc=False):
    """Envoie la commande (en ajoutant la parenthèse, le CRC et le retour à la ligne.
    Renvoie La réponse de la part du PLI"""
    with serial.Serial(COM_port_name, baudrate=2400, timeout=1) as s:
        sleep(2)  # nécessaire pour laisser le temps à la communication série de s'ouvrir.
        #  print(s.name + ' is open…')
        #  print("Paramètres de la communication : ", s.get_settings())  # Grace a ces 3 lignes lorsque le Port est ouvert c’est indiqué dans le LOG
        if not crc:  # Pour les commandes classiques, on connait déjà le CRC car il ne change pas. Donc pas besoin de le recalculer à chaque fois.
            crc = calculate_crc(commande)
            print("CRC : ", crc)
        s.write(bytes(commande, 'utf-8'))
        bytes_crc = crc.to_bytes(2, 'big')  # La méthode de calcul du crc proposé par Steca renvoie un CRC sur 16 bit.
        values = bytearray(bytes_crc)
        s.write(values)
        s.write(bytes('\r', 'utf-8'))
        sleep(0.5)
        retour = s.readline()
        retour = str(retour)[3:-5]  # les premiers bits sont simplement la guillemet et le caractère "b" pour dire
        # que c'est en binaire. Les derniers bits sont le crc et le retour à la ligne.
        # log("commande : " + commande + "; resultat = " + retour + ";")
        return retour


def requete_statuts():
    reponse = envoyerCommande("QFLAG", 39028)
    return str(reponse)


def request_rating_informations():
    reponse = envoyerCommande("QPIRI")
    # data = reponse.split(" ")
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
    # units = ["V", "A", "V", "Hz", "A", "VA", "W", "V", "V", "V", "V", "V", "", "A", "A", "", "", "", "", "", "", "", "", "", "", ""]
    # for i in range(len(data)):
    # dictionnaire[noms[i]] = (data[i], [units[i]])
    # print(noms[i] + " : " + data[i] + " " + units[i])
    return reponse, dictionnaire


def request_general_status_parameter():
    reponse = envoyerCommande("QPIGS", 47017)
    # data = reponse.split(" ")
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
    # units = ["V", "Hz", "V", "Hz", "VA", "W", "%", "V", "V", "A", "%", "°C", "A", "V", "V", "A", "", "10mV", "", "W", ""]
    # for i in range(len(data)):
    #    dictionnaire[noms[i]] = (data[i], [units[i]])
    #    print(noms[i] + " : " + data[i] + " " + units[i])
    return reponse, dictionnaire


def request_mode():
    return envoyerCommande("QMOD", 18881)


def request_warning_and_faults():
    return envoyerCommande("QPIWS", 46298)


def set_output_priority(requested_mode):
    """0=AC source / utility first
       1=solar first
       2=solar and AC source / utility
       3=only solar charging (unadvised)"""
    global current_output_priority_mode
    if mode in [0, 1, 2, 3]:
        if current_output_priority_mode != requested_mode:
            commande = "PCP" + "0" + str(mode)
            res = envoyerCommande()
            if "ACK" in res:  # Le PLI a confirmé qu'il a accepté la commande
                current_output_priority_mode = requested_mode
            else:
                message = "Refus de passer en mode 0" + str(requested_mode) + " suite à la commande '" + commande
                message += "'. Réponse du PLI : " + res
                log(message, "log")
    else:
        raise ValueError("Le mode doit être compris entre 0 et 4, sous forme d'un entier.")

def detect_COM_port():
    global COM_port_name
    com_ports = list(list_COM_ports())

    for com in com_ports:
        try:
            old_com_port_name = COM_port_name
            COM_port_name = com.device
            mode = request_mode()
            print("mode : ", mode)
            if mode != "":
                log("Nouveau port COM sélectionné : " + COM_port_name, "log")
                return
            else:
                old_com_port_name = COM_port_name
        except Exception as e:
            COM_port_name = old_com_port_name


#detect_COM_port()

while True:
    try:
        # statuts = requete_statuts()
        # r = request_rating_informations()
        sleep(1)
        status_param = request_general_status_parameter()
        mode = request_mode()
        warnings_faults = request_warning_and_faults()
        msg = status_param[0] + ";" + mode + ";" + warnings_faults
        log(msg, "log")
        print(msg)
    except Exception as e:
        detect_COM_port() #
        log(str(e), "log")



