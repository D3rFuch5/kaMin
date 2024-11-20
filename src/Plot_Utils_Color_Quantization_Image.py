import os
import sys

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src import Image_Reader

DEFAULT_PATH_IMAGES = "Grafiken"
DEFAULT_TITLE_ORIGINAL_IMAGE = "Orginalbild"
DEFAULT_TITLE_QUANTIZED_IMAGE = "Farbreduziertes Bild"

DEFAULT_ORIGINAL_IMAGE = "default_original_image.png"
DEFAULT_QUANTIZED_IMAGE = "default_reduced_image.png"



def initialize_figure(master):
    plt.style.use('seaborn-v0_8-whitegrid')
    figure = Figure()
    # Fügt der Figure die Sublots zwei Suplots hinzu
    ax1 = figure.add_subplot(1, 2, 1)
    figure.add_subplot(1, 2, 2, sharex=ax1, sharey=ax1)
    return FigureCanvasTkAgg(figure=figure, master=master)


def clear_axes(current_axes):
    for ax in current_axes:
        ax.cla()


def initialize_axes(current_axes):
    clear_image(ax=current_axes[0])
    clear_image(ax=current_axes[1])

    try:
        base_path = sys._MEIPASS
    except:
        base_path = "."

    img_path_def_orig = os.path.join(base_path, DEFAULT_PATH_IMAGES, DEFAULT_ORIGINAL_IMAGE)
    img_path_def_quant = os.path.join(base_path, DEFAULT_PATH_IMAGES, DEFAULT_QUANTIZED_IMAGE)
    update_title(current_axes=current_axes, plot_nr=0)
    current_axes[0].imshow(Image_Reader.read_image_as_numpy_array(image_path=img_path_def_orig))
    update_title(current_axes=current_axes, plot_nr=1)
    current_axes[1].imshow(Image_Reader.read_image_as_numpy_array(image_path=img_path_def_quant))


def clear_image(ax):
    ax.cla()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)


def clear_quantized_image(current_axes):
    clear_image(ax=current_axes[1])
    update_title(current_axes=current_axes, plot_nr=1)
    # Anpassen der Ausdehnung des Plots auf die
    current_axes[1].set_aspect(current_axes[0].get_aspect())


def display_original_image(current_axes, image_as_array, file_size):
    clear_image(ax=current_axes[0])
    clear_image(ax=current_axes[1])
    update_title(current_axes=current_axes, plot_nr=0, file_size=file_size)
    update_title(current_axes=current_axes, plot_nr=1)
    current_axes[0].imshow(image_as_array)
    # Anpassen der Ausdehnung des Plots auf die
    current_axes[1].set_aspect(current_axes[0].get_aspect())


def display_quantized_image(current_axes, image_as_array, num_colors, file_size):
    clear_image(ax=current_axes[1])
    current_axes[1].imshow(image_as_array)
    update_title(current_axes=current_axes, plot_nr=1, num_colors=num_colors, file_size=file_size)


def update_title(current_axes, plot_nr, num_colors=-1, file_size=""):
    if plot_nr == 0:
        title = DEFAULT_TITLE_ORIGINAL_IMAGE
        if file_size != "":
            title = title + " (" + file_size + ")"
        current_axes[0].set_title(label=title)
    elif plot_nr == 1:
        title = DEFAULT_TITLE_QUANTIZED_IMAGE
        if num_colors != -1:
            if num_colors == "1":
                title += " (" + str(num_colors) + " Farbe"
            else:
                title += " (" + str(num_colors) + " Farben"
            if file_size != "":
                title += ", " + file_size
            title += ")"
        current_axes[1].set_title(label=title)
