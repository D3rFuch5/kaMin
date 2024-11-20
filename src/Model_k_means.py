import copy
import math
import random
import time
import src.Exceptions

ELBOW_CALCULATION_WAY_INERTIA = "Inertia"


def euclidean_distance(point1, point2):
    """
    Berechnet für die zwei übergebenen Punkte den euklidischen Abstand
    :param point1: zweidimensionaler Punkt als Tupel oder Liste
    :param point2: zweidimensionaler Punkt als Tupel oder Liste
    :return: Euklidischer Abstand von point1 und point2.
    """
    square_sum = 0
    for p1, p2 in zip(point1, point2):
        square_sum += (p1 - p2) ** 2
    return math.sqrt(square_sum)


def squared_euclidean_distance(point1, point2):
    """
    Berechnet für die zwei übergebenen Punkte den quadratischen euklidischen Abstand
    :param point1: zweidimensionaler Punkt als Tupel oder Liste
    :param point2: zweidimensionaler Punkt als Tupel oder Liste
    :return: Quadratischer euklidischer Abstand von point1 und point2.
    """
    square_sum = 0
    for p1, p2 in zip(point1, point2):
        square_sum += (p1 - p2) ** 2
    return square_sum


def get_k_random_data_objects(parameter_k, dataset):
    """
    Liefert eine Liste von k unterschiedlichen Elementen aus dem Datensatz dataset. Es muss sichergestellt sein, dass
    ausreichend Elemente in dataset vorhanden sind.
    :param parameter_k: Anzahl, wie viele Datenpunkte ausgewählt werden sollen.
    :param dataset: Datensatz aus dem die Punkte ausgewählt werden.
    :return: Liste von k unterschiedlichen, zufälligen Datenpunkten
    """
    return random.sample(population=dataset, k=parameter_k)


def calculate_data_objects_for_centroids(distance_function, current_centroids, dataset):
    """
    Teilt den Datensatz auf die aktuellen Cluster-Zentren auf. Jeder Datenpunkt wird dabei immer dem am nächsten
    liegenden Cluster-Zentrum zugeordnet.
    :param distance_function: Funktion, welche als Metrik für die Abstandsberechnung verwendet wird
    :param current_centroids: Liste der Cluster-Zentren, wobei ein Cluster-Zentrum ein Tupel der Form (x_1,y_1) ist
    :param dataset: Datensatz in Form einer Liste von Tupeln, welcher auf die Cluster-Zentren aufgeteilt werden soll.
    :return:  Dictionary: key => Cluster-Zentrum als Tupel;
                          value => Liste von Tupeln, die den zum Cluster-Zentrum gehörenden Teildatensatz enthält.
    """
    current_smallest_centroid_distance = -1
    # Initialisieren des Dictionaries, welches die Daten aufgeteilt nach nächstem Cluster-Zentrum speichert
    data_split_by_centroid = {centroid: [] for centroid in current_centroids}

    # Aufteilen der Daten auf die jeweils am nächsten liegenden Centroids
    for data in dataset:
        for centroid in current_centroids:
            distance_data_to_centroid = distance_function(point1=centroid, point2=data)
            # Jeweils erster Durchlauf pro Datenpunkt
            # Initialisierung der lokalen Variablen
            if current_smallest_centroid_distance == -1:
                current_nearest_centroid = centroid
                current_smallest_centroid_distance = distance_data_to_centroid
            elif distance_data_to_centroid < current_smallest_centroid_distance:
                current_smallest_centroid_distance = distance_data_to_centroid
                current_nearest_centroid = centroid
        # Zurücksetzen des Zwischenspeichers für den berechneten Abstand
        current_smallest_centroid_distance = -1
        # Hinzufügen des Datenpunkts zur Liste an der Stelle des Keys des am nächsten liegenden Cluster-Zentrums
        data_split_by_centroid[current_nearest_centroid].append(data)
    return data_split_by_centroid


