from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

DEFAULT_TITLE_ORIGINAL_IMAGE = "Bild ohne gew\u00E4hlten Farbkanal"
DEFAULT_TITLE_QUANTIZED_IMAGE = "Farbreduziertes Bild"

DEFAULT_TITLE_ORIGINAL_COLORS = "Farben Bild"
DEFAULT_TITLE_QUANTIZED_COLORS = "Reduzierte Farben"

AXIS_LABEL_RED = "Farbkanal Rot"
AXIS_LABEL_GREEN = "Farbkanal Gr\u00FCn"
AXIS_LABEL_BLUE = "Farbkanal Blau"


def initialize_figure(master):
    plt.style.use('seaborn-v0_8-whitegrid')
    figure = Figure()
    # Fügt der Figure die Sublots zwei Suplots hinzu
    ax1 = figure.add_subplot(2, 2, 1)
    ax2 = figure.add_subplot(2, 2, 2, sharex=ax1, sharey=ax1)
    ax3 = figure.add_subplot(2, 2, 3)
    ax4 = figure.add_subplot(2, 2, 4, sharex=ax3, sharey=ax3)
    return FigureCanvasTkAgg(figure=figure, master=master)


def initialize_axes(current_axes):
    clear_image(ax=current_axes[0])
    clear_image(ax=current_axes[1])
    clear_plot(ax=current_axes[2])
    clear_plot(ax=current_axes[3])
    set_title_of_plot(current_axes=current_axes, plot_nr=0)
    set_title_of_plot(current_axes=current_axes, plot_nr=1)
    set_title_of_plot(current_axes=current_axes, plot_nr=2)
    set_title_of_plot(current_axes=current_axes, plot_nr=3)
    current_axes[0].set_aspect(current_axes[1].get_aspect())
    current_axes[1].set_aspect(current_axes[2].get_aspect())
    current_axes[3].set_aspect(current_axes[2].get_aspect())


def reset_plots(current_axes, ax_numbers):
    if len(ax_numbers) == 4:
        current_axes[0].set_aspect(current_axes[2].get_aspect())
    for nr in ax_numbers:
        if nr == 0:
            clear_image(ax=current_axes[nr])
        elif nr == 1:
            clear_image(ax=current_axes[nr])
            current_axes[1].set_aspect(current_axes[0].get_aspect())
        elif nr == 2:
            clear_plot(ax=current_axes[nr])
        elif nr == 3:
            clear_plot(ax=current_axes[nr])
            current_axes[3].set_aspect(current_axes[2].get_aspect())
        set_title_of_plot(current_axes=current_axes, plot_nr=nr)


def clear_image(ax):
    ax.cla()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)


def clear_plot(ax):
    ax.cla()
    ax.set_xlim(xmin=0, xmax=255)
    ax.set_ylim(ymin=0, ymax=255)
    ax.grid(False)


def plot_image_original(current_axes, image_as_array):
    current_axes[0].imshow(image_as_array)
    # Anpassen der Ausdehnung des Plots auf die
    current_axes[1].set_aspect(current_axes[0].get_aspect())


def plot_image_quantized(current_axes, image_as_array):
    current_axes[1].imshow(image_as_array)


def plot_color_samples(ax, data_array, colors_array, channels):
    if channels == "rot-gr\u00FCn":
        X = data_array[:, 0]
        Y = data_array[:, 1]
        ax.set_xlabel(xlabel=AXIS_LABEL_RED)
        ax.set_ylabel(ylabel=AXIS_LABEL_GREEN)
    elif channels == "rot-blau":
        X = data_array[:, 0]
        Y = data_array[:, 2]
        ax.set_xlabel(xlabel=AXIS_LABEL_RED)
        ax.set_ylabel(ylabel=AXIS_LABEL_BLUE)
    else:
        X = data_array[:, 1]
        Y = data_array[:, 2]
        ax.set_xlabel(xlabel=AXIS_LABEL_GREEN)
        ax.set_ylabel(ylabel=AXIS_LABEL_BLUE)
    ax.scatter(x=X, y=Y, c=colors_array / 255, s=1, alpha=1.0)


def plot_colors_centroids(ax, colors_centroids, channels):
    if channels == "rot-gr\u00FCn":
        X = colors_centroids[:, 0]
        Y = colors_centroids[:, 1]
    elif channels == "rot-blau":
        X = colors_centroids[:, 0]
        Y = colors_centroids[:, 2]
    else:
        X = colors_centroids[:, 1]
        Y = colors_centroids[:, 2]
    # Umrandung des Kreisrings um das Zentrum
    ax.scatter(x=X, y=Y, c='grey', s=100, alpha=1.0)
    # Kreisring des Zentrums
    ax.scatter(x=X, y=Y, c=colors_centroids / 255, s=50, alpha=1.0)
    # Zentrum an sich
    ax.scatter(x=X, y=Y, c='black', s=5, alpha=1.0)


def set_title_of_plot(current_axes, plot_nr, number_of_colors=-1, file_size="", channels=""):
    # Plot zur Anzeige des um den Farbkanal reduzierten Orginalbilds
    if plot_nr == 0:
        if channels == "rot-gr\u00FCn":
            title = "Bild ohne blauen Farbanteil"
        elif channels == "rot-blau":
            title = "Bild ohne gr\u00FCnen Farbanteil"
        elif channels == "gr\u00FCn-blau":
            title = "Bild ohne roten Farbanteil"
        else:
            title = DEFAULT_TITLE_ORIGINAL_IMAGE
        if file_size != "":
            title += " (" + file_size + ")"
        current_axes[0].set_title(label=title)
    elif plot_nr == 1:
        # Fall: Default-Title
        title = DEFAULT_TITLE_QUANTIZED_IMAGE
        if number_of_colors != -1:
            if number_of_colors == 1:
                title += " (" + str(number_of_colors) + " Farbe"
            else:
                title += " (" + str(number_of_colors) + " Farben"
            if file_size != "":
                title += ", " + file_size
            title += ")"
        current_axes[1].set_title(label=title)
    elif plot_nr == 2:
        current_axes[2].set_title(label=DEFAULT_TITLE_ORIGINAL_COLORS)
    else:
        if number_of_colors < 1:
            color_string = ""
        elif number_of_colors == 1:
            color_string = " (" + str(number_of_colors) + " Farbe)"
        else:
            color_string = " (" + str(number_of_colors) + " Farben)"
        current_axes[3].set_title(label=DEFAULT_TITLE_QUANTIZED_COLORS + color_string)
