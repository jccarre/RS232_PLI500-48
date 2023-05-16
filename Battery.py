import time




class Last_data:
    """Keeps last 5 data in memory in order to compute OCV and internal resistance estimation when a switching occurs
    between charging and discharging."""

    def __init__(self, size=10):
        self.tab = []
        self.size = size

    def appendData(self, data):
        self.tab.append(data)
        if len(self.tab) > self.size:
            self.tab.pop(0)
        if self.detectModeChange():
            self.compute_OCV_estimation()

    def compute_OCV_estimation(self):

    def detectModeChange(self):
        """Returns True if the charging status has changed only once, exactly at the middle of the data.
        Else, returns False."""
        firstStatus = self.tab["chargingStatus"][0]
        index = 1
        while (index < len(self.tab) and self.tab["chargingStatus"][index] == firstStatus):
            index += 1
        if index == self.size // 2:
            while (index < self.size and index < len(self.tab) and self.tab["chargingStatus"][index] != firstStatus):
                index += 1
            return index == self.size
        return False

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



    def __init__(self, SOC = -1, rated_voltage = 48, current_OCV = -1, capacity = -1, totalCapacity = 400):
        self.SOC = SOC # between 0 (battery empty) and 100 (fully charged)
        self.rated_voltage = rated_voltage
        self.current_OCV = current_OCV
        self.capacity = capacity
        self.totalCapacity = totalCapacity
        self.last_update_time = int(time.time())
        #self.charging_status = "unknown"
        self.last_data = Last_data()

    def charge(self, current = 0, voltage = -1):
        deltaT = int(time.time()) - self.last_update_time
        charge_status_change_detected = self.last_data.appendData({"chargingStatus":"charging",
                                                                   "voltage" : voltage,
                                                                   "current" : current})
        if charge_status_change_detected:
            # When we switch from charging to discharging (or vice-versa),
            # we can compute the OCV and the internal resistance
            pass

        #if self.charging_status != "charging":
        #    self.charging_status = "charging"



b = Battery()

X = [0, 1, 2, 3, 4, 5]
Y = [2.1, 3.9, 6.1, 8, 10, 12]

from scipy.stats import linregress
#linregress() renvoie plusieurs variables de retour. On s'interessera
# particulierement au slope et intercept
slope, intercept, r_value, p_value, std_err = linregress(X, Y)
print("slope : ", slope)
print("intercept : ", intercept)
print("r_value : ", r_value)
print("std_err : ", std_err)