def calculate_centroids(dataset_split_by_centroid):
    """
    Berechnet aus dem für die aktuellen Cluster-Zentren aufgeteilten Datensatz die neuen Cluster-Zentren.
    :param dataset_split_by_centroid:  Dictionary: key => Cluster-Zentrum als Tupel;
                                                   value => Liste von Tupeln, die den zum Cluster-Zentrum gehörenden
                                                            Teildatensatz enthält.
    :return: Liste mit den aktualisierten Cluster-Zentren als Tupel.
    """
    # Erstellen einer Liste für die neu berechneten Centroids
    calculated_centroids = []

    # Berechnung der neuen Centroids
    for centroid_key in dataset_split_by_centroid:
        centroid_coord_x = 0
        centroid_coord_y = 0
        number_of_elements_for_centroid = len(dataset_split_by_centroid[centroid_key])
        # Leerer Cluster
        # Momentan wird das Cluster-Zentrum einfach beibehalten
        if number_of_elements_for_centroid == 0:
            centroid_coord_x = centroid_key[0]
            centroid_coord_y = centroid_key[1]
            print("INFO: Leerer Cluster für ", centroid_key)
        else:
            for point in dataset_split_by_centroid[centroid_key]:
                centroid_coord_x += point[0]
                centroid_coord_y += point[1]
            centroid_coord_x = centroid_coord_x / number_of_elements_for_centroid
            centroid_coord_y = centroid_coord_y / number_of_elements_for_centroid
        # Hinzufügen des neuen Cluster-Zentrums an der Stelle des alten Cluster-Zentrums
        calculated_centroids.append((centroid_coord_x, centroid_coord_y))
    return calculated_centroids


def change_to_clusters(dataset_split_old, dataset_split_new):
    # Im ersten Durchlauf gab es noch keine Aufteilung der Datenpunkte aus dem vorherigen Durchlauf, d.h.
    # dataset_split_old = {}. Ist nun dataset_split_new auch {} hat es logischerweise keine Änderung gegeben, da es
    # keine Aufteilung gab. (eig. nicht auftretender Fehlerfall)
    # Falls dataset_split_new != {} ist, kat mit Sicherheit eine Änderung stattgefunden, da nun eine Aufteilung
    # existiert
    if dataset_split_old == {}:
        if dataset_split_new == {}:
            return False
        else:
            return True
    else:
        # Vergleich paarweise die Listen der Elemente an den Stellen der beiden Dictionaries in der Reihenfolge des
        # Vorkommens (Dictionary erhält in Reihenfolge des Einfügens).
        # Sobald ein Element in den Listen gefunden wird, dass nicht übereinstimmt, wird True zurückgegeben, d.h. es
        # wurde eine Änderung gefunden.
        for key_old, key_new in zip(dataset_split_old, dataset_split_new):
            for d_elm_old, d_elm_new in zip(dataset_split_old[key_old], dataset_split_new[key_new]):
                if d_elm_old != d_elm_new:
                    return True
        return False


def change_to_centroids(centroids_old, centroids_new):
    """
    Prüft, ob eine Änderung in den Cluster-Zentren stattgefunden hat. Die Keys der Cluster-Zentren müssen dabei vor und
    nach der Aktualisierung identisch sein. Identisch heißt dabei, dass die Unterschiede der neuen Cluster-Zentren zu
    den alten Cluster-Zentren jeweils kleiner als ein akzeptabler Differenzwert ist. Dieser ist auf 0.1 festgelegt.
    :param centroids_old: Liste der Cluster-Zentren als Tupel vor der Aktualisierung
    :param centroids_new: Liste der Cluster-Zentren als Tupel nach der Aktualisierung
    :return: True, falls sich mindestens ein Cluster-Zentrum geändert hat. False, sonst.
    """
    for a, b in zip(centroids_old, centroids_new):
        if not points_equal(point_A=a, point_B=b, distance_function=squared_euclidean_distance,
                            acceptable_distance=0.1):
            return True
    return False


def points_equal(point_A, point_B, distance_function, acceptable_distance):
    """
    Prüft, ob zwei Punkte weniger als eine akzeptable Distanz bezüglich einer Distanzfunktion auseinander liegen.
    :param point_A: Punkt als Tupel der Form (x_1, y_1)
    :param point_B: Punkt als Tupel der Form (x_2, y_2)
    :param distance_function: Metrik-Funktion für die Abstandsberechnung
    :param acceptable_distance: Wert für die für Gleichheit akzeptable Differenz
    :return: True, wenn der Abstand der Punkte bezüglich der Distanzfunktion kleiner oder gleich der akzeptablen
             Differenz ist; False, sonst
    """
    return distance_function(point_A, point_B) <= acceptable_distance


