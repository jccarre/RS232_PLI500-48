#This file is only intended to be used for debug purposes. It offers the same functions as Requests.py, but the data come from a csv file instead of requesting from the PLI.

from csv import DictReader as csvDictReader

num_ligne_en_cours = 1
consignes_demandees = {"QPIGS":False, "QMOD":False, "QPIWS":False}
QPIGS_demande = False
QMOD_demande = False
QPIWS_demande = False

def lireFichier(nomFichier):
    liste_fieldNames = ""
    with open(nomFichier, 'r', encoding='utf-8', newline='') as csvfile:
        liste_fieldNames = csvfile.readline().replace('\n', '').split(";")
    with open(nomFichier, 'r', encoding='utf-8', newline='') as csvfile:
        reader = csvDictReader(csvfile, delimiter=";")
        res = [{fieldName:row[fieldName] for fieldName in liste_fieldNames} for row in reader]
        return res

donnees_csv = lireFichier("log/2023-06-08")

def compterLignes(ordre):
    global num_ligne_en_cours
    consignes_demandees[ordre] = True
    if consignes_demandees["QPIGS"] and consignes_demandees["QMOD"] and consignes_demandees["QPIWS"]:
        consignes_demandees["QPIGS"] = False
        consignes_demandees["QMOD"] = False
        consignes_demandees["QPIWS"] = False
        num_ligne_en_cours += 1

def demander_donnee(liste_fieldNames):
    return donnees_csv[num_ligne_en_cours]

def request_general_status_parameter(mode='dict'):
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
    listeFieldNames = []
    for i in range(len(noms)):
        listeFieldNames.append(noms[i] + " (" + units[i] + ")")

    dictionnaire = demander_donnee(listeFieldNames)


    compterLignes("QPIGS")
    if mode == 'dict':
        return dictionnaire
    else:
        raise Exception("Ce cas là n'a pas été prévu en mode débug")


def request_mode(output='dict'):
    compterLignes("QMOD")
    if output == 'dict':
        return {'mode': demander_donnee(["mode"])["mode"]}
    else:
        raise Exception("Ce cas là n'a pas été prévu en mode débug")

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
    i = 0
    text = "00000100000000000000000000000000"
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
    compterLignes("QPIWS")
    if mode == 'dict':
        faults_warnings.update({'errors code': text})
        return faults_warnings
    else:
        raise Exception("Ce cas là n'a pas été prévu en mode débug")




def detect_COM_port():
    pass