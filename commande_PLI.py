from CRC import calculate_crc

import struct

import serial  # Importation de la bibliothèque « pySerial »
from Log import logCSV, logText
from time import sleep
from serial.tools.list_ports import comports as list_COM_ports
from CustomException import *

COM_port_name = '' #Le nom du port COM est déterminé dynamiquement, même s'il est modifié en cours d'exécution. Pas besoin de l'initialiser.

current_output_priority_mode = -1  # entre 0 et 3. Inconnu par défaut (d'où le -1)


def envoyerCommande(commande, crc=0):
    """Envoie la commande (en ajoutant la parenthèse, le CRC et le retour à la ligne).
    Renvoie La réponse de la part du PLI, si elle est conforme, sinon, lève une exception"""
    with serial.Serial(COM_port_name, baudrate=2400, timeout=1) as s:
        sleep(0.5)  # nécessaire pour laisser le temps à la communication série de s'ouvrir.
        if not crc:  # No need to compute again the CRC when it is already known
            crc = calculate_crc(commande)
            print("CRC : ", crc)
        s.write(bytes(commande, 'utf-8'))
        bytes_crc = crc.to_bytes(2, 'big')  # La méthode de calcul du crc proposé par Steca renvoie un CRC sur 16 bit.
        values = bytearray(bytes_crc)
        s.write(values)
        s.write(bytes('\r', 'utf-8'))
        sleep(0.5)
        retour = s.readline()
        crc_bytes = retour[-3:-1]
        crc_recu = struct.unpack('>H', crc_bytes)[0]
        retour = retour[0:-3]
        retour_decode = retour.decode('utf-8')
        crc_calc = calculate_crc(retour_decode)
        if retour_decode.startswith("("):
            retour_decode = retour_decode[1:]
        else:
            raise IntegrityException("Missing '(' character at beginning of message")
        if "NAK" in retour_decode:
            raise IntegrityException("PLI returned 'NAK'")
        if crc_recu != crc_calc:
            raise CRCException("CRC non conforme lors de la réception")
        return retour_decode


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


def request_general_status_parameter(mode='dict'):
    reponse = envoyerCommande("QPIGS", 47017)
    data = reponse.split(" ")
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
    units = ["V", "Hz", "V", "Hz", "VA", "W", "%", "V", "V", "A", "%", "°C", "A", "V", "V", "A", "", "10mV", "", "W", ""]
    dictionnaire = {}
    for i in range(len(data)):
        dictionnaire[noms[i] + " (" + units[i] + ")"] = data[i]

    if mode == 'dict':
        return dictionnaire
    else:
        return reponse


def request_mode(output='dict'):
    text = envoyerCommande("QMOD", 18881)

    modes_PLI = {'P': 'Power on',
                 'S': 'Stand By',
                 'L': 'AC source',
                 'B': 'Battery',
                 'F': 'Fault',
                 'H': 'Power saving'}
    if output == 'dict':
        return {'mode': modes_PLI[text]}
    else:
        return text

def request_warning_and_faults(mode='dict'):
    """
    Requests the list of errors status.
    Parameter mode :
       - if mode='dict' (default value) : returns a dictionary containing the name of the error as key and its status as value.
         If no error are present, simply returns 00000000000000000000000000000000
       - if mode = 'text' : returns the raw data sent by the PLI.
    """
    errors = [("Unknown",                        "Unknown error"),
              ("Inverter",                       "Fault"),
              ("Bus Over",                       "Fault"),
              ("Bus Under",                      "Fault"),
              ("Bus Soft Fail",                  "Fault"),
              ("LINE_FAIL",                      "Warning"),
              ("OPVShort",                       "Warning"),
              ("Inverter voltage too low",       "Fault"),
              ("Inverter voltage too high",      "Fault"),
              ("Over temperature",               "Warning"),
              ("Fan locked",                     "Warning"),
              ("Battery voltage high",           "Warning"),
              ("Battery voltage low alarm",      "Warning"),
              ("Overcharge",                     "Warning"),
              ("Battery under shutdown voltage", "Warning"),
              ("Battery derating",               "Warning"),
              ("Over load",                      "Warning"),
              ("EEPROM Fault",                   "Warning"),
              ("Inverter over-current",          "Fault"),
              ("Inverter Soft-Start fail",       "Fault"),
              ("Self-Test fail",                 "Fault"),
              ("AC output DC voltage too high",  "Fault"),
              ("Battery disconnected",           "Fault"),
              ("Current sensor fail",            "Fault"),
              ("Battery short-circuit",          "Fault"),
              ("Power limit",                    "Warning"),
              ("PV voltage high",                "Warning"),
              ("MPPT overload fault",            "Warning"),
              ("MPPT overload",                  "Warning"),
              ("Battery too low to charge",      "Warning"),
              ("Unknown",                        "Unknown error"),
              ("Unknown",                        "Unknown error")]
    text = envoyerCommande("QPIWS", 46298)
    i = 0
    inverter_fault = (text[0] == "1")
    faults_warnings = {}
    for bit in text:
        if bit == "1":
            if i in [9, 10, 11, 16]:
                if inverter_fault:
                    faults_warnings[errors[i][0]] = " Fault"
                else:
                    faults_warnings[errors[i][0]] = " Warning"
            else:
                faults_warnings[errors[i][0]] = errors[i][1]

        i += 1
    if mode == 'dict':
        faults_warnings.update({'errors code': text})
        return faults_warnings
    else:
        return text


def set_output_priority(requested_mode):
    """0=AC source / utility first
       1=solar first
       2=solar and AC source / utility
       3=only solar charging (unadvised)"""
    global current_output_priority_mode
    if mode in [0, 1, 2, 3]:
        if current_output_priority_mode != requested_mode:
            command = "PCP" + "0" + str(mode)
            res = envoyerCommande(command)
            if "ACK" in res:  # PLI has confirmed it accepted the command.
                current_output_priority_mode = requested_mode
            else:
                message = "Refus de passer en mode 0" + str(requested_mode) + " suite à la commande '" + command
                message += "'. Réponse du PLI : " + res
                logText(message, "log")
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
            if mode != "":
                logText("Nouveau port COM sélectionné : " + COM_port_name, "error_log")
                return
            else:
                old_com_port_name = COM_port_name
        except Exception as e:
            COM_port_name = old_com_port_name


while True:
    try:
        # statuts = requete_statuts()
        # r = request_rating_informations()
        sleep(1)
        status_param = request_general_status_parameter()
        mode = request_mode()
        warnings_faults = request_warning_and_faults()
        logCSV(status_param, mode, warnings_faults)
    except CRCException as e:
        logText(str(e), "error_log")
        print(str(e))
    except Exception as e:
        print(str(e))
        detect_COM_port()  #
        logText(str(e), "error_log")
