from src import View_Window, Controller_k_Means, Controller_Color_Quantization


class Controller:
    """
    Klasse realisiert den allgemeinen Controller des k-Means-Simulators, welcher das Hauptfenster erzeugt und hält, die
    Kontroller für die beiden App-Modi "Training des k-Means-Algorithmus" und "Farbreduktion" erstellt und hält sowie
    den Wechsel zwischen den App-Modi umsetzt.
    """
    def __init__(self):
        self.view_window = View_Window.Window()
        self.controller_simulation = Controller_k_Means.Controller_k_Means(
            operating_frame=self.view_window.frm_simulation_k_means)
        self.controller_quantization = Controller_Color_Quantization.Controller_Quantization(
            operating_frame=self.view_window.frm_color_quantization)
        self.bind_callbacks()

    def bind_callbacks(self):
        """
        Belegt die Menüeinträge der Frames für die beiden Modi mit den Funktionalitäten zum Wechsel dieser Frames
        je nach ausgewähltem Modus.
        """
        self.view_window.frm_simulation_k_means.menu_modes.entryconfig(
            index=self.view_window.frm_simulation_k_means.menu_modes.index(View_Window.APP_MODE_Simulation_K_Means),
            command=self.switch_app_mode)
        self.view_window.frm_simulation_k_means.menu_modes.entryconfig(
            index=self.view_window.frm_simulation_k_means.menu_modes.index(View_Window.APP_MODE_Color_Quantization),
            command=self.switch_app_mode)
        self.view_window.frm_color_quantization.menu_modes.entryconfig(
            index=self.view_window.frm_color_quantization.menu_modes.index(View_Window.APP_MODE_Simulation_K_Means),
            command=self.switch_app_mode)
        self.view_window.frm_color_quantization.menu_modes.entryconfig(
            index=self.view_window.frm_color_quantization.menu_modes.index(View_Window.APP_MODE_Color_Quantization),
            command=self.switch_app_mode)

    def switch_app_mode(self):
        """
        Setzt die jeweiligen Modi auf deren Initialzustand zurück und bindet den Frame für den ausgewählten Modus in das
        Hauptfenster ein.
        """
        if self.view_window.app_mode.get() == View_Window.APP_MODE_Simulation_K_Means:
            # Zurücksetzen des Simulationsmodus
            self.controller_simulation.reset_simulation_k_means()
        else:
            self.controller_quantization.reset_color_quantization()
        # Bindet den Frame der View ein, welche den ausgewählten App-Modus umsetzt
        self.view_window.set_operating_frame()

    def start(self):
        """
        Startet die Anwendung, indem die mainloop-Methode des Hauptfensters aufgerufen wird.
        """
        self.view_window.mainloop()
