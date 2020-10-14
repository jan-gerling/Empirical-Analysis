from configs import Level, LEVEL_MAP
from db.DBConnector import close_connection
from refactoring_statistics.plot_utils import box_plot_seaborn
from refactoring_statistics.query_utils import get_metrics_refactoring_level, get_metrics_refactorings, retrieve_columns
from utils.log import log_init, log_close, log
import time
import datetime
import pandas as pd
from pathlib import Path
from os import path


REFACTORING_SAMPLES = 50000
REFACTORING_LEVELS = [Level.Class, Level.Method, Level.Variable, Level.Field, Level.Other]
IMG_FORMAT = "svg"
DATASET = ""

# metrics
CLASS_METRICS_Fields = ["classCbo",
                        # "classLcom",
                        "classLCC",
                        "classTCC",
                        "classRfc",
                        "classWmc"]

CLASS_METRICS_REDUCED_Fields = ["classCbo",
                        "classTCC",
                        "classWmc"]

CLASS_LARGE_Fields = ["classLcom", "classLoc"]

CLASS_ATTRIBUTES_QTY_Fields = ["classUniqueWordsQty", "classNumberOfMethods", "classStringLiteralsQty", "classNumberOfPublicFields", "classVariablesQty"]


# plot all refactoring for each level
def metrics_refactorings_individual_levels(dataset, save_dir, yticks, metrics, title, file_descriptor):
    # refactoring metrics per level
    for level in REFACTORING_LEVELS:
        fig_path_box = f"{save_dir}{file_descriptor}_{str(level)}_log_box_plot_{dataset}.{IMG_FORMAT}"
        if not path.exists(fig_path_box):
            refactoring_metrics_level = get_metrics_refactorings(level, dataset, LEVEL_MAP[level], metrics, REFACTORING_SAMPLES)
            refactoring_metrics_level = pd.melt(refactoring_metrics_level, id_vars="refactoring", var_name="Metric", value_vars=metrics, value_name="values")

            refactoring_metrics_level['refactoring'] = refactoring_metrics_level['refactoring'].astype('category')
            refactoring_metrics_level['Metric'] = refactoring_metrics_level['Metric'].astype('category')
            box_plot_seaborn(refactoring_metrics_level, f"{title} {str(level)}", fig_path_box, scale="log", yticks=yticks, hue="refactoring")
        else:
            log(f"--Skipped box plot at {fig_path_box}, because it already exists.")


# plot the metrics for each refactoring level
def metrics_refactoring_levels(dataset, save_dir, yticks, metrics, title, file_descriptor):
    fig_path_box = f"{save_dir}{file_descriptor}_log_box_plot_{dataset}.{IMG_FORMAT}"
    if not path.exists(fig_path_box):
        combined_refactoring_metrics = pd.DataFrame()
        # refactoring metrics per level
        for level in REFACTORING_LEVELS:
            refactoring_metrics_level = get_metrics_refactoring_level(level, dataset, LEVEL_MAP[level], metrics, samples=REFACTORING_SAMPLES)
            refactoring_metrics_level['Instances'] = f"{str(level)}"
            refactoring_metrics_level = pd.melt(refactoring_metrics_level, id_vars="Instances", var_name="Metric", value_vars=metrics, value_name="values")
            combined_refactoring_metrics = combined_refactoring_metrics.append(refactoring_metrics_level)

        combined_refactoring_metrics['Instances'] = combined_refactoring_metrics['Instances'].astype('category')
        combined_refactoring_metrics['Metric'] = combined_refactoring_metrics['Metric'].astype('category')

        box_plot_seaborn(combined_refactoring_metrics, title, fig_path_box, scale="log", yticks=yticks)
    else:
        log(f"--Skipped box plot at {fig_path_box}, because it already exists.")


log_init(f"results/Distribution/class_metrics_distribution_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt")
start_time = time.time()

# class metrics individual refactorings
Path(path.dirname("results/Distribution/Class_Metrics/Refactorings/")).mkdir(parents=True, exist_ok=True)
metrics_refactorings_individual_levels(DATASET, "results/Distribution/Class_Metrics/Refactorings/", yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 50, 75, 100, 125, 150, 200], metrics=CLASS_ATTRIBUTES_QTY_Fields,
                                       title="Class Attributes: Refactorings",
                                       file_descriptor="Class_Attributes")

metrics_refactorings_individual_levels(DATASET, "results/Distribution/Class_Metrics/Refactorings/", yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 50, 100, 150, 250, 350, 500, 750, 1000], metrics=CLASS_METRICS_Fields,
                                       title="Class Metrics: Refactorings",
                                       file_descriptor="Class_Metrics")

metrics_refactorings_individual_levels(DATASET, "results/Distribution/Class_Metrics/Refactorings/", yticks=[10, 15, 20, 25, 50, 75, 90, 100, 125, 150, 200, 250, 350, 500, 650, 750, 1000, 1500], metrics=CLASS_LARGE_Fields,
                                       title="Class Metrics Large: Refactorings",
                                       file_descriptor="Class_Metrics_Large")

# class metrics refactoring levels
Path(path.dirname("results/Distribution/Class_Metrics/Refactoring/")).mkdir(parents=True, exist_ok=True)
metrics_refactoring_levels(DATASET, "results/Distribution/Class_Metrics/Refactoring/", yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 35, 50, 75, 100, 125, 150, 200], metrics=CLASS_ATTRIBUTES_QTY_Fields,
                           title="Class Attributes: Refactoring Levels",
                           file_descriptor="Class_Attributes_Refactoring")

metrics_refactoring_levels(DATASET, "results/Distribution/Class_Metrics/Refactoring/", yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 50, 100, 150, 250, 350, 500, 750, 1000], metrics=CLASS_METRICS_Fields,
                           title="Class Metrics: Refactoring Levels",
                           file_descriptor="Class_Metrics_Refactoring")

metrics_refactoring_levels(DATASET, "results/Distribution/Class_Metrics/Refactoring/", yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 50, 75, 90, 100, 125, 150, 200, 250, 350, 500, 650, 750], metrics=CLASS_LARGE_Fields,
                                       title="Class Metrics Large: Levels",
                                       file_descriptor="Class_Metrics_Large_Refactoring")

log('Generating Statistics took %s seconds.' % (time.time() - start_time))
log_close()
close_connection()

exit()