import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src import View_Frame_Training, Plot_Utils_Model

AXIS_X_LABEL_ELBOW = "Werte von k"
AXIS_Y_LABEL_ELBOW = "Within-Cluster Sum of Squares (WCSS)"
AXIS_X_LABEL_SILHOUETTE = "Datenpunkte"
AXIS_Y_LABEL_SILHOUETTE = "Silhouettenwerte"


def initialize_figure(master):
    """
    Erstellt das Figure-Objekt, sowie den Subplot (Figure.Ax) der in die Figure eingebettet ist und für die Anzeige
    des Analysegraphs genutzt wird
    :param master:  Master-Frame, welcher die Figure enthält
    :return: Figure-Objekt mit eingebetteter Ax
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    # Ausdehnung wird über das Layout und den verfügbaren Platz geregelt
    figure = Figure()
    figure.add_subplot()
    return FigureCanvasTkAgg(figure=figure, master=master)


def initialize_axes(current_figure):
    """
    Initialisiert den Plot zur Anzeige des Analysegraphs  und nimmt Standardeinstellungen für den Plot
    (u.a. Gitteranzeige, Gitterposition, Achsenbezeichnungen,...) vor.
    :param current_figure: Figure, welche die Ax zur graphischen Anzeige des Analysegraphen enthält
    """
    # Zurücksetzen des Plot-Layouts
    current_figure.subplots_adjust(bottom=0.1, top=0.9)
    current_axes = current_figure.get_axes()[0]
    current_axes.cla()
    current_axes.set_xlabel(AXIS_X_LABEL_ELBOW)
    current_axes.set_ylabel(AXIS_Y_LABEL_ELBOW)
    current_axes.grid(True)
    current_axes.set_axisbelow(True)


def reset_axes(current_figure, current_mode):
    """
    Löscht die Ax, die in der übergebenen Figure ist und setzt die Achsenbezeichnungen in Abhängigkeit vom übergebenen
    Modus auf Standardwerte
    :param current_figure: Figure, welche die Ax zur graphischen Anzeige des Analysegraphs enthält
    :param current_mode: Aktuell ausgewählter Analysemodus
    """
    # Zurücksetzen des Plot-Layouts
    current_figure.subplots_adjust(bottom=0.1, top=0.9)
    current_axes = current_figure.get_axes()[0]
    current_axes.cla()
    if current_mode == View_Frame_Training.ANALYSIS_MODE_elbow:
        current_axes.set_xlabel(AXIS_X_LABEL_ELBOW)
        current_axes.set_ylabel(AXIS_Y_LABEL_ELBOW)
    else:
        current_axes.set_xlabel(AXIS_X_LABEL_SILHOUETTE)
        current_axes.set_ylabel(AXIS_Y_LABEL_SILHOUETTE)


def draw_elbow_analysis_graph(current_figure, max_value_of_k, wcss_values_for_k_values):
    """
    Löscht den aktuell angezeigten Plot, setzt den Titel und die Achsenbezeichnungen für den Ellbogenplot und
    fügt der Ax in current_figure den Ellbogenplot für k=1,..., max_value_of_k als x-Werte und den
    wcss_values_for_k_values als y-Werte hinzu.
    :param current_figure: Figure, welche die Ax zur graphischen Anzeige des Analysegraphen enthält
    :param max_value_of_k: Obere Grenze des Werts für k; legt die x-Werte fest. Diese laufen von 1,...,k muss mit der
                           Anzahl der als y-Werte übergebenen wcss_values_for_k_values übereinstimmen
    :param wcss_values_for_k_values: y-Werte des Plots
    """
    # Zurücksetzen des Plot-Layouts
    current_figure.subplots_adjust(bottom=0.1, top=0.9)
    current_axes = current_figure.get_axes()[0]
    current_axes.cla()
    current_axes.set_xlabel(AXIS_X_LABEL_ELBOW)
    current_axes.set_ylabel(AXIS_Y_LABEL_ELBOW)
    # np.arange läuft bis zu stop exklusiv
    current_axes.plot(np.arange(start=1, stop=max_value_of_k + 1), wcss_values_for_k_values, color='blue',
                      linestyle='-', marker='o', )


def draw_silhouette_analysis_graph(current_figure, information_set_for_final_clusters):
    """
    Löscht den aktuell angezeigten Plot und die Achsenbezeichnungen des Analysegraphen und fügt der Ax in
    current_figure den Silhouetten-Plot für das in der Oberfläche ausgewählte k hinzu.
    :param current_figure: Figure, welche die Ax zur graphischen Anzeige des Analysegraphen enthält
    :param information_set_for_final_clusters: Dictionary mit keys=> Tupel, welches das finale Cluster-Zentrum repräsentiert;
                                             values=> Liste an 3-Tupeln der Form (Datenpunkt als Tupel (x,y);
                                             Silhouette des Datenpunkts; Tupel, welches das Zentrum des am nächsten
                                             liegenden Clusters repräsentiert)
    """
    # Anpassung des Plot-Layouts damit die Sekundärachse angezeigt werden kann
    current_figure.subplots_adjust(bottom=0.15, top=0.8)
    current_axes = current_figure.get_axes()[0]
    current_axes.cla()
    current_axes.set_xlabel(AXIS_X_LABEL_SILHOUETTE)
    current_axes.set_ylabel(AXIS_Y_LABEL_SILHOUETTE)
    position_sec_axis_labels = []
    num_els = 0
    # Zeichnen der. die Silhouetten darstellenden Bar-Charts der zu den Cluster-Zentren gehörenden Teildatensätzen
    for cent, col in zip(information_set_for_final_clusters, Plot_Utils_Model.COLOR_LIST):
        # Sortieren der Silhouetten der Datenpunkte des aktuellen Clusters
        information_set_for_final_clusters[cent].sort(key=lambda x: x[1])
        # Zeichnen des Bar-Charts für die Datenpunkte des aktuellen Cluster-Zentrums cent
        # Anzeige der Koordinaten der Datenpunkte mit zwei Nachkommastellen und ohne unnötige Nullen
        # Anmerkung: Falls eine Silhouette 0 ist, wird sie mit Höhe 0,005 angezeigt, um sie sichtbar zu machen
        current_axes.bar(
            [f'({x[0][0]:.2f}'.rstrip('0').rstrip('.') + ", " + f'{x[0][1]:.2f}'.rstrip('0').rstrip('.') + ")" for x
             in
             information_set_for_final_clusters[cent]],
            [x[1] if x[1] != 0 else 0.005 for x in information_set_for_final_clusters[cent]], width=0.3,
            color=col)
        # Berechnung der Tick-Positionen für die Labels (Cluster-Zentren) der Sekundärachse
        num_dataset_for_centroid = len(information_set_for_final_clusters[cent])
        position_sec_axis_labels.append(num_els + (num_dataset_for_centroid - 1) / 2)
        num_els += num_dataset_for_centroid

    # Rotieren der Tick-Labels der x-Achse
    for tick in current_axes.get_xticklabels():
        tick.set_rotation(45)

    # Anlegen der sekundären, oberen Achse zur Anzeige der Cluster-Zentren
    sec_axis = current_axes.secondary_xaxis('top')
    sec_axis.set_xticks(position_sec_axis_labels)
    sec_axis.set_xticklabels(
        [f'({x[0]:.2f}'.rstrip('0').rstrip('.') + ", " + f'{x[1]:.2f}'.rstrip('0').rstrip('.') + ")" for x in
         information_set_for_final_clusters.keys()], rotation=45)

    # Achsenbeschriftungen setzen
    sec_axis.set_xlabel(xlabel="Cluster-Zentren")
    current_axes.set_xlabel(xlabel="Datenpunkte")
    current_axes.set_ylabel(ylabel="Sillhouettenwert")
