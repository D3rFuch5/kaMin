import copy
import os
from tkinter.filedialog import askopenfilename, askdirectory

from matplotlib.backend_bases import PickEvent, MouseEvent
from matplotlib.lines import Line2D

import src.Exceptions
from src import View_Window, CSV_Utils, Model_k_means, Plot_Utils_Model


class Controller_k_Means:
    MIN_VALUE_K = 1
    DEFAULT_BORDER_K = 10
    default_X_LOW = Plot_Utils_Model.DEFAULT_X_LOW
    default_X_HIGH = Plot_Utils_Model.DEFAULT_X_HIGH
    default_Y_LOW = Plot_Utils_Model.DEFAULT_Y_LOW
    default_Y_HIGH = Plot_Utils_Model.DEFAULT_Y_HIGH

    DEFAULT_HEADER = (Plot_Utils_Model.DEFAULT_X_LABEL, Plot_Utils_Model.DEFAULT_Y_LABEL)

    ANALYSIS_MODE_elbow = "Ellbogen-Analyse"
    ANALYSIS_MODE_silhouette = "Silhouetten-Analyse"

    def __init__(self, operating_frame):
        self.train_mode_active = False
        self.parameter_analysis_active = False
        self.STATE_click_input_data_points_active = False
        self.STATE_click_input_centroids_active = False

        self.current_x_low = self.default_X_LOW
        self.current_x_high = self.default_X_HIGH
        self.current_y_low = self.default_Y_LOW
        self.current_y_high = self.default_Y_HIGH

        # Anlegen der Attribute zum Speichern der Trainingsdaten
        self.selected_filepath = ""
        self.read_in_data_header = ()
        self.read_in_dataset = []

        self.current_centroids = []
        self.previous_dataset_split_for_centroids = {}
        self.current_dataset_split_for_centroids = {}
        self.centroid_history = []

        # Attribute zum Speichern der ID der Callback-Funktionen für das Mouse bzw. Pick-Event zum Auswählen, Hinzufügen
        # oder Entfernen von Punkten
        self.ID_CALLBACK_Mouse_Pressed_event = None
        self.ID_CALLBACK_Pick_event = None

        # Attribute für den automatischen Endlos-Modus
        self.auto_mode_running = False
        self.auto_mode_running_speed = 1000
        self.ID_CALLBACK_Auto_Mode = None
        self.final_clusters_found = False
        self.auto_mode_train_step = 0
        self.auto_mode_init_step = True

        # Attribut für das Algorithmen-Schritt-Training
        # Es gibt nur zwei zu betrachtende Schritte.
        # Schritt 1: (True) Berechnung der den jeweiligen Zentren am nächsten liegenden Punkte
        # Schritt 2: (False) Berechnung der neuen Cluster-Zentren
        self.algorithm_step_one = True

        # Attribute zum Speichern der für die Parameter-Analyse notwendigen Informationen
        self.list_final_cluster_sets_distance_plot_elbow_analysis = []
        self.dict_distances_for_datapoints = {}

        # Erstellen der View und binden der Befehle an View-Interaktionen
        self.view_main_frame = operating_frame
        self.view_main_frame.update_view_train_mode(enable_train_mode=self.train_mode_active, clusters_found=False)
        self.bind_view_button_commands()

    def reset_simulation_k_means(self):
        """
        Setzt die Attribute auf die Initialwerte und zeigt den initial sichtbaren Zustand der Oberfläche an.
        Bereiche, die initial nicht sichtbar sind, müssen an dieser Stelle nicht zurückgesetzt werden, sondern erst bei
        Einblendung.
        """
        self.train_mode_active = False
        self.parameter_analysis_active = False
        # Setzt die Dateieingabe auf Auswahl aus einer Datei
        self.view_main_frame.reset_data_input_mode()

        # Anpassen der View je nach gewähltem Dateieingabemodus
        self.view_main_frame.update_view_data_selection()
        self.view_main_frame.update_view_train_mode(enable_train_mode=self.train_mode_active, clusters_found=False)

        self.read_in_dataset.clear()
        # Zurücksetzen des Analysegraphen
        self.view_main_frame.reset_parameter_analysis_plot()
        self.list_final_cluster_sets_distance_plot_elbow_analysis.clear()
        self.dict_distances_for_datapoints.clear()

        self.selected_filepath = ""
        self.view_main_frame.display_selected_filepath_training_data(filepath=self.selected_filepath)

        self.STATE_click_input_data_points_active = False
        self.STATE_click_input_centroids_active = False

        self.current_centroids.clear()
        self.centroid_history.clear()
        self.previous_dataset_split_for_centroids.clear()
        self.current_dataset_split_for_centroids.clear()

        # Attribute für den automatischen Endlos-Modus
        self.auto_mode_running = False
        self.auto_mode_running_speed = 1000
        self.ID_CALLBACK_Auto_Mode = None
        self.final_clusters_found = False
        self.auto_mode_train_step = 0
        self.auto_mode_init_step = True

        # Attribut für das Algorithmen-Schritt-Training
        self.algorithm_step_one = True

        self.current_x_low = self.default_X_LOW
        self.current_x_high = self.default_X_HIGH
        self.current_y_low = self.default_Y_LOW
        self.current_y_high = self.default_Y_HIGH

        # Setzen des Headers in Abhängigkeit vom gewählten Modus und initialisieren des Headers im Fall der
        # Mauseingabe, da in diesem Fall nur die Standardbezeichnungen für die x und y-Koordinate möglich sind
        if self.view_main_frame.get_data_selection_mode() == self.view_main_frame.DATA_INPUT_MODE_on_click:
            self.read_in_data_header = self.DEFAULT_HEADER
        else:
            self.read_in_data_header = ()
        self.view_main_frame.clear_treeview_centroids_header()
        self.view_main_frame.fill_treeview_centroids_with_header(header=self.read_in_data_header)

        # Zurücksetzen der Slider
        self.reset_slider_k_treeview_data_parameter_analysis(max_value_k=self.MIN_VALUE_K, centroids=[])
        self.reset_slider_k_treeview_data(max_value_k=self.MIN_VALUE_K)

        # Uncheck der Auswahl, ob die Achsenbezeichnungen ausgeblendet werden sollen, sodass diese initial
        # eingeblendet werden beim Reset des Plots
        self.view_main_frame.reset_show_axis_ck_box()

        # Zurücksetzen der Anzeigefläche mit den eingegebenen Abmessungen
        self.view_main_frame.reset_plot()

        # Entfernt ggf. an die Anzeigefläche gebundene Event-Callbacks und setzt die Attribute zum Speichern derer
        # IDs zurück
        self.unbind_callbacks_canvas()

    def open_file_training_data(self):
        """
        Lädt die Trainingsdaten aus einer .csv-Datei in das Programm und zeigt die geladenen Trainingsdaten an.
        Setzt zu Beginn die Attribute zurück, öffnet ein Auswahlfenster zu Auswahl der .csv-Datei mit den
        Trainingsdaten, liest diese ein und speichert sie in read_in_data_header und read_in_data. Zeichnet im
        Anschluss die eingelesenen Trainingsdaten auf die Zeichenfläche und speichert die Abmessungen der
        Anzeigefläche, welche in Abhängigkeit von den Trainingsdaten bestimmt wurden.
        """
        # Zurücksetzen der Oberfläche und Attribute
        self.view_main_frame.show_centroid_history.set(False)
        self.view_main_frame.show_decision_areas.set(False)
        self.view_main_frame.reset_parameter_analysis_plot()
        self.current_centroids.clear()
        self.unbind_callbacks_canvas()

        # Einlesen des ausgewählten Dateipfads
        self.selected_filepath = askopenfilename(parent=self.view_main_frame, filetypes=[("CSV Files", "*.csv")])
        try:
            self.read_in_data_header, self.read_in_dataset = CSV_Utils.read_in_csv(self.selected_filepath)
            self.view_main_frame.draw_dataset(axis_labels=self.read_in_data_header, dataset=self.read_in_dataset)
            # Setzen der Abmessungen des Plots in Abhängigkeit vom geladenen Datensatz
            (self.current_x_low, self.current_x_high, self.current_y_low,
             self.current_y_high) = self.view_main_frame.get_current_plot_dimensions()
            max_value_k = min(self.DEFAULT_BORDER_K, len(self.read_in_dataset))
        except Exception as e:
            if type(e) == src.Exceptions.EmptyFileException:
                err_msg = "Die eingelesene Datei war leer!"
            elif type(e) == src.Exceptions.DuplicateValuesException:
                err_msg = "Die eingelesene Datei enth\u00E4lt doppelte Werte!"
            elif type(e) == src.Exceptions.WrongDimensionException:
                err_msg = "Die eingelesene Datei enth\u00E4lt Zeilen unzul\u00E4ssiger L\u00E4nge!"
            elif type(e) == ValueError:
                err_msg = "In der eingelesenen Datei befanden sich ung\u00FCltige Werte!"
            elif type(e) == FileNotFoundError:
                err_msg = "Es wurde keine Datei ausgew\u00E4hlt!"
            else:
                err_msg = "Es ist ein Fehler aufgetreten!"
            self.selected_filepath = ""
            self.read_in_data_header = ()
            self.read_in_dataset.clear()
            self.view_main_frame.reset_plot()
            self.current_x_low = self.default_X_LOW
            self.current_x_high = self.default_X_HIGH
            self.current_y_low = self.default_Y_LOW
            self.current_y_high = self.default_Y_HIGH
            max_value_k = self.MIN_VALUE_K
            View_Window.display_error_message(parent_window=self.view_main_frame.master, error_message=err_msg)

        # Anzeige des Dateinamens erst am Ende, da bei Auftreten eines Fehlers beim Lesen der Datei der Pfad leer
        # bleibt
        self.view_main_frame.display_selected_filepath_training_data(filepath=os.path.basename(self.selected_filepath))
        # Leeren und initialisieren des Treeview-Headers
        self.view_main_frame.clear_treeview_centroids_header()
        self.view_main_frame.fill_treeview_centroids_with_header(header=self.read_in_data_header)
        self.reset_slider_k_treeview_data(max_value_k=max_value_k)

    def reset_slider_k_treeview_data(self, max_value_k):
        """
        Setzt den Wert des Sliders auf den Wert 1 und die Treeview-Daten zurück. Außerdem wird der Maximalwert des
        Sliders aktualisiert
        :param max_value_k: Maximalwert des Sliders
        """
        # Der Slider soll immer auf den Wert 1 gesetzt werden. Ändert sich dabei der Wert des Sliders, wird automatisch
        # auch ein Update/Reset der Treeview ausgeführt. Falls der Slider vorher schon bei 1 war, muss dies manuell
        # angestoßen werden. Ein Update des Slider-Wertebereichs triggert ein Update nur, wenn sich dadurch auch der
        # Wert des Sliders ändert, was durch das Zurücksetzen des Sliders nicht der Fall sein kann.
        if self.view_main_frame.selected_value_k.get() == 1:
            self.view_main_frame.clear_treeview_centroids_data()
            self.view_main_frame.fill_treeview_centroids_with_data(dataset=self.current_centroids)
        else:
            self.view_main_frame.set_slider_parameter_k_value(value=self.MIN_VALUE_K)
        self.view_main_frame.set_scale_area_slider_parameter_k(max_value_k=max_value_k)

    def set_initial_centroids_random(self):
        """
        Wählt zufällig k Punkte des Datensatzes als initiale Cluster-Zentren aus.
        """
        if self.read_in_dataset and self.read_in_data_header:
            # Zurücksetzen der Cluster-Zentren und der Anzeige in der TreeView, da neu initialisiert wird.
            self.current_centroids.clear()
            self.view_main_frame.clear_treeview_centroids_data()

            # Auswahl von k zufälligen Punkten als initiale Cluster-Zentren
            self.current_centroids = Model_k_means.get_k_random_data_objects(
                parameter_k=self.view_main_frame.selected_value_k.get(), dataset=self.read_in_dataset)

            # Anzeige in der Treeview
            self.view_main_frame.fill_treeview_centroids_with_data(dataset=self.current_centroids)

            # Zeichnen der Cluster-Zentren (ohne Anlegen der Historie oder Decision Areas der im Plot-Container)
            self.view_main_frame.draw_initial_centroids(centroids=self.current_centroids)
        else:
            View_Window.display_error_message(parent_window=self.view_main_frame.master,
                                              error_message="Es sind keine Daten geladen!")

    def activate_training(self):
        """
        Aktiviert bzw. setzt ein bisher durchgeführtes Training zurück.
        Soll das Training aktiviert werden, müssen Daten geladen und ausreichend Cluster-Zentren ausgewählt sein. Die
        View wird aktualisiert und der Status train_mode_active wird auf True gesetzt.
        Soll das Training deaktiviert/zurückgesetzt werden (d.h. aktuell train_mode_active=True), wird zuerst der
        Status geändert, die Cluster-Zentren betreffenden Attribute des Controllers zurückgesetzt auf den Stand, dass
        nur noch die initialen Zentren enthalten sind. Es wird die View angepasst und die Anzeige für die initialen
        Cluster-Zentren aktualisiert. (Plot-Container wird zurückgesetzt auf die initialen Cluster-Zentren)
        """
        # Zurücksetzen des Trainings, falls dieses aktiv war
        if self.train_mode_active:
            self.train_mode_active = not self.train_mode_active
            self.final_clusters_found = False
            self.auto_mode_train_step = 0
            self.auto_mode_init_step = True
            self.algorithm_step_one = True
            self.current_centroids = self.centroid_history[0]
            self.centroid_history.clear()
            self.previous_dataset_split_for_centroids.clear()
            self.current_dataset_split_for_centroids.clear()
            self.view_main_frame.clear_treeview_centroids_data()

            # Anpassung der View
            self.view_main_frame.update_view_train_mode(enable_train_mode=self.train_mode_active,
                                                        clusters_found=False)
            self.view_main_frame.update_view_train_button_algorithm_step_training()

            # Anzeige der initialen Cluster-Zentren in der Treeview
            self.view_main_frame.fill_treeview_centroids_with_data(dataset=self.current_centroids)

            # Anzeigen der initialen Cluster-Zentren und Zurücksetzen der Datenpunktfarbe
            self.view_main_frame.reset_for_start_training()

        # Aktivieren des Trainings, falls Daten geladen sind und genügend Cluster-Zentren ausgewählt sind
        else:
            err_msg = ""
            if self.read_in_data_header == () or self.read_in_dataset == []:
                err_msg = "Es sind keine Daten geladen!"
            elif self.view_main_frame.selected_value_k.get() > len(self.current_centroids):
                err_msg = "Es sind zu wenig Cluster-Zentren ausgewählt!"
            elif self.view_main_frame.selected_value_k.get() < len(self.current_centroids):
                err_msg = "Es sind zu viele Cluster-Zentren ausgewählt!"

            if err_msg == "":
                self.train_mode_active = not self.train_mode_active
                # Anpassung der View
                # An dieser Stelle sind die finalen Cluster noch nicht gefunden. Selbst wenn diese zufällig ausgewählt
                # wurden, muss in einem Trainingsschritt immer noch geprüft werden, ob diese final sind.
                # (final_centroids_found=False)
                self.view_main_frame.update_view_train_mode(enable_train_mode=self.train_mode_active,
                                                            clusters_found=False)
                # Hinzufügen der aktuellen Cluster-Zentren zur Historie, da dies nun auch die Zentren sind, welche im
                # Training verwendet werden sollen
                self.centroid_history.append(self.current_centroids)
                # Zeichnen der initialen Cluster-Zentren, Erstellen der Decision Areas, Färben der Punkte,...
                # self.current_dataset_split_for_centroids sind an dieser Stelle {}
                self.view_main_frame.draw_plot(centroids=self.current_centroids, before_training=True,
                                               split_dataset_centroids=self.current_dataset_split_for_centroids)

            else:
                View_Window.display_error_message(parent_window=self.view_main_frame.master, error_message=err_msg)

    def train(self):
        """
        Führt einen Trainingsschritt des k-means-Algorithmus aus, aktualisiert die Anzeige, erweitert die Historie
        sowie die Decision Areas und prüft, ob die finalen Cluster-Zentren bereits gefunden wurden.
        """
        perform_step_two = True
        if self.algorithm_step_one:
            self.helper_algorithm_step_one()
            # Falls das Algorithmen-Schritt-Training aktiv ist, ist der Schritt hier zu Ende und es muss die Anzeige-
            # fläche aktualisiert werden
            if self.view_main_frame.algorithm_step_training_active.get():
                # Anpassen der Punktfärbung
                self.view_main_frame.update_dataset(split_dataset_centroids=self.current_dataset_split_for_centroids)
                # Falls im Algorithmen-Schritt-Training bereits Schritt 1 ausgeführt wurde, soll Schritt 2 nicht mehr
                # ausgeführt werden.
                perform_step_two = False

        # Falls als Nächstes der Algorithmen-Schritt 2 ausgeführt werden soll
        if not self.algorithm_step_one and perform_step_two:
            self.final_clusters_found = not self.helper_algorithm_step_two()
            # Leeren und Anzeige der Koordinaten der berechneten Cluster-Zentren in der entsprechenden Treeview
            self.view_main_frame.clear_treeview_centroids_data()
            self.view_main_frame.fill_treeview_centroids_with_data(dataset=self.current_centroids)

            # Falls keine Änderung an den Clustern mehr stattgefunden hat, wurden die finalen Cluster und damit Zentren
            # gefunden.
            if self.final_clusters_found:
                # Anpassen der Punktfärbung
                self.view_main_frame.update_dataset(
                    split_dataset_centroids=self.current_dataset_split_for_centroids)
                # Deaktivieren der Trainingssteuerung und Anzeige einer Erfolgsmeldung
                self.view_main_frame.update_view_train_controls(enable=False)
                View_Window.display_info_message(parent_window=self.view_main_frame.master,
                                                 info_message="Erfolg! Cluster-Zentren gefunden!")
                # Im nächsten Schritt muss im AutoMode der Init Step stattfinden
                self.auto_mode_init_step = True
            # Andernfalls sind die finalen Cluster-Zentren noch nicht gefunden.
            else:
                # Anzeige der in diesem Trainingsschritt berechneten Cluster-Zentren in der Anzeigefläche
                self.view_main_frame.draw_plot(centroids=self.current_centroids, before_training=False,
                                               split_dataset_centroids=self.current_dataset_split_for_centroids)

        # Falls das Algorithmen-Schritt-Training aktiv ist, muss der Trainieren-Button aktualisiert werden
        if self.view_main_frame.algorithm_step_training_active.get():
            self.view_main_frame.update_view_train_button_algorithm_step_training(
                phase_nearest_points=self.algorithm_step_one)

    def activate_algorithm_step_training(self):
        """
        Setzt den Wechsel zwischen normalen Training und Einzelschritt-Training um, d.h. es werden die Schaltflächen in
        der Oberfläche entsprechend angepasst.
        """
        # Hier wird eigentlich nur die Anpassung der View aufgerufen.
        # Berechnungen finden erst in der train-Methode statt.
        # Algorithmen-Schritt-Training wird aktiviert
        if self.view_main_frame.algorithm_step_training_active.get():
            # Anpassen der Beschriftung des Trainieren-Buttons
            self.view_main_frame.update_view_train_button_algorithm_step_training(
                phase_nearest_points=self.algorithm_step_one)
        else:
            # Zurücksetzen des Trainieren-Buttons
            self.view_main_frame.update_view_train_button_algorithm_step_training()

    def train_complete(self):
        """
        Führt das Training des k-means-Algorithmus bis zum Finden der finalen Cluster-Zentren aus, aktualisiert die
        Anzeige, erweitert die Historie sowie die Decision Areas.
        """
        # Durch den Aufbau der View ist sichergestellt, dass Daten geladen und ausreichend Cluster-Zentren
        # ausgewählt sind
        # Abschließen eines ggf. noch nicht abgeschlossenen Trainingsschritts durch begonnenes
        # Algorithmen-Schritt-Training
        if not self.algorithm_step_one:
            self.final_clusters_found = not self.helper_algorithm_step_two()

            if self.final_clusters_found:
                # Anpassen der Punktfärbung
                self.view_main_frame.update_dataset(split_dataset_centroids=self.current_dataset_split_for_centroids)
                # Im nächsten Schritt muss im AutoMode der Init Step stattfinden
                self.auto_mode_init_step = True
            # Nur noch neue Elemente der Anzeigefläche berechnen, wenn eine Änderung der Cluster stattgefunden
            # hat, d.h. im letzten Schritt werden die Elemente nicht mehr neu erstellt
            else:
                # Erstellen der Elemente der Anzeigefläche und Speichern im Plot-Container. Angezeigt werden diese nur,
                self.view_main_frame.draw_plot(centroids=self.current_centroids, before_training=False,
                                               split_dataset_centroids=self.current_dataset_split_for_centroids,
                                               update_plot=False)

        while not self.final_clusters_found:
            self.helper_algorithm_step_one()
            self.final_clusters_found = not self.helper_algorithm_step_two()

            if self.final_clusters_found:
                # Anpassen der Punktfärbung und Aktualisierung der Anzeigefläche
                self.view_main_frame.update_dataset(split_dataset_centroids=self.current_dataset_split_for_centroids)
                # Im nächsten Schritt muss im AutoMode der Init Step stattfinden
                self.auto_mode_init_step = True
            # Nur noch neue Elemente der Anzeigefläche berechnen, wenn eine Änderung der Cluster stattgefunden
            # hat, d.h. im letzten Schritt werden die Elemente nicht mehr neu erstellt
            else:
                # Erstellen der Elemente der Anzeigefläche und Speichern im Plot-Container. Angezeigt werden diese nur,
                self.view_main_frame.draw_plot(centroids=self.current_centroids, before_training=False,
                                               split_dataset_centroids=self.current_dataset_split_for_centroids,
                                               update_plot=False)

        # Leeren und Anzeige der Koordinaten der finalen Cluster-Zentren in der entsprechenden Treeview
        self.view_main_frame.clear_treeview_centroids_data()
        self.view_main_frame.fill_treeview_centroids_with_data(dataset=self.current_centroids)

        # Deaktivieren der Trainingssteuerung
        self.view_main_frame.update_view_train_controls(enable=False)

    def helper_algorithm_step_one(self):
        """
        Hilfsmethode, welche den ersten Teil einer Trainingsrunde realisiert. Dies entspricht Schritt 1 im Einzelschritt
        Training. Dabei werden die Datenpunkte des Datensatzes bezüglich einer vorhandenen Menge an Cluster-Zentren
        aufgeteilt
        """
        # Speichern der letzten Aufteilung des Datensatzes
        self.previous_dataset_split_for_centroids = copy.deepcopy(self.current_dataset_split_for_centroids)
        # Aufteilung des Datensatzes auf die berechneten Cluster-Zentren
        self.current_dataset_split_for_centroids = Model_k_means.calculate_data_objects_for_centroids(
            distance_function=Model_k_means.squared_euclidean_distance, current_centroids=self.current_centroids,
            dataset=self.read_in_dataset)
        # Setzen des als nächsten auszuführenden Schritt
        self.algorithm_step_one = False

    def helper_algorithm_step_two(self):
        """
        Hilfsmethode, welche den zweiten Teil einer Trainingsrunde realisiert. Dies entspricht Schritt 2 im Einzelschritt
        Training. Auf Basis der in Schritt 1 berechneten Aufteilung des Datensatzes werden hier die Cluster-Zentren
        aktualisiert und zur Historie hinzugefügt. Im Anschluss wird überprüft, ob eine Änderung in den Cluster-Zentren
        stattgefunden hat und ein entsprechender Wahrheitswert zurückgegeben.
        :return: True, falls eine Änderung in der Menge der Cluster-Zentren bei der Aktualisierung stattgefunden hat,
                 False, falls keine Änderung mehr stattgefunden hat.
        """
        # Bestimmung der neuen Cluster-Zentren
        self.current_centroids = Model_k_means.calculate_centroids(
            dataset_split_by_centroid=self.current_dataset_split_for_centroids)
        self.centroid_history.append(self.current_centroids)
        # Setzen des als nächsten auszuführenden Schritt
        self.algorithm_step_one = True
        self.auto_mode_train_step = self.auto_mode_train_step + 1

        # centroid_history beinhaltet mindestens zwei Elemente (mind. die initialen Cluster-Zentren und die Cluster-
        # Zentren, die in diesem Trainingsschritt berechnet wurden)
        return Model_k_means.change_to_clusters(dataset_split_old=self.previous_dataset_split_for_centroids,
                                                dataset_split_new=self.current_dataset_split_for_centroids)
        # return Model_k_means.change_to_centroids(centroids_old=self.centroid_history[-2],
        #                                         centroids_new=self.centroid_history[-1])

    def increase_auto_mode_running_speed(self):
        """
        Erhöht die Geschwindigkeit des automatischen Ablaufs. Dafür wird der running_speed halbiert, welcher
        die Wartezeit zwischen den Iterationen darstellt.
        """
        self.auto_mode_running_speed = max(500, self.auto_mode_running_speed // 2)

        # Anpassen der Geschwindigkeitsbuttons
        self.view_main_frame.update_view_auto_mode_speed_bounds_reached(
            min_reached=self.auto_mode_running_speed == 2000,
            max_reached=self.auto_mode_running_speed == 500)

    def decrease_auto_mode_running_speed(self):
        """
        Reduziert die Geschwindigkeit des automatischen Ablaufs. Dafür wird der running_speed verdoppelt, welcher
        die Wartezeit zwischen den Iterationen darstellt.
        """
        self.auto_mode_running_speed = min(2000, self.auto_mode_running_speed * 2)

        # Anpassen der Geschwindigkeitsbuttons
        self.view_main_frame.update_view_auto_mode_speed_bounds_reached(
            min_reached=self.auto_mode_running_speed == 2000,
            max_reached=self.auto_mode_running_speed == 500)

    def auto_mode_running_method(self):
        """
        Realisiert eine Runde der Endlosanzeige des Trainingsverlaufs. Falls die finalen Cluster bereits
        gefunden wurden, wird nur noch mit der Historie gearbeitet. Eine Neuberechnung findet nicht mehr statt.
        Andernfalls wird normal trainiert und die Historie aufgebaut. Sobald die finalen Cluster gefunden wurden,
        arbeitet man mit der Historie weiter. Das Einzelschritt-Training wird unterstützt. Am Ende des Schritts wird
        eine gewisse Zeit gewartet.
        """
        # Falls die finalen Cluster bereits erstmalig gefunden wurden, soll nur noch mit der Historie
        # gearbeitet werden
        if self.final_clusters_found:
            # Wir befinden uns am Beginn eines neuen Durchlaufs. Es muss also zuerst die alte Information
            # entfernt werden
            # Der boolean ist nötig, da der auto_mode_training_step zwar auch erst hochgesetzt werden soll, sobald die
            # nächsten Zentren bestimmt werden
            if self.auto_mode_init_step:
                self.auto_mode_train_step = 0
                # Im nächsten Schritt muss ins reguläre Training übergegangen werden
                self.auto_mode_init_step = False
                self.current_centroids = self.centroid_history[self.auto_mode_train_step]
                # Initial sollen die blauen Punkte angezeigt werden
                self.current_dataset_split_for_centroids.clear()

                # Leeren und Anzeige der Koordinaten der berechneten Cluster-Zentren in der entsprechenden Treeview
                self.view_main_frame.clear_treeview_centroids_data()
                self.view_main_frame.fill_treeview_centroids_with_data(dataset=self.current_centroids)
                self.view_main_frame.update_plot_auto_mode(
                    split_dataset_centroids=self.current_dataset_split_for_centroids,
                    number_of_step=self.auto_mode_train_step)

            # Andernfalls befinden wir uns im Trainingsverlauf
            else:
                perform_step_two = True
                if self.algorithm_step_one:
                    self.helper_algorithm_step_one()
                    if self.view_main_frame.algorithm_step_training_active.get():
                        # Anpassen der Punktfärbung
                        self.view_main_frame.update_dataset(
                            split_dataset_centroids=self.current_dataset_split_for_centroids)
                        # Falls im Algorithmen-Schritt-Training bereits Schritt 1 ausgeführt wurde, soll Schritt 2
                        # nicht mehr ausgeführt werden.
                        perform_step_two = False

                # Falls als Nächstes der Algorithmen-Schritt 2 ausgeführt werden soll
                if not self.algorithm_step_one and perform_step_two:
                    # Hochzählen des Trainingsschritts um die Zentren des jeweiligen Schritts aus der Historie zu holen
                    self.auto_mode_train_step = self.auto_mode_train_step + 1
                    self.current_centroids = self.centroid_history[self.auto_mode_train_step]
                    if self.auto_mode_train_step == (len(self.centroid_history) - 1):
                        # Anpassen der Punktfärbung
                        self.view_main_frame.update_dataset(
                            split_dataset_centroids=self.current_dataset_split_for_centroids)
                        # Im nächsten Schritt muss im AutoMode der Init Step stattfinden
                        self.auto_mode_init_step = True
                    else:
                        # Leeren und Anzeige der Koordinaten der berechneten Cluster-Zentren in der entsprechenden
                        # Treeview
                        self.view_main_frame.clear_treeview_centroids_data()
                        self.view_main_frame.fill_treeview_centroids_with_data(dataset=self.current_centroids)
                        self.view_main_frame.update_plot_auto_mode(
                            split_dataset_centroids=self.current_dataset_split_for_centroids,
                            number_of_step=self.auto_mode_train_step)
                    self.algorithm_step_one = True
        # Falls die finalen Cluster noch nicht erstmalig gefunden wurden, muss zuerst die Historie während des
        # Trainingsprozesses aufgebaut werden
        else:
            perform_step_two = True
            if self.algorithm_step_one:
                self.helper_algorithm_step_one()
                # Falls das Algorithmen-Schritt-Training aktiv ist, ist der Schritt hier zu Ende und es muss die
                # Anzeige- fläche aktualisiert werden
                if self.view_main_frame.algorithm_step_training_active.get():
                    # Anpassen der Punktfärbung
                    self.view_main_frame.update_dataset(
                        split_dataset_centroids=self.current_dataset_split_for_centroids)
                    # Falls im Algorithmen-Schritt-Training bereits Schritt 1 ausgeführt wurde, soll Schritt 2 nicht
                    # mehr ausgeführt werden.
                    perform_step_two = False

            # Falls als Nächstes der Algorithmen-Schritt 2 ausgeführt werden soll
            if not self.algorithm_step_one and perform_step_two:
                self.final_clusters_found = not self.helper_algorithm_step_two()
                # Leeren und Anzeige der Koordinaten der berechneten Cluster-Zentren in der entsprechenden Treeview
                self.view_main_frame.clear_treeview_centroids_data()
                self.view_main_frame.fill_treeview_centroids_with_data(dataset=self.current_centroids)

                # Falls keine Änderung an den Clustern mehr stattgefunden hat, wurden die finalen Cluster und damit auch
                # die Zentren gefunden.
                if self.final_clusters_found:
                    # Anpassen der Punktfärbung
                    self.view_main_frame.update_dataset(
                        split_dataset_centroids=self.current_dataset_split_for_centroids)
                    # Im nächsten Schritt muss im AutoMode der Init Step stattfinden
                    self.auto_mode_init_step = True

                    # Deaktivieren der Trainingssteuerung
                    self.view_main_frame.update_view_train_disable_controls_found_auto_mode()
                # Andernfalls sind die finalen Cluster-Zentren noch nicht gefunden.
                else:
                    # Anzeige der in diesem Trainingsschritt berechneten Cluster-Zentren in der Anzeigefläche
                    self.view_main_frame.draw_plot(centroids=self.current_centroids, before_training=False,
                                                   split_dataset_centroids=self.current_dataset_split_for_centroids)

        # Falls das Algorithmen-Schritt-Training aktiv ist, muss die Phase aktualisiert werden und der Trainieren-Button
        # aktualisiert werden
        if self.view_main_frame.algorithm_step_training_active.get():
            self.view_main_frame.update_view_train_button_algorithm_step_training(
                phase_nearest_points=self.algorithm_step_one)

        # Warten zwischen den Trainingsrunden und anschließender Aufruf der Methode selbst
        # Speicherung der callID des Aufrufs der auto_mode_running_method um bei Beendigung des Auto-Modus diesen
        # direkt abbrechen zu können
        self.ID_CALLBACK_Auto_Mode = self.view_main_frame.after(ms=self.auto_mode_running_speed,
                                                                func=self.auto_mode_running_method)

    def auto_mode_control(self):
        """
        Startet bzw. beendet den automatischen Modus der Endlosanzeige des Trainingsverlaufs. Dafür wird die Oberfläche
        angepasst und beim Beenden ein ggf. noch wartender Aufruf beendet.
        """
        # Über die Oberfläche ist sichergestellt, dass der Trainingsmodus aktiv ist, sprich es sind Trainingsdaten
        # geladen und Cluster-Zentren vorhanden
        self.auto_mode_running = not self.auto_mode_running
        # Wechsel der Kontrollbuttons
        self.view_main_frame.update_view_train_controls_auto_mode_activation(enable=self.auto_mode_running)
        self.view_main_frame.update_view_train_mode_analysis_control(enable=not self.auto_mode_running)

        # Starten des automatischen Modus
        if self.auto_mode_running:
            self.auto_mode_running_speed = 1000
            # Starten der automatischen Ausführung
            self.auto_mode_running_method()

        # Beenden des automatischen Modus
        else:
            # Sicherheitsmaßnahme, dass kein Trainingsprozess neu gestartet werden kann, bevor der alte sauber
            # beendet wurde
            self.view_main_frame.update_view_btn_auto_mode(enable=False)

            # Beenden der automatischen Ausführung, falls momentan noch ein Aufruf am Warten ist
            if self.ID_CALLBACK_Auto_Mode is not None:
                self.view_main_frame.after_cancel(self.ID_CALLBACK_Auto_Mode)
                self.ID_CALLBACK_Auto_Mode = None

            # Rückgängigmachen von Sicherheitsmaßnahme
            self.view_main_frame.update_view_btn_auto_mode(enable=True)

    def display_centroid_history(self):
        """
        Ruft die Aktualisierung der Anzeige (Ein- bzw. Ausblenden) der Cluster-Zentren-Historie auf.
        """
        # Falls wir im letzten Schritt des Trainings sind, d.h. im Kontrollschritt, wurden keine neuen Zentren(Line2D)
        # in der Anzeigefläche berechnet, da diese sich nicht mehr ändern in diesem Schritt.
        if self.final_clusters_found and len(self.centroid_history) - 1 == self.auto_mode_train_step:
            self.view_main_frame.display_centroid_history(step_number=self.auto_mode_train_step - 1)
        else:
            self.view_main_frame.display_centroid_history(step_number=self.auto_mode_train_step)

    def display_decision_areas(self):
        """
        Ruft die Aktualisierung der Anzeige (Ein- bzw. Ausblenden) der Decision Areas auf.
        """
        # Falls wir im letzten Schritt des Trainings sind, d.h. im Kontrollschritt, wurden keine neuen Decision Areas
        # berechnet, da diese sich nicht mehr ändern in diesem Schritt. Man greift also auf die aus dem Vorschritt
        # zurück
        if self.final_clusters_found and len(self.centroid_history) - 1 == self.auto_mode_train_step:
            self.view_main_frame.display_decision_areas(index_to_show=self.auto_mode_train_step - 1)
        # Andernfalls wird auf die Decision Areas des aktuellen Schritts zurückgegriffen.
        else:
            self.view_main_frame.display_decision_areas(index_to_show=self.auto_mode_train_step)

    def display_axis(self):
        """
        Methode, welche aufgerufen wird, wenn die Checkbox zur Anzeige der Achsen-Ticks/Koordinatengitters aktiviert
        oder deaktiviert wird.
        """
        self.view_main_frame.display_plot_axis()

    def init_plot_area(self):
        """
        Initialisiert die Anzeigefläche für die Eingabe der Datenpunkte via Klick neu. Zuerst werden die eingegebenen
        Abmessungen der Anzeigefläche überprüft. Des Weiteren werden die Attribute zur Speicherung der Datenpunkte,
        Cluster-Zentren, usw. zurückgesetzt. Wurden zulässige Werte für die Abmessungen des Anzeigebereichs
        eingegeben, wird dieser geleert (Plot-Container und dessen Attribute,...) und mit den eingelesenen Abmessungen
        initialisiert.
        Andernfalls wird die Anzeigefläche geleert (inkl. Plot-Container) und mit Standardwerten initialisiert.
        Zusätzlich wird eine Fehlermeldung ausgegeben.
        """
        # Eingaben prüfen
        err_msg = ""

        try:
            self.current_x_low = int(self.view_main_frame.entered_x_low.get())
        except ValueError:
            err_msg += "Die untere Grenze der x-Werte ist keine ganze Zahl!\n"
            self.view_main_frame.entered_x_low.set("")

        try:
            self.current_x_high = int(self.view_main_frame.entered_x_high.get())
        except ValueError:
            err_msg += "Die obere Grenze der x-Werte ist keine ganze Zahl!\n"
            self.view_main_frame.entered_x_high.set("")

        try:
            self.current_y_low = int(self.view_main_frame.entered_y_low.get())
        except ValueError:
            err_msg += "Die untere Grenze der y-Werte ist keine ganze Zahl!\n"
            self.view_main_frame.entered_y_low.set("")

        try:
            self.current_y_high = int(self.view_main_frame.entered_y_high.get())
        except ValueError:
            err_msg += "Die obere Grenze der y-Werte ist keine ganze Zahl!\n"
            self.view_main_frame.entered_y_high.set("")

        if err_msg == "" and (
                self.current_x_low < -100 or self.current_y_low < -100 or self.current_x_high > 100 or
                self.current_y_high > 100):
            err_msg += "Die x-Achse und y-Achse müssen sich im Bereich [-100; 100] befinden!\n"

        if err_msg == "" and (self.current_x_low >= self.current_x_high or self.current_y_low >= self.current_y_high):
            err_msg += "Die untere Grenze muss jeweils echt kleiner sein als die obere Grenze!"

        # Zurücksetzen der Attribute
        self.read_in_data_header = self.DEFAULT_HEADER
        self.read_in_dataset.clear()
        self.current_centroids.clear()

        # Zurücksetzen des Sliders für die Auswahl des Parameters k
        self.reset_slider_k_treeview_data(max_value_k=self.MIN_VALUE_K)

        if err_msg == "":
            self.view_main_frame.reset_plot(plot_dimensions=[[self.current_x_low, self.current_x_high],
                                                             [self.current_y_low, self.current_y_high]],
                                            axis_labels=self.read_in_data_header)
        else:
            self.view_main_frame.reset_plot(axis_labels=self.read_in_data_header)
            View_Window.display_error_message(parent_window=self.view_main_frame.master, error_message=err_msg)

    def delete_entered_datapoints(self):
        """
        Entfernt die durch Klick zum Plot hinzugefügten Datenpunkte (und ggf. enthaltenen Cluster-Zentren),
        aktualisiert die Anzeige und löscht die gespeicherten Datenpunkte ggf. inkl. Cluster-Zentren.
        """
        # Löschen der Daten
        self.read_in_dataset.clear()
        # Löschen ggf. bereits vorhandener Cluster-Zentren
        self.current_centroids.clear()

        # Zurücksetzen des Sliders für die Auswahl von k
        self.reset_slider_k_treeview_data(max_value_k=self.MIN_VALUE_K)

        # Zurücksetzen der Anzeigefläche mit den eingegebenen Abmessungen
        self.view_main_frame.reset_plot(axis_labels=self.read_in_data_header,
                                        plot_dimensions=[[self.current_x_low, self.current_x_high],
                                                         [self.current_y_low, self.current_y_high]])

    def export_data_points_as_csv(self):
        """
        Speichert die aktuell vorliegenden Datenpunkte (read_in_data_header und read_in_dataset) in einer csv-Datei mit
        Namen "Datenpunkte" ab. Der Speicherort wird durch ein Auswahlfenster abgefragt.
        """
        if self.read_in_data_header and self.read_in_dataset:
            try:
                filepath = askdirectory()
                CSV_Utils.write_to_csv(filepath=filepath, data_header=self.read_in_data_header,
                                       data_to_write=self.read_in_dataset)
            except PermissionError:
                View_Window.display_error_message(parent_window=self.view_main_frame.master,
                                                  error_message="Es wurde kein Ordner ausgewählt.")
            except:
                View_Window.display_error_message(parent_window=self.view_main_frame.master,
                                                  error_message="Es ist ein Fehler aufgetreten.")

        else:
            View_Window.display_error_message(parent_window=self.view_main_frame.master,
                                              error_message="Es sind keine Datenpunkte für den Export vorhanden.")

    def delete_entered_centroids(self):
        """
        Löscht die ggf. aktuell vorhanden Cluster-Zentren aus dem Controller, von der Anzeigefläche und aus der Treeview
        zur Anzeige der Koordinaten der Zentren.
        """
        # Es müssen nur die Cluster-Zentren gelöscht werden. Außerhalb des Trainings werden die aufgeteilten Datenpunkte
        # nicht benötigt und da diese beim Deaktivieren des Trainings geleert werden, müssen sie an dieser Stelle nicht
        # behandelt werden
        self.current_centroids.clear()

        # Entfernen der Koordinaten ggf. vorhandener Cluster-Zentren aus der Treeview-Anzeige
        self.view_main_frame.clear_treeview_centroids_data()
        self.view_main_frame.fill_treeview_centroids_with_data(
            dataset=[("", "")] * self.view_main_frame.selected_value_k.get())

        # Entfernen aller Cluster-Zentren aus der Anzeigefläche
        self.view_main_frame.delete_centroids()

    def activate_data_point_input_on_click(self):
        """
        Ändert den Status der Datenpunkteingabe per Klick. Updatet dann im Anschluss in Abhängigkeit vom
        Status STATE_click_input_data_points_active die View. Sperrt bzw. entsperrt die Eingabemöglichkeiten während die
        Datenpunkteingabe per Klick aktiv ist. Bindet bzw. entfernt die Event-Callbackfunktionen für die
        Eingabe von Punkten per Klick.
        """
        self.STATE_click_input_data_points_active = not self.STATE_click_input_data_points_active
        # Sperren/Entsperren der Eingabe
        self.view_main_frame.update_view_data_point_selection_on_click(
            disable_data_point_selection=self.STATE_click_input_data_points_active)
        self.view_main_frame.btn_activate_selection_of_datapoints_on_click.update()
        if self.STATE_click_input_data_points_active:
            self.ID_CALLBACK_Mouse_Pressed_event = self.view_main_frame.canvas_display_model.figure.canvas.mpl_connect(
                'button_press_event', self.add_remove_data_point_on_click)
            self.ID_CALLBACK_Pick_event = self.view_main_frame.canvas_display_model.figure.canvas.mpl_connect(
                'pick_event', self.add_remove_data_point_on_click)
        else:
            self.unbind_callbacks_canvas()

    def activate_centroid_input_on_click(self):
        """
        Ändert den Status Auswahl der Cluster-Zentren per Klick. Updatet dann im Anschluss in Abhängigkeit vom
        Status STATE_click_input_centroids_active die View. Sperrt bzw. entsperrt die Eingabemöglichkeiten während die
        Zentren-Eingabe per Klick aktiv ist. Bindet bzw. entfernt die Event-Callbackfunktionen für die
        Eingabe von Cluster-Zentren per Klick.
        """
        if self.read_in_dataset and self.read_in_data_header:
            self.STATE_click_input_centroids_active = not self.STATE_click_input_centroids_active
            if self.STATE_click_input_centroids_active:
                # Sperren der Eingabe
                self.view_main_frame.update_view_centroid_selection_on_click(
                    disable_centroid_selection=self.STATE_click_input_centroids_active)
                self.view_main_frame.btn_activate_selection_of_centroids_on_click.update()
                # Mouse Pressed wird hier nicht benötigt
                self.ID_CALLBACK_Pick_event = self.view_main_frame.canvas_display_model.figure.canvas.mpl_connect(
                    'pick_event', self.select_unselect_centroid_on_click)
            else:
                self.unbind_callbacks_canvas()
                # Entsperren der Eingabe
                self.view_main_frame.btn_activate_selection_of_centroids_on_click.update()
                self.view_main_frame.update_view_centroid_selection_on_click(
                    disable_centroid_selection=self.STATE_click_input_centroids_active)

        else:
            View_Window.display_error_message(parent_window=self.view_main_frame.master,
                                              error_message="Es sind keine Daten geladen!")

    def switch_data_input_mode(self, event):
        """
        Setzt den Wechsel des Dateieingabemodus um. Bei Änderung des Eingabemodus werden die Attribute zum Speichern
        der Daten, Cluster-Zentren,... und die Anzeigefläche zurückgesetzt.
        :param event: Event
        """
        # Anpassen der View je nach gewähltem Dateieingabemodus
        self.view_main_frame.update_view_data_selection()

        self.read_in_dataset.clear()
        self.selected_filepath = ""
        self.view_main_frame.display_selected_filepath_training_data(filepath=self.selected_filepath)

        self.STATE_click_input_data_points_active = False
        self.STATE_click_input_centroids_active = False

        self.current_centroids.clear()

        self.current_x_low = self.default_X_LOW
        self.current_x_high = self.default_X_HIGH
        self.current_y_low = self.default_Y_LOW
        self.current_y_high = self.default_Y_HIGH

        # Setzen des Headers in Abhängigkeit vom gewählten Modus und initialisieren des Headers im Fall der
        # Mauseingabe, da in diesem Fall nur die Standardbezeichnungen für die x und y-Koordinate möglich sind
        if self.view_main_frame.get_data_selection_mode() == self.view_main_frame.DATA_INPUT_MODE_on_click:
            self.read_in_data_header = self.DEFAULT_HEADER
        else:
            self.read_in_data_header = ()
        self.view_main_frame.clear_treeview_centroids_header()
        self.view_main_frame.fill_treeview_centroids_with_header(header=self.read_in_data_header)

        # Zurücksetzen des Sliders (passt auch die Treeview an)
        self.reset_slider_k_treeview_data(max_value_k=self.MIN_VALUE_K)

        # Zurücksetzen der Anzeigefläche mit den eingegebenen Abmessungen
        self.view_main_frame.reset_plot()

        # Entfernt ggf. an die Anzeigefläche gebundene Event-Callbacks und setzt die Attribute zum Speichern derer
        # IDs zurück
        self.unbind_callbacks_canvas()

    def add_remove_data_point_on_click(self, event):
        """
        Regelt das Hinzufügen und Entfernen von Datenpunkten per Klick.
        Bei Linksklick wird, falls an der Klickstelle noch kein Datenpunkt existiert, ein neuer Datenpunkt zum
        verwendeten Datensatz read_in_data und zum Plot_Container(Line2D) hinzugefügt und auf der Anzeigefläche
        angezeigt.
        Bei Rechtsklick, falls dadurch ein Punkt der Anzeigefläche ausgewählt wurde, wird dieser aus dem verwendeten
        Datensatz read_in_data entfernt, aus dem Plot_Container entfernt und die Anzeigefläche wird aktualisiert.
        Insgesamt defensiv programmiert, da immer sowohl der Plot-Container als auch die Attribute im Controller über-
        prüft werden.
        :param event: auslösendes Event
        """
        if isinstance(event, PickEvent):
            # Falls ein Rechtsklick gemacht wurde und es sich um einen Punkt handelt
            if (event.mouseevent.button == 3 and isinstance(event.artist, Line2D) and (
                    event.artist.get_xdata()[0], event.artist.get_ydata()[0]) in self.read_in_dataset and
                    event.artist in self.view_main_frame.get_dataset_Line2D()):
                # Entfernen des Datenpunkts Tupel (x,y) aus read_in_dataset
                self.read_in_dataset.remove((event.artist.get_xdata()[0], event.artist.get_ydata()[0]))
                # Entfernen des Datenpunkts auf der Zeichenfläche und Entfernen aus dem Plot_Container
                self.view_main_frame.remove_data_point(data_point=(
                    event.artist.get_xdata()[0], event.artist.get_ydata()[0]))
                # Aktualisieren des Wertebereichs des Sliders für die Auswahl von k
                self.view_main_frame.set_scale_area_slider_parameter_k(
                    max_value_k=min(self.DEFAULT_BORDER_K, len(self.read_in_dataset)))
        # Falls ein Linksklick gemacht wurde und an der Stelle kein Punkt vorhanden ist
        elif isinstance(event, MouseEvent) and event.button == 1:
            if event.inaxes and (event.xdata, event.ydata) not in self.read_in_dataset:
                # Hinzufügen des Datenpunkts als Tupel (x,y) zu read_in_dataset
                self.read_in_dataset.append((event.xdata, event.ydata))
                # Zeichnen des Datenpunkts auf der Zeichenfläche und Hinzufügen zum Plot_Container
                self.view_main_frame.draw_data_point(x=event.xdata, y=event.ydata)
                # Aktualisieren des Wertebereichs des Sliders für die Auswahl von k
                self.view_main_frame.set_scale_area_slider_parameter_k(
                    max_value_k=min(self.DEFAULT_BORDER_K, len(self.read_in_dataset)))

    def select_unselect_centroid_on_click(self, event):
        """
        Regelt das Hinzufügen und Entfernen von Cluster-Zentren per Klick.
        Bei Linksklick wird, falls an der Klickstelle noch kein Zentrum existiert, aber ein Datenpunkt liegt und noch
        weitere Zentren bezüglich des Parameters k zugelassen sind, ein neues Zentrum eingefügt. Dieses wird in den
        Attributen des Controllers gespeichert und die Anzeigefläche (inkl. Plot-Container) sowie die Treeview werden
        aktualisiert. Der darunteliegende Punkt wird auf nicht auswählbar gesetzt.
        Bei Rechtsklick, falls dadurch ein Zentrum der Anzeigefläche ausgewählt wurde, wird dieses aus dem verwendeten
        Attribut current_centroids entfernt, aus dem Plot_Container entfernt und die Anzeigefläche wird aktualisiert.
        Insgesamt defensiv programmiert, da immer sowohl der Plot-Container als auch die Attribute im Controller über-
        prüft werden.
        :param event: auslösendes Event
        """
        if isinstance(event, PickEvent):
            # Falls ein Rechtsklick gemacht wurde, an der Stelle ein Datenpunkt, aber noch kein Cluster-Zentrum ist, und
            # noch weitere Cluster-Zentren bezüglich des Parameters k zugelassen sind, wird an der Stelle/auf des
            # ausgewählten Datenpunkts ein Cluster-Zentrum eingefügt
            if (event.mouseevent.button == 1 and isinstance(event.artist, Line2D) and (
                    event.artist.get_xdata()[0], event.artist.get_ydata()[0]) in self.read_in_dataset and
                    event.artist in self.view_main_frame.get_dataset_Line2D()):
                if ((event.artist.get_xdata()[0], event.artist.get_ydata()[0]) in self.current_centroids or
                        event.artist in self.view_main_frame.get_centroids_Line2D()):
                    View_Window.display_error_message(parent_window=self.view_main_frame.master,
                                                      error_message="Cluster-Zentrum existent bereits!")
                elif self.view_main_frame.selected_value_k.get() <= len(self.current_centroids):
                    View_Window.display_error_message(parent_window=self.view_main_frame.master,
                                                      error_message="Es sind bereits ausreichend Cluster-Zentren"
                                                                    " ausgew\u00E4hlt!")
                else:
                    # Hinzufügen des Cluster-Zentrums als Tupel (x,y) zu current_centroids
                    self.current_centroids.append((event.artist.get_xdata()[0], event.artist.get_ydata()[0]))
                    # Zeichnen des Cluster-Zentrums auf der Zeichenfläche und Hinzufügen zum Plot_Container
                    self.view_main_frame.draw_centroid(x=event.artist.get_xdata()[0], y=event.artist.get_ydata()[0])
                    # Anzeige der ausgewählten Cluster-Zentren in der Treeview
                    self.view_main_frame.clear_treeview_centroids_data()
                    self.view_main_frame.fill_treeview_centroids_with_data(
                        dataset=self.current_centroids + [("", "")] * (
                                self.view_main_frame.selected_value_k.get() - len(self.current_centroids)))
            # Falls ein Linksklick gemacht wurde und an der Stelle ein Zentrum liegt, wird dieses aus dem Controller
            # und der Anzeigefläche gelöscht und die Treeview wird aktualisiert mit den noch vorhandenen Zentren
            elif (event.mouseevent.button == 3 and isinstance(event.artist, Line2D)
                  and event.artist in self.view_main_frame.get_centroids_Line2D() and
                  (event.artist.get_xdata()[0], event.artist.get_ydata()[0]) in self.current_centroids):
                # Entfernen des Cluster-Zentrums als Tupel (x,y) aus current_centroids
                self.current_centroids.remove((event.artist.get_xdata()[0], event.artist.get_ydata()[0]))
                # Entfernen des Cluster-Zentrums von der Zeichenfläche und Entfernen aus dem Plot_Container
                self.view_main_frame.remove_centroid(
                    centroid=(event.artist.get_xdata()[0], event.artist.get_ydata()[0]))
                # Anzeige der verbleibenden Cluster-Zentren in der Treeview mit aktualisierter Nummerierung
                self.view_main_frame.clear_treeview_centroids_data()
                # Anzeige der (noch) vorhandenen Cluster-Zentren
                self.view_main_frame.fill_treeview_centroids_with_data(dataset=self.current_centroids + [("", "")] * (
                        self.view_main_frame.selected_value_k.get() - len(self.current_centroids)))

    def activate_parameter_analysis(self):
        """
        Aktiviert bzw. deaktiviert den Modus der Parameteranalyse. Beim Aktivieren wird die Oberfläche inklusive der
        Eingabemöglichkeiten entsprechend angepasst, die im Controller vorhandenen, für die Parameteranalyse nötigen
        Attribute zurückgesetzt und die Anzeigefläche des Parametergraphen (Ellenbogen- oder Silhouette) geleert.
        Beim Deaktivieren werden die Anpassungen der Oberfläche und Eingabemöglichkeiten rückgängig gemacht, eventuell
        vorhandene Callbacks des Distanzen-Plots entfernt und die Treeview mit den gegebenenfalls vorhandenen Cluster-
        Zentren gefüllt.
        """
        # Deaktivieren der Parameter-Analyse
        if self.parameter_analysis_active:
            self.parameter_analysis_active = not self.parameter_analysis_active
            self.view_main_frame.update_view_activate_parameter_analysis(set_active=self.parameter_analysis_active)
            # Setzt die Anzeigefläche des Models wieder auf den Zustand vor Aktivierung der Parameter-Analyse zurück
            self.view_main_frame.switch_plot_model_parameter_analysis_distances(
                activate_parameter_analysis=self.parameter_analysis_active)
            # Entfernen ggf. vorhandener Callbacks zur Auswahl der Datenpunkte
            self.unbind_callbacks_canvas()

            # Zurücksetzen der Datenpunkte in den richtigen Layer für das Training
            self.view_main_frame.update_layer_of_datapoints(in_front=False)

            # Füllen der Treeview mit den für das Training ggf. vorhandenen Cluster-Zentren
            self.view_main_frame.clear_treeview_centroids_data()
            self.view_main_frame.fill_treeview_centroids_with_data(dataset=self.current_centroids)
        # Aktivieren der Parameter-Analyse
        else:
            if self.read_in_data_header == () or self.read_in_dataset == []:
                err_msg = "Es sind keine Daten geladen!"
                View_Window.display_error_message(parent_window=self.view_main_frame.master, error_message=err_msg)
            else:
                self.parameter_analysis_active = not self.parameter_analysis_active
                self.view_main_frame.update_view_activate_parameter_analysis(set_active=self.parameter_analysis_active,
                                                                             number_of_datapoints=len(
                                                                                 self.read_in_dataset))
                # Bereitet die Anzeigefläche des Models für die Anzeige der Distanzen-Plots vor
                self.view_main_frame.switch_plot_model_parameter_analysis_distances(
                    activate_parameter_analysis=self.parameter_analysis_active)
                # Setzt die Attribute und die Anzeige des Analysegraphen zurück
                self.list_final_cluster_sets_distance_plot_elbow_analysis.clear()
                self.dict_distances_for_datapoints.clear()
                self.view_main_frame.reset_parameter_analysis_plot()

    def calculate_parameter_analysis(self):
        """
        Führt die Berechnungen der Parameteranalyse durch. Falls die Ellbogenanalyse ausgewählt ist, werden zuerst die
        möglichen Werte für k, die WCSS und die Aufteilung der Datenpunkte auf die jeweiligen finalen Cluster-
        Zentren bestimmt. Danach wird der Analysegraph gezeichnet die Elemente des Distanzen-Plots berechnet.
        Falls die Silhouetten-Analyse ausgewählt ist, wird zuerst der Wert von k bestimmt. Im Anschluss daran werden die
        Silhouetten und die mittleren Distanzen der Datenpunkte zum jeweils eigenen Cluster, als auch zum am nächsten
        liegenden Cluster bestimmt. Danach wird der Analysegraph gezeichnet die Elemente des Distanzen-Plots berechnet.
        Des Weiteren werden die für die Analyse berechneten, finalen Cluster-Zentren in der Treeview angezeigt und die
        Fortschrittsbalken zur Anzeige der Distanzenverhältnisse eines gewählten Datenpunkts anzuzeigen, zurückgesetzt.
        Für die Dauer der Berechnung wird die Oberfläche gesperrt, um einen erneuten Aufruf vor Abschluss des akutellen
        Aufrufs zu verhindern.
        """
        # Sperren der Eingabe während der Berechnung um erneute Ausführung vor Abschluss der Berechnung zu verhindern
        self.view_main_frame.update_view_enable_calculate_parameter_analysis(enable=False)
        self.view_main_frame.btn_calculate_analysis.update()
        # Falls die Ellbogenanalyse ausgewählt wird
        if self.view_main_frame.selected_analysis_mode.get() == self.ANALYSIS_MODE_elbow:
            max_k = min(self.DEFAULT_BORDER_K, len(self.read_in_dataset))
            try:
                wcss_values, self.list_final_cluster_sets_distance_plot_elbow_analysis = Model_k_means.elbow_analysis(
                    dataset=self.read_in_dataset, max_value_of_k=max_k)
                # Der Slider muss zuerst auf 1 zurückgesetzt werden, da im nächsten Schritt der Wert des Sliders für das
                # Update des Distanzplots verwendet wird; Verwendung der keys zulässig, da finale Cluster
                self.reset_slider_k_treeview_data_parameter_analysis(max_value_k=max_k, centroids=list(
                    self.list_final_cluster_sets_distance_plot_elbow_analysis[0].keys()))
                # Erstellt den Analysegraph und die Distanzen-Plots
                self.view_main_frame.draw_parameter_analysis_elbow(max_value_k=max_k, values_y=wcss_values,
                                                                   list_final_cluster_sets=self.list_final_cluster_sets_distance_plot_elbow_analysis)
                self.view_main_frame.update_view_enable_tab_distance_plot(enable=True)
            except src.Exceptions.CalculationTooLong:
                err_msg = "Die Berechnung ben\u00F6tigt zu viel Zeit!"
                View_Window.display_error_message(parent_window=self.view_main_frame.master, error_message=err_msg)
                self.view_main_frame.update_view_enable_tab_distance_plot(enable=False)
                self.view_main_frame.reset_parameter_analysis_plot()
        # Falls die Silhouetten-Analyse ausgewählt wird
        else:
            # Über die View ist sichergestellt, dass nur Werte von k gewählt werden können, die zulässig sind.
            value_k_silhouette_analysis = int(self.view_main_frame.selected_value_k_silhouette.get())
            try:
                dict_silhouettes_for_final_clusters, self.dict_distances_for_datapoints = Model_k_means.calculate_silhouette_scores_dataset(
                    value_k=value_k_silhouette_analysis, dataset=self.read_in_dataset)
                self.view_main_frame.draw_parameter_analysis_silhouette(
                    information_set_for_final_clusters=dict_silhouettes_for_final_clusters)
                # Anzeige der berechneten finalen Cluster-Zentren in der Treeview
                self.view_main_frame.clear_treeview_centroids_data()
                # Verwendung der keys zulässig, da finale Cluster
                self.view_main_frame.fill_treeview_centroids_with_data(
                    dataset=list(dict_silhouettes_for_final_clusters.keys()))
                # Setzt die Fortschrittsbalken zur Anzeige der mittleren Distanzsummen zurück
                self.view_main_frame.update_prog_bars_distances(distances_as_tuple=(0, 0))
                self.view_main_frame.update_view_enable_tab_distance_plot(enable=True)
            except src.Exceptions.CalculationTooLong:
                err_msg = "Die Berechnung ben\u00F6tigt zu viel Zeit!"
                View_Window.display_error_message(parent_window=self.view_main_frame.master, error_message=err_msg)
                self.view_main_frame.update_view_enable_tab_distance_plot(enable=False)
                self.view_main_frame.reset_parameter_analysis_plot()
        # Entsperren der Eingabemöglichkeiten
        self.view_main_frame.btn_calculate_analysis.update()
        self.view_main_frame.update_view_enable_calculate_parameter_analysis(enable=True)

    def reset_slider_k_treeview_data_parameter_analysis(self, max_value_k, centroids):
        """
        Setzt den Wert des Sliders auf den Wert 1 und die Treeview-Daten zurück. Außerdem wird der Maximalwert des
        Sliders für die Auswahl des Distanzplots aktualisiert
        :param max_value_k: Maximalwert des Sliders
        :param centroids:
        """
        # Der Slider soll immer auf den Wert 1 gesetzt werden. Ändert sich dabei der Wert des Sliders, wird automatisch
        # auch ein Update/Reset der Treeview ausgeführt. Falls der Slider vorher schon bei 1 war, muss dies manuell
        # angestoßen werden. Ein Update des Slider-Wertebereichs triggert ein Update nur, wenn sich dadurch auch der
        # Wert des Sliders ändert, was durch das Zurücksetzen des Sliders nicht der Fall sein kann.
        if self.view_main_frame.selected_value_k_elbow.get() == 1:
            self.view_main_frame.clear_treeview_centroids_data()
            self.view_main_frame.fill_treeview_centroids_with_data(dataset=centroids)
        else:
            self.view_main_frame.set_slider_parameter_k_value_parameter_analysis_elbow_distance_plot(
                value=self.MIN_VALUE_K)
        self.view_main_frame.set_scale_area_slider_parameter_k_parameter_analysis_elbow_distance_plot(
            max_value_k=max_value_k)

    def display_elbow_distances_for_value_k(self, value):
        """
        Blendet den Distanzen-Plot der Ellbogenanalyse für den über den Slider ausgewählten Wert k an. Methode wird
        durch Betätigung des Sliders aufgerufen. Des Weiteren werden die für den gewählten Wert k für die Ellbogen-
        Analyse berechneten, finalen Cluster-Zentren in der Treeview angezeigt.
        :param value:
        """
        index_current_value_k = self.view_main_frame.selected_value_k_elbow.get() - 1
        self.view_main_frame.update_parameter_analysis_elbow_distance_plot(
            final_clusters_for_k=self.list_final_cluster_sets_distance_plot_elbow_analysis[index_current_value_k],
            index_current_value_k=index_current_value_k)
        self.view_main_frame.clear_treeview_centroids_data()
        # Verwendung der keys zulässig, da finale Cluster
        self.view_main_frame.fill_treeview_centroids_with_data(
            dataset=list(self.list_final_cluster_sets_distance_plot_elbow_analysis[index_current_value_k].keys()))

    def switch_parameter_analysis_mode(self, event):
        """
        Wird bei Verwendung der Combobox zur Auswahl des Analysemodus der Parameteranalyse aufgerufen. Blendet die
        für den in der View gewählten Analysemodus notwendigen Kontrollmöglichkeiten ein und setzt den Plot zur
        Anzeige des Analysegraphen zurück. Des Weiteren werden die Datenpunkte in den, für den gewählten Modus,
        benötigten Layer gesetzt und ggf. benötigte Callbacks zur Auswahl per Klick gesetzt bzw. wieder entfernt.
        :param event: Combobox-Auswahl-Event
        """
        self.view_main_frame.update_view_controls_parameter_plot_for_mode()
        self.view_main_frame.reset_parameter_analysis_plot()
        if self.view_main_frame.selected_analysis_mode.get() == self.ANALYSIS_MODE_elbow:
            # Setzt die Datenpunkte in den regulären Layer und entfernt Callbacks zur Auswahl der Punkte via Klick
            self.view_main_frame.update_layer_of_datapoints(in_front=False)
            self.unbind_callbacks_canvas()
        else:
            # Setzt die Datenpunkte in den Vordergrund und setzt Callbacks zur Auswahl der Punkte via Klick
            self.view_main_frame.update_layer_of_datapoints(in_front=True)
            self.ID_CALLBACK_Pick_event = self.view_main_frame.canvas_display_model.figure.canvas.mpl_connect(
                'pick_event', self.show_silhouette_distances_on_click)

    def show_silhouette_distances_on_click(self, event):
        """
        Zeigt die Distanzlinien eines geklickten Datenpunkts im Rahmen der Silhouetten-Analyse an. Defensiv programmiert
        d.h. es wird sowohl auf das Vorhandensein der Elemente im Plot-Container als auch im Controller geprüft.
        Wird auf einen Punkt geklickt, wird der zugehörige Distanzen-Plot der Silhouetten-Analyse eingeblendet und die
        Fortschrittsbalken zur Visualisierung des Verhältnisses der mittleren Distanzsumme des ausgewählten Punkts zum
        eigenen und nächsten Cluster werden aktualisiert.
        :param event: auslösendes Event
        """
        if isinstance(event, PickEvent) and event.mouseevent.button == 1:
            if isinstance(event.artist, Line2D) and (
                    event.artist.get_xdata()[0], event.artist.get_ydata()[
                        0]) in self.read_in_dataset and event.artist in self.view_main_frame.get_dataset_Line2D():
                self.view_main_frame.update_parameter_analysis_silhouette_distance_plot(
                    x_coordinate=event.artist.get_xdata()[0], y_coordinate=event.artist.get_ydata()[0])
                self.view_main_frame.update_prog_bars_distances(distances_as_tuple=self.dict_distances_for_datapoints[
                    (event.artist.get_xdata()[0], event.artist.get_ydata()[0])])

    def bind_view_button_commands(self):
        """
        Belegt die Eingabemöglichkeiten der View der Trainingssimulation mit den auszuführenden Methoden.
        """
        self.view_main_frame.btn_choose_data_file.config(command=self.open_file_training_data)
        self.view_main_frame.btn_random_initial_centroids.config(command=self.set_initial_centroids_random)
        self.view_main_frame.btn_initiate_train_mode.config(command=self.activate_training)
        self.view_main_frame.btn_train.config(command=self.train)
        self.view_main_frame.btn_finish_training.config(command=self.train_complete)
        self.view_main_frame.ck_btn_show_centroid_history.config(command=self.display_centroid_history)
        self.view_main_frame.ck_btn_show_decision_areas.config(command=self.display_decision_areas)
        self.view_main_frame.ck_btn_show_axis_ticks.config(command=self.display_axis)
        self.view_main_frame.com_box_data_input_mode.bind('<<ComboboxSelected>>', self.switch_data_input_mode)
        self.view_main_frame.btn_init_plot_area.config(command=self.init_plot_area)
        self.view_main_frame.btn_delete_datapoints.config(command=self.delete_entered_datapoints)
        self.view_main_frame.btn_export_datapoints_csv.config(command=self.export_data_points_as_csv)
        self.view_main_frame.btn_activate_selection_of_datapoints_on_click.config(
            command=self.activate_data_point_input_on_click)
        self.view_main_frame.btn_activate_selection_of_centroids_on_click.config(
            command=self.activate_centroid_input_on_click)
        self.view_main_frame.btn_delete_centroids.config(command=self.delete_entered_centroids)
        self.view_main_frame.btn_auto_train.config(command=self.auto_mode_control)
        self.view_main_frame.btn_auto_train_slower.config(command=self.decrease_auto_mode_running_speed)
        self.view_main_frame.btn_auto_train_faster.config(command=self.increase_auto_mode_running_speed)
        self.view_main_frame.btn_initiate_parameter_analysis.config(command=self.activate_parameter_analysis)
        self.view_main_frame.com_box_analysis_mode.bind('<<ComboboxSelected>>', self.switch_parameter_analysis_mode)
        self.view_main_frame.btn_calculate_analysis.config(command=self.calculate_parameter_analysis)
        self.view_main_frame.ck_btn_algorithm_step_training_on.config(command=self.activate_algorithm_step_training)
        self.view_main_frame.slider_parameter_k.config(command=self.adapt_parameter_k_changed)
        self.view_main_frame.slider_parameter_k_parameter_analysis_elbow.config(
            command=self.display_elbow_distances_for_value_k)

    def adapt_parameter_k_changed(self, value=None):
        """
        Realisiert die automatische Anpassung der Treeview an den mithilfe des Silders gewählten Parameter k.
        Dafür wird zuerst die Differenz zwischen dem gewählten Parameter k und der Anzahl der vorliegenden Cluster-
        Zentren bestimmt.
        Ist diese positiv, sind weniger Cluster-Zentren vorliegend als der Parameter k zulässt. In diesem Fall wird
        die Treeview um leere Plätze für die noch festzulegenden Cluster-Zentren erweitert.
        Ist die Differenz negativ, sind zu viele Cluster-Zentren vorliegend als der Parameter k zulässt. In diesem
        Fall werden die überzähligen Cluster-Zentren aus der Treeview entfernt. Dabei werden die Cluster-Zentren
        entsprechend ihres Index entfernt, wobei Zentren mit hohem Index zuerst entfernt werden.
        Des Weiteren werden die so entfernten Cluster-Zentren auch aus der Anzeigefläche entfernt.
        :param value:
        """
        diff_value_k_centroids = self.view_main_frame.selected_value_k.get() - len(self.current_centroids)
        # Es sind momentan zu wenig Cluster-Zentren ausgewählt
        if diff_value_k_centroids > 0:
            # Leeren der Treeview und Anzeige der vorhandenen Cluster-Zentren und der nötigen Leerzeilen
            self.view_main_frame.clear_treeview_centroids_data()
            self.view_main_frame.fill_treeview_centroids_with_data(
                dataset=self.current_centroids + [("", "")] * diff_value_k_centroids)
        # Es sind momentan zu viele Cluster-Zentren ausgewählt
        elif diff_value_k_centroids < 0:
            # Entfernen der überzähligen Cluster-Zentren von der Anzeigefläche inklusive Plot-Container
            for centroid in self.current_centroids[self.view_main_frame.selected_value_k.get():]:
                self.view_main_frame.remove_centroid(centroid=centroid)
            # Entfernen der überzähligen Cluster-Zentren aus dem Attribut des Controllers
            del self.current_centroids[self.view_main_frame.selected_value_k.get():]
            # Leeren der Treeview und Anzeige der vorhandenen Cluster-Zentren und der nötigen Leerzeilen
            self.view_main_frame.clear_treeview_centroids_data()
            self.view_main_frame.fill_treeview_centroids_with_data(dataset=self.current_centroids)

    def unbind_callbacks_canvas(self):
        """
        Entfernt die Bindung der ggf. in den Attributen ID_CALLBACK_Mouse_Pressed_event und ID_CALLBACK_Pick_event
        gespeicherten Event-Callbackfunktionen.
        """
        if self.ID_CALLBACK_Pick_event:
            self.view_main_frame.canvas_display_model.figure.canvas.mpl_disconnect(
                self.ID_CALLBACK_Pick_event)
            self.ID_CALLBACK_Pick_event = None
        if self.ID_CALLBACK_Mouse_Pressed_event:
            self.view_main_frame.canvas_display_model.figure.canvas.mpl_disconnect(
                self.ID_CALLBACK_Mouse_Pressed_event)
            self.ID_CALLBACK_Mouse_Pressed_event = None