def calculate_final_clusters(dataset, initial_centroids):
    """
    Berechnet für den Datensatz dataset ausgehend von den initialen Cluster-Zentren initial_centroids mithilfe des
    k-means-Algorithmus die finalen Cluster-Zentren zur Einteilung des Datensatzes. Da es sich um die FINALEN
    Cluster handelt, sind haben sind die Keys des Dicts nun auch die Cluster-Zentren, da im Überprüfungsfall keine
    Änderungen an den Zentren mehr stattfinden.
    :param dataset: Liste von Tupeln, welche die Datenpunkte darstellen
    :param initial_centroids: Liste von Tupeln, welche die initialen Cluster-Zentren darstellen
    :return: Dictionary: key => finales Cluster-Zentrum als Tupel;
                         value => Liste von Tupeln, die den zum Cluster-Zentrum gehörenden Teildatensatz enthält.
    """
    clusters_changed = True
    current_centroids = initial_centroids
    clusters_previous_centroids = {}
    clusters_current_centroids = {}
    # Solange Änderungen an den Clustern stattgefunden haben, wird weiter gerechnet. Es findet mindestens ein
    # Durchgang statt um zu überprüfen, ob die initialen Cluster bereits die finalen Cluster sind.
    while clusters_changed:
        # Cluster des letzten Durchlaufs sichern
        clusters_previous_centroids = copy.deepcopy(clusters_current_centroids)
        # Aufteilung der Daten für die aktuell vorliegenden Cluster-Zentren
        clusters_current_centroids = calculate_data_objects_for_centroids(
            distance_function=squared_euclidean_distance, current_centroids=current_centroids, dataset=dataset)
        #centroids_old = current_centroids
        # Prüfen, ob sich beim Neuaufteilen der Daten auf die Cluster-Zentren eine Änderung ergab
        clusters_changed = change_to_clusters(dataset_split_old=clusters_previous_centroids, dataset_split_new=clusters_current_centroids)
        # Hat sich eine Änderung ergeben, dann Neuberechnung der Cluster-Zentren
        if clusters_changed:
            current_centroids = calculate_centroids(dataset_split_by_centroid=clusters_current_centroids)
        # Hat sich keine Änderung mehr ergeben, sind die Cluster-Zentren vor der Aktualisierung identisch mit denen
        # die man nun erhalten würde (keine Änderung an der Aufteilung)
        #clusters_changed = change_to_centroids(centroids_old=centroids_old, centroids_new=current_centroids)
    return clusters_current_centroids


def calculate_inertia(FINAL_CLUSTERS_data_split):
    """
    Berechnet die Inertia (Trägheit) für die übergebenen finalen Cluster-Zentren und zugehörigen Teildatensätze
    :param FINAL_CLUSTERS_data_split: Dictionary: key => finales Cluster-Zentrum als Tupel;
                                                   value => Liste von Tupeln, die den zum Cluster-Zentrum gehörenden
                                                            Teildatensatz darstellt.
    :return: Inertia-Wert für die übergebenen Cluster-Zentren und deren zugeordnete Teildatensätze.
    """
    within_clusters_squared_sum = 0
    for centroid in FINAL_CLUSTERS_data_split:
        for d_elm in FINAL_CLUSTERS_data_split[centroid]:
            within_clusters_squared_sum += squared_euclidean_distance(point1=centroid, point2=d_elm)
    return within_clusters_squared_sum


