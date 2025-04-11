from datetime import datetime

import numpy as np
from sklearn.cluster import KMeans
from sklearn.utils import shuffle

import src.Exceptions

DEFAULT_NUMBER_OF_COLOR_SAMPLES = 39200


def quantize_image_general(value_k, image_as_array):
    """
    Berechnet für das übergebene Bild das farbreduzierte Bild mit k Farben, wobei die Anzahl der Farben value_k
    entspricht. Die Farbreduktion wird mit dem k-Means-Algorithmus berechnet, welcher auf den unterschiedlichen Pixeln
    des übergebenen Bilds trainiert wird.
    :param value_k: Anzahl der Farben des farbreduzierten Bilds, Wert von k für den k-Means-Algorithmus
    :param image_as_array: Bild als dreidimensionales Array, wobei die innersten Arrays die Länge drei besitzen und
                           ein Pixel im RGB-Format darstellen.
    :exception Exceptions.NotEnoughColors: Falls im Bild weniger Farben vorhanden sind, als über den Wert value_k für
                                           die Reduktion ausgewählt wurden
    :return: Farbreduziertes Bild als zweidimensionales Array. Jede Zeile repräsentiert ein Pixel und besteht aus einem
             Array der Länge drei, welches das Pixel im RGB-Format darstellt. Die RGB-Werte sind auf den Bereich [0...1]
             normiert.
    """
    # Auslesen der Abmessungen des als Array dargestellten Bilds
    l, b, t = image_as_array.shape
    # Falls das Bild in RGB-Darstellung war
    assert t == 3
    # Überführt das Bild in ein 2D-Array mit je einer Zeile pro Pixel. Die Einträge der Zeile sind die
    # RGB-Werte des entsprechenden Pixels/Punkts
    image_array_2D = np.reshape(image_as_array, (l * b, t))

    # Subset für Training auswählen!NICHT VERWENDET!
    # image_array_2D_sample = shuffle(image_array_2D, random_state=0, n_samples=1_000)
    # Beim Trainieren sollen doppelte Datenpunkte vermieden werden. Diese werden hier gefiltert.
    image_array_2D_for_training = np.unique(image_array_2D, axis=0)
    # Falls im Bild weniger unterschiedliche Farben/Pixel vorhanden sind, als für den Wert k ausgewählt wurde,
    # wird die entsprechende Exception geworfen.
    number_of_unique_colors = len(image_array_2D_for_training)
    if number_of_unique_colors < value_k:
        raise src.Exceptions.NotEnoughColorsException(number_of_colors=number_of_unique_colors)

    # Initialisieren des kMeans-Objekts
    kmeans = KMeans(n_clusters=value_k)
    # Trainieren des kMeans-Objekts mit allen Daten
    kmeans.fit(X=image_array_2D)
    # Vorhersagen der Farbe für jedes Pixel mit dem trainierten kMeans-Modell, d.h. Reduzierung der Farben
    image_array_2D_quantized = kmeans.cluster_centers_[kmeans.predict(X=image_array_2D)]
    # Normierung der Einträge des farbreduzierten Bilds in den Bereich [0..1], da imshow von Matplotlib nur mit
    # floats im Bereich [0..1] oder int im Bereich [0..255] arbeiten kann. Da die Cluster-Zentren der Vorhersage aber
    # floats sind, muss hier noch normiert werden.
    return np.reshape(image_array_2D_quantized, (l, b, t)) / 255


