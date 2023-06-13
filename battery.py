import time
from scipy.stats import linregress
from Requests import request_rating_informations
import Log


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
        self.internalResistance = 0.06  # Valeur mesurée sur les logs de nos batteries. C'est juste pour initialiser. De toute façon, c'est mis à jour dynamiquement.
        #self.floatVoltage = request_rating_informations()["Battery float voltage"]

    def detectChargeModeChange(self):
        nb_lignes = 10  # la détection se fait sur les 10 dernières lignes.
        dico_charge = Log.readLastCSV("Battery charging current (A)", 10)
        dico_decharge = Log.readLastCSV("Battery discharge current (A)", 10)
        charge_avec_signe = [int(dico_charge[key]) - int(dico_decharge[key]) for key in dico_charge.keys()]
        charge_avec_signe = charge_avec_signe[-nb_lignes - 1:-1]
        firstStatus: bool = (charge_avec_signe[0] > 0)
        index = 1
        while (index < len(charge_avec_signe) and (charge_avec_signe[index] > 0) == firstStatus):
            index += 1
        if index == len(charge_avec_signe) // 2:
            while (index < len(charge_avec_signe) and (charge_avec_signe[index] > 0) != firstStatus):
                index += 1
            if index == len(
                    charge_avec_signe):  # On vient de détecter qu'un changement de charge s'est produit pile au milieu des dix dernières données. On en profite donc pour mesurer la résistance interne de la batterie.
                dico_tension = Log.readLastCSV("Battery voltage measured by inverter (V)", 10)
                tensions = [float(dico_tension[key]) for key in dico_tension.keys()][-nb_lignes - 1:-1]

                slope, intercept, r_value, p_value, std_err = linregress(charge_avec_signe, tensions)
                if (r_value > 0.99):  # Si les données sont exploitables
                    self.internalResistance = 0.8 * self.internalResistance + 0.2 * slope  # Moyenne glissante pour mettre à jour la résistance interne de la batterie.
                    dictionnaire = {"résistance interne (Ohm)": slope, "Tension OCV (V)": intercept, "r_value": r_value,
                                    "SOC estimé": self.SOC}
                    Log.logCSV(dictionnaire, dossier="Suivi_SOH_batterie")

    def initSOC(self, status_param):
        """Au début, on fait 100% confiance au SOC estimé par la tension et le courant, afin d'avoir une première valeur. Ensuite, on mettra à jour plus précisément."""
        charge = status_param["Battery charging current (A)"]
        decharge = status_param["Battery discharge current (A)"]
        courant = int(charge) - int(decharge)
        tension = float(status_param["Battery voltage measured by inverter (V)"])
        self.SOC = self.SOC_par_OCV(tension, courant)

    def updateSOC(self, status_param):
        #dico_charge = Log.readLastCSV("Battery charging current (A)", 1)
        #dico_decharge = Log.readLastCSV("Battery discharge current (A)", 1)
        charge = status_param["Battery charging current (A)"]
        decharge = status_param["Battery discharge current (A)"]
        current_time = float(time.time())
        delta_T = (current_time - self.last_update_time) / 3600  # en heures

        delta_T = delta_T * 2100 # TODO : supprimer cette ligne. Elle sert simplement à prendre en compte que dans les essais, j'accélère le temps.

        self.last_update_time = current_time
        courant = int(charge) - int(decharge)
        self.capacity += courant * delta_T
        tension = float(status_param["Battery voltage measured by inverter (V)"])
        self.SOC = 0.999 * (self.SOC + courant * delta_T / self.totalCapacity * 100) + 0.001 * self.SOC_par_OCV(tension, courant)
        return{"SOC":self.SOC, "Capacité":self.capacity}

    def SOC_par_OCV(self, U, I):
        """Estime le SOC à partir de la tension de circuit ouvert de la batterie.
        La tension de circuit ouvert est estimée en prenant un modèle de Norton de pile (OCV = U - r.I)
        Puis le SOC est estimé par la caractéristique générale des batteries au plomb (trouvée sur internet
        https://www.powertechsystems.eu/home/tech-corner/lithium-ion-state-of-charge-soc-measurement/"""
        OCV = U - self.internalResistance * I
        return 0.343460843 * pow(OCV, 2) - 26.7567 * OCV + 519.2

    def update(self, status_param):
        #dico_res_interne = self.detectChargeModeChange(status_param)
        dico_SOC = self.updateSOC(status_param)
        return dico_SOC