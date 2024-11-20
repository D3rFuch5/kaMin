import numpy as np
import os
from PIL import Image


def read_image_as_numpy_array(image_path):
    """
    Liest ein PNG-Bild unter dem angegebenen Pfad ein und gibt dieses als dreidimensionales Array mit Integer-Werten
    zurück.
    :param image_path: Dateipfad zum einzulesenden Bild
    :exception FileNotFoundError: Dateipfad zum einzulesenden Bild war leer
    :return: Bild in Form eines dreidimensionalen Arrays, wobei in der dritten Dimension Arrays der Länge 3 sind,
             welche jeweils ein Pixel im RGB-Format repräsentieren.
    """
    if image_path == "":
        raise FileNotFoundError
    # Öffnet die Datei unter dem übergebenen Pfad
    with Image.open(fp=image_path, mode='r', formats=["PNG"]) as read_in_image:
        image_as_array = np.array(read_in_image, dtype=np.uint8)
    return image_as_array[:, :, :3]


def save_image_from_array(image_array, file_name, optimize_image, int_image):
    """
    Speichert das als Array übergebene Bild im Ordner Temp unter dem übergebenen Dateinamen file_name
    mit dem übergebenen Dateityp file_type ab.
    :param image_array: Bild as numpy-Array (3-Dimensional; Zeile und Spalte entsprechen der Postion des Pixels;
                        Einträge an dieser jeweiligen Stelle ist ein Array der Länge drei mit den RGB-Werten des Bilds)
    :param file_name: Name, unter dem das Bild gespeichert werden soll.
    :param optimize_image: Falls True, wird das Bild bezüglich Speicherplatz optimiert, Sonst wird mit 100 Prozent der
                            Qualität gespeichert
    :param int_image: Falls True, werden die einzelnen Werte des übergebenen Bilds im Bereich von [0..255] erwartet;
                      Falls False, werden die einzelnen Werte des übergebenen Bilds im Bereich von [0..1] erwartet
    :return: Dateigröße auf der Festplatte in Bytes
    """
    folder_path = os.path.join('.', 'Temp')
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    file_path = os.path.join(folder_path, file_name + ".png")

    # Überführen des Bilds als Array in ein Image-Objekt des PIL-Pakets
    if int_image:
        image_file = Image.fromarray(obj=image_array, mode="RGB")
    else:
        image_file = Image.fromarray(obj=(image_array * 255).astype('uint8'), mode="RGB")
    # Abspeichern des Bilds
    if optimize_image:
        image_file.save(fp=file_path, optimize=True)
    else:
        image_file.save(fp=file_path, quailty=100)
    # Rückgabe der Dateigrösse des gespeicherten Bilds
    return os.path.getsize(file_path)
