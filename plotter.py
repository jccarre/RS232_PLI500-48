import pandas as pd
from math import log10 as log10
from math import pow as pow
from matplotlib import pyplot as plt
from datetime import timedelta as dateTimeTimeDelta
from time import strptime as timeStrptime


def generer_image(fichier, columns):
    df = pd.read_csv(fichier, sep=";")  # , usecols=columns)
    #mins = [df[c].min() for c in columns]
    maxs = {c:df[c].max() for c in columns}
    #min_absolu = min(mins)
    max_absolu = max(maxs.values())
    gain_echelle = {c:0 for c in columns}
    legendes = []
    for c in columns:
        gain_echelle[c] = round(log10(max_absolu / maxs[c]))
        modif_legende = ""
        if gain_echelle[c] != 0:
            modif_legende = " (x" + str(pow(10,gain_echelle[c])) + ")"
            df[c] = df[c].apply(lambda x: x * pow(10,gain_echelle[c]))
        legendes.append(c + modif_legende)

    plt.rcParams["figure.figsize"] = [20, 10]
    plt.rcParams["figure.autolayout"] = True

    # L'interprétation de l'heure en chaine de caractères se fait mal. Je convertis en heures à virgules.
    # def convertTime(timeAsString):
    #    x = timeStrptime(timeAsString.split('.')[0], '%H:%M:%S')
    #    seconds = dateTimeTimeDelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
    #    return round(seconds / 3600, 5)
    # df['time'] = df['time'].apply(convertTime)

    df.plot(x="time", y=columns, grid=True)
    plt.tight_layout()
    plt.legend(legendes, bbox_to_anchor=(0.5, 1.2), loc='upper center')
    #f = plt.get_figure()

    fichier_sans_extension = fichier.split(".")[0]
    plt.savefig(fichier_sans_extension + ".png")


#generer_image("log/2023-05-31", ['Grid voltage (V)', 'AC output active power (W)', 'Battery voltage measured by inverter (V)', 'Battery capacity (approximate SOC) (%)', 'Battery charging current (A)', "PV charging power (W)", "Battery discharge current (A)"])
generer_image("log/2023-06-19", ['SOC', 'Capacité', 'Battery voltage measured by inverter (V)', 'Battery capacity (approximate SOC) (%)', "OCV"]) # 'Battery charging current (A)', "Battery discharge current (A)"])