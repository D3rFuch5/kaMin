import os
from datetime import datetime
from tkinter.filedialog import askopenfilename

from PIL import UnidentifiedImageError

import src.Exceptions
from src import View_Window, Image_Reader, Model_Color_Quantization


def parse_filesize_from_bytes(filesize):
    """
    Konvertiert die in Bytes gegebene Dateigröße in Bytes, Kilobytes oder Megabytes in Abhängigkeit von der Dateigröße
    und setzt die Nachkommastellen auf geeignete Anzahlen.
    :param filesize: Dateigröße in Bytes
    :return: Konvertierte Dateigröße als String mit der jeweiligen Einheit B, KB oder MB
    """
    if 0 < filesize < 1024:
        size = f'{filesize:.0f}' + " B"
    elif filesize < 1048576:
        size = f'{filesize / 1024:.0f}' + " KB"
    elif filesize < 1073741824:
        size = f'{filesize / 1048576:.3f}' + " MB"
    else:
        raise ValueError("Unsupported file size")
    return size


class Controller_Quantization:
    """
    Controller der Funktionalität "Farbreduktion"
    """
    def __init__(self, operating_frame):
        self.selected_filepath = ""
        self.selected_number_of_colors_general = -1
        self.read_in_image_as_array = None
        self.image_as_array_quantized_general = None
        self.read_in_image_as_array_reduced_color_channel = None
        self.image_as_array_quantized_reduced_color_channel = None

        self.file_size_read_in_image = ""
        self.file_size_image_quantized_general = ""
        self.file_size_image_reduced_color_channel = ""
        self.file_size_image_quantized_reduced_color_channel = ""

        self.selected_color_channels = ""
        self.selected_number_of_colors_color_channels = -1

        self.step_remove_color_channel = True
        self.colors_array_image_reduced_color_channel = None
        # Erstellen der View und binden der Befehle an View-Interaktionen
        self.view_main_frame = operating_frame
        self.bind_view_button_commands()

    def reset_color_quantization(self):
        """
        Setzt die Attribute und die initial bei der Farbreduktion angezeigte Oberfläche auf den Ausgangszustand zurück.
        """
        self.selected_filepath = ""
        self.view_main_frame.display_selected_filepath_image(filepath=self.selected_filepath)
        self.read_in_image_as_array = None
        self.image_as_array_quantized_general = None

        self.step_remove_color_channel = True
        self.file_size_read_in_image = ""
        self.file_size_image_quantized_general = ""
        self.file_size_image_reduced_color_channel = ""
        self.file_size_image_quantized_reduced_color_channel = ""

        self.selected_number_of_colors_general = -1
        self.selected_color_channels = ""
        self.selected_number_of_colors_color_channels = -1

        self.read_in_image_as_array_reduced_color_channel = None
        self.image_as_array_quantized_reduced_color_channel = None
        self.colors_array_image_reduced_color_channel = None

        self.view_main_frame.reset_selection_number_of_colors_quantization_general()
        self.view_main_frame.reset_display_images()

        self.view_main_frame.reset_controls_quantization_color_channels()
        self.view_main_frame.reset_plots_quantization_color_channels()

        self.view_main_frame.update_view_button_calculate_color_channels(
            step_remove_channel=self.step_remove_color_channel)

        self.view_main_frame.update_view_enable_tab_color_channels(enable=False)

        self.view_main_frame.reset_ck_btn_show_file_size()

    def open_image(self):
        """
        Methode zum Öffnen eines Bilds für die Farbreduktion. Setzt zuerst die Attribute zur Speicherung der Bilder
        (farbreduziert, mit Farbkanal entfernt, mit Farbkanal entfernt und farbreduziert), der Speichergrößen, usw. auf
        die Initalwerte zurück. Öffnet dann ein Kontextmenü zur Auswahl einer png-Datei. Im Anschluss wird das Bild als
        Array eingelesen, ggf. dessen Dateigröße bestimmt und der Dateiname angezeigt. Das eingelesene Bild wird in der
        Oberfläche angezeigt und die Default-Bilder bzw. die Anzeigen einer vorherigen Farbreduktion werden entfernt.
        Falls ein Fehler auftritt werden, wird einer Fehlermeldung angezeigt, die Attribute zurückgesetzt und die
        Default-Bilder angezeigt.
        """
        self.step_remove_color_channel = True
        self.view_main_frame.update_view_button_calculate_color_channels(
            step_remove_channel=self.step_remove_color_channel)
        # Sperren der Eingabemöglichkeiten, damit während dem Laden des Bilds keine weiteren Aktionen gestartet werden
        # können
        self.view_main_frame.update_view_enable_quantization(enable=False)
        self.view_main_frame.btn_choose_image_file.update()
        self.step_remove_color_channel = True
        self.image_as_array_quantized_general = None
        self.selected_number_of_colors_general = -1
        self.file_size_image_quantized_general = ""

        self.selected_color_channels = ""
        self.selected_number_of_colors_color_channels = -1

        self.read_in_image_as_array_reduced_color_channel = None
        self.image_as_array_quantized_reduced_color_channel = None
        self.file_size_image_reduced_color_channel = ""
        self.file_size_image_quantized_reduced_color_channel = ""
        self.colors_array_image_reduced_color_channel = None
        # Einlesen des ausgewählten Dateipfads
        self.selected_filepath = askopenfilename(parent=self.view_main_frame,
                                                 filetypes=[("Image Files", "*.png")])
        try:
            self.read_in_image_as_array = Image_Reader.read_image_as_numpy_array(
                self.selected_filepath)
            if self.view_main_frame.show_image_file_size.get():
                self.file_size_read_in_image = parse_filesize_from_bytes(
                    Image_Reader.save_image_from_array(image_array=self.read_in_image_as_array,
                                                       file_name="Read_In_Image_Original",
                                                       optimize_image=False, int_image=True))
            else:
                self.file_size_read_in_image = ""
            self.view_main_frame.display_image_original(image_array=self.read_in_image_as_array,
                                                        file_size=self.file_size_read_in_image)
            self.view_main_frame.reset_plots_quantization_color_channels(plot_numbers=(0, 1, 2, 3))
            self.view_main_frame.update_view_enable_tab_color_channels(enable=True)
        except Exception as e:
            if type(e) == UnidentifiedImageError:
                err_msg = "Die Datei konnte nicht geöffnet werden!"
            elif type(e) == TypeError:
                err_msg = "Die eingelesene Datei hat keinen zugelassenen Dateityp!"
            elif type(e) == FileNotFoundError:
                err_msg = "Es wurde keine Datei ausgew\u00E4hlt!"
            else:
                err_msg = "Es ist ein Fehler aufgetreten!"
            self.selected_filepath = ""
            self.read_in_image_as_array = None
            self.file_size_read_in_image = ""
            self.view_main_frame.reset_display_images()
            self.view_main_frame.reset_selection_number_of_colors_quantization_general()
            self.view_main_frame.reset_controls_quantization_color_channels()
            self.view_main_frame.update_view_enable_tab_color_channels(enable=False)
            View_Window.display_error_message(parent_window=self.view_main_frame.master, error_message=err_msg)

        # Anzeige des Dateinamens erst am Ende, da bei Auftreten eines Fehlers beim Lesen der Datei der Pfad leer
        # bleibt
        self.view_main_frame.display_selected_filepath_image(filepath=os.path.basename(self.selected_filepath))
        # Rückgängigmachung der obigen Sperrung
        self.view_main_frame.btn_choose_image_file.update()
        self.view_main_frame.update_view_enable_quantization(enable=True,
                                                             step_remove_color_channel=self.step_remove_color_channel)

    def calculate_color_quantization(self):
        """
        Wenn ein Bild geladen ist, wird die Farbreduktion dieses Bilds auf die Anzahl der in der Oberfläche gewählten
        Anzahl an Farben bestimmt. Falls ausgewählt wird dabei auch die Dateigröße des reduzierten Bilds bestimmt und
        das farbreduzierte Bild wird in der Oberfläche angezeigt.
        Falls das Bild nicht über ausreichend Farben für die Reduktion verfügt oder kein Bild geladen ist, wird eine
        Fehlermeldung angezeigt.
        """
        if self.read_in_image_as_array is not None:
            # Sperren der Eingabemöglichkeiten, damit während der Berechnung der Farbreduktion des Bilds keine weiteren
            # Aktionen gestartet werden können
            self.view_main_frame.update_view_enable_quantization(enable=False)
            self.view_main_frame.btn_calculate_color_quantization.update()
            self.selected_number_of_colors_general = self.view_main_frame.selected_number_of_colors_color_quantization.get()
            try:
                self.image_as_array_quantized_general = Model_Color_Quantization.quantize_image_general(
                    value_k=self.selected_number_of_colors_general,
                    image_as_array=self.read_in_image_as_array)
                if self.view_main_frame.show_image_file_size.get():
                    self.file_size_image_quantized_general = parse_filesize_from_bytes(
                        Image_Reader.save_image_from_array(image_array=self.image_as_array_quantized_general,
                                                           file_name="Read_In_Image_Quantized",
                                                           optimize_image=True, int_image=False))
                else:
                    self.file_size_image_quantized_general = ""
                self.view_main_frame.display_quantized_image(image_array=self.image_as_array_quantized_general,
                                                             file_size=self.file_size_image_quantized_general)
            except src.Exceptions.NotEnoughColorsException as e:
                err_msg = "Der gewählte Wert für k ist zu groß. Das geladene Bild besitzt nur " + str(
                    e.number_of_colors)
                if e.number_of_colors == 1:
                    err_msg += " Farbe!"
                else:
                    err_msg += " Farben!"
                # Zurücksetzen der Attribute die zum farbreduzierten Bild gehören und Leeren der Anzeigefläche des
                # farbreduzierten Bildes
                self.image_as_array_quantized_general = None
                self.selected_number_of_colors_general = -1
                self.file_size_image_quantized_general = ""
                self.view_main_frame.clear_quantized_image()
                View_Window.display_error_message(parent_window=self.view_main_frame.master,
                                                  error_message=err_msg)
            # Aufheben der obigen Oberflächensperrung
            self.view_main_frame.btn_calculate_color_quantization.update()
            self.view_main_frame.update_view_enable_quantization(enable=True,
                                                                 step_remove_color_channel=self.step_remove_color_channel)
        else:
            View_Window.display_error_message(parent_window=self.view_main_frame.master,
                                              error_message="Kein Bild geladen!")

    def switch_tab_color_quantization(self, event):
        """
        Passt die Oberfläche an den ausgewählten Tab des Notebooks an. (Aktivierung bzw. Deaktivierung des "Öffnen"-
        Buttons, Ein- bzw. Ausblenden der benötigten Kontrollmöglichkeiten außerhalb des Tabs)
        """
        self.view_main_frame.update_view_color_channels_active()

    def calculate_color_quantization_channels(self):
        """
        Realisiert die zwei Phasen der Farbreduktion mit zwei Farbkanälen. In der ersten Phase wird aus dem geladenen
        Bild der in der Oberfläche ausgewählte Farbkanal entfernt, das sich ergebende Bild und die im Bild vorkommenden
        Farben (bei zu vielen eine Teilmenge) in der Oberfläche angezeigt.
        In Phase zwei wird für dieses um den Farbkanal reduzierte Bild die Farbreduktion auf die Anzahl der in der
        Oberfläche gewählten Anzahl an Farben bestimmt und sowohl dieses als auch die in Cluster aufgeteilten Farben
        angezeigt.
        Falls das Bild nicht über ausreichend Farben für die Reduktion verfügt oder kein Bild geladen ist, wird eine
        Fehlermeldung angezeigt.
        """
        # Abfrage, ob ein Bild geladen ist, nicht nötig, da dies über die View sichergestellt ist, dass man diese
        # Methode nur aufrufen kann, wenn vorher ein Bild erfolgreich geladen wurde
        # Sperren der Eingabemöglichkeiten, damit während der Berechnung der Farbreduktion des Bilds bzw. der Entfernung
        # der Farbkanals keine weiteren Aktionen gestartet werden können
        self.view_main_frame.update_view_enable_quantization(enable=False)
        self.view_main_frame.btn_calculate_quantization_color_channels.update()
        # Umsetzung der Entfernung des in der Oberfläche ausgewählten Farbkanals
        if self.step_remove_color_channel:
            self.view_main_frame.reset_plots_quantization_color_channels(plot_numbers=(0, 2))
            self.view_main_frame.reset_plots_quantization_color_channels(plot_numbers=(1, 3))
            # Falls bereits eine Farbreduktion durchgeführt wurde, müssen die Werte der in Phase 2 benötigten zurück-
            # gesetzt werden
            self.image_as_array_quantized_reduced_color_channel = None
            self.file_size_image_quantized_reduced_color_channel = ""
            self.selected_number_of_colors_color_channels = -1
            self.selected_color_channels = self.view_main_frame.selected_color_channels.get()
            # Reduzierung des eingelesenen Bilds um den gewählten Farbkanal
            self.read_in_image_as_array_reduced_color_channel = Model_Color_Quantization.remove_color_channel(
                image_as_array=self.read_in_image_as_array,
                color_channels=self.selected_color_channels)
            # Auswahl der Farbsamples aus dem Bild zum Training des kMeans-Objekts. Dabei ist sichergestellt, dass
            # nur unterschiedliche Farbwerte ausgewählt werden. Das Training an sich findet erst in Phase 2 statt.
            self.colors_array_image_reduced_color_channel = Model_Color_Quantization.get_color_samples_of_image(
                image_as_array=self.read_in_image_as_array_reduced_color_channel)
            if self.view_main_frame.show_image_file_size.get():
                self.file_size_image_reduced_color_channel = parse_filesize_from_bytes(
                    Image_Reader.save_image_from_array(image_array=self.read_in_image_as_array_reduced_color_channel,
                                                       file_name="Read_In_Image_Color_Channels_" + self.selected_color_channels,
                                                       optimize_image=True, int_image=True))
            else:
                self.file_size_image_reduced_color_channel = ""
            self.view_main_frame.display_original_plots_color_channels(
                image_array=self.read_in_image_as_array_reduced_color_channel,
                colors_array=self.colors_array_image_reduced_color_channel,
                file_size_reduced_color_channel=self.file_size_image_reduced_color_channel)
            # Weiterschalten der Phase und Anpassen der Oberfläche für die folgende Phase
            self.step_remove_color_channel = not self.step_remove_color_channel
            self.view_main_frame.update_view_button_calculate_color_channels(
                step_remove_channel=self.step_remove_color_channel)
        # Berechnung der Farbreduktion für das um den Farbkanal reduzierten Bilds
        else:
            self.selected_number_of_colors_color_channels = self.view_main_frame.selected_number_of_colors_color_channels.get()
            try:
                self.image_as_array_quantized_reduced_color_channel, col, cent = Model_Color_Quantization.quantize_color_channels(
                    value_k=self.selected_number_of_colors_color_channels,
                    colors_array=self.colors_array_image_reduced_color_channel,
                    image_as_array=self.read_in_image_as_array_reduced_color_channel)
                if self.view_main_frame.show_image_file_size.get():
                    self.file_size_image_quantized_reduced_color_channel = parse_filesize_from_bytes(
                        Image_Reader.save_image_from_array(
                            image_array=self.image_as_array_quantized_reduced_color_channel,
                            file_name="Image_Quantized_Color_Channels_" + self.selected_color_channels,
                            optimize_image=True, int_image=False))
                else:
                    self.file_size_image_quantized_reduced_color_channel = ""

                self.view_main_frame.display_quantized_plots_color_channels(
                    image_array=self.image_as_array_quantized_reduced_color_channel,
                    data_array=self.colors_array_image_reduced_color_channel,
                    colors_array=col, centroids=cent,
                    file_size_quantized_image=self.file_size_image_quantized_reduced_color_channel)
                # Weiterschalten der Phase und Anpassen der Oberfläche für die folgende Phase
                self.step_remove_color_channel = not self.step_remove_color_channel
                self.view_main_frame.update_view_button_calculate_color_channels(
                    step_remove_channel=self.step_remove_color_channel)
            except src.Exceptions.NotEnoughColorsException as e:
                err_msg = "Der gewählte Wert für k ist zu groß. Das geladene Bild besitzt nur " + str(
                    e.number_of_colors)
                if e.number_of_colors == 1:
                    err_msg += " Farbe!"
                else:
                    err_msg += " Farben!"
                # Zurücksetzen der Attribute die zum farbreduzierten Bild gehören und Leeren der Anzeigeflächen des
                # farbreduzierten Bildes und der Anzeige der quantifizierten Farben
                self.selected_number_of_colors_color_channels = -1
                self.image_as_array_quantized_reduced_color_channel = None
                self.file_size_image_quantized_reduced_color_channel = ""
                self.view_main_frame.reset_plots_quantization_color_channels(plot_numbers=(1, 3))
                View_Window.display_error_message(parent_window=self.view_main_frame.master,
                                                  error_message=err_msg)

        # Aufheben der obigen Sperrung
        self.view_main_frame.btn_calculate_quantization_color_channels.update()
        self.view_main_frame.update_view_enable_quantization(enable=True,
                                                             step_remove_color_channel=self.step_remove_color_channel)

    def display_file_size(self):
        """
        Blendet die Dateigröße der Bilder ein bzw. aus. Falls an einer Stelle noch keine Dateigröße bestimmt wurde,
        wird diese nun bestimmt, falls benötigt.
        """
        # Aktivieren der Dateigrößenanzeige
        if self.view_main_frame.show_image_file_size.get():
            self.view_main_frame.update_view_enable_quantization(enable=False)
            self.view_main_frame.ck_btn_show_image_file_size.update()
            # Plots Farbreduktion allgemein
            # Falls ein Bild geladen ist, aber noch keine Dateigröße berechnet wurde, wird diese berechnet
            if self.read_in_image_as_array is not None and self.file_size_read_in_image == "":
                self.file_size_read_in_image = parse_filesize_from_bytes(
                    Image_Reader.save_image_from_array(image_array=self.read_in_image_as_array,
                                                       file_name="Read_In_Image_Original",
                                                       optimize_image=False, int_image=True))
            # Falls ein farbreduziertes Bild vorhanden ist, davon aber noch nicht die Dateigröße bestimmt wurde, wird
            # diese nun berechnet
            if self.image_as_array_quantized_general is not None and self.file_size_image_quantized_general == "":
                self.file_size_image_quantized_general = parse_filesize_from_bytes(
                    Image_Reader.save_image_from_array(image_array=self.image_as_array_quantized_general,
                                                       file_name="Read_In_Image_Quantized",
                                                       optimize_image=True, int_image=False))
            # Anzeige der ggf. vorhandenen Dateigrößen
            self.view_main_frame.display_file_size_general(file_size_original=self.file_size_read_in_image,
                                                           file_size_quantized=self.file_size_image_quantized_general,
                                                           color_nums=self.selected_number_of_colors_general)

            # Plots Farbkanäle
            # Falls bereits ein Farbkanal entfernt wurde, aber noch keine Dateigröße für dieses Bild berechnet wurde
            if self.read_in_image_as_array_reduced_color_channel is not None and self.file_size_image_reduced_color_channel == "":
                self.file_size_image_reduced_color_channel = parse_filesize_from_bytes(
                    Image_Reader.save_image_from_array(image_array=self.read_in_image_as_array_reduced_color_channel,
                                                       file_name="Read_In_Image_Color_Channels_" + self.selected_color_channels,
                                                       optimize_image=True, int_image=True))
            # Falls bereits das eine Farbreduktion für ein Bild ohne einen einzelnen Farbkanal berechnet wurde, aber
            # keine Dateigröße vorliegt
            if self.image_as_array_quantized_reduced_color_channel is not None and self.file_size_image_quantized_reduced_color_channel == "":
                self.file_size_image_quantized_reduced_color_channel = parse_filesize_from_bytes(
                    Image_Reader.save_image_from_array(image_array=self.image_as_array_quantized_reduced_color_channel,
                                                       file_name="Image_Quantized_Color_Channels_" + self.selected_color_channels,
                                                       optimize_image=True, int_image=False))

            # Anzeige der ggf. vorhandenen Dateigrößen
            self.view_main_frame.display_file_size_color_channels(
                file_size_color_channels=self.file_size_image_reduced_color_channel,
                file_size_color_channels_quantized=self.file_size_image_quantized_reduced_color_channel,
                color_nums=self.selected_number_of_colors_color_channels, color_channels=self.selected_color_channels)

            self.view_main_frame.ck_btn_show_image_file_size.update()
            self.view_main_frame.update_view_enable_quantization(enable=True,
                                                                 step_remove_color_channel=self.step_remove_color_channel)
        # Ausblenden der Dateigröße
        else:
            # Allgemeiner Bereich
            self.view_main_frame.display_file_size_general(color_nums=self.selected_number_of_colors_general)

            # Bereich Farbkanäle
            self.view_main_frame.display_file_size_color_channels(color_channels=self.selected_color_channels,
                                                                  color_nums=self.selected_number_of_colors_color_channels)

    def bind_view_button_commands(self):
        """
        Belegt die Eingabemöglichkeiten der View der Farbreduktion mit den auszufahrenden Methoden.
        """
        self.view_main_frame.btn_choose_image_file.config(command=self.open_image)
        self.view_main_frame.btn_calculate_color_quantization.config(command=self.calculate_color_quantization)
        self.view_main_frame.notebook_display_color_quantization.bind("<<NotebookTabChanged>>",
                                                                      self.switch_tab_color_quantization)
        self.view_main_frame.btn_calculate_quantization_color_channels.config(
            command=self.calculate_color_quantization_channels)
        self.view_main_frame.ck_btn_show_image_file_size.config(command=self.display_file_size)
