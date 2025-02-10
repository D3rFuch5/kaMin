import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoLocator
from scipy.spatial import Voronoi

DEFAULT_X_LOW = -20
DEFAULT_X_HIGH = 20
DEFAULT_Y_LOW = -10
DEFAULT_Y_HIGH = 10

DEFAULT_X_LABEL = "x"
DEFAULT_Y_LABEL = "y"

# Es müssen immer so viele Farben vorhanden sein, wie der maximal zugelassene Wert von k ist
COLOR_LIST = ['#e81123', '#00188f', '#009e49', '#fff100', '#68217a', '#47231a', '#00bcf2', '#ff8c00', '#ec008c',
              '#000000']


class Plot_Container:

    def __init__(self, axes):
        # Plot (Figure.Axes) zur grafischen Anzeige von k-Means
        self.plot_axes = axes
        # Nimmt Standardeinstellungen für den Plot vor
        self.plot_axes.cla()
        self.plot_axes.set_xlabel(DEFAULT_X_LABEL)
        self.plot_axes.set_ylabel(DEFAULT_Y_LABEL)
        set_plot_dimensions(plot_ax=self.plot_axes,
                            dimensions=[[DEFAULT_X_LOW, DEFAULT_X_HIGH], [DEFAULT_Y_LOW, DEFAULT_Y_HIGH]])
        self.plot_axes.grid(True)
        self.plot_axes.set_axisbelow(True)
        # Skalierung des Plots in x und y Richtung auf gleiche Einheitengröße
        self.plot_axes.set_aspect(1)
        # Legt fest, dass die Abmessungen der Axes an sich geändert werden, um die eins zu eins Skalierung der Achsen
        # zu halten.
        self.plot_axes.set_adjustable("box")
        self.current_axis_ticks = set_common_tick_space(plot_ax=self.plot_axes)

        # Attribut zum Speichern der zu den Datenpunkten gehörenden Line2D-Objekten
        # key: Tupel (x,y) value: zugehöriges Line2D-Objekt
        self.dict_dataset = {}

        # key: Tupel (x,y) value: zugehöriges Line2D-Objekt
        self.dict_centroids = {}
        # Liste von Listen der Annotationen. Innere Liste immer die Annotationen für einen Satz Cluster-Zentren
        self.current_annotations = []

        # Liste der bisherigen dict_centroids
        self.centroid_history = []
        self.centroid_history_arrows = []

        self.current_decision_areas = []

        # Enthält die für die Anzeige des Distanzenplots der Ellbogen-Analyse notwendigen Objekte. An der k-1-ten Stelle
        # befinden sich die Objekte für die Darstellung im Fall k
        # An jeder Stelle der Liste ist ein Tupel der Form (list_lines, list_centroids, list_anns)
        self.elbow_analysis_distances_objects = []

        # Enthält die für die Anzeige des Distanzenplots notwendigen Objekte
        self.silhouette_analysis_distances_objects = []

        # Enthält den Punkt, der als letztes geklickt wurde um das Ausblenden effizienter zu gestalten
        self.silhouette_analysis_last_clicked = ()

        # Speichert die Tooltip-Annotation
        self.tooltip_annotation = None
        self.init_tooltip()

    def reset_plot_container(self, plot_dimensions, axis_labels):
        """
        Setzt den Plot_Container zurück. Dabei wird die Anzeigefläche (Axes) gesäubert, die Achsenbezeichnungen werden
        auf die Standardwerte gesetzt. Ebenso wird die Abmessung des Anzeigebereichs auf Standardwerte gesetzt, außer
        es werden Abmessungen in Form der plot_dimensions übergeben.
        Des Weiteren werden alle im Plot_Container gespeicherten Informationen (hauptsächlich Line2D-Objekte der
        angezeigten Elemente) gelöscht.
        :param plot_dimensions: Liste der Form [[X_LOW, X_HIGH], [Y_LOW, Y_HIGH]], welche die Abmessungen der Anzeige
                                fläche beinhaltet
        :param axis_labels: Liste der Achsenbezeichnungen der Form [x_Achse, y_Achse]
        """
        self.plot_axes.cla()
        if axis_labels:
            self.plot_axes.set_xlabel(axis_labels[0])
            self.plot_axes.set_ylabel(axis_labels[1])
        else:
            self.plot_axes.set_xlabel(DEFAULT_X_LABEL)
            self.plot_axes.set_ylabel(DEFAULT_Y_LABEL)
        if plot_dimensions:
            set_plot_dimensions(plot_ax=self.plot_axes, dimensions=plot_dimensions)
        else:
            set_plot_dimensions(plot_ax=self.plot_axes,
                                dimensions=[[DEFAULT_X_LOW, DEFAULT_X_HIGH], [DEFAULT_Y_LOW, DEFAULT_Y_HIGH]])
        self.current_axis_ticks = set_common_tick_space(plot_ax=self.plot_axes)
        self.dict_dataset.clear()
        self.dict_centroids.clear()
        self.centroid_history_arrows.clear()
        self.centroid_history.clear()
        self.current_annotations.clear()
        self.current_decision_areas.clear()
        self.elbow_analysis_distances_objects.clear()
        self.silhouette_analysis_distances_objects.clear()
        self.silhouette_analysis_last_clicked = ()
        self.init_tooltip()
        self.tooltip_annotation.set_visible(False)

    def init_tooltip(self):
        self.tooltip_annotation = self.plot_axes.annotate("abcdefghi", xy=(10,10), annotation_clip=False, va='center', xycoords='data',
                xytext=(6, 8), textcoords='offset points')
        self.tooltip_annotation.set_bbox(dict(facecolor='lightgrey', alpha=0.5, edgecolor='darkgrey', boxstyle="round"))
        self.tooltip_annotation.set_visible(False)

    def get_current_centroids_Line2D(self):
        """
        Gibt die aktuell gespeicherten Line2D-Objekte der im Plot-Container gespeicherten Cluster-Zentren zurück. Es
        muss sichergestellt sein, dass diese vorhanden sind.
        :return: eine View der Line2D-Objekte der im Plot-Container gespeicherten Cluster-Zentren
        """
        return self.dict_centroids.values()


