import matplotlib.pyplot as plt
import numpy as np
from configs import Level, LEVEL_MAP
from refactoring_statistics.query_utils import query_count
from utils.log import log_init, log_close, log
import time
from os import path
from pathlib import Path


def plot_distribution(table_name: str, refactorings, descriptor: str, scale: str = "log"):
    data = query_count(table_name, refactorings)
    fig, ax = plt.subplots(figsize=(max(len(refactorings), 6), 8), dpi=240)
    ax.set_title(f"Refactoring type distribution with mean per {descriptor} ({str(level)})")

    ax.set_yticks(np.append(np.arange(1, 11, 1), np.arange(20, 51, 10)))
    ax.violinplot(data, widths=0.7, points=1000, showmeans=True, showextrema=True, showmedians=False)
    plt.xticks(np.arange(len(refactorings)), refactorings, rotation=30)
    plt.yscale(scale)
    plt.ylabel(f"Refactoring count")
    plt.xlabel("Refactoring types")
    ax.set_ylim(ymin=1)

    fig_path = f"results/Distribution/{descriptor}_{table_name}_{str(level)}_1000_mean_extrema.png"
    plt.savefig(fig_path)


log_init(f"")
log('Begin Statistics')
start_time = time.time()

Path(path.dirname("results/Distribution/")).mkdir(parents=True, exist_ok=True)

for level in Level:
    refactorings = LEVEL_MAP[level]
    if len(refactorings) > 0:
        # plot_distribution("refactoringspercommit", refactorings, "commit")
        # plot_distribution("refactoringsperclass", refactorings, "class", "log")

log(f"Processing statistics took {time.time() - start_time:.2f} seconds.")
log_close()

exit()
