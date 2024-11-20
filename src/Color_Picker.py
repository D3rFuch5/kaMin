import math
import random

color_list10 = ['#ff0029', '#ff7000', '#f5ff00', '#5cff00', '#00ff3d', '#00ffd5', '#008fff', '#0b00ff',
                '#a500ff', '#ff00bf']

color_list100 = ['#ff0029', '#ff001b', '#ff000d', '#ff0000', '#ff0e00', '#ff1c00', '#ff2a00', '#ff3800',
                 '#ff4600', '#ff5400', '#ff6200', '#ff7000', '#ff7e00', '#ff8c00', '#ff9a00', '#ffa700',
                 '#ffb500', '#ffc300', '#ffd100', '#ffdf00', '#ffed00', '#fffb00', '#f5ff00', '#e7ff00',
                 '#d9ff00', '#cbff00', '#bdff00', '#afff00', '#a2ff00', '#94ff00', '#86ff00', '#78ff00',
                 '#6aff00', '#5cff00', '#4eff00', '#40ff00', '#32ff00', '#24ff00', '#16ff00', '#08ff00',
                 '#00ff06', '#00ff13', '#00ff21', '#00ff2f', '#00ff3d', '#00ff4b', '#00ff59', '#00ff66',
                 '#00ff74', '#00ff82', '#00ff90', '#00ff9e', '#00ffac', '#00ffba', '#00ffc7', '#00ffd5',
                 '#00ffe3', '#00fff1', '#00ffff', '#00f1ff', '#00e3ff', '#00d5ff', '#00c7ff', '#00b9ff',
                 '#00abff', '#009dff', '#008fff', '#0081ff', '#0073ff', '#0065ff', '#0057ff', '#0049ff',
                 '#003bff', '#002dff', '#001fff', '#0011ff', '#0003ff', '#0b00ff', '#1900ff', '#2700ff',
                 '#3500ff', '#4300ff', '#5100ff', '#5f00ff', '#6d00ff', '#7b00ff', '#8900ff', '#9700ff',
                 '#a500ff', '#b300ff', '#c100ff', '#cf00ff', '#dd00ff', '#eb00ff', '#f900ff', '#ff00f7',
                 '#ff00e9', '#ff00db', '#ff00cd', '#ff00bf']


def get_color_List(number_of_colors, alpha):
    """
    Liefert eine Liste von number_of_colors Strings, die Farben im RGBA-Format als Hexadezimalzahl darstellen
    :param alpha: Alpha-Wert für die Farben
    :param number_of_colors: Anzahl an gewünschten Farben
    :return: Liste der Farben
    """
    color_list_length = len(color_list100)
    # Auslesen der notwendigen Zahlen aus einer vorbereiteten Farbliste
    if number_of_colors <= color_list_length:
        step = math.floor(color_list_length / number_of_colors)
        node_colors = color_list100[:step * number_of_colors:step]
        if alpha != 100:
            for i in range(number_of_colors):
                node_colors[i] += str(alpha)

    # Falls in der Farbliste zu wenig Farben sind, werden zufällig weitere generiert
    else:
        node_colors = color_list100.copy()
        for i in range(number_of_colors - color_list_length):
            # Erstellen einer zufälligen Zahl im RGB-Zahlenbereich
            new_color_as_int = random.randrange(start=0, stop=2 ** 24)

            # Umwandlung in eine Hexadezimalzahl
            new_hex_color = hex(new_color_as_int)

            # Anfügen der zufälligen Zahl
            if alpha != 100:
                node_colors.append("#" + new_hex_color[2:] + str(alpha))
            else:
                node_colors.append("#" + new_hex_color[2:])

    return node_colors


#TODO: Nicht verwendet
def get_centroid_colors(centroids):
    """
    Erstellt ein Dictionary mit Farben für die Cluster-Zentren anhand der Liste der aktuellen Cluster-Zentren..
    :param centroids: Dictionary der aktuellen Centroids; key => ID der Cluster-Zentren, value => Liste der
                              Koordinaten des Cluster-Zentren
    :return: Dictionary mit den Farben für die Clusterzentren.
    """
    centroid_keys = centroids.keys()
    dict_centroid_colors = {key: [] for key in centroid_keys}
    colors = get_color_List(number_of_colors=len(centroid_keys), alpha=99)
    for (key, color) in zip(dict_centroid_colors, colors):
        dict_centroid_colors[key] = color
    return dict_centroid_colors