def initialize_figure(master):
    """
    Erstellt das Figure-Objekt, sowie den Subplot (Figure.Axes), der in die Figure eingebettet ist und für die Anzeige
    der Punkte, usw. genutzt wird
    :param master:  Master-Frame, welcher die Figure enthält
    :return: Figure-Objekt mit eingebetteter Ax
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    # Ausdehnung wird über das Layout und den verfügbaren Platz geregelt
    figure = Figure()
    figure.add_subplot()
    return FigureCanvasTkAgg(figure=figure, master=master)


def reset_centroids_to_start_of_training(current_plot_container):
    """
    Setzt den Plot-Container auf den Stand vor dem Training zurück, d.h. es sind nur die initialen Cluster-Zentren
    und deren Decision Areas (falls diese bereits berechnet wurden) vorhanden. Bereits darüber hinausgehende Elemente
    der Anzeigefläche werden aus dem Plot-Container gelöscht und von der Anzeigefläche entfernt.
    :param current_plot_container: aktueller Plot-Container
    """
    # Entfernen aller vorhandener Cluster-Zentren in der Historie und der Historien-Pfeile, aller Annotationen und
    # Decision Areas bis auf die der initialen Zentren.
    # Die Annotationen werden sichtbar gesetzt und die initialen Cluster-Zentren werden sichtbar und wieder auf volle
    # Farbstärke gesetzt.

    # Enthält bereits mehr als ein Element, d.h. es hat mindestens ein Trainingsschritt stattgefunden.
    # Andernfalls befinden wir uns noch in der initialen Situation (siehe else-Fall).
    if len(current_plot_container.centroid_history) > 1:
        # Entfernen aller Cluster-Zentren, außer denen an erster Stelle der Historie von der Anzeigefläche
        for centroid_dict in current_plot_container.centroid_history[1:]:
            for centroid in centroid_dict:
                centroid_dict[centroid].remove()

        # Initiale Cluster-Zentren aus der Historie holen und in dict_centroids speichern
        current_plot_container.dict_centroids = current_plot_container.centroid_history[0]
        # Komplette Historie löschen, da beim (Re-)Aktivieren des Trainings die aktuell verfügbaren initialen Cluster-
        # Zentren zur Historie hinzugefügt werden (Elemente wurden bereits oben von der Anzeigefläche entfernt)
        current_plot_container.centroid_history.clear()

        # Initiale Cluster-Zentren sichtbar und wieder auf volle Farbstärke setzen
        for centroid in current_plot_container.dict_centroids:
            current_plot_container.dict_centroids[centroid].set(visible=True,
                                                                color=current_plot_container.dict_centroids[
                                                                          centroid].get_color()[:7])

        # Entfernen der Annotationen aller Cluster-Zentren, außer der initialen Cluster-Zentren
        for ann_list in current_plot_container.current_annotations[1:]:
            for ann in ann_list:
                ann.remove()
        del current_plot_container.current_annotations[1:]

        # Anzeige der Annotationen der initialen Cluster-Zentren
        for ann in current_plot_container.current_annotations[0]:
            ann.set_visible(True)

        # Verlaufspfeile gibt es erst nach dem ersten Trainingsschritt. Diese können also alle gelöcht werden.
        for arrow_set in current_plot_container.centroid_history_arrows:
            for arrow in arrow_set:
                arrow.remove()
        current_plot_container.centroid_history_arrows.clear()

        # Entfernen aller Decision Areas bis auf die der initialen Cluster-Zentren
        for area_set in current_plot_container.current_decision_areas[1:]:
            for area in area_set:
                area.remove()
        del current_plot_container.current_decision_areas[1:]
    # Falls die Länge der Historie eins ist, hat noch kein Training stattgefunden, d.h. dict_centroids und
    # centroid_history enthalten nur die initialen Cluster-Zentren und nur diese werden angezeigt
    # Es muss also nichts passieren, außer das Leeren der Historie, da beim Aktivieren des Trainings immer die
    # aktuellen Cluster-Zentren zur Historie hinzugefügt werden.
    else:
        # Historie leeren, da beim (Re-)Aktivieren des Trainings die aktuell verfügbaren initialen Cluster-
        # Zentren zur Historie hinzugefügt werden
        current_plot_container.centroid_history.clear()


def add_centroids(current_plot_container, centroids):
    """
    Fügt dem aktuellen Plot (plot_axes) die in der Liste centroids übergebenen Cluster-Zentren hinzu. Dafür
    werden entsprechende Line2D-Objekte erstellt und passende Annotationen hinzugefügt. Die Line2D-Objekte werden in
    dict_centroids des Plot-Containers gespeichert. Die Liste der Annotationen wird an die current_annotations des
    Plot-Containers angehängt.
    :param current_plot_container: aktueller Plot_Container
    :param centroids: Liste der aktuellen Cluster-Zentren
    """
    # Hinzufügen der Cluster-Zentren(Line2D) und speichern im dict_centroids des current_plot_containers
    for d_elm, col in zip(centroids, COLOR_LIST):
        current_plot_container.dict_centroids[d_elm] = current_plot_container.plot_axes.plot(d_elm[0], d_elm[1],
                                                                                             marker='X',
                                                                                             markersize=8,
                                                                                             color=col,
                                                                                             picker=3,
                                                                                             visible=True,
                                                                                             zorder=4)[0]

    # Hinzufügen der Nummern der Cluster-Zentren als Annotationen im Plot
    xl = current_plot_container.plot_axes.get_xlim()
    pad_x = abs(xl[1] - xl[0]) / 100
    yl = current_plot_container.plot_axes.get_ylim()
    pad_y = abs(yl[1] - yl[0]) / 100
    current_plot_container.current_annotations.append([current_plot_container.plot_axes.annotate(
        text=str(i + 1), xy=(centroids[i][0] + pad_x, centroids[i][1] - 4 * pad_y), visible=True)
        for i in range(len(centroids))])


def add_decision_areas(current_plot_container, centroids):
    """
    Erstellen der Elemente der Anzeigefläche zur Darstellung der Decision Areas für die übergebene Liste an Cluster-
    Zentren und Anfügen der Elemente als Liste an die Liste current_decision_areas des aktuellen Plot-Containers.
    :param current_plot_container: aktueller Plot-Container
    :param centroids: Liste der aktuell vorhandenen Cluster-Zentren in Tupelform (x,y)
    """
    # Hinzufügen der Entscheidungsbereiche
    # Distanzpunkte bestimmen und Voronoi-Parkettierung berechnen.
    # Die Koordinaten der Distanzpunkte sind jeweils die obere bzw. untere Grenze der Ausdehnung in die jeweilige
    # Achsendimension um das 10-fache erhöht bzw. erniedrigt.
    # centroids + [(min_x, min_y), (min_x, max_y), (max_x, min_y), (max_x, max_y)]
    voronoi_tess = Voronoi(centroids + [(current_plot_container.plot_axes.get_xlim()[0] - 10 * (
            current_plot_container.plot_axes.get_xlim()[1] - current_plot_container.plot_axes.get_xlim()[0]),
                                         current_plot_container.plot_axes.get_ylim()[0] - 10 * (
                                                 current_plot_container.plot_axes.get_ylim()[1] -
                                                 current_plot_container.plot_axes.get_ylim()[0])),
                                        (current_plot_container.plot_axes.get_xlim()[0] - 10 * (
                                                current_plot_container.plot_axes.get_xlim()[1] -
                                                current_plot_container.plot_axes.get_xlim()[0]),
                                         current_plot_container.plot_axes.get_ylim()[1] + 10 * (
                                                 current_plot_container.plot_axes.get_ylim()[1] -
                                                 current_plot_container.plot_axes.get_ylim()[0])),
                                        (current_plot_container.plot_axes.get_xlim()[1] + 10 * (
                                                current_plot_container.plot_axes.get_xlim()[1] -
                                                current_plot_container.plot_axes.get_xlim()[0]),
                                         current_plot_container.plot_axes.get_ylim()[0] - 10 * (
                                                 current_plot_container.plot_axes.get_ylim()[1] -
                                                 current_plot_container.plot_axes.get_ylim()[0])),
                                        (current_plot_container.plot_axes.get_xlim()[1] + 10 * (
                                                current_plot_container.plot_axes.get_xlim()[1] -
                                                current_plot_container.plot_axes.get_xlim()[0]),
                                         current_plot_container.plot_axes.get_ylim()[1] + 10 * (
                                                 current_plot_container.plot_axes.get_ylim()[1] -
                                                 current_plot_container.plot_axes.get_ylim()[0]))])

    # Hinzufügen der Voronoi-Parkettierung zur Anzeigefläche
    # Bestimmt das Mapping der Eingabe Cluster-Zentren auf die Eingabepunkte der Voronoi-Parkettierung.
    # Man kann nicht sicher sein, dass diese in der gleichen Reihenfolge bleiben.
    # Folgende Liste speichert die Indizes der Voronoi-Eingabepunkte in der Reihenfolge der Cluster-Zentren.
    indices_of_centroids_in_voronoi_points = []
    for centroid in centroids:
        index_num = 0
        for point in voronoi_tess.points:
            if point[0] == centroid[0] and point[1] == centroid[1]:
                indices_of_centroids_in_voronoi_points.append(index_num)
                break
            index_num += 1

    # Färben der Regionen der Cluster-Zentren in den Farben der Cluster-Zentren.
    # Wir durchlaufen die indices_of_centroids_in_voronoi_points. Diese enthalten die Indizes Voronoi-Eingabepunkte
    # in der Reihenfolge der Cluster-Zentren. (Index des Voronoi-Eingabepunkts des ersten Cluster-Zentrums am Anfang,..)
    # point_region enthält die Indizes der Regionen in der Reihenfolge der Voronoi-Eingabepunkte. Wir holen also
    # den Index des ersten Voronoi-Eingabepunkts über indices_of_centroids_in_voronoi_points[j]. An diesem Index
    # findet man in point_region den Index der Region, welche zum aktuellen Voronoi-Eingabepunkt gehört.
    # Diese zeichnen wir in der Farbe des aktuellen Cluster-Zentrums (COLOR_LIST[j]).
    current_plot_container.current_decision_areas.append([current_plot_container.plot_axes.fill(
        *zip(*[voronoi_tess.vertices[i] for i in
               voronoi_tess.regions[voronoi_tess.point_region[indices_of_centroids_in_voronoi_points[j]]]]),
        color=COLOR_LIST[j],
        alpha=0.25, picker=0, visible=False, zorder=1)[0] for j in range(len(indices_of_centroids_in_voronoi_points))])


def remove_current_centroids(current_plot_container):
    """
    Entfernt alle momentan in dict_centroids vorhandenen Cluster-Zentren von der Anzeigefläche und entfernt die
    zugehörigen Annotationen.
    :param current_plot_container: aktueller Plot_Container
    """
    for d_elm in current_plot_container.dict_centroids:
        current_plot_container.dict_centroids[d_elm].remove()
    current_plot_container.dict_centroids.clear()

    if current_plot_container.current_annotations:
        for ann in current_plot_container.current_annotations[-1]:
            ann.remove()
        current_plot_container.current_annotations.pop()


def clear_centroid_history(current_plot_container):
    for arrow_set in current_plot_container.centroid_history_arrows:
        for arrow in arrow_set:
            arrow.remove()
    current_plot_container.centroid_history_arrows.clear()

    for centroid_dict in current_plot_container.centroid_history:
        for centroid in centroid_dict:
            centroid_dict[centroid].remove()
    current_plot_container.centroid_history.clear()

    for ann_list in current_plot_container.current_annotations:
        for ann in ann_list:
            ann.remove()
    current_plot_container.current_annotations.clear()


def clear_decision_areas(current_plot_container):
    """
    Löscht die ggf. aktuell vorhandenen Decision Areas von der Anzeigefläche und entfernt die Elemente aus dem aktuellen
    Plot-Container
    :param current_plot_container: aktueller Plot-Container
    """
    if current_plot_container.current_decision_areas:
        for area_set in current_plot_container.current_decision_areas:
            for area in area_set:
                area.remove()
        current_plot_container.current_decision_areas.clear()


def update_centroids(current_plot_container, index):
    """
    Blendet die sich am Index der Historie stehenden Cluster-Zentren in voller Farbstärke ein.
    Die vorherigen Cluster-Zentren werden verblasst. Zusätzlich werden die Annotationen der vorherigen Cluster-Zentren
    aus und die der aktuell betrachteten Cluster-Zentren eingeblendet.
    :param current_plot_container: aktueller Plot-Container
    :param index: Index der aktuell anzuzeigenden Cluster-Zentren in der Historie
    """
    # Alte Cluster-Zentren verblassen und ausblenden
    for centroid in current_plot_container.dict_centroids:
        current_plot_container.dict_centroids[centroid].set(
            color=current_plot_container.dict_centroids[centroid].get_color() + "80",
            visible=False)

    # Aktuell zu betrachtende Cluster-Zentren holen
    current_plot_container.dict_centroids = current_plot_container.centroid_history[index]
    # Cluster-Zentren sichtbar und wieder auf volle Farbstärke setzen
    for centroid in current_plot_container.dict_centroids:
        current_plot_container.dict_centroids[centroid].set(visible=True, color=current_plot_container.dict_centroids[
                                                                                    centroid].get_color()[:7])

    # Ausblenden der Annotationen der letzten Cluster-Zentren
    for ann in current_plot_container.current_annotations[index - 1]:
        ann.set_visible(False)

    # Einblenden der Annotationen der aktuellen Cluster-Zentren
    for ann in current_plot_container.current_annotations[index]:
        ann.set_visible(True)


def add_centroids_train_mode(current_plot_container, centroids, init_step):
    """
    Fügt dem aktuellen Plot (plot_axes) die für die Anzeige des Trainings notwendigen Elemente  zur Anzeigefläche hinzu.
    Falls es sich um den Initialisierungsschritt (init_step=True) beim Aktivieren des Trainings handelt, sind die
    Line2D-Objekte der Cluster-Zentren bereits in dict_centroids vorhanden. Es müssen nur noch die passenden Decision
    Areas berechnet und deren Elemente hinzugefügt werden.
    Handelt es sich um einen normalen Trainingsschritt (init_step=False), werden für die übergebenen Cluster-Zentren
    centroids passende Line2D-Objekte erstellt.
    Zuerst werden die alten Cluster-Zentren verblasst, ausgeblendet und zur Historie hinzugefügt und die zugehörigen
    Annotationen ausgeblendet.
    Dann werden für die neuen Cluster-Zentren Line2D-Objekte erstellt, in dict_centroids abgespeichert und Annotationen
    erstellt und gespeichert. Des Weiteren werden die Verlaufspfeile für die Historie der Cluster-Zentren berechnet.
    Dann werden die Decision Areas bestimmt und gespeichert.
    :param init_step: True, falls es sich um den Initialisierungschritt bei Aktivierung des Trainings handelt.
                      False, sonst
    :param current_plot_container: aktueller Plot_Container
    :param centroids: Liste der aktuellen Cluster-Zentren
    """
    if not init_step:
        # Alte Cluster-Zentren verblassen und ausblenden
        for centroid in current_plot_container.dict_centroids:
            current_plot_container.dict_centroids[centroid].set(
                color=current_plot_container.dict_centroids[centroid].get_color() + "80",
                visible=False)

        # dict_centroids auf ein neues Dictionary setzen
        current_plot_container.dict_centroids = {}

        # Ausblenden der Annotationen der letzten Cluster-Zentren
        for ann in current_plot_container.current_annotations[-1]:
            ann.set_visible(False)

        # Erstellen der Line2D-Objekte der übergebenen Cluster-Zentren centroids, Speicherung dieser in dict_centroids
        # und Anlegen der Annotationen
        add_centroids(current_plot_container=current_plot_container, centroids=centroids)
        current_plot_container.centroid_history.append(current_plot_container.dict_centroids)

        # Hinzufügen der Verlaufspfeile
        current_arrows = []
        for centroid_old, centroid_new, col in zip(current_plot_container.centroid_history[-2],
                                                   current_plot_container.centroid_history[-1], COLOR_LIST):
            current_arrows.append(current_plot_container.plot_axes.arrow(x=centroid_old[0], y=centroid_old[1],
                                                                         dx=(centroid_new[0] - centroid_old[0]),
                                                                         dy=(centroid_new[1] - centroid_old[1]),
                                                                         color=col + "80",
                                                                         head_width=0.12, zorder=2,
                                                                         length_includes_head=True,
                                                                         picker=0,
                                                                         linestyle='--', visible=False))
        current_plot_container.centroid_history_arrows.append(current_arrows)
        add_decision_areas(current_plot_container=current_plot_container, centroids=centroids)
    else:
        # Hinzufügen der nun ausgewählten Cluster-Zentren zur Historie
        current_plot_container.centroid_history.append(current_plot_container.dict_centroids)
        # Es liegen noch keine Decision Areas aus einer ggf. vorherigen Zurücksetzung des Trainings vor
        if len(current_plot_container.current_decision_areas) == 0:
            add_decision_areas(current_plot_container=current_plot_container, centroids=centroids)


def display_centroid_history(current_plot_container, fade_in_history, index=None):
    """
    Blendet den Verlauf der Cluster-Zentren in der Anzeigefläche ein oder aus in Abhängigkeit von dem übergebenen
    Wahrheitswert fade_in_history. Es muss an anderer Stelle sichergestellt sein, dass Index im Bereich der Liste
    centroid_history_arrows liegt.
    :param current_plot_container: aktueller Plot_Container
    :param fade_in_history: True, falls der Verlauf der Cluster-Zentren angezeigt werden soll; False, sonst
    """
    # Ein/Ausblenden der Verlaufspfeile bis zum übergebenen Index(exklusive) bzw. bei index=None aller Pfeile
    for arrow_list in current_plot_container.centroid_history_arrows[:index]:
        for arrow in arrow_list:
            arrow.set(visible=fade_in_history)
    # Falls ein Index übergeben wurde, werden die ab dem Index vorhandenen Pfeile ausgeblendet
    if index is not None:
        # Ausblenden aller folgenden Verlaufspfeile
        for arrow_l in current_plot_container.centroid_history_arrows[index:]:
            for arr in arrow_l:
                arr.set(visible=False)

    # Einblenden der Cluster-Zentren der History
    # An der letzten Stelle bzw. der Stelle des Index befinden sich die aktuellen Cluster-Zentren.
    # Diese sollen immer angezeigt werden.
    if index is None:
        for centroid_dict in current_plot_container.centroid_history[:-1]:
            for centroid_id in centroid_dict:
                centroid_dict[centroid_id].set(visible=fade_in_history)
    else:
        for centroid_dict in current_plot_container.centroid_history:
            for centroid_id in centroid_dict:
                centroid_dict[centroid_id].set(visible=False)
        for cent_dict in current_plot_container.centroid_history[:index]:
            for c_id in cent_dict:
                cent_dict[c_id].set(visible=fade_in_history)
        for centroid in current_plot_container.centroid_history[index]:
            current_plot_container.centroid_history[index][centroid].set(visible=True)


def display_decision_areas(current_plot_container, fade_in_decision_areas, index=-1):
    """
    Blendet Decision Areas aus. In Abhängigkeit von dem übergebenen Wahrheitswert fade_in_decision_areas
    werden die Decision Areas an der Stelle Index ein- oder ausgeblendet.
    :param current_plot_container: aktueller Plot_Container
    :param fade_in_decision_areas: True, falls die Decision Areas angezeigt werden sollen; False, sonst
    :param index: Index der Decision Areas die betrachtet werden sollen. Default: -1, d.h. es werden die letzten Areas
                  in der Liste ggf. eingeblendet
    """
    # Ausblenden aller der Decision Areas
    for areas in current_plot_container.current_decision_areas:
        for area in areas:
            area.set(visible=False)

    # Einblenden der Decision Areas an der Stelle des Index
    if fade_in_decision_areas:
        for d_area in current_plot_container.current_decision_areas[index]:
            d_area.set(visible=True)


def display_plot_axis(current_plot_container, fade_out_axis):
    """
    Blendet das Koordinatensystem und die Achsenticks ein- bzw. aus in Abhängigkeit von dem übergebenen Wahrheitswert
    fade_out_axis
    :param current_plot_container: aktueller Plot_Container
    :param fade_out_axis: True, falls die das Koordinatensystem und die Achsenticks angezeigt werden sollen;
                          False, sonst
    """
    if fade_out_axis:
        current_plot_container.plot_axes.grid(False)
        current_plot_container.plot_axes.set_xticks([])
        current_plot_container.plot_axes.set_yticks([])
    else:
        current_plot_container.plot_axes.grid(True)
        current_plot_container.plot_axes.set_axisbelow(True)
        current_plot_container.plot_axes.set_xticks(current_plot_container.current_axis_ticks[0])
        current_plot_container.plot_axes.set_yticks(current_plot_container.current_axis_ticks[1])


def add_dataset_to_plot(current_plot_container, label_x, label_y, dataset):
    """
    Fügt dem aktuellen Plot (plot_axes) die Punkte des Datensatzes dataset hinzu und speichert die zugehörigen
    Line2D-Objekte im dict_dataset des current_plot_containers
    :param label_y: Label der x-Achse
    :param label_x: Label der y-Achse
    :param current_plot_container: aktueller Plot_Container
    :param dataset: Punkte des Datensatzes als Liste von Tupeln [(x_1, y_1), (x_2,y_2),...]
    """
    # Hinzufügen der Datenpunkte zu Plot und speichern der Datenpunkte und zugehörigen Line2D-Objekten im dict_dataset
    # des current_plot_containers
    for data_point in dataset:
        draw_data_point(current_plot_container=current_plot_container, x=data_point[0], y=data_point[1])

    # Setzen der Achsen-Labels im Plot
    current_plot_container.plot_axes.set_xlabel(label_x)
    current_plot_container.plot_axes.set_ylabel(label_y)


def draw_data_point(current_plot_container, x, y):
    """
    Fügt dem aktuellen Plot (plot_ax) einen einzelnen Punkt(Line2D) an der Stelle (x,y) hinzu und speichert diesen in
    dict_dataset des plot_containers
    :param current_plot_container: aktueller Plot_Container
    :param x: x-Koordinate des neuen Punkts
    :param y: y-Koordinate des neuen Punkts
    """
    current_plot_container.dict_dataset[(x, y)] = current_plot_container.plot_axes.plot(x, y, marker='o', markersize=5,
                                                                                        color='blue',
                                                                                        picker=3, zorder=3)[0]


def update_dataset(current_plot_container, split_dataset_centroids={}):
    """
    Färbt die Punkte des Datensatzes nach der Zugehörigkeit zum jeweiligen Cluster-Zentrum ein. Falls das übergebene
    Dictionary leer ist, werden alle Punkte in der Standardfarbe blau eingefärbt.
    :param current_plot_container: aktueller Plot_Container
    :param split_dataset_centroids: Dictionary: key => Cluster-Zentrum; value=> Liste von Tupeln, die den
                                    aufgeteilten Datensatz enthält. Jedes Element der Liste stellt den Teildatensatz
                                    dar, welcher zum jeweiligen Cluster-Zentrum in current_centroids gehört.
                                    Default: {}
    """
    # Falls keine nach Cluster-Zentren aufgeteilten Daten übergeben werden, werden die Datenpunkte blau eingefärbt.
    if split_dataset_centroids == {}:
        for point in current_plot_container.dict_dataset:
            current_plot_container.dict_dataset[point].set_color(color='blue')
    else:
        for key_centroid, col in zip(split_dataset_centroids, COLOR_LIST):
            for d_elm in split_dataset_centroids[key_centroid]:
                current_plot_container.dict_dataset[d_elm].set_color(color=col)


def set_plot_dimensions(plot_ax, dimensions):
    """
    Setzt die Dimension der x- und y-Ausdehnung des Plots.
    :param plot_ax: aktueller Plot (Figure.Ax)
    :param dimensions: Ausdehnung des Plots in der Form [[x_low, x_high],[y_low, y_high]]
    """
    plot_ax.set_xlim(dimensions[0])
    plot_ax.set_ylim(dimensions[1])


def get_plot_dimensions(plot_ax):
    """
    Gibt die Dimension der x- und y-Ausdehnung des Plots zurück in Form (x_low, x_high, y_low, y_high)
    :param plot_ax: aktueller Plot (Figure.Ax)
    """
    # Kombiniert die beiden Tupel
    return plot_ax.get_xlim() + plot_ax.get_ylim()


def set_common_tick_space(plot_ax):
    """
    Bestimmt unter Ausnutzung von built-in Tick-Locators die gemeinsame Größe der Einheit des Koordinatensystems der
    grafischen Darstellung des Modells in Abhängigkeit von den darzustellenden Daten.
    :param plot_ax: aktueller Plot (Figure.Ax)
    :return: Zwei Arrays, welche die Positionen/Werte der einzelnen Ticks des Koordinatensystems enthalten in der
             Reihenfolge Array für x-Achse, Array für y-Achse
    """
    plot_ax.xaxis.set_major_locator(AutoLocator())
    plot_ax.yaxis.set_major_locator(AutoLocator())
    common_tick_space = min(
        plot_ax.xaxis.get_majorticklocs()[1] - plot_ax.xaxis.get_majorticklocs()[0],
        plot_ax.yaxis.get_majorticklocs()[1] - plot_ax.yaxis.get_majorticklocs()[0])
    plot_ax.xaxis.set_major_locator(MultipleLocator(common_tick_space))
    plot_ax.yaxis.set_major_locator(MultipleLocator(common_tick_space))
    plot_ax.set_xticks(plot_ax.get_xticks()[1:-1])
    plot_ax.set_yticks(plot_ax.get_yticks()[1:-1])
    return plot_ax.get_xticks(), plot_ax.get_yticks()


def draw_centroid_on_datapoint(current_plot_container, x, y):
    """
    Fügt dem aktuellen Plot (plot_ax) ein einzelnes Cluster-Zentrum(Line2D) an der Stelle (x,y) hinzu und speichert
    dieses dict_centroids des plot_containers
    :param current_plot_container: aktueller Plot_Container
    :param x: x-Koordinate des Cluster-Zentrums
    :param y: y-Koordinate des Cluster-Zentrums
    """
    current_plot_container.dict_centroids[(x, y)] = current_plot_container.plot_axes.plot(
        x, y, marker='X', markersize=8, color=COLOR_LIST[len(current_plot_container.dict_centroids)], picker=3,
        zorder=4)[0]

    # Hinzufügen der Nummer des Cluster-Zentrums als Annotation im Plot
    xl = current_plot_container.plot_axes.get_xlim()
    pad_x = abs(xl[1] - xl[0]) / 100
    yl = current_plot_container.plot_axes.get_ylim()
    pad_y = abs(yl[1] - yl[0]) / 100
    if not current_plot_container.current_annotations:
        current_plot_container.current_annotations.append([])
    current_plot_container.current_annotations[0].append(current_plot_container.plot_axes.annotate(
        text=str(len(current_plot_container.dict_centroids)), xy=(x + pad_x, y - 4 * pad_y)))


def remove_data_point(current_plot_container, data_point):
    """
    Entfernt, falls möglich, den übergebenen Punkte (Line2D) von der Zeichenfläche (plot_axes).
    :param current_plot_container: aktueller Plot_Container
    :param data_point: Punkt der Zeichenfläche, welcher entfernt werden soll
    """
    # Entfernen des zum data_point gehörenden Line2D-Objekts
    current_plot_container.dict_dataset.pop(data_point).remove()


def remove_centroid_from_datapoint(current_plot_container, centroid_to_remove):
    """
    Entfernt das übergebene Cluster-Zentrum von der Zeichenfläche, aktualisiert die Annotationen der verbleibenden
    Zentren und aktualisiert die im Plot_Container gespeicherten Informationen.
    :param current_plot_container: aktueller Plot_Container
    :param centroid_to_remove: Cluster-Zentrum als Tuple (x,y) der Zeichenfläche, welches entfernt werden soll
    """
    # Entfernen des Cluster-Zentrums
    current_plot_container.dict_centroids.pop(centroid_to_remove).remove()

    # Update der Farben der verbleibenden Cluster-Zentren
    for centroid_to_update, col in zip(current_plot_container.dict_centroids, COLOR_LIST):
        current_plot_container.dict_centroids[centroid_to_update].set_color(col)

    # Entfernen der letzten Annotationen
    for ann in current_plot_container.current_annotations.pop():
        ann.remove()

    # Neu setzen aller Annotationen der aktuellen Cluster-Zentren und Hinzufügen zum Plot_Container
    xl = current_plot_container.plot_axes.get_xlim()
    pad_x = abs(xl[1] - xl[0]) / 100
    yl = current_plot_container.plot_axes.get_ylim()
    pad_y = abs(yl[1] - yl[0]) / 100

    centroid_num = 1
    new_ann = []
    for centroid in current_plot_container.dict_centroids:
        new_ann.append(current_plot_container.plot_axes.annotate(text=str(centroid_num),
                                                                 xy=(centroid[0] + pad_x, centroid[1] - 4 * pad_y)))
        centroid_num += 1
    current_plot_container.current_annotations.append(new_ann)


def set_pickability_of_all_centroid_containing_datapoints(current_plot_container, enable_pickability):
    """
    Setzt die Auswählbarkeit aller Punkte, die unter den aktuell vorhandenen Cluster-Zentren der Anzeigefläche liegen.
    Diese Methode soll nur außerhalb des Trainings aufgerufen werden, wenn sichergestellt ist, dass unter jedem
    Cluster-Zentrum ein Datenpunkt liegt. Die Cluster-Zentren müssen zum Zeitpunkt des Setztens der Auswählbarkeit
    der Datenpunkt in dict_dataset des current_plot_containers vorhanden sein.
    :param current_plot_container: aktueller Plot_Container
    :param enable_pickability: True, falls der Punkt auswählbar gesetzt werden soll; False, sonst
    """
    for centroid in current_plot_container.dict_centroids:
        set_pickability_of_datapoint(current_plot_container=current_plot_container, centroid_as_tuple=centroid,
                                     enable_pickability=enable_pickability)


def set_pickability_of_datapoint(current_plot_container, centroid_as_tuple, enable_pickability):
    """
    Setzt das Line2D-Objekt des Datenpunkts (x_coor, y_coor) auswählbar, falls enable_pickability True ist. 
    Andernfalls wird der Punkt auf nicht auswählbar gesetzt. Es muss sichergestellt sein, dass unter dem Centroid ein
    Datenpunkt liegt.
    :param current_plot_container: aktueller Plot_Container
    :param centroid_as_tuple: (x,y) Cluster-Zentrum in Form eines Tupels
    :param enable_pickability: True, falls der Punkt auswählbar gesetzt werden soll; False, sonst
    """
    if enable_pickability:
        current_plot_container.dict_dataset[centroid_as_tuple].set_picker(3)
    else:
        current_plot_container.dict_dataset[centroid_as_tuple].set_picker(0)


def set_pickability_of_all_centroids(current_plot_container, enable_pickability):
    """
    Setzt die Auswählbarkeit aller Cluster-Zentren der Anzeigefläche.
    :param current_plot_container: aktueller Plot-Container
    :param enable_pickability: True, falls der Punkt auswählbar gesetzt werden soll; False, sonst
    """
    if enable_pickability:
        pick_radius = 3
    else:
        pick_radius = 0

    for d_cent in current_plot_container.dict_centroids:
        current_plot_container.dict_centroids[d_cent].set_picker(pick_radius)


def draw_distances_parameter_elbow_analysis(current_plot_container, list_final_cluster_sets):
    """
    Erstellt die Elemente (Line2D), welche für die Darstellung des Distanzen-Plots der Ellbogen-Analyse benötigt
    werden und speichert diese in elbow_analysis_distances_objects des Plot-Containers ab. Für jeden Wert von k
    werden Elemente für die berechneten, bezüglich k finalen Cluster-Zentren der Ellbogen-Analyse, deren Annotationen
    und die Distanzlinien der einzelnen Datenpunkte zu den eigenen Cluster-Zentren erstellt.
    :param current_plot_container: aktueller Plot_Container
    :param list_final_cluster_sets: Liste von Dictionaries, welches jeweils die Aufteilung der Datenpunkte auf die
                           jeweiligen finalen Cluster-Zentren enthalten. Für jeden Wert von k ist ein Dictionary enthalten.
                           Aufbau der Dictionaries: keys => finaleCluster-Zentren, welche für k und die Datenpunkte
                           bestimmt wurden; values => Liste mit Tupeln, welche die Datenpunkte repräsentieren, die zum
                           jeweiligen finalen Cluster-Zentrum gehören.
    """
    xl = current_plot_container.plot_axes.get_xlim()
    pad_x = abs(xl[1] - xl[0]) / 100
    yl = current_plot_container.plot_axes.get_ylim()
    pad_y = abs(yl[1] - yl[0]) / 100
    for split_set in list_final_cluster_sets:
        # Linien und Zentren in Farbe des Zentrums zeichnen
        list_lines = []
        list_centroids = []
        list_anns = []
        index_nr = 1
        for centroid, col in zip(split_set, COLOR_LIST):
            for point in split_set[centroid]:
                list_lines.append(
                    current_plot_container.plot_axes.plot([point[0], centroid[0]], [point[1], centroid[1]],
                                                          color=col, alpha=0.25, zorder=1, visible=False)[0])

            list_centroids.append(
                current_plot_container.plot_axes.plot(centroid[0], centroid[1], marker='X', markersize=8,
                                                      color=col, picker=0, visible=False, zorder=4)[0])
            # Annotationen für die Zentren zeichnen
            # Hinzufügen der Nummer des Cluster-Zentrums als Annotation im Plot
            list_anns.append(current_plot_container.plot_axes.annotate(
                text=str(index_nr), xy=(centroid[0] + pad_x, centroid[1] - 4 * pad_y), visible=False, zorder=4))
            index_nr += 1

        current_plot_container.elbow_analysis_distances_objects.append((list_lines, list_centroids, list_anns))


def update_distances_parameter_elbow_analysis(current_plot_container, index_selected_value_k, final_cluster_set):
    """
    Blendet die Elemente des Distanzen-Plots für die Ellbogen-Analyse für das gewählte k ein und die Elemente für
    alle anderen Werte von k aus. Des Weiteren wird die Färbung der Datenpunkte an die Situation angepasst.
    :param current_plot_container: aktueller Plot_Container
    :param index_selected_value_k: Index, an dem die Elemente für die Darstellung des Distanzen-Plots der Ellbogen-
                                   Analyse im entsprechenden Attribut elbow_analysis_distances_objects gespeichert sind.
                                   In der Regel ist dieser um 1 kleiner als das ausgewählte k, da die Indizierung der
                                   Liste bei 0 beginnt.
    :param final_cluster_set:  Dictionary: key => finales Cluster-Zentrum; value=> Liste von Tupeln, die den
                               aufgeteilten Datensatz enthält.
    """
    # Datenpunkte passend einfärben (update_dataset nutzt nur die Reihenfolge der Cluster im Dict, nicht deren Werte)
    update_dataset(current_plot_container=current_plot_container, split_dataset_centroids=final_cluster_set)
    # Einblenden der Elemente des Distanzen-Plots für das ausgewählte k. Ausblenden der Elemente für alle anderen Werte
    # von k
    for i in range(len(current_plot_container.elbow_analysis_distances_objects)):
        lines, centroids, anns = current_plot_container.elbow_analysis_distances_objects[i]
        if i == index_selected_value_k:
            visibility = True
        else:
            visibility = False
        # Ein- bzw. Ausblenden der Elemente je nach vorliegendem Index.
        for line in lines:
            line.set(visible=visibility)
        for centroid, ann in zip(centroids, anns):
            centroid.set(visible=visibility)
            ann.set_visible(visibility)


def remove_distances_parameter_elbow_analysis(current_plot_container):
    """
    Entfernt die Elemente aus der grafischen Anzeige des Modells, welche für die Darstellung des Distanzen-Plots der
    Ellbogen-Analyse benötigt werden und anschließend das zwischenspeichernde Attribut geleert.
    :param current_plot_container: aktueller Plot_Container
    """
    for d_set in current_plot_container.elbow_analysis_distances_objects:
        for d_line in d_set[0]:
            d_line.remove()
        for d_cent in d_set[1]:
            d_cent.remove()
        for d_ann in d_set[2]:
            d_ann.remove()
    current_plot_container.elbow_analysis_distances_objects.clear()


def update_plot_model_training_parameter_analysis_distances(current_plot_container, activate_parameter_analysis):
    """
    Bereitet die Darstellung der Datenpunkte/des Modells für den jeweiligen Modus vor.
    Beim Aktivieren der Parameter-Analyse werden ggf. vorhandene Cluster-Zentren des Trainings-Modus ausgeblendet.
    Beim Deaktivieren werden die ggf. aus den Distanzen-Plots zusätzlich vorhandenen Elemente entfernt, die Punkt-
    färbung wird auf die Standardfarbe zurückgesetzt und die aus der Trainingsinitialisierung ggf. vorhandenen
    Cluster-Zentren werden wieder eingeblendet.
    :param current_plot_container: aktueller Plot_Container
    :param activate_parameter_analysis: True, wenn die Parameter-Analyse aktiviert wird. False, sonst
    """
    # Ausblenden der ggf. vorhandenen ausgewählten initialen Cluster-Zentren
    if activate_parameter_analysis:
        if current_plot_container.dict_centroids:
            for centroid, ann in zip(current_plot_container.dict_centroids,
                                     current_plot_container.current_annotations[0]):
                current_plot_container.dict_centroids[centroid].set(visible=False)
                ann.set_visible(False)

    # Zurücksetzen der Farbe der Punkte und vorhandener Elemente im Distanzen-Plot
    else:
        remove_distances_parameter_elbow_analysis(current_plot_container=current_plot_container)
        remove_distances_parameter_silhouette_analysis(current_plot_container=current_plot_container)
        update_dataset(current_plot_container=current_plot_container)
        if current_plot_container.dict_centroids:
            for centroid, ann in zip(current_plot_container.dict_centroids,
                                     current_plot_container.current_annotations[0]):
                current_plot_container.dict_centroids[centroid].set(visible=True)
                ann.set_visible(True)


def draw_distances_parameter_silhouette_analysis(current_plot_container, final_clusters_information_set):
    """
    Erstellt die Elemente (Line2D), welche für die Darstellung des Distanzen-Plots der Silhouetten-Analyse benötigt
    werden und speichert diese in silhouette_analysis_distances_objects des Plot-Containers ab.
    Es werden Elemente für die berechneten finalen Cluster-Zentren der aktuellen Silhouetten-Analyse, die Annotationen,
    die Hervorhebungen bei geklicktem Punkt und die Distanzlinien der einzelnen Datenpunkte für den eigenen Cluster und
    den am nächsten liegenden Cluster erstellt.
    :param current_plot_container: aktueller Plot_Container
    :param final_clusters_information_set: Dictionary mit keys=> Tupel, welches das finale Cluster-Zentrum repräsentiert
                                             values=> Liste an 3-Tupeln der Form (Datenpunkt als Tupel (x,y),
                                             Silhouette des Datenpunkts, Tupel, welches des Zentrums des am nächsten
                                             liegenden Clusters repräsentiert)
    """
    # Extrahiert aus dem übergebenen Dictionary nur die Aufteilung der Datenpunkte, damit diese passend eingefärbt
    # werden können
    split_dataset = {}
    dict_highlight_datapoints = {}
    for d_cent in final_clusters_information_set:
        split_dataset[d_cent] = list(map(lambda x: x[0], final_clusters_information_set[d_cent]))
        # Erstellt die Hervorhebung für die Datenpunkte, wenn diese geklickt werden. (Zu Beginn ausgeblendet)
        for d_point in split_dataset[d_cent]:
            dict_highlight_datapoints[d_point] = \
                current_plot_container.plot_axes.plot(d_point[0], d_point[1], marker='o', markersize=10,
                                                      color='yellow', alpha=0.5, markeredgecolor='black',
                                                      picker=0, zorder=2, visible=False)[0]
    # split_dataset enthält die Datenaufteilung für die finalen Cluster-Zentren, d.h. die keys können ggf. genutzt
    # werden
    update_dataset(current_plot_container=current_plot_container, split_dataset_centroids=split_dataset)

    # Berechnungen für die Positionierung der Annotationen
    xl = current_plot_container.plot_axes.get_xlim()
    pad_x = abs(xl[1] - xl[0]) / 100
    yl = current_plot_container.plot_axes.get_ylim()
    pad_y = abs(yl[1] - yl[0]) / 100

    list_centroids = []
    list_anns = []
    dict_lines = {}
    index_nr = 1
    # Bezüglich der Färbung, wird ausgenutzt, dass die Reihenfolge der keys eines Dicts erhalten bleibt
    for centroid, col in zip(final_clusters_information_set, COLOR_LIST):
        # Hinzufügen der final gefundenen Cluster-Zentren. Diese sind ab Beginn eingeblendet
        # Da es sich um finale Cluster handelt, kann mit den keys gearbeitet werden
        list_centroids.append(current_plot_container.plot_axes.plot(centroid[0], centroid[1], marker='X', markersize=8,
                                                                    color=col, picker=0, visible=True, alpha=0.75,
                                                                    zorder=4)[0])
        # Annotationen für die Zentren zeichnen
        # Hinzufügen der Nummer des Cluster-Zentrums als Annotation im Plot
        list_anns.append(current_plot_container.plot_axes.annotate(text=str(index_nr),
                                                                   xy=(centroid[0] + pad_x, centroid[1] - 4 * pad_y),
                                                                   visible=True, zorder=4))
        index_nr += 1
        # Hinzufügen der Linien
        # (Linien zu den Datenpunkten des eigenen Clusters, Linien zu den Datenpunkten des am nächsten liegenden
        # Clusters)
        for datapoint in final_clusters_information_set[centroid]:
            # Dies tritt nur in dem Sonderfall auf, in dem der Cluster nur aus einem Element besteht. In diesem Fall
            # ist die Silhouette 0 und es gibt keinen am nächsten liegenden besten Cluster per Definition
            if datapoint[2] is None:
                dict_lines[datapoint[0]] = ([], [])
            # Andernfalls können die Verbindungslinien zum eigenen und zu den Elementen des am nächsten liegenden
            # Clusters berechnet werden
            else:
                dict_lines[datapoint[0]] = (
                    [current_plot_container.plot_axes.plot([datapoint[0][0], other_point_own[0][0]],
                                                           [datapoint[0][1], other_point_own[0][1]],
                                                           color="blue", alpha=0.25, zorder=1, visible=False)[
                         0] for other_point_own in final_clusters_information_set[centroid] if
                     datapoint != other_point_own],
                    [current_plot_container.plot_axes.plot([datapoint[0][0], other_point_next[0][0]],
                                                           [datapoint[0][1], other_point_next[0][1]],
                                                           color="red", alpha=0.25, zorder=1,
                                                           visible=False)[
                         0] for other_point_next in final_clusters_information_set[datapoint[2]]]
                )
    current_plot_container.silhouette_analysis_distances_objects = [list_centroids, list_anns, dict_lines,
                                                                    dict_highlight_datapoints]


def remove_distances_parameter_silhouette_analysis(current_plot_container):
    """
    Entfernt die Elemente aus der grafischen Anzeige des Modells, welche für die Darstellung des Distanzenplots der
    Silhouetten-Analyse benötigt werden und leert das zwischenspeichernde Attribut. Falls keine Elemente in dem
    entsprechenden Attribut silhouette_analysis_distances_objects des Plot-Containers sind, werden keine Elemente
    entfernt. In jedem Fall wird der zwischengespeicherte, in der Silhouetten-Analyse zuletzt geklickte Punkt auf ()
    gesetzt.
    :param current_plot_container: aktueller Plot_Container
    """
    # Falls Elemente für die Darstellung des Distanzenplots der Silhouettenanalyse vorhanden sind
    if current_plot_container.silhouette_analysis_distances_objects:
        for d_cent in current_plot_container.silhouette_analysis_distances_objects[0]:
            d_cent.remove()
        for d_ann in current_plot_container.silhouette_analysis_distances_objects[1]:
            d_ann.remove()
        for d_key in current_plot_container.silhouette_analysis_distances_objects[2]:
            for d_line_own in current_plot_container.silhouette_analysis_distances_objects[2][d_key][0]:
                d_line_own.remove()
            for d_line_next in current_plot_container.silhouette_analysis_distances_objects[2][d_key][1]:
                d_line_next.remove()
        for e_val in current_plot_container.silhouette_analysis_distances_objects[3].values():
            e_val.remove()
        current_plot_container.silhouette_analysis_distances_objects.clear()
    current_plot_container.silhouette_analysis_last_clicked = ()


def set_layer_datapoints(current_plot_container, in_front=False):
    """
    Setzt die Anzeigeebene aller vorhandenen, im Plot-Container gespeicherten Datenpunkte in Abhängigkeit von dem
    übergebenen Wahrheitswert.
    :param current_plot_container: aktueller Plot_Container
    :param in_front: True, wenn die Datenpunkte in den Vordergrund verschoben werden soll; False, sonst (default)
    """
    if in_front:
        layer = 5
    else:
        layer = 3
    for key_point in current_plot_container.dict_dataset:
        current_plot_container.dict_dataset[key_point].set(zorder=layer)


def update_distances_parameter_silhouette_analysis(current_plot_container, x_coord_clicked, y_coord_clicked):
    """
    Blendet die Distanzlinien der Silhouetten-Analyse des ggf. zuletzt geklickten Datenpunkts inkl. dessen Hervorhebung
    aus und die Linien des aktuell geklickten Datenpunkts inklusive dessen Hervorhebung ein. Zusätzlich wird der
    zwischengespeicherte, zuletzt geklickte Datenpunkt aktualisiert. Es muss sichergestellt sein, dass der geklickte
    Datenpunkt in der Anzeigefläche vorhanden ist.
    :param current_plot_container: aktueller Plot_Container
    :param x_coord_clicked: x-Koordinate des geklickten Datenpunkts
    :param y_coord_clicked: y-Koordinate des geklickten Datenpunkts
    """
    # Ausblenden der Elemente für die Darstellung der letzten Auswahl
    # ggf. Behandlung, falls bisher kein Punkt ausgewählt wurde
    if current_plot_container.silhouette_analysis_last_clicked != ():
        for last_own in current_plot_container.silhouette_analysis_distances_objects[2][
            current_plot_container.silhouette_analysis_last_clicked][0]:
            last_own.set(visible=False)
        for last_next in current_plot_container.silhouette_analysis_distances_objects[2][
            current_plot_container.silhouette_analysis_last_clicked][1]:
            last_next.set(visible=False)
        current_plot_container.silhouette_analysis_distances_objects[3][
            current_plot_container.silhouette_analysis_last_clicked].set(visible=False)
    # Speichern des zuletzt geklickten Punkts
    current_plot_container.silhouette_analysis_last_clicked = (x_coord_clicked, y_coord_clicked)
    # Einblenden der Elemente für die Darstellung des aktuell ausgewählten Punkts
    for line_own in current_plot_container.silhouette_analysis_distances_objects[2][(x_coord_clicked, y_coord_clicked)][
        0]:
        line_own.set(visible=True)
    for line_next in \
            current_plot_container.silhouette_analysis_distances_objects[2][(x_coord_clicked, y_coord_clicked)][1]:
        line_next.set(visible=True)
    current_plot_container.silhouette_analysis_distances_objects[3][
        current_plot_container.silhouette_analysis_last_clicked].set(visible=True)


def update_tooltip_annotation(current_plot_container, x_coord=None, y_coord=None):
    if x_coord is not None and y_coord is not None:
        current_plot_container.tooltip_annotation.xy = (x_coord, y_coord)
        current_plot_container.tooltip_annotation.set_text("(" + str(x_coord)[:5] + ", " + str(y_coord)[:5] + ")")
        current_plot_container.tooltip_annotation.set_visible(True)
    else:
        current_plot_container.tooltip_annotation.set_visible(False)