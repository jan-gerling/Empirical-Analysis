from configs import Level, LEVEL_MAP
from db.DBConnector import close_connection
from refactoring_statistics.plot_utils import box_plot_seaborn, line_plot_seaborn
from refactoring_statistics.query_utils import get_metrics_refactoring_level, get_metrics_stable_level, \
    get_metrics_refactorings, get_metrics_stable_all
from utils.log import log_init, log_close, log
import time
import datetime
import pandas as pd
from pathlib import Path
from os import path


REFACTORING_SAMPLES = 50000
STABLE_SAMPLES = 50000
REFACTORING_LEVELS = [Level.Class, Level.Method, Level.Variable, Level.Field, Level.Other]
STABLE_LEVELS = [Level.Class, Level.Method, Level.Variable, Level.Field]
STABLE_Ks = [15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]
IMG_FORMAT = "svg"
DATASET = ""

PROCESS_METRICS_FIELDS = ["qtyOfCommits",
                          "bugFixCount",
                          "refactoringsInvolved"]

OWNERSHIP_METRICS_FIELDS = ["authorOwnership",
                            "qtyMajorAuthors",
                            # "qtyMinorAuthors",
                            "qtyOfAuthors"]


# plot all refactoring for each level
def metrics_refactorings_individual_levels(dataset, save_dir, yticks, metrics, title, file_descriptor):
    # refactoring metrics per level
    for level in REFACTORING_LEVELS:
        fig_path_box = f"results/{save_dir}/{file_descriptor}_{str(level)}_log_box_plot_{dataset}.{IMG_FORMAT}"
        if not path.exists(fig_path_box):
            refactoring_metrics_level = get_metrics_refactorings(level, dataset, LEVEL_MAP[level], metrics)
            refactoring_metrics_level = pd.melt(refactoring_metrics_level, id_vars="refactoring", var_name="Metric", value_vars=metrics, value_name="values")
            refactoring_metrics_level['refactoring'] = refactoring_metrics_level['refactoring'].astype('category')
            refactoring_metrics_level['Metric'] = refactoring_metrics_level['Metric'].astype('category')
            box_plot_seaborn(refactoring_metrics_level, f"{title} {str(level)}", fig_path_box, scale="log", yticks=yticks, hue="refactoring")
        else:
            log(f"--Skipped box plot at {fig_path_box}, because it already exists.")


# plot the metrics for each refactoring level and for all stable levels, only applicable for process and ownership metrics
def process_metrics_levels(dataset, save_dir, yticks, metrics, title, file_descriptor):
    combined_refactoring_metrics = pd.DataFrame()
    # refactoring metrics per level
    for level in REFACTORING_LEVELS:
        refactoring_metrics_level = get_metrics_refactoring_level(level, dataset, LEVEL_MAP[level], metrics, samples=REFACTORING_SAMPLES)
        refactoring_metrics_level['Instances'] = f"{str(level)}"
        refactoring_metrics_level = pd.melt(refactoring_metrics_level, id_vars="Instances", var_name="Metric", value_vars=metrics, value_name="values")
        combined_refactoring_metrics = combined_refactoring_metrics.append(refactoring_metrics_level)

    # stable metrics for all level and k
    for k in STABLE_Ks:
        fig_path_box = f"results/{save_dir}/{file_descriptor}_K{k}_log_box_plot_{dataset}.{IMG_FORMAT}"
        if not path.exists(fig_path_box):
            combined_stable_metrics = get_metrics_stable_all(k, dataset, STABLE_LEVELS, metrics, samples=STABLE_SAMPLES)
            combined_stable_metrics['Instances'] = f"Stable K={k}"
            combined_stable_metrics = pd.melt(combined_stable_metrics, id_vars="Instances", var_name="Metric", value_vars=metrics, value_name="values")

            # merge stable and refactoring metrics
            data_combined = pd.concat([combined_refactoring_metrics, combined_stable_metrics])
            data_combined['Instances'] = data_combined['Instances'].astype('category')
            data_combined['Metric'] = data_combined['Metric'].astype('category')

            box_plot_seaborn(data_combined, title, fig_path_box, scale="log", yticks=yticks)
        else:
            log(f"--Skipped plot at {fig_path_box}, because it already exists.")


def process_stable_k(dataset, save_dir, metrics, yticks, title, file_descriptor):
    # stable metrics for all level and k
    fig_path_box = f"results/{save_dir}/{file_descriptor}_line_plot_{dataset}.{IMG_FORMAT}"
    if not path.exists(fig_path_box):
        combined_stable_metrics = pd.DataFrame()
        for k in STABLE_Ks:
            stable_metrics = get_metrics_stable_all(k, dataset, STABLE_LEVELS, metrics, samples=STABLE_SAMPLES)
            stable_metrics['K'] = k
            stable_metrics = pd.melt(stable_metrics, id_vars="K", var_name="Metric", value_vars=metrics, value_name="values")
            combined_stable_metrics = combined_stable_metrics.append(stable_metrics)
        # plot
        line_plot_seaborn(combined_stable_metrics, title, fig_path_box, xticks=STABLE_Ks, yticks=yticks, scale="log")
    else:
        log(f"--Skipped plot at {fig_path_box}, because it already exists.")


