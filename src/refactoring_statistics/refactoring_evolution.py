import pandas as pd
import datetime
from configs import Level, LEVEL_MAP
from refactoring_statistics.query_utils import get_metrics_refactorings, get_metrics_stable_level
from utils.log import log_init, log_close, log
import time
from os import path
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


REFACTORING_SAMPLES = 150000
STABLE_SAMPLES = 300000
STABLE_Ks = [15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]
REFACTORING_LEVELS = [Level.Class, Level.Method, Level.Variable, Level.Field, Level.Other]
STABLE_LEVELS = [Level.Class, Level.Method, Level.Variable, Level.Field]
SAVE_DIR = "results/Evolution/"
METRICS = ["qtyOfCommits", "refactoringsInvolved"]


def get_frequency_data_refactorings(level, metric):
    data_path = f"{SAVE_DIR}refactoring_{level.name}_{metric}.csv"
    if not path.exists(data_path):
        refactorings = LEVEL_MAP[level]
        data = get_metrics_refactorings(level, "", refactorings, METRICS)

        frequency_data = pd.DataFrame()
        for refactoring_name in refactorings:
            refactoring_data = data[data["refactoring"] == refactoring_name]
            fraction = refactoring_data[metric].value_counts(normalize=True, sort=False)
            frequency_data[refactoring_name] = fraction
        # convert the index to a column, as it inherently contains the metric count
        frequency_data = frequency_data.sort_index()
        frequency_data[metric] = frequency_data.index
        frequency_data.to_csv(data_path, index=False)
        return frequency_data.sort_index()
    else:
        return pd.read_csv(data_path)


def get_frequency_data_stable(level, metric):
    data_path = f"{SAVE_DIR}stable_{level.name}_{metric}.csv"
    if not path.exists(data_path):
        frequency_data = pd.DataFrame()
        for k in STABLE_Ks:
            data = get_metrics_stable_level(level, k, "", [metric], STABLE_SAMPLES)
            fraction = data[metric].value_counts(normalize=True, sort=False)
            frequency_data[k] = fraction
        # convert the index to a column, as it inherently contains the metric count
        frequency_data = frequency_data.sort_index()
        frequency_data[metric] = frequency_data.index
        frequency_data.to_csv(data_path, index=False)
        return frequency_data.sort_index()
    else:
        return pd.read_csv(data_path)


def line_plot_seaborn(data, x: str, y: str, hue: str, level, scale: str = "log", figsize=(22, 16), custom_palette="tab20"):
    fig_path = f"{SAVE_DIR}{hue}_{level.name}_{x}_{y}_plot.svg"
    title = f"{y} per {x} for {level.name} refactorings"
    xticks = [1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100]
    sns.set(style="darkgrid")
    plt.figure(figsize=figsize)
    sns_plot = sns.lineplot(x=x, y=y, hue=hue, data=data, markers=True, palette=custom_palette)
    sns_plot.set_xlabel(x, fontsize=22)
    sns_plot.set_ylabel(y, fontsize=22)
    sns_plot.set_title(title, fontsize=26)
    plt.xscale(scale)
    plt.xticks(xticks, fontsize=18)
    sns_plot.set_xticklabels(["$%i$" % x for x in xticks], fontsize=18)
    plt.legend(loc=0, borderaxespad=0., fontsize=22)
    plt.savefig(f"{fig_path}")
    plt.close()
    log(f"--Saved box plot to {fig_path}")


def plot_cdf(frequency_data, metric, var_name, level):
    frequency_data_cdf = frequency_data.loc[:, frequency_data.columns != metric].cumsum()
    frequency_data_cdf[metric] = frequency_data[metric]
    frequency_data_cdf_melt = pd.melt(frequency_data_cdf, id_vars=metric, var_name=var_name, value_name="CDF")
    line_plot_seaborn(frequency_data_cdf_melt, x=metric, y="CDF", hue=var_name, level=level)


def plot_frequency(frequency_data, metric, var_name, level):
    frequency_data_melt = pd.melt(frequency_data, id_vars=metric, var_name=var_name, value_name="Frequency")
    line_plot_seaborn(frequency_data_melt, x=metric, y="Frequency", hue=var_name, level=level)


log_init(f"results/Evolution/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt")
log('Begin Statistics')
start_time = time.time()

Path(path.dirname(SAVE_DIR)).mkdir(parents=True, exist_ok=True)
for metric in METRICS:
    for level in REFACTORING_LEVELS:
        frequency_data = get_frequency_data_refactorings(level, metric).head(101)
        plot_frequency(frequency_data, metric, "refactoring", level)
        plot_cdf(frequency_data, metric, "refactoring", level)

    for level in STABLE_LEVELS:
        frequency_data_stable = get_frequency_data_stable(level, metric).head(101)
        plot_frequency(frequency_data_stable, metric, "k", level)
        plot_cdf(frequency_data_stable, metric, "k", level)

log(f"Processing refactoring evolution took {time.time() - start_time:.2f} seconds.")
log_close()

exit()