from configs import Level, LEVEL_MAP
from refactoring_statistics.query_utils import query_evolution, query_evolution_level
from utils.log import log_init, log_close, log
import time
from os import path
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


def plot_violin(data, label, count, level, scale: str = "symlog", points: int = 500):
    fig, ax = plt.subplots(figsize=(max(len(label), 32), 12), dpi=120)
    ax.set_title(f"Refactoring type distribution with mean per {count} ({str(level)})")
    ax.violinplot(data, widths=0.7, points=points, showmeans=True, showextrema=True, showmedians=False)
    plt.xticks(np.arange(len(label)), label, rotation=30)
    plt.yscale(scale)
    plt.ylabel(f"{count}")
    plt.xlabel("Refactoring types")

    fig_path = f"results/Evolution/Refactorings_Commit_Count_{count}_{str(level)}_{scale}_{points}_mean_extrema_violin.png"
    plt.savefig(fig_path)
    log(f"Saved violin plot to {fig_path}")


def plot_distribution(x_data, y_data, label, count, level, scale: str = "symlog"):
    fig, ax = plt.subplots(figsize=(max(len(label), 32), 12), dpi=120)
    ax.set_title(f"Refactoring type distribution per {count} ({str(level)})")
    plt.xscale(scale)
    plt.xlabel(f"{count}")
    plt.ylabel(f"likelihood")
    for index, distribution in enumerate(x_data):
        plt.plot(x_data[index], y_data[index], label=f"{label[index]}")
    plt.legend()
    fig_path = f"results/Evolution/Refactorings_Commit_Count_{count}_{str(level)}_{scale}_pf.png"
    plt.savefig(fig_path)
    log(f"Saved distribution plot to {fig_path}")


def query_plot(refactorings, level, count: str):
    counts_aggregate = query_evolution("Refactorings_Commit_Count", count, True, refactorings)
    plot_distribution([df[f"{count}"] for df in counts_aggregate],
                      [df["refactoring_count"].div(df[f"{count}_total"]) for df in counts_aggregate],
                      refactorings, count, level)
    counts_raw = query_evolution("Refactorings_Commit_Count", count, False, refactorings)
    plot_violin([df[f"{count}"].values for df in counts_raw], refactorings, count, level)
    return counts_aggregate, counts_raw


def query_plot_level(levels, count: str):
    counts_aggregate = query_evolution_level("Refactorings_Commit_Count", count, True, levels)
    plot_distribution([df[f"{count}"] for df in counts_aggregate],
                      [df["refactoring_count"].div(df[f"{count}_total"]) for df in counts_aggregate],
                      levels, count, "all_level")
    counts_raw = query_evolution_level("Refactorings_Commit_Count", count, False, levels)
    plot_violin([df[f"{count}"].values for df in counts_raw], levels, count, "all_level")
    return counts_aggregate, counts_raw


log_init(f"")
log('Begin Statistics')
start_time = time.time()

Path(path.dirname("results/Evolution/")).mkdir(parents=True, exist_ok=True)

levels = list(Level)[1:]
query_plot_level(levels, "qtyOfCommits")
query_plot_level(levels, "qtyOfRefactorings")
# for level in Level:
# refactorings = LEVEL_MAP[level]
#   if len(refactorings) > 0:
#       log(f"-----{str(level)}")
#       commit_counts_aggregate, commit_counts_raw = query_plot(refactorings, level, "qtyOfCommits")
#       refactoring_counts_aggregate, refactoring_counts_raw = query_plot(refactorings, level, "qtyOfRefactorings")


log(f"Processing statistics took {time.time() - start_time:.2f} seconds.")
log_close()

exit()