def quantize_color_channels(value_k, colors_array, image_as_array):
    """
    Berechnet für das übergebene Bild das farbreduzierte Bild mit k Farben, wobei die Anzahl der Farben value_k
    entspricht. Die Farbreduktion wird mit dem k-Means-Algorithmus berechnet, welcher auch einer Menge an
    unterschiedlichen Farben trainiert wird, die im colors_array übergeben werden.
    :param value_k: Anzahl der Farben des farbreduzierten Bilds, Wert von k für den k-Means-Algorithmus
    :param colors_array: Array an unterschiedlichen Farben, welche für das Training des k-Means-Algorithmus verwendet
                         werden.
    :param image_as_array: Bild als dreidimensionales Array, wobei die innersten Arrays die Länge drei besitzen und
                           ein Pixel im RGB-Format darstellen.
    :exception Exceptions.NotEnoughColors: Falls im Array colors_array weniger Farben vorhanden sind, als über den Wert
                                           value_k für die Reduktion ausgewählt wurden
    :return: Farbreduziertes Bild als zweidimensionales Array. Jede Zeile repräsentiert ein Pixel und besteht aus einem
             Array der Länge drei, welches das Pixel im RGB-Format darstellt. Die RGB-Werte sind auf den Bereich [0...1]
             normiert;
             Array der Farben, welche auch mithilfe des k-Means-Algorithmus farbreduziert wurden;
             Mithilfe des k-Means-Algorithmus berechnete Cluster-Zentren/Farben, auf die reduziert wird

    """
    # Falls im Farbarray weniger unterschiedliche Farben/Pixel vorhanden sind, als für den Wert k ausgewählt wurde,
    # wird die entsprechende Exception geworfen.
    number_of_unique_colors = len(colors_array)
    if number_of_unique_colors < value_k:
        raise src.Exceptions.NotEnoughColorsException(number_of_colors=number_of_unique_colors)
    # Initialisieren des kMeans-Objekts
    kmeans = KMeans(n_clusters=value_k)
    # Trainieren des kMeans-Objekts mit den ausgewählten Color Samples
    kmeans.fit(X=colors_array)
    colors_array_quantized = kmeans.cluster_centers_[kmeans.predict(X=colors_array)]

    # Auslesen der Abmessungen des als Array dargestellten Farbpunkte
    l, b, t = image_as_array.shape
    # Falls die Farbpunkte in RGB-Darstellung war
    assert t == 3
    # Überführt das Bild in ein 2D-Array mit je einer Zeile pro Pixel. Die Einträge der Zeile sind die
    # RGB-Werte des entsprechenden Pixels/Punkts
    image_array_2D = np.reshape(image_as_array, (l * b, t))
    image_array_2D_quantized = kmeans.cluster_centers_[kmeans.predict(X=image_array_2D)]
    # Normierung der Einträge des farbreduzierten Bilds in den Bereich [0..1], da imshow von Matplotlib nur mit
    # floats im Bereich [0..1] oder int im Bereich [0..255] arbeiten kann. Da die Cluster-Zentren der Vorhersage aber
    # floats sind, muss hier noch normiert werden.
    return np.reshape(image_array_2D_quantized,(l, b, t)) / 255, colors_array_quantized, kmeans.cluster_centers_


def remove_color_channel(image_as_array, color_channels):
    """
    Entfernt aus dem übergebenen 3D-Array den übergebenen Farbkanal, d.h. alle entsprechenden Einträge des Farbkanals
    der innersten Arrays der Länge 3, welche die Pixel im RGB-Format darstellen, werden auf 0 gesetzt. Gearbeitet wird
    auf einer echten Kopie des Arrays/Bilds.
    :param image_as_array:  Bild als dreidimensionales Array, wobei die innersten Arrays die Länge drei besitzen und
                            ein Pixel im RGB-Format darstellen.
    :param color_channels: String, welcher die verbleibenden Farbkanäle benennt. Zur Auswahl stehen: "gr\u00FCn-blau",
                           rot-blau, rot-gr\u00FCn

    :return: 3D-Array, welches das Bild darstellt und aus dem der nicht gewählte Farbkanal entfernt wurde
    """
    if color_channels == "gr\u00FCn-blau":
        channel_to_remove = 0
    elif color_channels == "rot-blau":
        channel_to_remove = 1
    else:
        channel_to_remove = 2
    image_as_array_without_channel = image_as_array.copy()
    image_as_array_without_channel[:, :, channel_to_remove] = 0
    return image_as_array_without_channel


def get_color_samples_of_image(image_as_array):
    """
    Entnimmt aus einem, als 3-dimensionales Array dargestellten Bilds, eine Anzahl an zufälligen unterschiedlichen
    Farben und gibt diese Farben als 2D-Array zurück, wobei die inneren Arrays jeweils ein Pixel im RGB-Format
    darstellen.
    :param image_as_array: Bild als dreidimensionales Array, wobei die innersten Arrays die Länge drei besitzen und
                            ein Pixel im RGB-Format darstellen.
    :return: 2D-dimensionales Array an unterschiedlichen Farben aus dem übergebenen Bild. Die Anzahl der Farben ist
             durch das Minimum eines internen Parameters bzw. der Anzahl der vorhandenen unterschiedlichen Farben
             bestimmt.
    """
    l, b, t = image_as_array.shape
    image_as_array_2D = np.unique(np.reshape(image_as_array, (l * b, t)), axis=0)
    return shuffle(image_as_array_2D, random_state=0,
                   n_samples=min(DEFAULT_NUMBER_OF_COLOR_SAMPLES, len(image_as_array_2D)))
