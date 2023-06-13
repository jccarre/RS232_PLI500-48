from Log import logCSV, logText
from time import sleep
from CustomException import *
from battery import Battery
from Requests_debug import request_mode, request_general_status_parameter, request_warning_and_faults, detect_COM_port


init_sucess = False
while not init_sucess:
    try:
        b = Battery()
        b.initSOC(request_general_status_parameter())
        init_sucess = True
    except Exception as e :
        print(str(e))
        detect_COM_port()  #
        logText(str(e), "error_log")


while True:
    try:
        # statuts = requete_statuts()
        # r = request_rating_informations()
        sleep(0.01)
        status_param = request_general_status_parameter()
        mode = request_mode()
        warnings_faults = request_warning_and_faults()
        info_batterie = b.update(status_param)
        logCSV(status_param, mode, warnings_faults, info_batterie)

    except CRCException as e:
        logText(str(e), "error_log")
        print(str(e))
    except Exception as e:
        print(str(e))
        detect_COM_port()  #
        logText(str(e), "error_log")
