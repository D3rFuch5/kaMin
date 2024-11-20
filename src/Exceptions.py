class EmptyFileException(Exception):
    """
    Klasse setzt die Exception um, welche geworfen wird, wenn die ausgewählte CSV-Datei keine Einträge enthält.
    """
    pass


class UnequalSizeException(Exception):
    """
    Klasse setzt die Exception um, welche geworfen wird, wenn der in der Treeview anzuzeigende Datensatz zu viele oder
    zu wenig Spalten besitzt.
    """
    pass


class WrongDimensionException(Exception):
    """
    Klasse setzt die Exception um, welche geworfen wird, wenn die ausgewählte CSV-Datei Zeilen enthält, die mehr oder
    weniger als zwei Einträge enthalten.
    """
    pass


class DuplicateValuesException(Exception):
    """
    Klasse setzt die Exception um, welche geworfen wird, wenn die ausgewählte CSV-Datei doppelte Einträge enthält.
    """
    pass

class CalculationTooLong(Exception):
    """
    Klasse setzt die Exception um, welche geworfen wird, wenn die Berechnung zu lange dauert.
    """
    pass

class NotEnoughColorsException(Exception):
    """
    Klasse setzt die Exception um, welche geworfen wird, wenn das ausgewählte Bild über weniger Farben verfügt, als für
    k als Anzahl an Farben auf die das Bild reduziert werden soll, ausgewählt wurde
    """

    def __init__(self, number_of_colors):
        self.number_of_colors = number_of_colors
