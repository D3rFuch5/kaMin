import tkinter as tk
import tkinter.ttk as ttk

import src.Exceptions
from src import Plot_Utils_Model, Plot_Utils_Analysis, View_Window

ANALYSIS_MODE_elbow = "Ellbogen-Analyse"
ANALYSIS_MODE_silhouette = "Silhouetten-Analyse"
SELECTABLE_ANALYSIS_MODES = [ANALYSIS_MODE_elbow, ANALYSIS_MODE_silhouette]
SELECTABLE_VALUES_K_SILHOUETTE = ["2", "3", "4", "5", "6", "7", "8", "9", "10"]


class Frame_Training(tk.Frame):
    """
    Klasse realisiert den Frame, welcher die Widgets für die Simulation des Trainingsprozesses enthält.
    Der Klasse erbt direkt aus der Klasse Frame von Tkinter
    """
    DATA_INPUT_MODE_file = "Aus Datei"
    DATA_INPUT_MODE_on_click = "Via Maus"

    def __init__(self, parent_window, logo_image, app_mode_variable):
        super().__init__(master=parent_window)

        # Dynamische Größenanpassung an das Fenster.
        # Alles in column 0 wird an die Breite des Fensters angepasst
        self.columnconfigure(index=0, weight=1)

        # Aktivierung der Ausdehnung des Anzeigebereichs
        self.rowconfigure(index=2, weight=1)

        # Widgets für die Auswahl der Trainingsdaten
        self.selected_data_input_mode = None
        self.selected_filepath_data_file = None
        self.entered_x_low = None
        self.entered_x_high = None
        self.entered_y_low = None
        self.entered_y_high = None
        self.frm_choose_data_container = None

        self.frm_choose_data_mode = None
        self.com_box_data_input_mode = None

        self.frm_choose_data_from_file = None
        self.btn_choose_data_file = None
        self.lbl_display_selected_filepath_data_file = None

        self.frm_choose_data_from_click = None
        self.lbl_range_x_axis = None
        self.etr_x_low = None
        self.lbl_range_x_axis_to = None
        self.etr_x_high = None
        self.lbl_range_y_axis = None
        self.etr_y_low = None
        self.lbl_range_y_axis_to = None
        self.etr_y_high = None
        self.btn_init_plot_area = None
        self.menu_modes = None
        self.menu_app_mode = None

        self.lbl_logo = None

        self.init_data_selection(logo_image=logo_image, mode_variable=app_mode_variable)

        # Widgets für die Einstellungen zu den Cluster-Zentren und Kontroll-Buttons
        self.selected_value_k = None
        self.show_axis_ticks = None
        self.frm_cluster_settings = None
        self.lbl_parameter_k = None
        self.frm_controls = None
        self.lbl_parameter_k_value = None
        self.slider_parameter_k = None
        self.lbl_selection_initial_centroids = None
        self.btn_random_initial_centroids = None
        self.btn_activate_selection_of_centroids_on_click = None
        self.btn_delete_centroids = None

        self.frm_settings_datapoint_on_click = None
        self.btn_activate_selection_of_datapoints_on_click = None
        self.frm_further_datapoints_settings = None
        self.btn_delete_datapoints = None
        self.btn_export_datapoints_csv = None

        self.frm_train_analysis_control = None
        self.btn_initiate_train_mode = None
        self.btn_initiate_parameter_analysis = None
        self.ck_btn_show_axis_ticks = None

        self.init_cluster_settings()

        # Widgets für die Anzeige der grafischen Anzeige und der ausgewählten Cluster-Zentren
        self.algorithm_step_training_active = None
        self.show_centroid_history = None
        self.show_decision_areas = None
        self.selected_value_k_elbow = None
        self.frm_display_model_container = None
        self.frm_display_model = None
        self.frm_display_model_controls = None
        self.btn_auto_train = None
        self.btn_train = None
        self.ck_btn_algorithm_step_training_on = None
        self.btn_finish_training = None
        self.ck_btn_show_centroid_history = None
        self.ck_btn_show_decision_areas = None
        self.btn_auto_train_faster = None
        self.btn_auto_train_slower = None
        self.canvas_display_model = None
        self.current_plot_model = None
        self.frm_display_elbow_distances_controls = None
        self.frm_label_container = None
        self.lbl_parameter_k_parameter_analysis_elbow = None
        self.lbl_parameter_k_value_parameter_analysis_elbow = None
        self.slider_parameter_k_parameter_analysis_elbow = None

        self.frm_display_distance_sums = None
        self.lbl_distA = None
        self.prog_bar_display_distA = None
        self.lbl_distB = None
        self.prog_bar_display_distB = None

        self.frm_display_centroid_information = None
        self.frm_display_centroids = None
        self.treeview_centroids = None
        self.scrollbar_vertical_display_centroids = None
        self.frm_display_WCSS = None
        self.lbl_WCSS = None

        # Widgets für die Anzeige der Analyse
        self.selected_analysis_mode = None
        self.selected_value_k_silhouette = None
        self.frm_display_analysis_container = None
        self.frm_display_analysis = None
        self.frm_display_analysis_controls = None
        self.frm_choose_analysis_mode = None
        self.com_box_analysis_mode = None
        self.frm_choose_value_k_silhouette = None
        self.com_box_value_k_silhouette = None
        self.btn_calculate_analysis = None
        self.canvas_display_analysis = None
        self.current_figure_analysis = None

        self.main_notebook = None
        self.init_notebook()

    def init_data_selection(self, logo_image, mode_variable):
        """
        Erstellt die Oberfläche zur Auswahl der Trainingsdatendatei, der Anzeige des ausgewählten Dateinamens und des
        Logos.
        """
        self.selected_data_input_mode = tk.StringVar()
        self.selected_filepath_data_file = tk.StringVar()

        self.entered_x_low = tk.StringVar()
        self.entered_x_high = tk.StringVar()
        self.entered_y_low = tk.StringVar()
        self.entered_y_high = tk.StringVar()

        # Frame, welcher alle Widgets in der Reihe der Datenauswahl enthält. Extra-Frame, da so die Auswahl des Modus
        # links mit fixer Größe umgesetzt werden konnte
        self.frm_choose_data_container = tk.Frame(master=self, borderwidth=0)
        self.frm_choose_data_container.grid(column=0, row=0, sticky="ew", padx=(2, 0), pady=(0, 10))
        # Ausdehnung des Bereichs für Auswahl der Datei auf die verfügbare Breite
        self.frm_choose_data_container.columnconfigure(index=1, weight=1)

        self.frm_choose_data_mode = tk.LabelFrame(master=self.frm_choose_data_container, text="Dateneingabe:",
                                                  font=View_Window.default_FONT_BOLD, borderwidth=0)
        self.frm_choose_data_mode.grid(column=0, row=0, sticky="nw", padx=(0, 10))
        self.com_box_data_input_mode = ttk.Combobox(master=self.frm_choose_data_mode,
                                                    textvariable=self.selected_data_input_mode,
                                                    state="readonly", width=24,
                                                    values=[self.DATA_INPUT_MODE_file, self.DATA_INPUT_MODE_on_click])
        self.com_box_data_input_mode.current(newindex=0)
        self.com_box_data_input_mode.grid(column=0, row=0, sticky="w")

        # Frame, welcher alle Widgets enthält, die zur Auswahl der Daten aus einer Datei nötig sind
        self.frm_choose_data_from_file = tk.LabelFrame(master=self.frm_choose_data_container,
                                                       text="W\u00E4hlen Sie eine Datei aus:",
                                                       borderwidth=0, font=View_Window.default_FONT_BOLD)
        self.frm_choose_data_from_file.grid(column=1, row=0, sticky="ew")
        # Ausdehnung des Bereichs für die Anzeige des Dateinamens auf verfügbare Breite
        self.frm_choose_data_from_file.columnconfigure(index=1, weight=1)

        self.btn_choose_data_file = ttk.Button(master=self.frm_choose_data_from_file, text="\u00D6ffnen", width=21)
        self.btn_choose_data_file.grid(column=0, row=0, sticky="e", padx=(2, 0))

        self.lbl_display_selected_filepath_data_file = ttk.Label(master=self.frm_choose_data_from_file)
        self.lbl_display_selected_filepath_data_file.grid(column=1, row=0, padx=(5, 0), sticky="ew")

        # Frame, welcher alle Widgets enthält, die zur Initialisierung nötig des Plots bei Eingabe der Datenpunkte
        # durch Klick nötig sind.
        # Wird noch nicht zur Oberfläche hinzugefügt, da standardmäßig die Datenaingabe via Datei ausgewählt ist
        self.frm_choose_data_from_click = tk.LabelFrame(master=self.frm_choose_data_container,
                                                        text="W\u00E4hlen Sie die Abmessungen des Anzeigebereichs aus:",
                                                        borderwidth=0, font=View_Window.default_FONT_BOLD)

        self.lbl_range_x_axis = ttk.Label(master=self.frm_choose_data_from_click, text="x-Achse:",
                                          font=View_Window.default_FONT_ITALIC)
        self.lbl_range_x_axis.grid(column=0, row=0, sticky="nw")
        self.etr_x_low = ttk.Entry(master=self.frm_choose_data_from_click, width=7, textvariable=self.entered_x_low)
        self.etr_x_low.grid(column=1, row=0, sticky="nw")
        self.lbl_range_x_axis_to = ttk.Label(master=self.frm_choose_data_from_click, text=" bis ",
                                             font=View_Window.default_FONT_ITALIC)
        self.lbl_range_x_axis_to.grid(column=2, row=0, sticky="nw")
        self.etr_x_high = ttk.Entry(master=self.frm_choose_data_from_click, width=7, textvariable=self.entered_x_high)
        self.etr_x_high.grid(column=3, row=0, sticky="nw", padx=(0, 10))

        self.lbl_range_y_axis = ttk.Label(master=self.frm_choose_data_from_click, text="y-Achse:",
                                          font=View_Window.default_FONT_ITALIC)
        self.lbl_range_y_axis.grid(column=4, row=0, sticky="nw")
        self.etr_y_low = ttk.Entry(master=self.frm_choose_data_from_click, width=7, textvariable=self.entered_y_low)
        self.etr_y_low.grid(column=5, row=0, sticky="nw")
        self.lbl_range_y_axis_to = ttk.Label(master=self.frm_choose_data_from_click, text=" bis ",
                                             font=View_Window.default_FONT_ITALIC)
        self.lbl_range_y_axis_to.grid(column=6, row=0, sticky="nw")
        self.etr_y_high = ttk.Entry(master=self.frm_choose_data_from_click, width=7, textvariable=self.entered_y_high)
        self.etr_y_high.grid(column=7, row=0, sticky="nw")

        self.btn_init_plot_area = ttk.Button(master=self.frm_choose_data_from_click, text="Initialisieren", width=21)
        self.btn_init_plot_area.grid(column=8, row=0, sticky="nw", padx=(5, 0))

        self.menu_modes = tk.Menu(tearoff=False)
        self.menu_modes.add_radiobutton(label=View_Window.APP_MODE_Simulation_K_Means, variable=mode_variable,
                                        value=View_Window.APP_MODE_Simulation_K_Means)
        self.menu_modes.add_radiobutton(label=View_Window.APP_MODE_Color_Quantization, variable=mode_variable,
                                        value=View_Window.APP_MODE_Color_Quantization)

        self.menu_app_mode = ttk.Menubutton(master=self.frm_choose_data_container, text="App-Modus",
                                            menu=self.menu_modes)
        self.menu_app_mode.grid(column=2, row=0, sticky="ne", padx=(0, 10))

        self.lbl_logo = ttk.Label(master=self.frm_choose_data_container, image=logo_image)
        self.lbl_logo.grid(column=3, row=0, sticky="e")

    def init_cluster_settings(self):
        """
        Erstellt die Oberfläche zur Auswahl des Parameters k, die Festlegung der initialen Cluster-Zentren und der
        Kontroll-Buttons.
        """
        self.selected_value_k = tk.IntVar()
        self.show_axis_ticks = tk.BooleanVar()
        self.frm_controls = ttk.Frame(master=self)
        self.frm_controls.grid(column=0, row=1, sticky="ew", padx=(1, 0))
        # Anpassung damit sich die drei Teilframes in frm_control mit der Fenstergröße anpassen
        self.frm_controls.columnconfigure(index=0, weight=1)
        self.frm_controls.columnconfigure(index=1, weight=1)
        # Freier Bereich in der Mitte des Kontroll-Frames
        self.frm_controls.columnconfigure(index=2, weight=5)
        self.frm_controls.columnconfigure(index=3, weight=1)

        self.frm_cluster_settings = tk.LabelFrame(master=self.frm_controls, text="Einstellungen f\u00FCr die "
                                                                                 "Cluster-Zentren:",
                                                  font=View_Window.default_FONT_BOLD)
        self.frm_cluster_settings.grid(column=0, row=0, sticky="nsew", padx=(2, 2))
        self.frm_cluster_settings.columnconfigure(index=0, weight=5)
        self.frm_cluster_settings.columnconfigure(index=1, weight=1)

        # Anzeigebereich für die Auswahl des Parameters k
        self.lbl_parameter_k = ttk.Label(master=self.frm_cluster_settings, text="Parameter k:",
                                         font=View_Window.default_FONT_ITALIC)
        self.lbl_parameter_k.grid(column=0, row=0, sticky="nwe", padx=(0, 5))

        self.lbl_parameter_k_value = ttk.Label(master=self.frm_cluster_settings, textvariable=self.selected_value_k,
                                               font=View_Window.default_FONT_ITALIC, width=3)
        self.lbl_parameter_k_value.grid(column=1, row=0, sticky="nwe")

        self.slider_parameter_k = tk.Scale(master=self.frm_cluster_settings, variable=self.selected_value_k, from_=1,
                                           to=1, orient=tk.HORIZONTAL, showvalue=False)
        self.slider_parameter_k.grid(column=0, row=1, columnspan=2, sticky="nwe", padx=(0, 10))

        # Anzeigebereich für die Auswahl der initialen Cluster-Zentren
        self.lbl_selection_initial_centroids = ttk.Label(master=self.frm_cluster_settings,
                                                         text="Initiale Clusterzentren:",
                                                         font=View_Window.default_FONT_ITALIC)
        self.lbl_selection_initial_centroids.grid(column=2, row=0, sticky="nww")
        self.btn_random_initial_centroids = ttk.Button(master=self.frm_cluster_settings,
                                                       text="Zuf\u00E4llig ausw\u00E4hlen", width=21)
        self.btn_random_initial_centroids.grid(column=2, row=1, sticky='nwe')
        self.btn_activate_selection_of_centroids_on_click = ttk.Button(master=self.frm_cluster_settings,
                                                                       text="Per Klick ausw\u00E4hlen", width=21)
        self.btn_activate_selection_of_centroids_on_click.grid(column=2, row=2, sticky="nwe")

        # Button vorbereiten zur Löschung aller Zentren auf einmal, wenn die Auswahl der Zentren per Klick aktiv ist
        self.btn_delete_centroids = ttk.Button(master=self.frm_cluster_settings,
                                               text="Cluster-Zentren l\u00F6schen", width=21)

        # Der Frame dient zur Anzeige der Einstellungen für die Eingabe von Datenpunkten per Klick.
        # Deshalb soll er nur in diesem Fall eingeblendet werden. Hier wird der Frame vorbereitet.
        self.frm_settings_datapoint_on_click = tk.LabelFrame(master=self.frm_controls,
                                                             text="Einstellungen f\u00FCr die Punkteingabe:",
                                                             font=View_Window.default_FONT_BOLD)
        # Anzeige der weiteren Einstellungen bündig unten
        self.frm_settings_datapoint_on_click.rowconfigure(index=1, weight=1)

        self.btn_activate_selection_of_datapoints_on_click = ttk.Button(master=self.frm_settings_datapoint_on_click,
                                                                        text="Eingabe aktivieren", width=21)
        self.btn_activate_selection_of_datapoints_on_click.grid(column=0, row=0, sticky="nw")

        self.frm_further_datapoints_settings = ttk.Frame(master=self.frm_settings_datapoint_on_click)
        self.frm_further_datapoints_settings.grid(column=0, row=1, sticky="sew")
        self.btn_delete_datapoints = ttk.Button(master=self.frm_further_datapoints_settings,
                                                text="Datenpunkte l\u00F6schen", width=21)
        self.btn_delete_datapoints.grid(column=0, row=0, sticky="nw")
        self.btn_export_datapoints_csv = ttk.Button(master=self.frm_further_datapoints_settings,
                                                    text="Als .csv-Datei exportieren", width=21)
        self.btn_export_datapoints_csv.grid(column=0, row=1, sticky="nw")

        # Oberfläche des Trainings-, Ellbogen- und silhouettenanalyse-Buttons
        self.frm_train_analysis_control = tk.LabelFrame(master=self.frm_controls,
                                                        text="Training und Analyse",
                                                        font=View_Window.default_FONT_BOLD)
        self.frm_train_analysis_control.grid(column=3, row=0, sticky="nsew", padx=(0, 1))
        self.frm_train_analysis_control.columnconfigure(index=0, weight=1)

        self.btn_initiate_train_mode = ttk.Button(master=self.frm_train_analysis_control,
                                                  text="Training beginnen", width=27)
        self.btn_initiate_train_mode.grid(column=0, row=0, sticky='ew', pady=(2, 2))

        self.btn_initiate_parameter_analysis = ttk.Button(master=self.frm_train_analysis_control,
                                                          text="Parameteranalyse aktivieren", width=27)
        self.btn_initiate_parameter_analysis.grid(column=0, row=1, sticky="ew", pady=(2, 2))

        self.ck_btn_show_axis_ticks = ttk.Checkbutton(master=self.frm_train_analysis_control,
                                                      text="Achsenbezeichnungen ausblenden",
                                                      takefocus=0,
                                                      variable=self.show_axis_ticks,
                                                      onvalue=True,
                                                      offvalue=False)
        self.ck_btn_show_axis_ticks.grid(column=0, row=2, sticky="sw")

    def init_notebook(self):
        # Erstellen des Notebooks
        self.main_notebook = ttk.Notebook(master=self)
        self.main_notebook.grid(column=0, row=2, sticky="nsew", pady=(5, 0))

        # Erstellen der Frames, welche im Notebook angezeigt werden/auswählbar sein sollen
        self.init_frame_display_model()

        self.init_frame_display_analysis()

        # Hinzufügen der Frames zum Notebook
        # Tab 0
        self.main_notebook.add(child=self.frm_display_model_container,
                               text="Grafische Darstellung des k-Means-Algorithmus  ",
                               sticky="nsew")
        # Tab 1
        self.main_notebook.add(child=self.frm_display_analysis_container,
                               text=" Parameter-Analyse ",
                               sticky="nsew")

        self.main_notebook.select(0)
        self.main_notebook.hide(tab_id=1)

    def init_frame_display_model(self):
        self.algorithm_step_training_active = tk.BooleanVar()
        self.show_centroid_history = tk.BooleanVar()
        self.show_decision_areas = tk.BooleanVar()
        self.selected_value_k_elbow = tk.IntVar()

        self.frm_display_model_container = tk.Frame(master=self.main_notebook, borderwidth=0, bg="white")
        self.frm_display_model_container.pack(fill="both", expand=True)
        # Ausbreitung des Plots und frm_display_model auf maximale Größe
        self.frm_display_model_container.columnconfigure(index=0, weight=1)
        self.frm_display_model_container.rowconfigure(index=0, weight=1)

        self.frm_display_model = tk.Frame(master=self.frm_display_model_container, bg="white", borderwidth=0)

        self.frm_display_model.grid(column=0, row=0, sticky="nsew")
        self.frm_display_model.columnconfigure(index=0, weight=1)
        self.frm_display_model.rowconfigure(index=0, weight=1)

        # Hier wird nur das Tkinter Canvas-Widget gespeichert. Dieses enthält eine Matplotlib-Figure und den aktuellen
        # Plot (Ax). Zugriff durch self.canvas_display_model.figure.get_axes()[0]. Alle Änderungen an der Figure bzw.
        # deren Plot (Ax) finden in den Plot_Utils statt und werden in der View nur aufgerufen.
        self.canvas_display_model = Plot_Utils_Model.initialize_figure(master=self.frm_display_model)
        self.current_plot_model = Plot_Utils_Model.Plot_Container(axes=self.canvas_display_model.figure.get_axes()[0])

        self.canvas_display_model.get_tk_widget().grid(column=0, row=0, sticky="nsew")

        # Anlegen der Kontroll-Buttons für das Training
        self.frm_display_model_controls = tk.Frame(master=self.frm_display_model, bg="white", borderwidth=0)
        self.frm_display_model_controls.grid(column=0, row=1, sticky="nsew", pady=(5, 0))
        self.frm_display_model_controls.columnconfigure(index=0, weight=1)
        self.frm_display_model_controls.columnconfigure(index=1, weight=1)
        self.frm_display_model_controls.columnconfigure(index=2, weight=1)
        self.frm_display_model_controls.columnconfigure(index=3, weight=1)
        self.frm_display_model_controls.rowconfigure(index=1, weight=1)
        self.btn_auto_train = ttk.Button(master=self.frm_display_model_controls, text="Automatisch trainieren",
                                         style="WhiteButton.TButton")
        self.btn_auto_train.grid(column=0, row=0, sticky="nwe", padx=(0, 2))
        self.btn_train = ttk.Button(master=self.frm_display_model_controls, text="Trainieren",
                                    style="WhiteButton.TButton")
        self.btn_train.grid(column=1, row=0, sticky="nwe", padx=(0, 2))
        self.btn_finish_training = ttk.Button(master=self.frm_display_model_controls, text="Training abschlie\u00DFen",
                                              style="WhiteButton.TButton")
        self.btn_finish_training.grid(column=2, row=0, sticky="nwe", padx=(0, 5))

        self.ck_btn_algorithm_step_training_on = ttk.Checkbutton(master=self.frm_display_model_controls,
                                                                 text="Training in Einzelschritten",
                                                                 takefocus=0,
                                                                 variable=self.algorithm_step_training_active,
                                                                 onvalue=True,
                                                                 offvalue=False,
                                                                 style="whiteCheckButton.TCheckbutton")
        self.ck_btn_algorithm_step_training_on.grid(column=1, row=1, sticky="nw", padx=(0, 2))
        self.ck_btn_show_centroid_history = ttk.Checkbutton(master=self.frm_display_model_controls,
                                                            text="Verlauf der Cluster-Zentren",
                                                            takefocus=0,
                                                            variable=self.show_centroid_history,
                                                            onvalue=True,
                                                            offvalue=False,
                                                            style="whiteCheckButton.TCheckbutton")
        self.ck_btn_show_centroid_history.grid(column=3, row=0, sticky="nw")
        self.ck_btn_show_decision_areas = ttk.Checkbutton(master=self.frm_display_model_controls,
                                                          text="Decision Areas zeigen",
                                                          takefocus=0,
                                                          variable=self.show_decision_areas,
                                                          onvalue=True,
                                                          offvalue=False,
                                                          style="whiteCheckButton.TCheckbutton")
        self.ck_btn_show_decision_areas.grid(column=3, row=1, sticky="nw")

        # Vorbereitung der Buttons für das automatische Training. Diese werden noch nicht zur Oberfläche hinzugefügt,
        # sondern nur erstellt.
        self.btn_auto_train_faster = ttk.Button(master=self.frm_display_model_controls, text="Schneller",
                                                style="WhiteButton.TButton")
        self.btn_auto_train_slower = ttk.Button(master=self.frm_display_model_controls, text="Langsamer",
                                                style="WhiteButton.TButton")

        # Vorbereitung des Frames zur Kontrolle der Darstellung der Distanzen im Rahmen der Parameteranalyse Ellbogen
        self.frm_display_elbow_distances_controls = tk.Frame(master=self.frm_display_model, bg="white", borderwidth=0)
        # self.frm_display_elbow_distances_controls.grid(column=0, row=1, sticky="nsew", pady=(5, 0))
        self.frm_display_elbow_distances_controls.columnconfigure(index=0, weight=1)

        # Anzeigebereich für die Auswahl des Parameters k
        self.frm_label_container = tk.Frame(master=self.frm_display_elbow_distances_controls, bg="white", borderwidth=0)
        self.frm_label_container.grid(column=0, row=0, sticky="nw")
        self.lbl_parameter_k_parameter_analysis_elbow = ttk.Label(master=self.frm_label_container,
                                                                  text="Parameter k:",
                                                                  font=View_Window.default_FONT_ITALIC,
                                                                  style="whiteLabel.TLabel")
        self.lbl_parameter_k_parameter_analysis_elbow.grid(column=0, row=0, sticky="nw", padx=(0, 5))

        self.lbl_parameter_k_value_parameter_analysis_elbow = ttk.Label(master=self.frm_label_container,
                                                                        textvariable=self.selected_value_k_elbow,
                                                                        font=View_Window.default_FONT_ITALIC, width=3,
                                                                        style="whiteLabel.TLabel")
        self.lbl_parameter_k_value_parameter_analysis_elbow.grid(column=1, row=0, sticky="w")

        self.slider_parameter_k_parameter_analysis_elbow = tk.Scale(master=self.frm_display_elbow_distances_controls,
                                                                    variable=self.selected_value_k_elbow,
                                                                    background="white", from_=1,
                                                                    highlightbackground="white",
                                                                    to=1, orient=tk.HORIZONTAL, showvalue=False)
        self.slider_parameter_k_parameter_analysis_elbow.grid(column=0, row=1, sticky="nwe")

        # Vorbereitung des Frames zur Darstellung der Distanzensummen im Rahmen der Parameteranalyse Silhouette
        self.frm_display_distance_sums = tk.LabelFrame(master=self.frm_display_model, text="Mittlere Distanzsummen:",
                                                       font=View_Window.default_FONT_BOLD, borderwidth=0, bg="white")
        # Ausdehnung der Slider in Spalte 2
        self.frm_display_distance_sums.columnconfigure(index=1, weight=1)
        # self.frm_display_distance_sums.grid(column=0, row=1, sticky="nsew", padx=(0,5), pady=(5, 0))
        self.lbl_distA = ttk.Label(master=self.frm_display_distance_sums, text="Eigener Cluster: ",
                                   font=View_Window.default_FONT_ITALIC,
                                   style="whiteLabel.TLabel")
        self.lbl_distA.grid(column=0, row=0, sticky='nw')
        self.prog_bar_display_distA = ttk.Progressbar(master=self.frm_display_distance_sums, orient='horizontal',
                                                      mode='determinate',
                                                      style="blue.ColorProgress.Horizontal.TProgressbar")
        self.prog_bar_display_distA.grid(column=1, row=0, sticky="ew")
        self.lbl_distB = ttk.Label(master=self.frm_display_distance_sums, text="N\u00E4chster Cluster: ",
                                   font=View_Window.default_FONT_ITALIC,
                                   style="whiteLabel.TLabel")
        self.lbl_distB.grid(column=0, row=1, sticky='nw')
        self.prog_bar_display_distB = ttk.Progressbar(master=self.frm_display_distance_sums, orient='horizontal',
                                                      mode='determinate',
                                                      style="red.ColorProgress.Horizontal.TProgressbar")
        self.prog_bar_display_distB.grid(column=1, row=1, sticky="ew")

        self.frm_display_centroid_information = tk.Frame(master=self.frm_display_model_container,borderwidth=0, bg="white")
        self.frm_display_centroid_information.grid(column=1, row=0, sticky="ns", pady=(5, 0))
        # Ausdehnung der Anzeige maximal nach unten
        self.frm_display_centroid_information.rowconfigure(index=0, weight=1)

        self.frm_display_centroids = tk.LabelFrame(master=self.frm_display_centroid_information,
                                                              text="Cluster-Zentren:",
                                                              font=View_Window.default_FONT_BOLD, borderwidth=0, bg="white")
        self.frm_display_centroids.grid(column=0, row=0, sticky="ns", pady=(5, 0))
        # Ausdehnung der Treeview maximal nach unten
        self.frm_display_centroids.rowconfigure(index=0, weight=1)

        # TreeView zum Anzeigen der Daten
        self.treeview_centroids = ttk.Treeview(master=self.frm_display_centroids)
        self.init_treeview_centroids(number_of_columns=2, space_in_px=200)
        self.treeview_centroids.grid(column=0, row=0, sticky="nsew")

        self.scrollbar_vertical_display_centroids = ttk.Scrollbar(master=self.frm_display_centroids, orient="vertical")
        self.scrollbar_vertical_display_centroids.config(command=self.treeview_centroids.yview)
        self.scrollbar_vertical_display_centroids.grid(column=1, row=0, sticky="ens")
        self.treeview_centroids.configure(yscrollcommand=self.scrollbar_vertical_display_centroids.set)

        self.frm_display_WCSS = tk.LabelFrame(master=self.frm_display_centroid_information,
                                                   text="Within Cluster Squared Sum:",
                                                   font=View_Window.default_FONT_BOLD, borderwidth=0, bg="white")
        # Initial ausgeblendet
        # self.frm_display_WCSS.grid(column=0, row=1, sticky="new")
        self.lbl_WCSS = tk.Label(master=self.frm_display_WCSS, text="Noch nicht berechnet.", bg="white", font=View_Window.default_FONT)
        self.lbl_WCSS.grid(column=0, row=0, sticky="new")



    def init_frame_display_analysis(self):
        self.selected_analysis_mode = tk.StringVar()
        self.selected_value_k_silhouette = tk.StringVar()

        self.frm_display_analysis_container = tk.Frame(master=self.main_notebook, borderwidth=0)
        self.frm_display_analysis_container.pack(fill="both", expand=True)

        # Ausbreitung des Plots und frm_display_ auf maximale Größe
        self.frm_display_analysis_container.columnconfigure(index=0, weight=1)
        self.frm_display_analysis_container.rowconfigure(index=0, weight=1)

        # Frame, welcher alle Elemente der Analyseseite enthält
        self.frm_display_analysis = tk.Frame(master=self.frm_display_analysis_container, bg="white", borderwidth=0)
        self.frm_display_analysis.grid(column=0, row=0, sticky="nsew")
        self.frm_display_analysis.columnconfigure(index=0, weight=1)
        self.frm_display_analysis.rowconfigure(index=1, weight=1)

        # Anlegen der Widgets für die Analyse-Steuerung
        self.frm_display_analysis_controls = tk.Frame(master=self.frm_display_analysis, bg="white", borderwidth=0)
        self.frm_display_analysis_controls.grid(column=0, row=0, sticky="nsew", pady=(5, 5))
        self.frm_display_analysis_controls.rowconfigure(index=0, weight=1)

        # Auswahl der Art der Analyse
        self.frm_choose_analysis_mode = tk.LabelFrame(master=self.frm_display_analysis_controls, text="Analyseart:",
                                                      background="white", font=View_Window.default_FONT_BOLD,
                                                      borderwidth=0)
        self.frm_choose_analysis_mode.grid(column=0, row=0, sticky="nw", padx=(0, 10))
        self.com_box_analysis_mode = ttk.Combobox(master=self.frm_choose_analysis_mode,
                                                  textvariable=self.selected_analysis_mode,
                                                  state="readonly", width=24,
                                                  values=SELECTABLE_ANALYSIS_MODES)
        self.com_box_analysis_mode.current(newindex=0)
        self.com_box_analysis_mode.grid(column=0, row=0, sticky="w")

        self.btn_calculate_analysis = ttk.Button(master=self.frm_display_analysis_controls,
                                                 text="Ellbogengraph berechnen",
                                                 style="WhiteButton.TButton")
        self.btn_calculate_analysis.grid(column=1, row=0, sticky="sw", padx=(0, 5))

        # Vorbereitung der zusätzlichen Kombo-Box für die Auswahl des Werts von k im Silhouetten-Plot
        self.frm_choose_value_k_silhouette = tk.LabelFrame(master=self.frm_display_analysis_controls,
                                                           text="Wert von k:",
                                                           background="white", font=View_Window.default_FONT_BOLD,
                                                           borderwidth=0)

        self.com_box_value_k_silhouette = ttk.Combobox(master=self.frm_choose_value_k_silhouette,
                                                       textvariable=self.selected_value_k_silhouette,
                                                       state="readonly", width=24,
                                                       values=SELECTABLE_VALUES_K_SILHOUETTE)
        self.com_box_value_k_silhouette.current(newindex=0)
        self.com_box_value_k_silhouette.grid(column=0, row=0, sticky="w")

        # Hier wird das Tkinter Canvas - Widget gespeichert. Dieses enthält eine Matplotlib - Figure und den aktuellen
        # Plot (Ax). Zugriff durch self.canvas_display_analysis.figure.get_axes()[0]. Alle Änderungen an der Figure bzw.
        # deren Plot (Ax) finden in den Plot_Utils statt und werden in der View nur aufgerufen.
        self.canvas_display_analysis = Plot_Utils_Analysis.initialize_figure(master=self.frm_display_analysis)
        self.current_figure_analysis = self.canvas_display_analysis.figure
        Plot_Utils_Analysis.initialize_axes(current_figure=self.current_figure_analysis)
        self.canvas_display_analysis.get_tk_widget().grid(column=0, row=1, sticky="nsew")

    def reset_plot(self, plot_dimensions=[], axis_labels=[]):
        """
        Säubert den aktuellen Plot des k-Means_Models, setzt diesen auf die Standardkonfiguration zurück und
        aktualisiert die Anzeigefläche. Setzt des Weiteren die Werte des Plot_Containers current_plot zurück.
        :param plot_dimensions: Liste der Form [[X_LOW, X_HIGH], [Y_LOW, Y_HIGH]], welche die Abmessungen der Anzeige
                                fläche beinhaltet; Default: [] In diesem Fall werden die Standardabmessungen verwendet.
        :param axis_labels: Liste der Achsenbezeichnungen der Form [x_Achse, y_Achse];  Default: []
        """
        self.current_plot_model.reset_plot_container(plot_dimensions=plot_dimensions, axis_labels=axis_labels)
        Plot_Utils_Model.display_plot_axis(current_plot_container=self.current_plot_model,
                                           fade_out_axis=self.show_axis_ticks.get())

        # Anzeige des Plots
        self.redraw_model()

    def get_current_plot_dimensions(self):
        """
        Gibt die Abmessungen der aktuellen Anzeigefläche in Form (x_low, x_high, y_low, y_high) zurück
        :return: Abmessungen der Anzeigefläche
        """
        return Plot_Utils_Model.get_plot_dimensions(plot_ax=self.current_plot_model.plot_axes)

    def draw_dataset(self, axis_labels, dataset):
        """
        Fügt dem aktuellen Plot (plot_axes) die Punkte des Datensatzes dataset hinzu und speichert die zugehörigen
        Line2D-Objekte im dict_dataset des current_plot_containers. Des Weiteren werden die Achsenbezeichnungen gesetzt.
        :param axis_labels: Achsenbezeichnungen der Form (label_x, label_y)
        :param dataset: Liste von Tupeln, welche die Punkte des aktuellen Datensatzes repräsentieren.
        """
        self.current_plot_model.reset_plot_container(axis_labels=axis_labels, plot_dimensions=None)
        Plot_Utils_Model.add_dataset_to_plot(current_plot_container=self.current_plot_model, label_x=axis_labels[0],
                                             label_y=axis_labels[1],
                                             dataset=dataset)

        # Automatische Anpassung des Anzeigebereichs an die gezeichneten Punkte aktivieren
        self.current_plot_model.plot_axes.autoscale(enable=True)
        self.current_plot_model.current_axis_ticks = Plot_Utils_Model.set_common_tick_space(
            plot_ax=self.current_plot_model.plot_axes)

        Plot_Utils_Model.display_plot_axis(current_plot_container=self.current_plot_model,
                                           fade_out_axis=self.show_axis_ticks.get())
        # Anzeige des Plots
        self.redraw_model()

        # Automatische Anpassung des Anzeigebereichs deaktivieren
        self.current_plot_model.plot_axes.autoscale(enable=False)

    def reset_for_start_training(self):
        """
        Setzt die Anzeige und den Plot_Container den Stand der initialen Cluster-Zentren zurück.
        """
        # Zurücksetzen der Färbung der Punkte
        Plot_Utils_Model.update_dataset(current_plot_container=self.current_plot_model)

        # Zurücksetzen der Anzeige der Cluster-Zentren auf die initialen Cluster-Zentren und entfernen ggf. vorhandener
        # Decision Areas aus vorherigem Training (bis auf die initialen DA)
        Plot_Utils_Model.reset_centroids_to_start_of_training(current_plot_container=self.current_plot_model)

        # Ausblenden eines ggf. vorhandenen Decision Areas (Für Historie nicht nötig, da diese immer komplett
        # gelöscht wird beim Zurücksetzen auf den Vor-Trainings-Stand)
        Plot_Utils_Model.display_decision_areas(current_plot_container=self.current_plot_model,
                                                fade_in_decision_areas=self.show_decision_areas.get())
        # Anzeige des Plots
        self.redraw_model()

    def draw_initial_centroids(self, centroids):
        """
        Fügt dem aktuellen Plot (plot_axes) die Punkte der Cluster-Zentren centroids hinzu und speichert die zugehörigen
        Line2D-Objekte im dict_centroids des current_plot_containers. Es werden nur die Elemente (Line2D) der
        Zentren erstellt und gespeichert, sowie die Auswählbarkeit der ggf. enthaltenden Datenpunkte gesetzt. Ggf.
        vorhandene Decision Areas werden entfernt.
        Ein Anlegen der Historie, von Decision Areas,... findet nicht statt.
        :param centroids: Liste der aktuellen Cluster-Zentren als Tupel
        """
        # Wiederherstellen der Auswählbarkeit aller Datenpunkte (für den Fall, dass bereits Cluster-Zentren gezeichnet
        # sind)
        Plot_Utils_Model.set_pickability_of_all_centroid_containing_datapoints(
            current_plot_container=self.current_plot_model, enable_pickability=True)
        # Entfernen ggf. vorhandener, alter Cluster-Zentren und deren Decision Areas
        Plot_Utils_Model.remove_current_centroids(current_plot_container=self.current_plot_model)
        Plot_Utils_Model.clear_decision_areas(current_plot_container=self.current_plot_model)
        # Hinzufügen der neuen Cluster-Zentren
        Plot_Utils_Model.add_centroids(current_plot_container=self.current_plot_model, centroids=centroids)
        # Datenpunkte unter den Cluster-Zentren werden auf nicht auswählbar gesetzt
        Plot_Utils_Model.set_pickability_of_all_centroid_containing_datapoints(
            current_plot_container=self.current_plot_model, enable_pickability=False)

        # Anzeige des Plots
        self.redraw_model()

    def delete_centroids(self):
        """
        Entfernt alle in der Anzeigefläche vorhanden der Cluster-Zentren und setzt die enthaltenden Datenpunkte wieder
        auf auswählbar. Ggf. vorhandene Decision Areas werden entfernt.
        """
        Plot_Utils_Model.set_pickability_of_all_centroid_containing_datapoints(
            current_plot_container=self.current_plot_model, enable_pickability=True)
        Plot_Utils_Model.remove_current_centroids(current_plot_container=self.current_plot_model)
        Plot_Utils_Model.clear_decision_areas(current_plot_container=self.current_plot_model)

        # Anzeige des Plots
        self.redraw_model()

    def draw_plot(self, centroids, split_dataset_centroids={}, before_training=False, update_plot=True):
        """
        Fügt dem aktuellen Plot (plot_axes) die Punkte der Cluster-Zentren centroids hinzu und speichert die zugehörigen
        Line2D-Objekte im dict_centroids des current_plot_containers. Je nach Auswahl in der View, werden auch die
        Cluster-Zentren-Historie und die Decision Areas angezeigt. Des Weiteren werden die Datenpunkte in den
        Farben des am nächsten liegenden Cluster-Zentrums gefärbt.
        :param centroids: Liste der aktuellen Cluster-Zentren als Tupel
        :param split_dataset_centroids: Dictionary: key => Cluster-Zentrum; value=> Liste von Tupeln, die den
                                         aufgeteilten Datensatz enthält. Jedes Element der Liste stellt den
                                         Teildatensatz dar, welcher zum jeweiligen Cluster-Zentrum in current_centroids
                                         gehört.
        :param before_training: True, falls es sich um den Schritt vor Beginn des Trainings handelt. Es müssen nur die
                                neuen Decision Areas angelegt werden.
                                False, sonst
        :param update_plot: True, wenn die Anzeigefläche neu gezeichnet, sprich aktualisiert werden soll; False, sonst
                            Default ist True
        """
        Plot_Utils_Model.update_dataset(current_plot_container=self.current_plot_model,
                                        split_dataset_centroids=split_dataset_centroids)
        Plot_Utils_Model.add_centroids_train_mode(current_plot_container=self.current_plot_model, centroids=centroids,
                                                  init_step=before_training)
        # Übergabe einer Indexnummer ist nicht nötig, da sich hier die Historie im Aufbau befindet und ggf. immer
        # komplett angezeigt werden soll
        Plot_Utils_Model.display_centroid_history(current_plot_container=self.current_plot_model,
                                                  fade_in_history=self.show_centroid_history.get())
        Plot_Utils_Model.display_decision_areas(current_plot_container=self.current_plot_model,
                                                fade_in_decision_areas=self.show_decision_areas.get())

        # Benötigt für die Berechnung der Elemente der Anzeigefläche für den Abschluss des Trainings auf einmal
        if update_plot:
            # Anzeige des Plots
            self.redraw_model()

    def update_dataset(self, split_dataset_centroids):
        """
        Färbt die Punkte des Datensatzes nach der Zugehörigkeit zum jeweiligen Cluster-Zentrum ein und aktualisiert die
        Anzeigefläche. Falls das übergebene Dictionary leer ist, werden alle Punkte in der Standardfarbe eingefärbt.
        :param split_dataset_centroids: Dictionary: key => Cluster-Zentrum; value=> Liste von Tupeln, die den
                                        aufgeteilten Datensatz enthält. Jedes Element der Liste stellt den Teildatensatz
                                        dar, welcher zum jeweiligen Cluster-Zentrum in current_centroids gehört.
        """
        Plot_Utils_Model.update_dataset(current_plot_container=self.current_plot_model,
                                        split_dataset_centroids=split_dataset_centroids)
        # Anzeige des Plots
        self.redraw_model()

    def update_plot_auto_mode(self, number_of_step, split_dataset_centroids={}):
        """
        Darf nicht im Kontrollschritt des Ablaufs aufgerufen werden, da an dieser Stelle keine Elemente für die
        Decision Areas und Cluster-Zentren mehr vorliegen. Diese ändern sich im Vergleich zum Vorschritt nicht mehr.
        :param number_of_step: Schrittnummer
        :param split_dataset_centroids: Dictionary: key => Cluster-Zentrum; value=> Liste von Tupeln, die den
                                        aufgeteilten Datensatz enthält.
        """
        Plot_Utils_Model.update_dataset(current_plot_container=self.current_plot_model,
                                        split_dataset_centroids=split_dataset_centroids)

        Plot_Utils_Model.update_centroids(current_plot_container=self.current_plot_model, index=number_of_step)
        # Hier benötigt man jeweils Index, da wir im Auto Mode sind und mit der Historie arbeiten.
        Plot_Utils_Model.display_decision_areas(current_plot_container=self.current_plot_model,
                                                fade_in_decision_areas=self.show_decision_areas.get(),
                                                index=number_of_step)
        # Initial die komplette, ggf. angezeigte Historie ausblenden
        Plot_Utils_Model.display_centroid_history(current_plot_container=self.current_plot_model,
                                                  fade_in_history=self.show_centroid_history.get(),
                                                  index=number_of_step)

        # Anzeige des Plots
        self.redraw_model()

    def display_centroid_history(self, step_number):
        """
        Methode, welche in Abhängigkeit von der Auswahl auf der View die Historie der Cluster-Zentren ein-/ausblendet
        und die Anzeige aktualisiert.
        """
        Plot_Utils_Model.display_centroid_history(current_plot_container=self.current_plot_model,
                                                  fade_in_history=self.show_centroid_history.get(), index=step_number)
        self.redraw_model()

    def display_decision_areas(self, index_to_show):
        """
        Methode, welche in Abhängigkeit von der Auswahl auf der View die Decision Areas ein-/ausblendet
        und die Anzeige aktualisiert.
        """
        Plot_Utils_Model.display_decision_areas(current_plot_container=self.current_plot_model,
                                                fade_in_decision_areas=self.show_decision_areas.get(),
                                                index=index_to_show)

        # Anzeige des Plots
        self.redraw_model()

    def display_plot_axis(self):
        """
        Blendet das Koordinatensystem und die Achsenticks ein bzw. aus in Abhängigkeit von dem Wert der View-Variable
        show_axis_ticks, welche den Wert der entsprechenden Checkbox speichert. Im Anschluss daran wird die Anzeige-
        fläche aktualisiert.
        """
        Plot_Utils_Model.display_plot_axis(current_plot_container=self.current_plot_model,
                                           fade_out_axis=self.show_axis_ticks.get())

        self.redraw_model()

    def draw_data_point(self, x, y):
        """
        Zeichnet einen einzelnen Punkt an der Stelle (x,y) und fügt das Line2D-Objekt von Matplotlib zum plot_container
        in dict_dataset hinzu.
        :param x: x-Koordinate des neuen Punkts
        :param y: y-Koordinate des neuen Punkts
        """
        Plot_Utils_Model.draw_data_point(current_plot_container=self.current_plot_model, x=x, y=y)
        self.redraw_model()

    def remove_data_point(self, data_point):
        """
        Entfernt, falls möglich, den übergebenen Punkte (Line2D) von der Zeichenfläche (plot_axes).
        :param data_point: Punkt der Zeichenfläche, welcher entfernt werden soll
        """
        Plot_Utils_Model.remove_data_point(current_plot_container=self.current_plot_model, data_point=data_point)
        self.redraw_model()

    def draw_centroid(self, x, y):
        """
        Zeichnet ein einzelnes Cluster-Zentrum an der Stelle (x,y) und fügt das Line2D-Objekt von Matplotlib zum
        plot_container in dict_centroids hinzu und setzt den darunterliegenden Datenpunkt auf nicht auswählbar.
        :param x: x-Koordinate des neuen Cluster-Zentrums
        :param y: y-Koordinate des neuen Cluster-Zentrums
        """
        # Wird ein Cluster-Zentrum hinzugefügt, ändern sich somit auch die Decision Areas. Falls bereits welche aus
        # einem früheren Training vorhanden sind für die initialen Zentren, werden diese nun gelöscht.
        # Beim Aktivieren des Trainings werden die Decision Areas für die dann vorhandenen Cluster-Zentren erstellt.
        Plot_Utils_Model.clear_decision_areas(current_plot_container=self.current_plot_model)
        Plot_Utils_Model.draw_centroid_on_datapoint(current_plot_container=self.current_plot_model, x=x, y=y)
        Plot_Utils_Model.set_pickability_of_datapoint(current_plot_container=self.current_plot_model,
                                                      centroid_as_tuple=(x, y), enable_pickability=False)
        self.redraw_model()

    def remove_centroid(self, centroid):
        """
        Entfernt, falls möglich, das übergebene Cluster-Zentrum (Line2D) von der Zeichenfläche (plot_axes) setzt den
        darunterliegenden Datenpunkt auf auswählbar.
        :param centroid: Cluster-Zentrum als Tupel der Zeichenfläche, welches entfernt werden soll
        """
        Plot_Utils_Model.clear_decision_areas(current_plot_container=self.current_plot_model)
        Plot_Utils_Model.remove_centroid_from_datapoint(current_plot_container=self.current_plot_model,
                                                        centroid_to_remove=centroid)
        Plot_Utils_Model.set_pickability_of_datapoint(current_plot_container=self.current_plot_model,
                                                      centroid_as_tuple=centroid, enable_pickability=True)
        self.redraw_model()

    def redraw_model(self):
        """
        Zeichnet die Anzeigefläche.
        """
        self.canvas_display_model.draw()

    def get_dataset_Line2D(self):
        """
        Liefert die Line2D-Objekte der vorhandenen Datenpunkte aus dem Plot-Container.
        :return: ViewObjekt, welches eine Liste aller Line2D-Objekte der vorhandenen Datenpunkte des Plot-Containers
                 enthält
        """
        return self.current_plot_model.dict_dataset.values()

    def get_centroids_Line2D(self):
        """
        Liefert die Line2D-Objekte der vorhandenen Cluster-Zentren aus dem Plot-Container.
        :return: ViewObjekt, welches eine Liste aller Line2D-Objekte der vorhandenen Cluster-Zentren des Plot-Containers
                 enthält
        """
        return self.current_plot_model.get_current_centroids_Line2D()


    def get_data_selection_mode(self):
        """
        Gibt den momentan ausgewählten Dateieingabemodus zurück.
        :return: Dateieingabemodus als Text
        """
        return self.selected_data_input_mode.get()

    def display_selected_filepath_training_data(self, filepath):
        """
        Zeigt den übergebenen String filepath in der Oberfläche an.
        :param filepath: Dateipfad der ausgewählten Datei
        """
        self.lbl_display_selected_filepath_data_file.config(text=filepath)

    def set_scale_area_slider_parameter_k(self, max_value_k):
        """
        Setzt die obere Begrenzung des Sliders zur Auswahl des Parameters k auf den Wert max_value_k
        :param max_value_k: obere Grenze für die Auswahl von k
        """
        self.slider_parameter_k.configure(to=max_value_k)

    def set_slider_parameter_k_value(self, value):
        """
        Setzt des Wert der Sliders für den Parameter k auf den übergebenen Parameter
        :param value: Wert des Sliders
        """
        self.slider_parameter_k.set(value=value)

    def update_view_WCSS_enable(self, enable):
        if enable:
            self.lbl_WCSS['state'] = tk.NORMAL
        else:
            self.lbl_WCSS['state'] = tk.DISABLED

    def set_value_WCSS(self, value=None):
        """
        Setzt den Wert des Anzeigelabels der WCSS auf den übergebenen Wert oder einen Default-Text.
        :param value: zu setzender Wert der WCSS; Default: None
        """
        if value is None:
            self.lbl_WCSS.config(text="Noch nicht berechnet.")
        else:
            self.lbl_WCSS.config(text="WCSS: " + str(value))

    def update_view_train_mode(self, enable_train_mode, clusters_found):
        """
        Passt die View an in Abhängigkeit, ob der Trainingsmodus aktiv ist oder nicht.
        Falls aktiv, werden die Dateiauswahl und die Auswahl des Parameters k, sowie der initialen Cluster-Zentren
        deaktiviert und die Kontrollmöglichkeiten für das Training aktiviert. Die Kontrollmöglichkeiten, werden aber nur
        aktiviert, wenn die finalen Cluster-Zentren noch nicht gefunden wurden.
        Falls inaktiv, werden die Kontrollmöglichkeiten für das Training deaktiviert und die Dateiauswahl und die
        Auswahl des Parameters k, sowie der initialen Cluster-Zentren aktiviert.
        :param enable_train_mode: Wahrheitswert True, falls der Trainingsmodus aktiviert werden soll. False, sonst
        :param clusters_found: Wahrheitswert True, falls die finalen Cluster-Zentren bereits gefunden wurden. False,
                               sonst
        """
        if enable_train_mode:
            self.btn_initiate_train_mode.configure(text="Training zur\u00FCcksetzen")
            state_other_controls = tk.DISABLED
            self.com_box_data_input_mode['state'] = tk.DISABLED
            self.ck_btn_show_centroid_history['state'] = tk.NORMAL
            self.ck_btn_show_decision_areas['state'] = tk.NORMAL
            self.lbl_WCSS['state'] = tk.DISABLED
            self.set_value_WCSS(value=None)
            self.frm_display_WCSS.grid(column=0, row=1, sticky="new")
        else:
            self.btn_initiate_train_mode.configure(text="Training beginnen")
            self.com_box_data_input_mode['state'] = "readonly"
            state_other_controls = tk.NORMAL
            self.show_centroid_history.set(False)
            self.show_decision_areas.set(False)
            self.algorithm_step_training_active.set(False)
            self.ck_btn_show_centroid_history['state'] = tk.DISABLED
            self.ck_btn_show_decision_areas['state'] = tk.DISABLED
            self.frm_display_WCSS.grid_forget()

        self.menu_app_mode['state'] = state_other_controls
        self.btn_choose_data_file['state'] = state_other_controls
        self.etr_x_low['state'] = state_other_controls
        self.etr_x_high['state'] = state_other_controls
        self.etr_y_low['state'] = state_other_controls
        self.etr_y_high['state'] = state_other_controls
        self.btn_init_plot_area['state'] = state_other_controls
        self.slider_parameter_k['state'] = state_other_controls
        self.btn_random_initial_centroids['state'] = state_other_controls
        self.btn_activate_selection_of_centroids_on_click['state'] = state_other_controls
        self.btn_activate_selection_of_datapoints_on_click['state'] = state_other_controls
        self.btn_delete_datapoints['state'] = state_other_controls
        self.btn_export_datapoints_csv['state'] = state_other_controls
        self.btn_initiate_parameter_analysis['state'] = state_other_controls

        if not clusters_found:
            self.update_view_train_controls(enable=enable_train_mode)

    def update_view_train_controls(self, enable):
        """
        Aktiviert oder deaktiviert die Kontrollmöglichkeiten (Training, Historie und Decision Areas) der Anzeigefläche
        in der View.
        :param enable: Wahrheitswert True, falls die Kontrollmöglichkeiten aktiviert werden sollen. False, sonst
        """
        if enable:
            state_train_controls = tk.NORMAL
        else:
            state_train_controls = tk.DISABLED

        self.btn_train['state'] = state_train_controls
        self.ck_btn_algorithm_step_training_on['state'] = state_train_controls
        self.btn_auto_train['state'] = state_train_controls
        self.btn_finish_training['state'] = state_train_controls
        self.btn_auto_train_faster['state'] = state_train_controls
        self.btn_auto_train_slower['state'] = state_train_controls

    def update_view_train_disable_controls_found_auto_mode(self):
        """
        Deaktiviert den "Trainieren" und "Training abschließen"-Button.
        :param enable: Wahrheitswert True, falls die Kontrollmöglichkeiten aktiviert werden sollen. False, sonst
        """
        self.btn_train['state'] = tk.DISABLED
        self.btn_finish_training['state'] = tk.DISABLED

    def update_view_train_controls_auto_mode_activation(self, enable):
        """
        Passt die Trainingskontrolle entsprechend der Aktivierung oder Deaktivierung der automatischen Ausführung an
        :param enable:True, wenn die automatische Ausführung aktiviert wird; False, Sonst
        """
        # Falls das Training gestartet wird
        if enable:
            # Ein- und Ausblenden der Button
            self.btn_train.grid_forget()
            self.ck_btn_algorithm_step_training_on.grid_forget()
            self.btn_finish_training.grid_forget()
            self.btn_auto_train_slower.grid(column=1, row=0, sticky="nwe", padx=(0, 2))
            self.btn_auto_train_faster.grid(column=2, row=0, sticky="nwe", padx=(0, 5))

            self.ck_btn_show_decision_areas['state'] = tk.DISABLED
            self.ck_btn_show_centroid_history['state'] = tk.DISABLED
            self.ck_btn_show_axis_ticks['state'] = tk.DISABLED

            self.btn_auto_train['text'] = "Training stoppen"
        # Falls das Training gestoppt wird
        else:
            # Ein- und Ausblenden der Button
            self.btn_auto_train_slower.grid_forget()
            self.btn_auto_train_faster.grid_forget()
            self.btn_train.grid(column=1, row=0, sticky="nwe", padx=(0, 2))
            self.ck_btn_algorithm_step_training_on.grid(column=1, row=1, sticky="nwe", padx=(0, 2))
            self.btn_finish_training.grid(column=2, row=0, sticky="nwe", padx=(0, 5))

            self.ck_btn_show_decision_areas['state'] = tk.NORMAL
            self.ck_btn_show_centroid_history['state'] = tk.NORMAL
            self.ck_btn_show_axis_ticks['state'] = tk.NORMAL
            self.btn_auto_train['text'] = "Automatisch trainieren"

            # Falls einer der Geschwindigkeit-Buttons aufgrund der Erreichung der Grenzgeschwindigkeit deaktiviert wurde
            self.btn_auto_train_faster['state'] = tk.NORMAL
            self.btn_auto_train_slower['state'] = tk.NORMAL

    def update_view_auto_mode_speed_bounds_reached(self, min_reached, max_reached):
        """
        Aktiviert bzw. deaktiviert den Langsamer-Button
        :param min_reached: True, wenn die niedrigste Geschwindigkeit erreicht und der Button  deaktiviert werden soll
                             False, sonst
        :param max_reached: True, wenn die höchste Geschwindigkeit erreicht und der Button somit deaktiviert werden soll
                             False, sonst
        """
        if min_reached:
            self.btn_auto_train_slower['state'] = tk.DISABLED
        else:
            self.btn_auto_train_slower['state'] = tk.NORMAL

        if max_reached:
            self.btn_auto_train_faster['state'] = tk.DISABLED
        else:
            self.btn_auto_train_faster['state'] = tk.NORMAL

    def update_view_btn_auto_mode(self, enable):
        """
        Aktiviert bzw. deaktiviert den Auto-Mode Button
        :param enable: True, wenn der Button aktiviert werden soll; False, sonst
        """
        if enable:
            self.btn_auto_train['state'] = tk.NORMAL
        else:
            self.btn_auto_train['state'] = tk.DISABLED

    def update_view_train_mode_analysis_control(self, enable):
        """
        Aktivieren bzw. deaktivieren der Kontrollbuttons der Trainings- bzw. Analyses-Aktivierung
        :param enable: True, wenn die Buttons aktiviert werden sollen; False, sonst
        """
        if enable:
            state_train_analysis_controls = tk.NORMAL
        else:
            state_train_analysis_controls = tk.DISABLED

        self.btn_initiate_train_mode['state'] = state_train_analysis_controls
        self.btn_initiate_parameter_analysis['state'] = state_train_analysis_controls

    def reset_data_input_mode(self):
        """
        Setzt den Wert der Combobox zur Auswahl des Dateieingabemodus auf den Standardwert an Stelle 0 zurück. Methode
        verhindert, dass im Controller direkt aus Elemente der View zugegriffen werden muss.
        """
        self.com_box_data_input_mode.current(newindex=0)

    def reset_show_axis_ck_box(self):
        """
        Setzt den Wert der Variable, welche den Wert der Checkbox zur Anzeige der Achsen speichert auf False. Dadurch
        wird auch die verknüpfte Checkbox auf "nicht ausgewählt" gesetzt.
        Methode verhindert, dass im Controller direkt aus Elemente der View zugegriffen werden muss.
        """
        self.show_axis_ticks.set(value=False)

    def update_view_data_selection(self):
        """
        Blendet je nach ausgewähltem Modus für die Dateneingabe die benötigten Widgets ein oder aus.
        """
        if self.selected_data_input_mode.get() == self.DATA_INPUT_MODE_file:
            self.frm_choose_data_from_click.grid_forget()
            self.frm_settings_datapoint_on_click.grid_forget()
            self.frm_choose_data_from_file.grid(column=1, row=0, sticky="ew")
            self.frm_cluster_settings.grid(column=0, row=0, sticky="nsew", padx=(2, 2))
            # Anpassung des Bereichs mit dem Slider mit der Fenstergröße
            self.frm_controls.columnconfigure(index=0, weight=1)

        else:
            self.frm_choose_data_from_file.grid_forget()
            self.frm_choose_data_from_click.grid(column=1, row=0, sticky="ew")
            self.frm_settings_datapoint_on_click.grid(column=0, row=0, sticky="nsew", padx=(0, 1))
            self.frm_cluster_settings.grid(column=1, row=0, sticky="nsew", padx=(2, 2))
            # Bereich für die Einstellungen zur Punkteingabe soll sich nicht mit der Fenstergröße ändern
            self.frm_controls.columnconfigure(index=0, weight=0)

    def update_view_data_point_selection_on_click(self, disable_data_point_selection):
        """
        Aktiviert bzw. Deaktiviert die Eingabemöglichkeiten während der Punkteingabe per Klick.
        Es wird davon ausgegangen, dass über die View sichergestellt ist, dass die Eingabemöglichkeiten des Trainings
        gesperrt sind, da diese nur während des Trainingsmodus aktiv sind und in diesem Modus keine Punkteingabe über
        die View aktiviert werden kann
        :param disable_data_point_selection: True, wenn die Eingabemöglichkeiten deaktiviert werden sollen; False, sonst
        """
        if disable_data_point_selection:
            state_selection_on_click = tk.DISABLED
            self.com_box_data_input_mode['state'] = tk.DISABLED
            self.btn_activate_selection_of_datapoints_on_click.configure(text='Eingabe deaktivieren')
        else:
            state_selection_on_click = tk.NORMAL
            self.com_box_data_input_mode['state'] = "readonly"
            self.btn_activate_selection_of_datapoints_on_click.configure(text='Eingabe aktivieren')

        self.etr_x_low['state'] = state_selection_on_click
        self.etr_x_high['state'] = state_selection_on_click
        self.etr_y_low['state'] = state_selection_on_click
        self.etr_y_high['state'] = state_selection_on_click
        self.btn_init_plot_area['state'] = state_selection_on_click
        self.slider_parameter_k['state'] = state_selection_on_click
        self.btn_random_initial_centroids['state'] = state_selection_on_click
        self.btn_activate_selection_of_centroids_on_click['state'] = state_selection_on_click
        self.btn_export_datapoints_csv['state'] = state_selection_on_click

        self.btn_initiate_train_mode['state'] = state_selection_on_click
        self.btn_initiate_parameter_analysis['state'] = state_selection_on_click

        # Durch View eigentlich nicht zugreifbare Kontrollmöglichkeiten
        self.btn_choose_data_file['state'] = state_selection_on_click

    def update_view_centroid_selection_on_click(self, disable_centroid_selection):
        """
        Aktiviert bzw. Deaktiviert die Eingabemöglichkeiten während der Cluster-Zentrenauswahl per Klick.
        Es wird davon ausgegangen, dass über die View sichergestellt ist, dass die Eingabemöglichkeiten des Trainings
        gesperrt sind, da diese nur während des Trainingsmodus aktiv sind und in diesem Modus keine Punkteingabe über
        die View aktiviert werden kann
        :param disable_centroid_selection: True, wenn die Eingabemöglichkeiten deaktiviert werden sollen; False, sonst
        """
        if disable_centroid_selection:
            state_selection_on_click = tk.DISABLED
            self.com_box_data_input_mode['state'] = tk.DISABLED
            self.btn_activate_selection_of_centroids_on_click.configure(text='Eingabe deaktivieren')

            self.btn_random_initial_centroids.grid_forget()
            self.btn_activate_selection_of_centroids_on_click.grid(column=2, row=1, sticky="nwe")
            self.btn_delete_centroids.grid(column=2, row=2, sticky="nwe")

        else:
            state_selection_on_click = tk.NORMAL
            self.com_box_data_input_mode['state'] = "readonly"
            self.btn_activate_selection_of_centroids_on_click.configure(text='Per Klick ausw\u00E4hlen')
            self.btn_delete_centroids.grid_forget()
            self.btn_random_initial_centroids.grid(column=2, row=1, sticky="nwe")
            self.btn_activate_selection_of_centroids_on_click.grid(column=2, row=2, sticky="nwe")

        self.etr_x_low['state'] = state_selection_on_click
        self.etr_x_high['state'] = state_selection_on_click
        self.etr_y_low['state'] = state_selection_on_click
        self.etr_y_high['state'] = state_selection_on_click
        self.btn_init_plot_area['state'] = state_selection_on_click
        self.slider_parameter_k['state'] = state_selection_on_click
        self.btn_random_initial_centroids['state'] = state_selection_on_click
        self.btn_activate_selection_of_datapoints_on_click['state'] = state_selection_on_click
        self.btn_delete_datapoints['state'] = state_selection_on_click
        self.btn_export_datapoints_csv['state'] = state_selection_on_click

        self.btn_initiate_train_mode['state'] = state_selection_on_click
        self.btn_initiate_parameter_analysis['state'] = state_selection_on_click

        # Durch View eigentlich nicht zugreifbare Kontrollmöglichkeiten
        self.btn_choose_data_file['state'] = state_selection_on_click

    def update_view_activate_parameter_analysis(self, set_active, number_of_datapoints=-1):
        """
        Wird nur bei Aktivierung bzw. Deaktivierung der Parameter-Analyse aufgerufen.
        Sperrt bzw. aktiviert die nötigen Schaltflächen bei Aktivierung bzw. Deaktivierung der Parameter-Analyse.
        Es wird mithilfe des Parameters number_of_datapoints sichergestellt, dass die Auswahl des Silhouetten-Plots nur
        möglich ist, wenn bei Aktivierung der Parameter-Analyse genügend Datenpunkte vorhanden sind. Da über die View
        sichergestellt ist, das initial nach Aktivierung der Parameter-Analyse die Ellbogen-Analyse ausgewählt ist, wird
        die Oberfläche hierfür vorbereitet bei Aktivierung.
        :param set_active: True, wenn die Parameter-Analyse aktiviert werden soll; False, sonst
        :param number_of_datapoints: Anzahl der aktuell vorhandenen Datenpunkte
        """
        if set_active:
            self.btn_initiate_parameter_analysis.configure(text='Parameteranalyse deaktivieren')
            state_other_controls = tk.DISABLED
            self.com_box_data_input_mode['state'] = tk.DISABLED

            self.main_notebook.tab(tab_id=0, state=tk.DISABLED, text="Grafische Darstellung der Cluster-Distanzen ")
            self.main_notebook.add(child=self.frm_display_analysis_container)
            self.main_notebook.select(1)

            # Ausblenden der Kontrollmöglichkeiten des Modells für das Training
            self.frm_display_model_controls.grid_forget()
            # Einblenden der Kontrollmöglichkeit des Distanzen-Plots für die Ellbogen-Analyse
            self.frm_display_elbow_distances_controls.grid(column=0, row=1, sticky="nsew", pady=(5, 0))

            # Einblenden der Kontrollmöglichkeiten für die Berechnung der Ellbogen-Analyse und Ausblenden der ggf.
            # noch zusätzlich vorhandenen Kontrollmöglichkeiten der Silhouetten-Analyse
            self.frm_choose_analysis_mode.grid(column=0, row=0, sticky="nw", padx=(0, 10))
            self.btn_calculate_analysis.configure(text="Ellbogengraph berechnen")
            self.btn_calculate_analysis.grid(column=1, row=0, sticky="sw", padx=(0, 5))
            self.frm_choose_value_k_silhouette.grid_forget()

            # Zurücksetzen der Eingabemöglichkeiten auf den Ellbogen-Modus
            self.com_box_analysis_mode.current(0)

            # Anpassen der Combobox zur Auswahl der möglichen Analyse-Arten an die zur Verfügung stehenden Datenpunkte
            # Silhouettenplot ist nicht auswählbar für weniger als 2 Datenpunkte
            if number_of_datapoints < 2:
                self.com_box_analysis_mode['values'] = SELECTABLE_ANALYSIS_MODES[0]
            else:
                self.com_box_analysis_mode['values'] = SELECTABLE_ANALYSIS_MODES
                if number_of_datapoints > 9:
                    self.com_box_value_k_silhouette['values'] = SELECTABLE_VALUES_K_SILHOUETTE
                else:
                    self.com_box_value_k_silhouette['values'] = SELECTABLE_VALUES_K_SILHOUETTE[
                                                                :number_of_datapoints - 1]

        else:
            self.btn_initiate_parameter_analysis.configure(text='Parameteranalyse aktivieren')
            self.com_box_data_input_mode['state'] = "readonly"
            state_other_controls = tk.NORMAL

            self.main_notebook.tab(tab_id=0, state=tk.NORMAL, text="Grafische Darstellung des k-Means-Algorithmus  ")
            self.main_notebook.hide(tab_id=1)
            self.main_notebook.select(0)
            # Einbinden der normalen Kontrollmöglichkeiten der Anzeigefläche und Ausblenden der für die Parameter-
            # Analyse spezifischen Kontrollbereiche des Modells
            self.frm_display_elbow_distances_controls.grid_forget()
            self.frm_display_distance_sums.grid_forget()
            self.frm_display_model_controls.grid(column=0, row=1, sticky="nsew", pady=(5, 0))

        self.btn_choose_data_file['state'] = state_other_controls
        self.etr_x_low['state'] = state_other_controls
        self.etr_x_high['state'] = state_other_controls
        self.etr_y_low['state'] = state_other_controls
        self.etr_y_high['state'] = state_other_controls
        self.btn_init_plot_area['state'] = state_other_controls
        self.slider_parameter_k['state'] = state_other_controls
        self.btn_random_initial_centroids['state'] = state_other_controls
        self.btn_activate_selection_of_centroids_on_click['state'] = state_other_controls
        self.btn_activate_selection_of_datapoints_on_click['state'] = state_other_controls
        self.btn_delete_datapoints['state'] = state_other_controls
        self.btn_export_datapoints_csv['state'] = state_other_controls
        self.btn_initiate_train_mode['state'] = state_other_controls
        self.ck_btn_show_axis_ticks['state'] = state_other_controls
        self.menu_app_mode['state'] = state_other_controls

    def update_view_controls_parameter_plot_for_mode(self):
        """
        Blendet die Kontrollmöglichkeiten für die Parameteranalyse in Abhängigkeit von dem in der View ausgewählten
        Analyse-Modus ein bzw. aus.
        """
        if self.selected_analysis_mode.get() == ANALYSIS_MODE_elbow:
            self.frm_choose_analysis_mode.grid(column=0, row=0, sticky="nw", padx=(0, 10))
            self.btn_calculate_analysis.configure(text="Ellbogengraph berechnen")
            self.btn_calculate_analysis.grid(column=1, row=0, sticky="sw", padx=(0, 5))
            self.frm_choose_value_k_silhouette.grid_forget()
            self.frm_display_distance_sums.grid_forget()
            self.frm_display_elbow_distances_controls.grid(column=0, row=1, sticky="nsew", pady=(5, 0))
            self.main_notebook.tab(tab_id=0, state=tk.DISABLED)
        else:
            self.frm_choose_analysis_mode.grid(column=0, row=0, sticky="nw", padx=(0, 10))
            self.btn_calculate_analysis.configure(text="Silhouettengraph berechnen")
            self.frm_choose_value_k_silhouette.grid(column=1, row=0, sticky="sw", padx=(0, 10))
            self.com_box_value_k_silhouette.current(0)
            self.btn_calculate_analysis.grid(column=2, row=0, sticky="sw", padx=(0, 5))
            self.frm_display_elbow_distances_controls.grid_forget()
            self.frm_display_distance_sums.grid(column=0, row=1, sticky="nsew", padx=(0, 5), pady=(5, 0))
            self.main_notebook.tab(tab_id=0, state=tk.DISABLED)

    def update_view_enable_tab_distance_plot(self, enable=True):
        """
        Aktiviert bzw. Deaktiviert in Abhängigkeit vom übergebenen Wahrheitswert den ersten Reiter des Notebooks.
        Methode wird nur im Controller verwendet, um keinen direkten Zugriff auf Elemente der View notwendig zu machen.
        In der View wird direkt auf die Elemente zugegriffen
        :param enable: True, wenn der erste Reiter aktiviert werden soll; False, sonst
        """
        if enable:
            self.main_notebook.tab(tab_id=0, state=tk.NORMAL)
        else:
            self.main_notebook.tab(tab_id=0, state=tk.DISABLED)

    def update_view_train_button_algorithm_step_training(self, phase_nearest_points=None):
        """
        Passt die Beschriftung des Trainieren-Buttons an. In Abhängigkeit von dem übergebenen Wert phase_nearest_points
        wird die angepasst.
        :param phase_nearest_points: None: Im regulären Training; Default-Wert
                                     True: Einzelschritt-Training ist aktiv und man befindet sich im ersten der beiden
                                           Schritte
                                     False: Einzelschritt-Training ist aktiv und man befindet sich im zweiten der
                                            beiden Schritte
        """
        if phase_nearest_points == True:
            self.btn_train['text'] = "Trainieren (1. Nächste Punkte)"
        elif phase_nearest_points == False:
            self.btn_train['text'] = "Trainieren (2. Neue Zentren)"
        else:
            self.btn_train['text'] = "Trainieren"

    def update_view_enable_calculate_parameter_analysis(self, enable):
        """
        Methode wird nur genutzt um für die Dauer der Berechnung einer Parameter-Analyse alle bis dato ggf. aktiven
        Eingabemöglichkeiten zu sperren bzw. zu entsperren. Die betrifft nur Eingabemöglichkeiten, welche zu diesem
        Zeitpunkt über die View zugreifbar wären, d.h. bei der Anzeige des Plots auswählbar sind.
        :param enable: True, wenn die Kontrollmöglichkeiten aktiviert werden sollen; False, sonst
        """
        if enable:
            state_controls = tk.NORMAL
            self.com_box_analysis_mode['state'] = "readonly"
            self.com_box_value_k_silhouette['state'] = "readonly"
        else:
            state_controls = tk.DISABLED
            self.com_box_analysis_mode['state'] = state_controls
            self.com_box_value_k_silhouette['state'] = state_controls
        self.btn_calculate_analysis['state'] = state_controls
        self.btn_initiate_parameter_analysis['state'] = state_controls


    def init_treeview_centroids(self, number_of_columns, space_in_px):
        """
        Initialisiert die Treeview zu Anzeige der Cluster-Zentren, auf einer Breite von space_in_px und mit
        number_of_columns+1 Spalten.
        Wenn die Namen der Spalten, also die column_labels bereits bekannt sind, werden diese auch gleich in der
        Header-Zeile angezeigt.
        :param number_of_columns: Anzahl an Spalten.
        :param space_in_px: verfügbare Breite in Pixel für die Treeview.
        """
        columns = [i for i in range(number_of_columns + 1)]
        self.treeview_centroids["columns"] = columns
        self.treeview_centroids["show"] = "headings"
        self.treeview_centroids["selectmode"] = "none"

        # Anlegen der Spalte für die Nummer des Cluster-Zentrums
        self.treeview_centroids.column(column=columns[0], width=40, anchor='c', stretch=False)

        col_width = (space_in_px - 40) // number_of_columns
        for i in range(1, number_of_columns + 1):
            self.treeview_centroids.column(column=columns[i], width=col_width, anchor='c', stretch=False)

        # Header-Eintrag in der ersten Spalte auf das # setzen
        self.treeview_centroids.heading(column=self.treeview_centroids["columns"][0], text='#')

        # Anzeigen der ersten Zeile mit Farbe und Nr 1.
        # Da k nicht kleiner als 1 sein kann
        self.treeview_centroids.insert(parent="", index='end', text="L1", values=(1, "", ""), tags='even')
        self.treeview_centroids.tag_configure("even", background='#C6E2FF')

    def clear_treeview_centroids_header(self):
        """
        Löscht alle Werte aus der treeview. Behält aber die Struktur bei, sprich die Breite, Modus, Anzahl an Spalten,...
        """
        # Leeren der Header-Zeile
        for d in self.treeview_centroids["columns"][1:]:
            self.treeview_centroids.heading(column=d, text=str(''))

    def clear_treeview_centroids_data(self):
        """
        Löscht alle Datenwerte aus der treeview. Behält aber den Header und die Struktur bei, sprich die Breite, Modus,
        Anzahl an Spalten,...
        """
        # Leeren des Treeview
        for child in self.treeview_centroids.get_children():
            self.treeview_centroids.delete(child)

    def fill_treeview_centroids_with_header(self, header):
        """
        Setzt die Headerwerte der Spalten der Treeview auf die übergebenen Werte. Die Anzahl an Headerwerten in der Liste
        header müssen mit den verfügbaren Spalten der Treeview übereinstimmen.
        :param header: Liste aus Strings, welche die Headerwerte enthält.
        """
        if header == ():
            header = ('', '')
        elif len(header) + 1 != len(self.treeview_centroids["columns"]):
            raise src.Exceptions.UnequalSizeException

        # Header-Eintrag für die Nummer des Cluster-Zentrums
        header = ('#',) + header

        # Werte in der Headerzeile speichern
        for i in range(len(header)):
            self.treeview_centroids.heading(column=self.treeview_centroids["columns"][i], text=str(header[i]))

    def fill_treeview_centroids_with_data(self, dataset):
        """
        Füllt die übergebenen Daten in die ausgewählte Treeview. Die Elementreihenfolge der inneren Listen aus Dataset
        muss der Reihenfolge der Spalten der Treeview entsprechen.
        :param dataset: Daten als Liste von Listen, welche die Daten enthält, die angezeigt werden sollen.
        """
        if dataset and len(dataset[0]) + 1 != len(self.treeview_centroids["columns"]):
            raise src.Exceptions.UnequalSizeException

        even_flag = "even"

        if dataset:
            # Befüllen der Treeview-Tabelle mit den Werten
            for i in range(len(dataset)):
                # Anzeige von Leereinträgen
                if dataset[i] == ("", ""):
                    values = dataset[i]
                # Anzeige von formatierten Werten auf maximal zwei Nachkommastellen und keine unnötigen Nullen rechts
                else:
                    values = (
                        f'{dataset[i][0]:.2f}'.rstrip('0').rstrip('.'), f'{dataset[i][1]:.2f}'.rstrip('0').rstrip('.'))
                self.treeview_centroids.insert(parent="", index='end', text="L1", values=(i + 1,) + values,
                                               tags=even_flag)
                if even_flag == "even":
                    even_flag = "odd"
                else:
                    even_flag = "even"
        else:
            # Anzeigen der ersten Zeile mit Farbe und Nr 1.
            # Da k nicht kleiner als 1 sein kann
            self.treeview_centroids.insert(parent="", index='end', text="L1", values=(1, "", ""), tags='even')

        self.treeview_centroids.tag_configure("even", background='#C6E2FF')
        self.treeview_centroids.tag_configure("odd", background='#EEEEEE')

        # Anzeige von Beginn an
        treeview_elements = self.treeview_centroids.get_children()
        if treeview_elements != ():
            self.treeview_centroids.see(treeview_elements[0])

    def reset_parameter_analysis_plot(self):
        """
        Setzt die Anzeige des Analysegraphen zurück, initialisiert diesen in Abhängigkeit vom aktuellen Modus
         und aktualisiert die Anzeige des Plots.
        """
        Plot_Utils_Analysis.reset_axes(current_figure=self.current_figure_analysis,
                                       current_mode=self.selected_analysis_mode.get())

        # Anzeige des Parametergraphs
        self.redraw_parameter_analysis()

    def draw_parameter_analysis_elbow(self, max_value_k, values_y, list_final_cluster_sets):
        """
        Zeigt den Ellbogengraph (x=1,.., max_value_k, y=values_y)  an. Setzt den Distanzenplot zurück, berechnet die
        für die aktuelle Berechnung notwendigen Elemente der Distanzenplots und zeigt den Distanzenplot für das in der
        View ausgewählte k an.
        :param max_value_k: Obere Grenze des Werts für k; legt die x-Werte fest. Diese laufen von 1,...,k,
                            Anzahl der als y-Werte übergebenen wcss_values_for_k_values übereinstimmen
        :param values_y: y-Werte des Ellbogengraphs
        :param list_final_cluster_sets: Liste der Länge max_value_k. An jeder Position der Liste befindet sich ein Dictionary.
                               Dieses hat jeweils als keys => finale Cluster-Zentren, welche für k und die Datenpunkte
                               bestimmt wurden; values => Liste mit Tupeln, welche die Datenpunkte repräsentieren, die
                               zum jeweiligen Cluster-Zentrum gehören
        """
        # Anzeige des Ellbogengraphs
        Plot_Utils_Analysis.draw_elbow_analysis_graph(current_figure=self.current_figure_analysis,
                                                      max_value_of_k=max_value_k, wcss_values_for_k_values=values_y)
        # Entfernen ggf. vorhandener Distanzplots, die während dieser Aktivierung der Parameteranalyse berechnet und
        # angezeigt wurden
        Plot_Utils_Model.remove_distances_parameter_elbow_analysis(current_plot_container=self.current_plot_model)
        Plot_Utils_Model.remove_distances_parameter_silhouette_analysis(current_plot_container=self.current_plot_model)
        # Berechnung der für die Darstellung der Distanzenplots notwendigen Line2D-Objekte. Diese sind zu Beginn
        # alle ausgeblendet
        Plot_Utils_Model.draw_distances_parameter_elbow_analysis(current_plot_container=self.current_plot_model,
                                                                 list_final_cluster_sets=list_final_cluster_sets)
        # Einblenden des Distanzenplots für das aktuell ausgewählte k
        index_current_value_k = self.selected_value_k_elbow.get() - 1
        Plot_Utils_Model.update_distances_parameter_elbow_analysis(current_plot_container=self.current_plot_model,
                                                                   index_selected_value_k=index_current_value_k,
                                                                   final_cluster_set=list_final_cluster_sets[
                                                                       index_current_value_k])
        # Anzeige des Distanzen-Plots
        self.redraw_model()

        # Anzeige des Parametergraphs
        self.redraw_parameter_analysis()

    def update_parameter_analysis_elbow_distance_plot(self, final_clusters_for_k, index_current_value_k):
        """
        Blendet die Elemente des Distanzen-Plots für die Ellbogen-Analyse für das gewählte k ein und passt die Färbung
        der Datenpunkte an. Im Anschluss wird die grafische Anzeige des Distanzen-Plots/Modells aktualisiert.
        :param final_clusters_for_k: Dictionary: key => finales Cluster-Zentrum; value=> Liste von Tupeln, die den
                                    aufgeteilten Datensatz enthält. Jedes Element der Liste stellt den Teildatensatz
                                    dar, welcher zum jeweiligen Cluster-Zentrum in current_centroids gehört.
        :param index_current_value_k:Index, an dem die Elemente für die Darstellung des Distanzen-Plots der Ellbogen-
                                   Analyse im entsprechenden Attribut gespeichert sind.
        """
        Plot_Utils_Model.update_distances_parameter_elbow_analysis(current_plot_container=self.current_plot_model,
                                                                   index_selected_value_k=index_current_value_k,
                                                                   final_cluster_set=final_clusters_for_k)
        # Anzeige des Distanzen-Plots
        self.redraw_model()

    def switch_plot_model_parameter_analysis_distances(self, activate_parameter_analysis):
        """
        Wird nur beim Aktivieren bzw. Deaktivieren er Parameter-Analyse aufgerufen.
        Beim Aktivieren der Parameter-Analyse werden ggf. vorhandene Cluster-Zentren des Trainings-Modus ausgeblendet.
        Beim Deaktivieren werden die ggf. aus den Distanzen-Plots zusätzlich vorhandenen Elemente entfernt, die Punkt-
        färbung wird auf die Standardfarbe zurückgesetzt und die aus der Trainingsinitialisierung ggf. vorhandenen
        Cluster-Zentren werden wieder eingeblendet.
        Außerdem wird die Auswählbarkeit der Datenpunkte und Cluster-Zentren aus dem Training geregelt. Beim Aktivieren
        werden alle Datenpunkte auswählbar und die ggf. ausgeblendeten Cluster-Zentren auf nicht auswählbar gesetzt.
        Beim Deaktivieren genau andersherum.
        Im Anschluss wird die grafische Anzeige des Modells aktualisiert.
        :param activate_parameter_analysis: True, falls die Parameter-Analyse aktiviert werden soll; False, sonst
        """
        Plot_Utils_Model.update_plot_model_training_parameter_analysis_distances(
            current_plot_container=self.current_plot_model,
            activate_parameter_analysis=activate_parameter_analysis)

        Plot_Utils_Model.set_pickability_of_all_centroid_containing_datapoints(
            current_plot_container=self.current_plot_model, enable_pickability=activate_parameter_analysis)
        Plot_Utils_Model.set_pickability_of_all_centroids(current_plot_container=self.current_plot_model,
                                                          enable_pickability=not activate_parameter_analysis)

        self.redraw_model()

    def set_scale_area_slider_parameter_k_parameter_analysis_elbow_distance_plot(self, max_value_k):
        """
        Setzt die obere Begrenzung des Sliders zur Auswahl des Parameters k auf den Wert max_value_k
        :param max_value_k: obere Grenze für die Auswahl von k
        """
        self.slider_parameter_k_parameter_analysis_elbow.configure(to=max_value_k)

    def set_slider_parameter_k_value_parameter_analysis_elbow_distance_plot(self, value):
        """
        Setzt des Wert der Sliders für den Parameter k auf den übergebenen Parameter
        :param value: Wert des Sliders
        """
        self.slider_parameter_k_parameter_analysis_elbow.set(value=value)

    def draw_parameter_analysis_silhouette(self, information_set_for_final_clusters):
        """
        Zeigt den Silhouetten-Plot berechnet die Elemente für den zugehörigen Distanzen-Plot. Zuerst wird der
        Silhouetten-Plot gezeichnet. Dann werden Elemente von ggf. vorherigen Distanzen-Plots entfernt bevor die
        Elemente des zur akutellen Silhouetten-Analyse gehörenden Distanzen-Plots berechnet werden.
        Im Anschluss daran wird die Anzeigefläche des Parameter-Plots und des Distanzen-Plots/Modell aktualisiert.
        :param information_set_for_final_clusters: Dictionary mit keys=> Tupel, welches das finale Cluster-Zentrum
                                                                         repräsentiert;
                                             values=> Liste an 3-Tupeln der Form (Datenpunkt als Tupel (x,y),
                                             Silhouette des Datenpunkts, Tupel, welches den am nächsten liegenden
                                             Cluster repräsentiert)
        """
        # Zeichnen des Silhouetten-Graphen
        Plot_Utils_Analysis.draw_silhouette_analysis_graph(current_figure=self.current_figure_analysis,
                                                           information_set_for_final_clusters=information_set_for_final_clusters)

        # Entfernen ggf. vorhandener Distanzplots, die während dieser Aktivierung der Parameteranalyse berechnet und
        # angezeigt wurden
        Plot_Utils_Model.remove_distances_parameter_elbow_analysis(current_plot_container=self.current_plot_model)
        Plot_Utils_Model.remove_distances_parameter_silhouette_analysis(current_plot_container=self.current_plot_model)
        # Berechnung der für die Darstellung der Distanzen-Plots notwendigen Line2D-Objekte. Diese sind zu Beginn
        # alle ausgeblendet
        Plot_Utils_Model.draw_distances_parameter_silhouette_analysis(current_plot_container=self.current_plot_model,
                                                                      final_clusters_information_set=information_set_for_final_clusters)

        # Anzeige des Distanzen-Plots
        self.redraw_model()

        # Anzeige des Parametergraphs
        self.redraw_parameter_analysis()

    def update_parameter_analysis_silhouette_distance_plot(self, x_coordinate, y_coordinate):
        """
        Blendet die Distanzlinien der Silhouetten-Analyse des aktuell geklickten Datenpunkts ein. Es muss sichergestellt
        sein, dass der geklickte Datenpunkt in der Anzeigefläche vorhanden ist. Im Anschluss wird die grafische Anzeige
        des Distanzen-Plots/Modells aktualisiert.
        :param x_coordinate: x-Koordinate des geklickten Datenpunkts
        :param y_coordinate: y-Koordinate des geklickten Datenpunkts
        """
        Plot_Utils_Model.update_distances_parameter_silhouette_analysis(current_plot_container=self.current_plot_model,
                                                                        x_coord_clicked=x_coordinate,
                                                                        y_coord_clicked=y_coordinate)
        # Anzeige des Distanzen-Plots
        self.redraw_model()

    def update_layer_of_datapoints(self, in_front):
        """
        Setzt die Anzeigeebene aller vorhandenen Datenpunkte in Abhängigkeit von dem übergebenen Wahrheitswert und
        aktualisiert die Anzeigefläche.
        :param in_front: True, wenn die Datenpunkte in den Vordergrund verschoben werden soll; False, sonst
        """
        Plot_Utils_Model.set_layer_datapoints(current_plot_container=self.current_plot_model, in_front=in_front)
        # Anzeige des Distanzen-Plots
        self.redraw_model()

    def update_prog_bars_distances(self, distances_as_tuple):
        """
        Aktualisiert die Anzeige der Progressbars für die Distanzsummen
        :param distances_as_tuple: Tupel (distA, distB) mit distA als den mittleren Abstand des aktuell gewählten
                                   Datenpunkts zu den anderen Datenpunkten des eigenen Clusters und distB als den
                                   mittleren Abstand des aktuell gewählten Datenpunkts zu den anderen Datenpunkten des
                                   am nächsten liegenden Clusters
        """
        if distances_as_tuple[0] == 0 and distances_as_tuple[1] == 0:
            unit = 1
        else:
            unit = 100 / (distances_as_tuple[0] + distances_as_tuple[1])
        self.prog_bar_display_distA['value'] = distances_as_tuple[0] * unit
        self.prog_bar_display_distB['value'] = distances_as_tuple[1] * unit

    def redraw_parameter_analysis(self):
        """
        Zeichnet die Anzeigefläche des Parametergraphen neu.
        """
        self.canvas_display_analysis.draw()

    def update_tooltip(self, show_tooltip=False):
        """
        Ein- bzw. Ausblenden des Tooltips zur Anzeige der Punktkoordinaten on Hover.
        :param show_tooltip: True, wenn der Tooltip angezeigt werden soll; False, sonst
        """
        self.current_plot_model.tooltip_annotation.set_visible(show_tooltip)
        self.redraw_model()