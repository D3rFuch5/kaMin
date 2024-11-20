import tkinter as tk
import tkinter.ttk as ttk

from src import View_Window, Plot_Utils_Color_Quantization_Image, Plot_Utils_Color_Quantization_Color_Channels


class Frame_Color_Quantization(tk.Frame):
    """
    Klasse realisiert den Frame, welcher die Widgets für die Demonstration der Farbreduzierung enthält.
    Der Klasse erbt direkt aus der Klasse Frame von Tkinter
    """

    SELECTABLE_VALUES_K = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "15", "20", "25", "30", "35", "40"]

    def __init__(self, parent_window, logo_image, app_mode_variable):
        super().__init__(master=parent_window)

        # Dynamische Größenanpassung an das Fenster.
        # Alles in column 0 wird an die Breite des Fensters angepasst
        self.columnconfigure(index=0, weight=1)

        # Aktivierung der Ausdehnung des Anzeigebereichs
        self.rowconfigure(index=2, weight=1)

        # Widgets für die Auswahl der Trainingsdaten
        self.selected_filepath_image_file = None
        self.frm_choose_image_container = None

        self.frm_choose_image_from_file = None
        self.btn_choose_image_file = None
        self.lbl_display_selected_filepath_image_file = None

        self.menu_modes = None
        self.menu_app_mode = None

        self.lbl_logo = None

        self.init_image_selection(logo_image=logo_image, mode_variable=app_mode_variable)

        # Widgets für die Einstellungen zur Farbreduktion und des Kontroll-Buttons
        self.show_image_file_size = None
        self.selected_number_of_colors_color_quantization = None
        self.frm_color_quantization_controls_container = None
        self.frm_color_quantization_controls = None
        self.frm_color_num_selection_color_quantization = None
        self.com_box_number_of_colors_color_quantization = None
        self.btn_calculate_color_quantization = None
        self.ck_btn_show_image_file_size = None

        self.selected_number_of_colors_color_channels = None
        self.selected_color_channels = None
        self.frm_quantization_color_channels_controls = None
        self.frm_color_num_selection_color_channels = None
        self.com_box_number_of_colors_color_channels = None
        self.frm_color_channel_selection = None
        self.com_box_color_channels = None
        self.btn_calculate_quantization_color_channels = None

        self.init_quantization_settings()

        # Widgets für die Anzeige der beiden Bilder der Farbreduktion
        self.frm_display_color_quantization = None
        self.canvas_display_color_quantization = None
        self.current_axes_color_quantization = None

        # Widgets für die Anzeige der beiden Bilder der Farbreduktion mit weggelassenen Farben
        self.frm_display_k_means_quantization_color_channels = None
        self.canvas_display_quantization_color_channels = None
        self.current_axes_quantization_color_channels = None

        self.notebook_display_color_quantization = None
        self.init_notebook()

    def init_image_selection(self, logo_image, mode_variable):
        """
        Erstellt die Oberfläche zur Auswahl des Bilds, der Anzeige des ausgewählten Dateinamens und des
        Logos.
        """
        self.selected_filepath_image_file = tk.StringVar()

        # Frame, welcher alle Widgets in der Reihe der Bildauswahl enthält.
        self.frm_choose_image_container = tk.Frame(master=self, borderwidth=0)
        self.frm_choose_image_container.grid(column=0, row=0, sticky="ew", padx=(2, 0), pady=(0, 10))
        # Ausdehnung des Bereichs für Auswahl der Datei auf die verfügbare Breite
        self.frm_choose_image_container.columnconfigure(index=0, weight=1)

        # Frame, welcher alle Widgets enthält, die zur Auswahl des Bilds aus einer Datei nötig sind
        self.frm_choose_image_from_file = tk.LabelFrame(master=self.frm_choose_image_container,
                                                        text="W\u00E4hlen Sie eine Bilddatei aus:",
                                                        borderwidth=0, font=View_Window.default_FONT_BOLD)
        self.frm_choose_image_from_file.grid(column=0, row=0, sticky="w")
        # Ausdehnung des Bereichs für die Anzeige des Dateinamens auf verfügbare Breite
        self.frm_choose_image_from_file.columnconfigure(index=0, weight=1)
        self.frm_choose_image_from_file.columnconfigure(index=1, weight=1)

        self.btn_choose_image_file = ttk.Button(master=self.frm_choose_image_from_file, text="\u00D6ffnen", width=21)
        self.btn_choose_image_file.grid(column=0, row=0, sticky="w", padx=(2, 0))

        self.lbl_display_selected_filepath_image_file = ttk.Label(master=self.frm_choose_image_from_file)
        self.lbl_display_selected_filepath_image_file.grid(column=1, row=0, padx=(5, 0), sticky="w")

        self.menu_modes = tk.Menu(tearoff=False)
        self.menu_modes.add_radiobutton(label=View_Window.APP_MODE_Simulation_K_Means, variable=mode_variable,
                                        value=View_Window.APP_MODE_Simulation_K_Means)
        self.menu_modes.add_radiobutton(label=View_Window.APP_MODE_Color_Quantization, variable=mode_variable,
                                        value=View_Window.APP_MODE_Color_Quantization)

        self.menu_app_mode = ttk.Menubutton(master=self.frm_choose_image_container, text="App-Modus",
                                            menu=self.menu_modes)
        self.menu_app_mode.grid(column=1, row=0, sticky="ne", padx=(10, 10))

        self.lbl_logo = ttk.Label(master=self.frm_choose_image_container, image=logo_image)
        self.lbl_logo.grid(column=2, row=0, sticky="e")

    def init_quantization_settings(self):
        """
        Erstellt die Oberfläche zur Auswahl des Parameters k der Farbanzahl und des Kontroll-Buttons.
        """
        # Frame für die Kontroll-Widgets im Farbreduktions-Modus
        self.selected_number_of_colors_color_quantization = tk.IntVar()
        self.show_image_file_size = tk.BooleanVar()
        self.frm_color_quantization_controls_container = tk.Frame(master=self, borderwidth=0)
        self.frm_color_quantization_controls_container.grid(column=0, row=1, sticky="ew", padx=(2, 0), pady=(0, 10))
        self.frm_color_quantization_controls_container.columnconfigure(index=0, weight=1)
        self.frm_color_quantization_controls_container.columnconfigure(index=1, weight=1)

        self.frm_color_quantization_controls = tk.Frame(master=self.frm_color_quantization_controls_container,
                                                        borderwidth=0)
        self.frm_color_quantization_controls.grid(column=0, row=1, sticky="w")
        self.frm_color_quantization_controls.columnconfigure(index=0, weight=1)
        self.frm_color_quantization_controls.columnconfigure(index=1, weight=1)
        self.frm_color_quantization_controls.columnconfigure(index=2, weight=1)

        self.frm_color_num_selection_color_quantization = tk.LabelFrame(
            master=self.frm_color_quantization_controls,
            text="Anzahl an Farben (k)",
            font=View_Window.default_FONT_BOLD, borderwidth=0)
        self.frm_color_num_selection_color_quantization.columnconfigure(index=0, weight=1)
        self.frm_color_num_selection_color_quantization.grid(column=0, row=0, sticky="nw", padx=(1, 0))

        self.com_box_number_of_colors_color_quantization = ttk.Combobox(
            master=self.frm_color_num_selection_color_quantization,
            textvariable=self.selected_number_of_colors_color_quantization,
            state="readonly", width=24,
            values=self.SELECTABLE_VALUES_K)
        self.com_box_number_of_colors_color_quantization.current(newindex=0)
        self.com_box_number_of_colors_color_quantization.grid(column=0, row=0, sticky="w", padx=(0, 10))

        self.btn_calculate_color_quantization = ttk.Button(master=self.frm_color_quantization_controls,
                                                           text="Farbreduktion berechnen", width=21)
        self.btn_calculate_color_quantization.grid(column=1, row=0, sticky='sw')

        self.ck_btn_show_image_file_size = ttk.Checkbutton(
            master=self.frm_color_quantization_controls_container,
            text="Dateigr\u00F6ssen anzeigen",
            takefocus=0,
            variable=self.show_image_file_size,
            onvalue=True,
            offvalue=False)
        self.ck_btn_show_image_file_size.grid(column=1, row=0, sticky="e", padx=(2, 2))

        # Frame für die Kontroll-Widgets im Reduktionsmodus-Modus für die einzelnen Farbkanäle
        self.selected_number_of_colors_color_channels = tk.IntVar()
        self.selected_color_channels = tk.StringVar()
        self.frm_quantization_color_channels_controls = tk.Frame(master=self.frm_color_quantization_controls_container,
                                                                 borderwidth=0)
        # self.frm_quantization_color_channels_controls.grid(column=0, row=1, sticky="w", padx=(2, 0),
        #                                                             pady=(0, 10))
        self.frm_quantization_color_channels_controls.columnconfigure(index=0, weight=1)
        self.frm_quantization_color_channels_controls.columnconfigure(index=1, weight=1)
        self.frm_quantization_color_channels_controls.columnconfigure(index=2, weight=1)

        self.frm_color_channel_selection = tk.LabelFrame(
            master=self.frm_quantization_color_channels_controls,
            text="Farbkan\u00E4le w\u00E4hlen",
            font=View_Window.default_FONT_BOLD, borderwidth=0)
        self.frm_color_channel_selection.grid(column=0, row=0, sticky="nw", padx=(1, 0))
        self.frm_color_channel_selection.columnconfigure(index=0, weight=1)

        self.com_box_color_channels = ttk.Combobox(
            master=self.frm_color_channel_selection,
            textvariable=self.selected_color_channels,
            state="readonly", width=24,
            values=["rot-gr\u00FCn", "rot-blau", "gr\u00FCn-blau"])
        self.com_box_color_channels.current(newindex=0)
        self.com_box_color_channels.grid(column=0, row=0, sticky="w", padx=(0, 10))

        self.frm_color_num_selection_color_channels = tk.LabelFrame(
            master=self.frm_quantization_color_channels_controls,
            text="Anzahl an Farben (k)",
            font=View_Window.default_FONT_BOLD, borderwidth=0)
        self.frm_color_num_selection_color_channels.grid(column=1, row=0, sticky="nw", padx=(1, 0))
        self.frm_color_num_selection_color_channels.columnconfigure(index=0, weight=1)

        self.com_box_number_of_colors_color_channels = ttk.Combobox(
            master=self.frm_color_num_selection_color_channels,
            textvariable=self.selected_number_of_colors_color_channels,
            state="readonly", width=24,
            values=self.SELECTABLE_VALUES_K)
        self.com_box_number_of_colors_color_channels.current(newindex=0)
        self.com_box_number_of_colors_color_channels.grid(column=0, row=0, sticky="w", padx=(0, 10))

        self.btn_calculate_quantization_color_channels = ttk.Button(
            master=self.frm_quantization_color_channels_controls,
            text="1. Farbkanal entfernen", width=25)
        self.btn_calculate_quantization_color_channels.grid(column=2, row=0, sticky='sw')

    def init_notebook(self):
        # Erstellen des Notebooks
        self.notebook_display_color_quantization = ttk.Notebook(master=self)
        self.notebook_display_color_quantization.grid(column=0, row=2, sticky="nsew", pady=(5, 0))

        # Erstellen der Frames, welche im Notebook angezeigt werden/auswählbar sein sollen
        self.init_frame_display_color_quantization()
        self.init_frame_display_k_means_color_channels()

        # Hinzufügen der Frames zum Notebook
        # Tab 0
        self.notebook_display_color_quantization.add(child=self.frm_display_color_quantization,
                                                     text="Farbreduktion allgemein ",
                                                     sticky="nsew")

        # Tab 1
        self.notebook_display_color_quantization.add(child=self.frm_display_k_means_quantization_color_channels,
                                                     text=" Farbreduktion Farbkan\u00E4le k ",
                                                     sticky="nsew")

        self.notebook_display_color_quantization.select(0)
        self.notebook_display_color_quantization.tab(tab_id=1, state="disabled")

    def init_frame_display_color_quantization(self):
        self.frm_display_color_quantization = tk.Frame(master=self.notebook_display_color_quantization, borderwidth=0)
        self.frm_display_color_quantization.pack(fill="both", expand=True)

        # Ausbreitung des Canvas zur Anzeige der Figure auf maximale Größe
        self.frm_display_color_quantization.columnconfigure(index=0, weight=1)
        self.frm_display_color_quantization.rowconfigure(index=0, weight=1)

        # Hier wird das Tkinter Canvas - Widget gespeichert. Dieses enthält eine Matplotlib - Figure und die aktuellen
        # Plots (Axes).
        self.canvas_display_color_quantization = Plot_Utils_Color_Quantization_Image.initialize_figure(
            master=self.frm_display_color_quantization)
        self.current_axes_color_quantization = self.canvas_display_color_quantization.figure.get_axes()
        Plot_Utils_Color_Quantization_Image.initialize_axes(current_axes=self.current_axes_color_quantization)
        self.canvas_display_color_quantization.get_tk_widget().grid(column=0, row=0, sticky="nsew")

    def init_frame_display_k_means_color_channels(self):
        self.frm_display_k_means_quantization_color_channels = tk.Frame(master=self.notebook_display_color_quantization,
                                                                        borderwidth=0)
        self.frm_display_k_means_quantization_color_channels.pack(fill="both", expand=True)
        # Ausbreitung des Canvas zur Anzeige der Figure auf maximale Größe
        self.frm_display_k_means_quantization_color_channels.columnconfigure(index=0, weight=1)
        self.frm_display_k_means_quantization_color_channels.rowconfigure(index=0, weight=1)

        # Hier wird das Tkinter Canvas - Widget gespeichert. Dieses enthält eine Matplotlib - Figure und die aktuellen
        # Plots (Axes).
        self.canvas_display_quantization_color_channels = (Plot_Utils_Color_Quantization_Color_Channels.
        initialize_figure(
            master=self.frm_display_k_means_quantization_color_channels))
        self.current_axes_quantization_color_channels = self.canvas_display_quantization_color_channels.figure.get_axes()
        Plot_Utils_Color_Quantization_Color_Channels.initialize_axes(
            current_axes=self.current_axes_quantization_color_channels)
        self.canvas_display_quantization_color_channels.get_tk_widget().grid(column=0, row=0, sticky="nsew")

    def update_view_enable_quantization(self, enable, step_remove_color_channel=True):
        if enable:
            state_controls = tk.NORMAL
            self.com_box_number_of_colors_color_quantization['state'] = "readonly"
            if step_remove_color_channel:
                self.com_box_color_channels['state'] = "readonly"
                self.com_box_number_of_colors_color_channels['state'] = tk.DISABLED
            else:
                self.com_box_number_of_colors_color_channels['state'] = "readonly"
                self.com_box_color_channels['state'] = tk.DISABLED
            if self.notebook_display_color_quantization.index("current") == 1:
                self.btn_choose_image_file['state'] = tk.DISABLED
            else:
                self.btn_choose_image_file['state'] = state_controls
        else:
            state_controls = tk.DISABLED
            self.com_box_number_of_colors_color_quantization['state'] = state_controls
            self.com_box_color_channels['state'] = state_controls
            self.com_box_number_of_colors_color_channels['state'] = state_controls

        self.menu_app_mode['state'] = state_controls
        self.btn_calculate_color_quantization['state'] = state_controls
        self.ck_btn_show_image_file_size['state'] = state_controls
        self.btn_calculate_quantization_color_channels['state'] = state_controls

    def update_view_color_channels_active(self):
        if self.notebook_display_color_quantization.index("current") == 0:
            self.btn_choose_image_file['state'] = tk.NORMAL
            self.frm_quantization_color_channels_controls.grid_forget()
            self.frm_color_quantization_controls.grid(column=0, row=0, sticky="w", padx=(2, 0), pady=(0, 10))
        else:
            self.btn_choose_image_file['state'] = tk.DISABLED
            self.frm_color_quantization_controls.grid_forget()
            self.frm_quantization_color_channels_controls.grid(column=0, row=0, sticky="w", padx=(2, 0),
                                                               pady=(0, 10))

    def update_view_enable_tab_color_channels(self, enable):
        if enable:
            self.notebook_display_color_quantization.tab(tab_id=1, state=tk.NORMAL)
        else:
            self.notebook_display_color_quantization.tab(tab_id=1, state=tk.DISABLED)

    def update_view_button_calculate_color_channels(self, step_remove_channel):
        if step_remove_channel:
            self.btn_calculate_quantization_color_channels['text'] = "1. Farbkanal entfernen"
            self.com_box_color_channels['state'] = "readonly"
            self.com_box_number_of_colors_color_channels['state'] = tk.DISABLED
        else:
            self.btn_calculate_quantization_color_channels['text'] = "2. Farbreduktion berechnen"
            self.com_box_color_channels['state'] = tk.DISABLED
            self.com_box_number_of_colors_color_channels['state'] = "readonly"

    # Methoden für die Anzeige der generellen Farbreduktion
    def display_selected_filepath_image(self, filepath):
        """
        Zeigt den übergebenen String filepath in der Oberfläche an.
        :param filepath: Dateipfad der ausgewählten Datei
        """
        self.lbl_display_selected_filepath_image_file.config(text=filepath)

    def clear_quantized_image(self):
        Plot_Utils_Color_Quantization_Image.clear_quantized_image(current_axes=self.current_axes_color_quantization)
        self.redraw_color_quantization()

    def display_image_original(self, image_array, file_size):
        Plot_Utils_Color_Quantization_Image.display_original_image(current_axes=self.current_axes_color_quantization,
                                                                   image_as_array=image_array, file_size=file_size)

        self.redraw_color_quantization()

    def display_quantized_image(self, image_array, file_size):
        Plot_Utils_Color_Quantization_Image.display_quantized_image(current_axes=self.current_axes_color_quantization,
                                                                    image_as_array=image_array,
                                                                    num_colors=self.selected_number_of_colors_color_quantization.get(),
                                                                    file_size=file_size)
        self.redraw_color_quantization()

    def display_file_size_general(self, file_size_original="", file_size_quantized="", color_nums=-1):
        Plot_Utils_Color_Quantization_Image.update_title(current_axes=self.current_axes_color_quantization, plot_nr=0,
                                                         file_size=file_size_original)
        Plot_Utils_Color_Quantization_Image.update_title(current_axes=self.current_axes_color_quantization, plot_nr=1,
                                                         file_size=file_size_quantized, num_colors=color_nums)
        self.redraw_color_quantization()

    def reset_display_images(self):
        Plot_Utils_Color_Quantization_Image.initialize_axes(current_axes=self.current_axes_color_quantization)

        self.redraw_color_quantization()

    def reset_selection_number_of_colors_quantization_general(self):
        self.com_box_number_of_colors_color_quantization.current(newindex=0)

    def redraw_color_quantization(self):
        """
        Zeichnet die Anzeigefläche.
        """
        self.canvas_display_color_quantization.draw()

    # Methoden für die Anzeige der Farbreduktion mit reduzierten Farbkanälen
    def display_original_plots_color_channels(self, image_array, colors_array, file_size_reduced_color_channel):
        Plot_Utils_Color_Quantization_Color_Channels.plot_image_original(
            current_axes=self.current_axes_quantization_color_channels, image_as_array=image_array)
        Plot_Utils_Color_Quantization_Color_Channels.set_title_of_plot(
            current_axes=self.current_axes_quantization_color_channels, plot_nr=0,
            channels=self.selected_color_channels.get(), file_size=file_size_reduced_color_channel)
        Plot_Utils_Color_Quantization_Color_Channels.plot_color_samples(
            ax=self.current_axes_quantization_color_channels[2], data_array=colors_array, colors_array=colors_array,
            channels=self.selected_color_channels.get())
        Plot_Utils_Color_Quantization_Color_Channels.set_title_of_plot(
            current_axes=self.current_axes_quantization_color_channels, plot_nr=2)

        self.redraw_quantization_color_channels()

    def display_quantized_plots_color_channels(self, image_array, data_array, colors_array, centroids,
                                               file_size_quantized_image):
        Plot_Utils_Color_Quantization_Color_Channels.plot_image_quantized(
            current_axes=self.current_axes_quantization_color_channels, image_as_array=image_array)
        Plot_Utils_Color_Quantization_Color_Channels.set_title_of_plot(
            current_axes=self.current_axes_quantization_color_channels, plot_nr=1, number_of_colors=len(centroids),
            file_size=file_size_quantized_image)
        Plot_Utils_Color_Quantization_Color_Channels.plot_color_samples(
            ax=self.current_axes_quantization_color_channels[3], data_array=data_array, colors_array=colors_array,
            channels=self.selected_color_channels.get())
        Plot_Utils_Color_Quantization_Color_Channels.plot_colors_centroids(
            ax=self.current_axes_quantization_color_channels[3], colors_centroids=centroids,
            channels=self.selected_color_channels.get())
        Plot_Utils_Color_Quantization_Color_Channels.set_title_of_plot(
            current_axes=self.current_axes_quantization_color_channels, plot_nr=3, number_of_colors=len(centroids))

        self.redraw_quantization_color_channels()

    def display_file_size_color_channels(self, file_size_color_channels="", file_size_color_channels_quantized="",
                                         color_nums=-1, color_channels=""):
        Plot_Utils_Color_Quantization_Color_Channels.set_title_of_plot(
            current_axes=self.current_axes_quantization_color_channels, plot_nr=0, file_size=file_size_color_channels,
            channels=color_channels)
        Plot_Utils_Color_Quantization_Color_Channels.set_title_of_plot(
            current_axes=self.current_axes_quantization_color_channels, plot_nr=1,
            file_size=file_size_color_channels_quantized, number_of_colors=color_nums)
        self.redraw_quantization_color_channels()

    def reset_plots_quantization_color_channels(self, plot_numbers=(0, 1, 2, 3)):
        Plot_Utils_Color_Quantization_Color_Channels.reset_plots(
            current_axes=self.current_axes_quantization_color_channels, ax_numbers=plot_numbers)

        self.redraw_quantization_color_channels()

    def reset_controls_quantization_color_channels(self):
        self.com_box_number_of_colors_color_channels.current(newindex=0)
        self.com_box_color_channels.current(newindex=0)

    def reset_ck_btn_show_file_size(self):
        self.show_image_file_size.set(value=False)

    def redraw_quantization_color_channels(self):
        """
        Zeichnet die Anzeigefläche.
        """
        self.canvas_display_quantization_color_channels.draw()
