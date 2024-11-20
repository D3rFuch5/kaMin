import csv
import os
import src.Exceptions

characters_to_remove = ["\uFEFF"]


def read_in_csv(data_path):
    """
    Methode liest die Datei unter dem übergebenen Pfad aus und gibt die eingelesenen Daten zurück.
    Die Datei muss in der ersten Zeile die Header-Werte mit ; getrennt enthalten.
    In den folgenden Zeilen folgen die Daten in der durch den Header festgelegten Reihenfolge. Diese werden beim
    Einlesen in den Datentyp Float gecastet.
    :param data_path: Pfad der zu lesenden csv-Datei
    :return: 2 Elemente: 1. Zeile des eingelesenen Datensatzes(Header) als Tupel
                         2. restliche eingelesene Daten als Liste von Tupeln
    """
    # Öffnet die Datei unter dem übergebenen Pfad
    with open(data_path, encoding='utf-8', mode='r') as read_in_data_file:

        # Erstellen des csv-Readers. Das erwartete Trennzeichen lauter ;
        csvreader = csv.reader(read_in_data_file, delimiter=';')

        read_in = []
        # Einlesen des Headers; Falls die Datei leer ist, wird eine EmptyFileException geworfen
        try:
            read_in.append(tuple(next(csvreader)))
        except StopIteration:
            raise src.Exceptions.EmptyFileException

        if len(read_in[0]) != 2:
            raise src.Exceptions.WrongDimensionException

        # Entfernt ungewollte Zeichen am Anfang des eingelesenen Strings
        cleared = read_in[0][0]
        for character in characters_to_remove:
            if cleared.find(character) != -1:
                cleared = cleared.replace(character, '')
            read_in[0] = (cleared,) + read_in[0][1:]

        # Einlesen der Daten
        for row in csvreader:
            # Überspringen von leeren Zeilen
            if len(row) > 0:
                if len(row) == 2:
                    read_in.append(tuple(float(data) for data in row))
                else:
                    raise src.Exceptions.WrongDimensionException

        # Überprüfung, ob Duplikate in der eingelesenen Datei sind
        if duplicates_found(dataset=read_in[1:]):
            raise src.Exceptions.DuplicateValuesException

    return read_in[0], read_in[1:]


def write_to_csv(filepath, data_header, data_to_write):
    """
    Schreibt den Datei-Header data_header und die übergebenen Daten in eine CSV-Datei im übergebenen Dateipfad filepath
    mit dem Namen Datenpunkte.csv
    :param filepath: Pfad des Ordners, in dem die CSV-Datei abgelegt werden soll.
    :param data_header: Header-Zeile als Liste.
    :param data_to_write: Zu schreibender Datensatz als Liste von Tupeln. Die Tupel müssen dabei die Länge des
    data_headers haben.
    """
    # Unterscheidung des Pfadtrennzeichens in Abhängigkeit vom Betriebssystem
    if os.name == 'nt':
        path_delimiter = '\u002F'
    # posix für Linux und MacOS
    else:
        path_delimiter = '\u005C'
    with open(file=filepath + path_delimiter + "Datenpunkte.csv", mode='w', encoding='UTF8',
              newline='') as file_to_write:
        writer = csv.writer(file_to_write, delimiter=';')
        writer.writerow(data_header)
        writer.writerows(data_to_write)


def duplicates_found(dataset):
    """
    Überprüft, ob in der übergebenen Liste dataset mindestens ein Duplikat vorhanden ist.
    :param dataset: Liste, welche auf Duplikate überprüft werden soll
    :return: True, falls ein Duplikat gefunden wurde; False, sonst
    """
    for i in range(len(dataset) - 1):
        if dataset[i] in dataset[i + 1:]:
            return True
    return False
