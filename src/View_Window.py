import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

from src import View_Frame_Training, View_Frame_Color_Quantization

default_FONT_SMALL = "Calibri 11"
default_FONT_SMALL_ITALIC = "Calibri 11 italic"

default_FONT = "Calibri 12"
default_FONT_BOLD = "Calibri 12 bold"
default_FONT_ITALIC = "Calibri 12 italic"

APP_MODE_Color_Quantization = "Farbreduktion"
APP_MODE_Simulation_K_Means = "Simulation k Means"


# Functions, die unabhängig vom Main_Window sind
def display_error_message(parent_window, error_message):
    """
    Zeigt ein Fehlerfenster mit der übergebenen Fehlermeldung an.
    :param parent_window: Fenster, oberhalb dessen das Fehlerfenster angezeigt werden soll.
    :param error_message: Fehlermeldung als Text, die angezeigt werden soll.
    """
    tk.messagebox.showerror(parent=parent_window, title="Fehler", message=error_message)


def display_info_message(parent_window, info_message):
    """
    Zeigt ein Fehlerfenster mit der übergebenen Informationsmeldung an.
    :param parent_window: Fenster, oberhalb dessen das Fehlerfenster angezeigt werden soll.
    :param info_message: Information als Text, die angezeigt werden soll.
    """
    tk.messagebox.showinfo(parent=parent_window, title="Information", message=info_message)


class Window(tk.Tk):
    """
    Klasse realisiert das Hauptfenster der Software.
    Das Hauptfenster erbt direkt aus der Klasse TK von Tkinter, entspricht also dem Hauptfenster
    """
    WINDOWS_icon_image = "logo_k_means.ico"
    path_MAC_icon_image = "./Grafiken/logo_k_means.png"
    DEFAULT_PATH_IMAGES = "Grafiken"
    LOGO_IMAGE = "logo_fuchs_wolf.png"

    def __init__(self):
        super().__init__()
        self.title("kaMin - kMeans App (Alpha 1.2)")
        # Setze Fenstergröße
        self.geometry("1080x700")

        app_style = ttk.Style()
        app_style.configure(style='.', font=default_FONT)
        app_style.configure(style="whiteLabel.TLabel", background="white")
        app_style.configure(style="whiteCheckButton.TCheckbutton", background="white")
        app_style.configure(style="WhiteButton.TButton", background="white", width=25)
        app_style.configure(style="TNotebook.Tab", foreground="blue", font=default_FONT_ITALIC, padding=[2, 2])
        app_style.configure(style='Treeview.Heading', font=default_FONT_BOLD)

        # Erstellung einer beutzerdefinierten Umsetzung der Progressbar, da sich im Theme "Vista" (default unter
        # Windows) die Farbe der Balken nicht setzen lässt.
        app_style.element_create("color.pbar", "from", "clam")
        app_style.layout(style="ColorProgress.Horizontal.TProgressbar",
                         layoutspec=[('Horizontal.Progressbar.trough',
                                      {'sticky': 'nswe',
                                       'children': [('Horizontal.Progressbar.color.pbar',
                                                     {'side': 'left', 'sticky': 'ns'})]})])

        app_style.configure(style="red.ColorProgress.Horizontal.TProgressbar", foreground='red', background='red',
                            bordercolor='red')
        app_style.configure(style="blue.ColorProgress.Horizontal.TProgressbar", foreground='blue', background='blue',
                            bordercolor='blue')

        # Vorbereitung für die Erstellung der ausführbaren Datei
        try:
            base_path = sys._MEIPASS
        except:
            base_path = "."

        if os.name == 'nt':
            self.iconbitmap(os.path.join(base_path, self.DEFAULT_PATH_IMAGES, self.WINDOWS_icon_image))
            app_style.theme_use("vista")
        # posix für Linux und MacOS
        else:
            self.iconphoto(True, tk.PhotoImage(file=self.path_MAC_icon_image))
            app_style.theme_use("clam")

        self.current_logo_path = os.path.join(base_path, self.DEFAULT_PATH_IMAGES, self.LOGO_IMAGE)
        self.img_logo = tk.PhotoImage(file=self.current_logo_path)

        self.app_mode = tk.StringVar(master=self, value=APP_MODE_Simulation_K_Means)

        # Dynamische Größenanpassung an das Fenster.
        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=1)

        # Erzeugen und Hinzufügen des Frames, welcher alle Widgets für die Simulation des k Means-Algorithmus enthält
        self.frm_simulation_k_means = View_Frame_Training.Frame_Training(parent_window=self, logo_image=self.img_logo,
                                                                         app_mode_variable=self.app_mode)

        # Erzeugen und Hinzufügen des Frames, welcher alle Widgets für die Simulation des k Means-Algorithmus enthält.
        # Da initial die Simulation des Algorithmus gezeigt wird, wird der Frame nicht hinzugefügt
        self.frm_color_quantization = View_Frame_Color_Quantization.Frame_Color_Quantization(parent_window=self,
                                                                                             logo_image=self.img_logo,
                                                                                             app_mode_variable=self.app_mode)
        self.frm_simulation_k_means.grid(column=0, row=0, sticky='nsew')

        self.init_gui_footer_credits()

    def set_operating_frame(self):
        """
        Fügt, je nach gewähltem App-Modus, den passenden Frame zum Hauptfenster hinzu und entfernt den anderen Frame.
        """
        if self.app_mode.get() == APP_MODE_Simulation_K_Means:
            self.frm_color_quantization.grid_forget()
            self.frm_simulation_k_means.grid(column=0, row=0, sticky='nsew')
        else:
            self.frm_simulation_k_means.grid_forget()
            self.frm_color_quantization.grid(column=0, row=0, sticky='nsew')

    def init_gui_footer_credits(self):
        """
        Fügt den Footer zu Oberfläche hinzu und befüllt diesen mit Informationen.
        """
        # Anlegen der Credit-Zeile.
        # Nur lokale Widgets, da diese nach dem Öffnen des Fensters nicht mehr zugreifbar sein müssen.
        frm_credits = ttk.Frame(master=self)
        frm_credits.grid(column=0, row=1, sticky="sew")
        frm_credits.columnconfigure(index=0, weight=1)
        lbl_didaktik = tk.Label(master=frm_credits, anchor=tk.W, justify=tk.LEFT,
                                text=" Didaktik der Informatik - Universit\u00E4t Passau",
                                font=default_FONT_SMALL_ITALIC)
        lbl_didaktik.grid(column=0, row=0, sticky="w")
        lbl_university = tk.Label(master=frm_credits, anchor=tk.E, justify=tk.RIGHT,
                                  text="Tobias Fuchs, Wolfgang Pfeffer  ", font=default_FONT_SMALL_ITALIC)
        lbl_university.grid(column=1, row=0, sticky="e")
