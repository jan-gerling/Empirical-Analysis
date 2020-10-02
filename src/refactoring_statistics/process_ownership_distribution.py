from configs import Level, LEVEL_MAP
from db.DBConnector import close_connection
from refactoring_statistics.plot_utils import box_plot_seaborn
from refactoring_statistics.query_utils import get_metrics_refactoring_level, get_metrics_stable_all
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

PROCESS_METRICS_FIELDS = ["authorOwnership",
                          "bugFixCount",
                          "refactoringsInvolved"]

OWNERSHIP_METRICS_FIELDS = ["authorOwnership",
                            "qtyMajorAuthors",
                            # "qtyMinorAuthors",
                            "qtyOfAuthors"]


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


log_init(f"results/Distribution/po_metrics_distribution_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt")
start_time = time.time()

Path(path.dirname(f"results/Distribution/PO_Metrics/")).mkdir(parents=True, exist_ok=True)
process_metrics_levels("", "Distribution/PO_Metrics", yticks=[0.1, 1, 10], metrics=OWNERSHIP_METRICS_FIELDS,
                            title="Ownership Metrics: Refactorings vs Stable Instances",
                            file_descriptor="Ownership_Metrics")

process_metrics_levels("", "Distribution/PO_Metrics", yticks=[1, 10, 50, 100], metrics=PROCESS_METRICS_FIELDS,
                           title="Process Metrics: Refactorings vs Stable Instances",
                           file_descriptor="Process_Metrics")

log('Generating Statistics took %s seconds.' % (time.time() - start_time))
log_close()
close_connection()

exit()