def elbow_analysis(dataset, max_value_of_k):
    """
    Berechnet jeweils für k = 1,..., max_value_of_k und zufällig, aus dataset ausgewählte, initiale Cluster-Zentren
    mithilfe des k-Means-Algorithmus die zugehörigen finalen Cluster-Zentren und die zugehörige Aufteilung der
    Datenpunkte auf die bestimmten finalen Cluster-Zentren. Dafür werden dann die Inertia-Werte für den Ellbogengraph
    berechnet.
    WICHTIG: Voraussetzung ist, dass für jeden Wert von k eine Aufteilung gefunden werden kann, sodass KEIN Cluster
             leer ist.
    :param dataset: Liste an Tupeln, welche die aktuellen Datenpunkte repräsentieren
    :param max_value_of_k: Grenze bis zu der Parameter k laufen soll.
    :exception src.Exceptions.CalculationTooLong: Wird geworfen, falls die Suche nach den nicht-leeren, finalen Cluster-
                                                  Zentren mehr als 2 Minuten dauert.
    :return: Liste der Inertia-Werte für k = 1 bis max_value_of_k;
             Liste an Dictionaries, welche an der k-ten Stelle ein Dictionary (key=> finales Zentrum als Tupel,
             values=Liste an Tupeln der Datenpunkte zu den jeweiligen Zentren) mit den finalen Zentren und den zugehörig
             aufgeteilten Datensatz auf die Zentren enthält.
    """
    time_start = time.time()
    # Liste an Dictionaries, welche an der k-ten Stelle ein Dictionary (key => finale Zentren als Tupel, value = Liste
    # Tupeln der Datenpunkte zu den jeweiligen Zentren) mit den finalen Zentren und den zugehörig aufgeteilten Datensatz
    # auf die Zentren enthält. Für die Berechnung des dicts an dieser Stelle wurde der Parameterwert k verwendet.
    # (wg. Indexbeginn bei 0 in der Liste)
    list_final_clusters_dataset_split_dicts = []
    # Sicherstellung, dass keine leeren Cluster in den finalen Clustern vorhanden sind
    while True:
        # Bestimmen von k zufälligen Datenpunkten, welche als initial Cluster-Zentren verwendet werden
        random_initial_centroids = get_k_random_data_objects(parameter_k=max_value_of_k, dataset=dataset)
        empty_cluster = False
        for i in range(1, max_value_of_k + 1):
            # Berechnung der finalen Cluster-Zentren mithilfe des k-Means-Algorithmus und der Aufteilung des
            # Datensatzes in Teildatensätze für die gefundenen Cluster-Zentren
            final_clusters_dataset_split = calculate_final_clusters(dataset=dataset,
                                                                  initial_centroids=random_initial_centroids[:i])
            # Prüfen, ob leere Cluster vorhanden
            for centroid in final_clusters_dataset_split:
                if len(final_clusters_dataset_split[centroid]) == 0:
                    empty_cluster = True
                    list_final_clusters_dataset_split_dicts.clear()
                    break
            if not empty_cluster:
                list_final_clusters_dataset_split_dicts.append(final_clusters_dataset_split)
            else:
                break
        # Es wurden für alle Werte von k keine leeren Cluster in den jeweiligen finalen Cluster-Zentren gefunden.
        # Die gefundenen Cluster-Zentren können also sämtlich verwendet werden.
        if not empty_cluster:
            break
        # Falls die Berechnung länger als 2 Minuten dauert, wird eine Exception geworfen
        if time.time() - time_start > 120:
            raise src.Exceptions.CalculationTooLong
    return [calculate_inertia(FINAL_CLUSTERS_data_split=split_set) for split_set in
            list_final_clusters_dataset_split_dicts], list_final_clusters_dataset_split_dicts


def calculate_mean_distance(datapoint_from, dataset_to):
    """
    Berechnet den mittleren Abstand ausgehend vom Datenpunkt datapoint_from zu allen Datenpunkten aus dataset_to
    :param datapoint_from: Punkt in Listen oder Tupelform, von dem aus die Abstände bestimmt werden sollen
    :param dataset_to: Liste von Punkten in Listen oder Tupelform zu denen der Abstand bestimmt werden soll
    :return: Mittlerer Abstand des Datenpunkts zu allen Datenpunkten des Datasets
    """
    current_sum = 0
    for point in dataset_to:
        current_sum += squared_euclidean_distance(point1=datapoint_from, point2=point)
    return current_sum / len(dataset_to)


