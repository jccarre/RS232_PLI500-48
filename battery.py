import time
from scipy.stats import linregress
#from Requests import request_rating_informations
import Log
from numpy import std as numpyStd


class Battery:
    """
       A class to represent the lead-acid battery used by the PLI.
       Every parameter is updated at each call of "charge" or "discharge" methods.
       A value of -1 indicates that the parameter is unknown.

       Attributes
       ----------
       SOC : float
           The estimated State of Charge of the battery, between 0 (battery empty) and 100 (battery full)
       current_OCV : float
           The estimated Open Circuit Voltage of the battery, in volts.
       internal_resistance : float
           The estimated internal resistance of the battery, in Ohms
       capacity : float
           The current estimated capacity of the battery, in A.h
           In theory, we have the following :
               capacity = Total_Capacity when SOC = 100
               capacity = 0 when SOC = 0
           In practice, all values are estimations. Thus, the capacity might take values over total_capacity or below 0.
       totalCapacity : float
           The total Capacity of the battery, in A.h
           This attribute will be updated each time the battery gets fully discharged and fully recharged.

       Methods
       -------
       charge(current = 0, voltage = -1):
           Informs the battery that it is currently being charged by the given current, at the given voltage.
       discharge(current = 0, voltage = -1):
           Informs the battery that it is currently being charged by the given current, at the given voltage.
       """

    def __init__(self, SOC=-1, rated_voltage=48, current_OCV=-1, capacity=400, totalCapacity=400):
        self.SOC = SOC  # between 0 (battery empty) and 100 (fully charged)
        self.rated_voltage = rated_voltage
        self.current_OCV = current_OCV
        self.capacity = capacity
        self.totalCapacity = totalCapacity
        self.last_update_time = int(time.time())
        self.internalResistance = 0.1  # Valeur mesurée sur les logs de nos batteries. C'est juste pour initialiser. De toute façon, c'est mis à jour dynamiquement.
        #self.floatVoltage = request_rating_informations()["Battery float voltage"]
        self.last_100_U_I = []
        self.floatVoltageProcessInProgress = False # True lorsque la batterie a commencé la phase constant voltage lors de sa charge.
        self.floatVoltageProcessStartTime = None # Horaire auquel la phase de charge en tension constante a démarré.


    def updateLast_100_U_I(self, stat_param):
        charge = int(stat_param["Battery charging current (A)"])
        decharge = int(stat_param["Battery discharge current (A)"])
        self.last_100_U_I.append({"U":float(stat_param["Battery voltage measured by inverter (V)"]), "I":(charge - decharge)})
        while len(self.last_100_U_I) > 100:
            self.last_100_U_I.pop(0)

    def detectChargeModeChange(self):
        if(len(self.last_100_U_I) < 10):
            return {}
        charge_avec_signe = [self.last_100_U_I[i]["I"] for i in range(len(self.last_100_U_I)-10, len(self.last_100_U_I))]
        tensions = [self.last_100_U_I[i]["U"] for i in range(len(self.last_100_U_I)-10, len(self.last_100_U_I))]
        firstStatus: bool = (charge_avec_signe[0] > 0)
        index = 1
        while index < len(charge_avec_signe) and (charge_avec_signe[index] > 0) == firstStatus:
            index += 1
        if index == len(charge_avec_signe) // 2:
            while index < len(charge_avec_signe) and (charge_avec_signe[index] > 0) != firstStatus:
                index += 1
            if index == len(charge_avec_signe):  # On vient de détecter qu'un changement de charge s'est produit pile au milieu des dix dernières données. On en profite donc pour mesurer la résistance interne de la batterie.
                # dico_tension = Log.readLastCSV("Battery voltage measured by inverter (V)", 10)
                # tensions = [float(dico_tension[key]) for key in dico_tension.keys()][-nb_lignes - 1:-1]

                slope, intercept, r_value, p_value, std_err = linregress(charge_avec_signe, tensions)
                if (r_value > 0.99):  # Si les données sont exploitables
                    self.internalResistance = 0.8 * self.internalResistance + 0.2 * slope  # Moyenne glissante pour mettre à jour la résistance interne de la batterie.
                    dictionnaire = {"résistance interne (Ohm)": slope, "Tension OCV (V)": intercept, "r_value": r_value,
                                    "SOC estimé": self.SOC}
                    Log.logCSV(dictionnaire, dossier="Suivi_SOH_batterie")

    def detectFloatVoltageProcess(self):
        """La charge de la batterie s'effectue en suivant un cycle CC-CV. La phase Constant Voltage se fait à une
        tension moyenne de 56.4V. Cette fonction sert à détecter le moment où on sort de ce palier, ce qui indique que
        la batterie est totalement chargée. Le SOC est alors forcé à 100%."""
        if(len(self.last_100_U_I) < 100):
            return
        if(self.last_100_U_I[99]["U"] >= 56.4 and self.last_100_U_I[99]["I"] > 0 and not self.floatVoltageProcessInProgress):
            self.floatVoltageProcessInProgress = True
            self.floatVoltageProcessStartTime = time.time()
        if(self.floatVoltageProcessInProgress and self.last_100_U_I[99]["I"] < 0): #Potentiellement, la phase de charge est terminée.
            tensions = [self.last_100_U_I[i]["U"] for i in range(len(self.last_100_U_I) - 1)]
            ecartType = numpyStd(tensions)
            moyenne = sum(tensions) / len(tensions)
            if(moyenne > 56.2 and ecartType < 0.45):
                self.SOC = 100.0
                duree_charge_CV = time.time() - self.floatVoltageProcessStartTime
                self.floatVoltageProcessInProgress = False
                self.floatVoltageProcessStartTime = None
                dictionnaire = {
                    "durée charge CV (sec)" : duree_charge_CV,
                    "courant en début de phase CV (A)" : self.last_100_U_I[0]["I"],
                    "courant en fin de phase CV (A)" : self.last_100_U_I[98]["I"] # La dernière case (indice 99) correspond à la première en décharge. On veut la dernière en charge).
                }
                Log.logCSV(dictionnaire, dossier="Suivi_SOH_batterie")


    def initSOC(self, status_param):
        """Au début, on fait 100% confiance au SOC estimé par la tension et le courant, afin d'avoir une première valeur. Ensuite, on mettra à jour plus précisément."""
        charge = status_param["Battery charging current (A)"]
        decharge = status_param["Battery discharge current (A)"]
        courant = int(charge) - int(decharge)
        tension = float(status_param["Battery voltage measured by inverter (V)"])
        self.SOC = self.SOC_par_OCV(tension, courant)["SOC"]

    def updateSOC(self, status_param):
        #dico_charge = Log.readLastCSV("Battery charging current (A)", 1)
        #dico_decharge = Log.readLastCSV("Battery discharge current (A)", 1)
        charge = status_param["Battery charging current (A)"]
        decharge = status_param["Battery discharge current (A)"]
        current_time = float(time.time())
        delta_T = (current_time - self.last_update_time) / 3600  # en heures

        delta_T = delta_T * 331 # TODO : supprimer cette ligne. Elle sert simplement à prendre en compte que dans les essais, j'accélère le temps.
        #0.03137 sec après
        #10.41 sec avant
        self.last_update_time = current_time
        courant = int(charge) - int(decharge)
        self.capacity += courant * delta_T
        tension = float(status_param["Battery voltage measured by inverter (V)"])
        SOCparOCV = self.SOC_par_OCV(tension, courant)["SOC"]
        OCV = self.SOC_par_OCV(tension, courant)["OCV"]
        self.SOC = 0.999 * (self.SOC + courant * delta_T / self.totalCapacity * 100) + 0.001 * SOCparOCV
        return{"SOC":round(self.SOC, 2), "Capacité":round(self.capacity, 1), "OCV":OCV}

    def SOC_par_OCV(self, U, I):
        """Estime le SOC à partir de la tension de circuit ouvert de la batterie.
        La tension de circuit ouvert est estimée en prenant un modèle de Norton de pile (OCV = U - r.I)
        Puis le SOC est estimé par la caractéristique générale des batteries au plomb (trouvée sur internet
        https://www.powertechsystems.eu/home/tech-corner/lithium-ion-state-of-charge-soc-measurement/

        Avec notre configuration (au 16 juin 2023 en tout cas), on a observé des coupures basses :
         - 40.7V sous 40A de décharge, le 8 juin.
         - 42.0V sous 11A de décharge, le 4 juin.
         """
        OCV = U - self.internalResistance * I
        return {"SOC":0.3432 * pow(OCV, 2) - 26.83 * OCV + 521.5, "OCV":OCV}

    def update(self, status_param):
        self.updateLast_100_U_I(status_param)
        dico_res_interne = self.detectChargeModeChange()
        self.detectFloatVoltageProcess()
        dico_SOC = self.updateSOC(status_param)
        if dico_res_interne:
            dico_SOC.update(dico_res_interne)
        return dico_SOC