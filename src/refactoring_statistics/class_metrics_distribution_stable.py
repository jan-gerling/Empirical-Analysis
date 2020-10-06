from configs import Level
from db.DBConnector import close_connection
from refactoring_statistics.plot_utils import box_plot_seaborn, line_plot_seaborn
from refactoring_statistics.query_utils import get_metrics_stable_level_unqique_metrics
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

# Found by mauricio:
# also relevant attributes for class level refactorings are "classLoc", "classUniqueWordsQty"
# also relevant attributes for method level refactorings are "classNumberOfMethods", number of unique words in a class, classLOC
# also relevant attributes for variable level refactorings arenumber of string literals in a class, number of variables in the method, "number of public fields in a class", number of variables in a class
CLASS_ATTRIBUTES_QTY_Fields = ["classUniqueWordsQty", "classNumberOfMethods", "classStringLiteralsQty", "classNumberOfPublicFields", "classVariablesQty"]


def metrics_stable_levels(save_dir, yticks, metrics, title, file_descriptor):
    fig_path_box = f"results/{save_dir}/{file_descriptor}_log_box_plot.{IMG_FORMAT}"
    for k in STABLE_Ks:
        fig_path_box = f"results/{save_dir}/{file_descriptor}_K{k}_log_box_plot.{IMG_FORMAT}"
        if not path.exists(fig_path_box):
            combined_stable_metrics = pd.DataFrame()
            for level in STABLE_LEVELS:
                stable_metrics = get_metrics_stable_level_unqique_metrics(level, k, metrics, samples=STABLE_SAMPLES)
                stable_metrics['Instances'] = f"Stable {str(level)}"
                stable_metrics = pd.melt(stable_metrics, id_vars="Instances", var_name="Metric", value_vars=metrics, value_name="values")
                combined_stable_metrics = combined_stable_metrics.append(stable_metrics)

            combined_stable_metrics['Instances'] = combined_stable_metrics['Instances'].astype('category')
            combined_stable_metrics['Metric'] = combined_stable_metrics['Metric'].astype('category')
            # plot
            box_plot_seaborn(combined_stable_metrics, title, fig_path_box, scale="log", yticks=yticks)
    else:
        log(f"--Skipped box plot at {fig_path_box}, because it already exists.")


def level_stable_k(level, save_dir, metrics, yticks, title, file_descriptor):
    # stable metrics for all level and k
    fig_path_box = f"results/{save_dir}/{file_descriptor}_line_plot.{IMG_FORMAT}"
    if not path.exists(fig_path_box):
        combined_stable_metrics = pd.DataFrame()
        for k in STABLE_Ks:
            stable_metrics = get_metrics_stable_level_unqique_metrics(level, k, metrics, samples=STABLE_SAMPLES)
            stable_metrics['K'] = k
            stable_metrics = pd.melt(stable_metrics, id_vars="K", var_name="Metric", value_vars=metrics, value_name="values")
            combined_stable_metrics = combined_stable_metrics.append(stable_metrics)
        # plot
        line_plot_seaborn(combined_stable_metrics, title, fig_path_box, xticks=STABLE_Ks, yticks=yticks, scale="log")

    else:
        log(f"--Skipped plot at {fig_path_box}, because it already exists.")


def level_merged_stable_k(save_dir, metrics, yticks, title, file_descriptor):
    # stable metrics for all level and k
    fig_path_box = f"results/{save_dir}/{file_descriptor}_line_plot.{IMG_FORMAT}"
    if not path.exists(fig_path_box):
        combined_stable_metrics = pd.DataFrame()
        for level in STABLE_LEVELS:
            for k in STABLE_Ks:
                stable_metrics = get_metrics_stable_level_unqique_metrics(level, k, metrics, samples=STABLE_SAMPLES)
                stable_metrics['K'] = k
                stable_metrics = pd.melt(stable_metrics, id_vars="K", var_name="Metric", value_vars=metrics, value_name="values")
                stable_metrics["Metric"] = stable_metrics["Metric"].apply(lambda x: f"{x} {str(level)}")
                combined_stable_metrics = combined_stable_metrics.append(stable_metrics)
        # plot
        line_plot_seaborn(combined_stable_metrics, title, fig_path_box, xticks=STABLE_Ks, yticks=yticks, scale="log")
    else:
        log(f"--Skipped plot at {fig_path_box}, because it already exists.")


log_init(f"results/Distribution/class_metrics_distribution_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt")
start_time = time.time()

level_merged_stable_k("Distribution/Class_Metrics/K", metrics=CLASS_METRICS_REDUCED_Fields, yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 50, 75, 90, 100, 125, 150, 200, 250, 300, 350],
                      title=f"Class Metrics: Stable K's",
                      file_descriptor=f"Class_Metrics_Reduced_K")

# class metrics stable for k's (line plot)
for level in STABLE_LEVELS:
    Path(path.dirname("results/Distribution/Class_Metrics/K/")).mkdir(parents=True, exist_ok=True)
    level_stable_k(level, "Distribution/Class_Metrics/K", metrics=CLASS_ATTRIBUTES_QTY_Fields, yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 50, 75, 90, 100, 125, 150, 200, 250, 300, 350],
                   title=f"Class Attributes: Stable K's at {str(level)}",
                   file_descriptor=f"Class_Attributes_K_{int(level)}")

    level_stable_k(level, "Distribution/Class_Metrics/K", metrics=CLASS_METRICS_Fields, yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 50, 75, 90, 100, 125, 150, 200, 250, 300, 350, 400, 500],
                   title=f"Class Metrics: Stable K's at {str(level)}",
                   file_descriptor=f"Class_Metrics_K_{int(level)}")

    level_stable_k(level, "Distribution/Class_Metrics/K", yticks=[50, 75, 90, 100, 125, 150, 200, 250, 350, 500, 650, 750, 1000, 1500, 2500, 5000, 7500, 10000], metrics=CLASS_LARGE_Fields,
                   title=f"Class Metrics Large: Stable K's at {str(level)}",
                   file_descriptor=f"Class_Metrics_Large_K_{int(level)}")

# class metrics stable levels
Path(path.dirname("results/Distribution/Class_Metrics/Stable/")).mkdir(parents=True, exist_ok=True)
metrics_stable_levels("Distribution/Class_Metrics/Stable", yticks=[10, 15, 20, 25, 50, 75, 90, 100, 125, 150, 200, 250, 350, 500, 650, 750, 1000, 1500], metrics=CLASS_ATTRIBUTES_QTY_Fields,
                      title="Class Attributes: Stable Instances Levels",
                      file_descriptor="Class_Attributes_Stable")

metrics_stable_levels("Distribution/Class_Metrics/Stable", yticks=[10, 15, 20, 25, 50, 75, 90, 100, 125, 150, 200, 250, 350, 500, 650, 750, 1000, 1500], metrics=CLASS_METRICS_Fields,
                      title="Class Metrics: Stable Instances Levels",
                      file_descriptor="Class_Metrics_Stable")

metrics_stable_levels("Distribution/Class_Metrics/Stable", yticks=[10, 15, 20, 25, 50, 75, 90, 100, 125, 150, 200, 250, 350, 500, 650, 750, 1000, 1500], metrics=CLASS_LARGE_Fields,
                      title="Class Metrics Large: Stable Instances Levels",
                      file_descriptor="Class_Metrics_Large_Stable")

log('Generating Statistics took %s seconds.' % (time.time() - start_time))
log_close()
close_connection()

exit()