log_init(f"results/Distribution/class_metrics_distribution_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt")
start_time = time.time()

# process and ownership metrics individual refactorings
Path(path.dirname("results/Distribution/PO_Metrics/Refactorings/")).mkdir(parents=True, exist_ok=True)
metrics_refactorings_individual_levels(DATASET, "Distribution/PO_Metrics/Refactorings", yticks=[0.1, 0.15, 0.25, 0.5, 0.75, 1, 1.5, 2.0, 2.5, 5, 6, 7.5, 10, 15, 20, 25, 50, 75, 100, 125, 150], metrics=PROCESS_METRICS_FIELDS+OWNERSHIP_METRICS_FIELDS,
                                       title="Process- and Ownership Metrics: Refactorings",
                                       file_descriptor="Process_Ownership_Metrics")

metrics_refactorings_individual_levels(DATASET, "Distribution/PO_Metrics/Refactorings", metrics=PROCESS_METRICS_FIELDS, yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 50, 75, 90, 100],
                                       title="Process Metrics: Refactorings",
                                       file_descriptor="Process_Metrics")

Path(path.dirname("results/Distribution/PO_Metrics/Refactorings/")).mkdir(parents=True, exist_ok=True)
metrics_refactorings_individual_levels(DATASET, "Distribution/PO_Metrics/Refactorings", metrics=OWNERSHIP_METRICS_FIELDS, yticks=[0.1, 0.15, 0.25, 0.5, 0.75, 1, 1.5, 2.0, 2.5, 5, 6],
                                       title="Ownership Metrics: Refactorings",
                                       file_descriptor="Ownership_Metrics")

# process metrics all levels
Path(path.dirname("results/Distribution/PO_Metrics/Levels/")).mkdir(parents=True, exist_ok=True)
process_metrics_levels(DATASET, "Distribution/PO_Metrics/Levels", yticks=[0.1, 0.15, 0.25, 0.5, 0.75, 1, 1.5, 2.0, 2.5, 5, 6], metrics=OWNERSHIP_METRICS_FIELDS,
                       title="Ownership Metrics: Refactorings vs Stable Instances",
                       file_descriptor="Ownership_Metrics")

process_metrics_levels(DATASET, "Distribution/PO_Metrics/Levels", yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 50, 75, 90, 100], metrics=PROCESS_METRICS_FIELDS,
                       title="Process Metrics: Refactorings vs Stable Instances",
                       file_descriptor="Process_Metrics")

process_metrics_levels(DATASET, "Distribution/PO_Metrics/Levels", yticks=[0.1, 0.15, 0.25, 0.5, 0.75, 1, 1.5, 2.0, 2.5, 5, 6, 7.5, 10, 15, 20, 25, 50, 75, 90, 100, 125, 150], metrics=PROCESS_METRICS_FIELDS+OWNERSHIP_METRICS_FIELDS,
                       title="Process- and Ownership Metrics: Refactorings vs Stable Instances",
                       file_descriptor="Process_Ownership_Metrics")

# process- and ownership metrics stable for k's (line plot)
Path(path.dirname("results/Distribution/PO_Metrics/K/")).mkdir(parents=True, exist_ok=True)
process_stable_k(DATASET, "Distribution/PO_Metrics/K", metrics=PROCESS_METRICS_FIELDS+OWNERSHIP_METRICS_FIELDS, yticks=[0.1, 0.15, 0.25, 0.5, 0.75, 1, 1.5, 2.0, 2.5, 5, 6, 7.5, 10, 15, 20, 25, 50, 75, 90, 100],
                 title="Process- and Ownership Metrics: Stable K's",
                 file_descriptor="Process_Ownership_Metrics")

Path(path.dirname("results/Distribution/PO_Metrics/K/")).mkdir(parents=True, exist_ok=True)
process_stable_k(DATASET, "Distribution/PO_Metrics/K", metrics=PROCESS_METRICS_FIELDS, yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 50, 75, 90, 100],
                 title="Process Metrics: Stable K's",
                 file_descriptor="Process_Metrics")

Path(path.dirname("results/Distribution/PO_Metrics/K/")).mkdir(parents=True, exist_ok=True)
process_stable_k(DATASET, "Distribution/PO_Metrics/K", metrics=OWNERSHIP_METRICS_FIELDS, yticks=[0.1, 0.15, 0.25, 0.5, 0.75, 1, 1.5, 2.0, 2.5, 5, 6],
                 title="Ownership Metrics: Stable K's",
                 file_descriptor="Ownership_Metrics")

log('Generating Statistics took %s seconds.' % (time.time() - start_time))
log_close()
close_connection()

exit()