def calculate_silhouette_scores_dataset(value_k, dataset):
    """
    Berechnet die Silhouetten für die Datenpunkte des aktuellen Datensatzes.
    :param value_k: Wert k, welcher im k-Means-Algorithmus zur Bestimmung der Cluster-Zentren verwendet wird. Es ergeben
                    sich somit k Cluster
    :param dataset: Liste von Tupeln, welche die Datenpunkte darstellen
    :exception src.Exceptions.CalculationTooLong: Wird geworfen, falls die Suche nach den nicht-leeren, finalen Cluster-
                                                  Zentren mehr als 2 Minuten dauert.
    :return: Dictionary mit keys=> Tupel, welches das finale Cluster-Zentrum repräsentiert;
                            values=> Liste an 3-Tupeln der Form (Datenpunkt als Tupel (x,y);
                                     Silhouette des Datenpunkts; Tupel, welches das am nächsten liegende
                                     finalen Cluster-Zentrum repräsentiert),
            Dictionary mit keys => Tupel, welche den jeweiligen Datenpunkt repräsentiert
                           values => Tupel (distA, distB) für den jeweiligen Datenpunkt
    """
    time_start = time.time()
    # Sicherstellung, dass keine leeren Cluster in den finalen Clustern vorhanden sind
    while True:
        # Bestimmen von k zufälligen Datenpunkten, welche als initial Cluster-Zentren verwendet werden
        random_initial_centroids = get_k_random_data_objects(parameter_k=value_k, dataset=dataset)
        # Berechnung der finalen Cluster-Zentren mithilfe des k-Means-Algorithmus und der Aufteilung des Datensatzes in
        # Teildatensätze für die gefundenen Cluster-Zentren
        empty_clusters = False
        final_clusters_dataset_split = calculate_final_clusters(dataset=dataset,
                                                              initial_centroids=random_initial_centroids)
        # Prüfen, ob leere Cluster vorhanden
        for centroid in final_clusters_dataset_split:
            if len(final_clusters_dataset_split[centroid]) == 0:
                empty_clusters = True
                break
        # Beenden der while-Schleife, welche so lange läuft, bis sie ausschließlich nicht-leere Cluster gefunden hat
        if not empty_clusters:
            break
        # Falls die Berechnung länger als 2 Minuten dauert, wird eine Exception geworfen
        if time.time() - time_start > 120:
            raise src.Exceptions.CalculationTooLong

    # Berechnung der Silhouetten für die einzelnen Datenpunkte
    dict_silhouettes_for_cluster_sets = {}
    dict_distances_for_datapoints = {}
    for centroid in final_clusters_dataset_split:
        silhouette_scores_for_cluster = [] 
        num_dataset = len(final_clusters_dataset_split[centroid])
        # Falls im aktellen Cluster nur ein Element ist, ist die Silhouette Null
        if num_dataset == 1:
            silhouette_scores_for_cluster.append((final_clusters_dataset_split[centroid][0], 0, None, (0, 0)))
            dict_distances_for_datapoints[final_clusters_dataset_split[centroid][0]] = (0, 0)
        # Andernfalls muss der Wert der Silhouette berechnet werden
        else:
            # Für jeden Datenpunkt des Teildatensatzes des aktuellen Clusters wird der Mittelwert der Abstände zu den
            # anderen Datenpunkten des eigenen Clusters berechnet ==> distA
            # Des Weiteren wird der Mittelwert der Abstände zu den Datenpunkten des dem aktuell betrachteten Datenpunkts
            # am nächsten liegenden Cluster berechnet ==> distB
            for i_o in range(num_dataset):
                distA = 0
                for j_o in range(num_dataset):
                    if i_o != j_o:
                        distA += squared_euclidean_distance(point1=final_clusters_dataset_split[centroid][i_o],
                                                            point2=final_clusters_dataset_split[centroid][j_o])
                distA = distA / (num_dataset - 1)
                # Berechnet den mittleren Abstand distB vom aktuellen Datenpunkt zu allen Datenpunkten des am nächsten
                # liegenden Clusters nearest_cluster.
                # Dafür werden vom aktuellen Datenpunkt dataset_split_by_centroids[centroid][i_o] die mittleren
                # Abstände zu jeweils allen Datenpunkten der anderen Cluster (mittlerer Gesamtabstand je Cluster)
                # berechnet. Diese werden zusammen mit dem zugehörigen Cluster-Zentrum als Tupel in der Liste
                # gespeichert. Im Anschluss wird das Minimum der Listenelemente bezüglich des ersten Elements der Tupel,
                # d.h. bzgl. der distBs, bestimmt.
                distB, nearest_cluster = min(
                    [(calculate_mean_distance(datapoint_from=final_clusters_dataset_split[centroid][i_o],
                                              dataset_to=final_clusters_dataset_split[centroid_other]), centroid_other)
                     for
                     centroid_other in final_clusters_dataset_split if centroid_other != centroid], key=lambda x: x[0])
                silhouette_scores_for_cluster.append(
                    (final_clusters_dataset_split[centroid][i_o], (distB - distA) / max(distB, distA), nearest_cluster))
                dict_distances_for_datapoints[final_clusters_dataset_split[centroid][i_o]] = (distA, distB)
        dict_silhouettes_for_cluster_sets[centroid] = silhouette_scores_for_cluster
    return dict_silhouettes_for_cluster_sets, dict_distances_for_datapoints
