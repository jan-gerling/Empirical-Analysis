import matplotlib.pyplot as plt
import numpy as np
#Copied from https://matplotlib.org/3.1.1/gallery/images_contours_and_fields/image_annotated_heatmap.html#sphx-glr-gallery-images-contours-and-fields-image-annotated-heatmap-py
from utils.log import log
import seaborn as sns


def heatmap(data, row_labels, col_labels, ax=None, cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1), minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1), minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def plot_errorbar(x_label, mean, error, errortype:str, descriptor: str):
    fig, ax = plt.subplots()
    ax.errorbar(x_label, mean, error, linestyle='None', fmt='o')
    plt.ylabel(f"Refactoring count")
    plt.xlabel("Refactoring types")
    plt.title(f"Mean and {errortype} for {descriptor}")

    plt.ylim(ymin=1)
    fig_path = f"results/Aggregate/{descriptor}_mean_{errortype}.svg"
    plt.savefig(fig_path)
    plt.close(fig)


def box_plot(data, label, title, fig_path, scale: str = "log", yticks=[]):
    fig, ax = plt.subplots()
    ax.set_title(f"{title}")
    ax.boxplot(data, showmeans=True, showfliers=False, notch=True, patch_artist=True)
    plt.xticks(np.arange(1, len(label) + 1), label, rotation=30)
    plt.yscale(scale)
    if len(yticks) > 0:
        ax.set_yticks(yticks)
    plt.xlabel("Metrics")
    # plt.legend()
    plt.savefig(fig_path)
    log(f"Saved box plot to {fig_path}")
    plt.close(fig)


def box_plot_seaborn(data, title, fig_path, scale: str, yticks=[], figsize=(22, 16), hue="Instances"):
    sns.set(style="darkgrid")
    plt.figure(figsize=figsize)
    sns_plot = sns.boxplot(x="Metric", y="values", hue=hue, data=data, showfliers=False, showmeans=True,
                           meanprops={"marker":"o", "markerfacecolor":"white", "markeredgecolor":"black", "markersize":"18"})
    sns_plot.set_title(title, fontsize=26)
    plt.xticks(fontsize=18, rotation=30)
    plt.yscale(scale)
    sns_plot.set_xlabel("", fontsize=0)
    sns_plot.set_ylabel("", fontsize=0)
    plt.yticks(yticks, fontsize=18)
    plt.legend(bbox_to_anchor=(1, 1), loc=1, borderaxespad=0., fontsize=22)
    plt.savefig(f"{fig_path}")
    plt.close()
    log(f"--Saved box plot to {fig_path}")