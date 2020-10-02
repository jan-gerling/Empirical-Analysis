from configs import Level, LEVEL_MAP
from db.DBConnector import close_connection
from refactoring_statistics.plot_utils import box_plot_seaborn
from refactoring_statistics.query_utils import get_metrics_refactoring_level, get_metrics_stable_level
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
                        "classLcom",
                        "classLCC",
                        "classTCC",
                        "classRfc",
                        "classWmc"]

# Found by mauricio:
# also relevant attributes for class level refactorings are "classLoc", "classUniqueWordsQty"
# also relevant attributes for method level refactorings are "classNumberOfMethods", number of unique words in a class, classLOC
# also relevant attributes for variable level refactorings arenumber of string literals in a class, number of variables in the method, "number of public fields in a class", number of variables in a class
CLASS_ATTRIBUTES_QTY_Fields = ["classLoc", "classUniqueWordsQty", "classNumberOfMethods", "classStringLiteralsQty", "classNumberOfPublicFields", "classVariablesQty"]


def class_metrics_levels_refactoring(dataset, save_dir, yticks, metrics, title, file_descriptor):
    fig_path_box = f"results/{save_dir}/{file_descriptor}_log_box_plot_{dataset}.{IMG_FORMAT}"
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


def class_metrics_levels_stable(dataset, save_dir, yticks, metrics, title, file_descriptor):
    for k in STABLE_Ks:
        fig_path_box = f"results/{save_dir}/{file_descriptor}_K{k}_log_box_plot_{dataset}.{IMG_FORMAT}"
        if not path.exists(fig_path_box):
            combined_stable_metrics = pd.DataFrame()
            for level in STABLE_LEVELS:
                stable_metrics = get_metrics_stable_level(level, k, dataset, metrics, samples=STABLE_SAMPLES)
                stable_metrics['Instances'] = f"Stable {str(level)}"
                stable_metrics = pd.melt(stable_metrics, id_vars="Instances", var_name="Metric", value_vars=metrics, value_name="values")
                combined_stable_metrics = combined_stable_metrics.append(stable_metrics)

            combined_stable_metrics['Instances'] = combined_stable_metrics['Instances'].astype('category')
            combined_stable_metrics['Metric'] = combined_stable_metrics['Metric'].astype('category')

            box_plot_seaborn(combined_stable_metrics, title, fig_path_box, scale="log", yticks=yticks)
    else:
        log(f"--Skipped box plot at {fig_path_box}, because it already exists.")


log_init(f"results/Distribution/class_metrics_distribution_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt")
start_time = time.time()

Path(path.dirname(f"results/Distribution/Class_Metrics/")).mkdir(parents=True, exist_ok=True)

y_ticks = [0.1, 1, 10, 50, 100]
class_metrics_levels_refactoring("", "Distribution/Class_Metrics", yticks=y_ticks, metrics=CLASS_ATTRIBUTES_QTY_Fields,
                                 title="Class Attributes: Refactoring Levels",
                                 file_descriptor="Refactoring_ClassAttributes")

class_metrics_levels_refactoring("", "Distribution/Class_Metrics", yticks=y_ticks, metrics=CLASS_METRICS_Fields,
                                 title="Class Metrics: Refactoring Levels",
                                 file_descriptor="Refactoring_ClassMetrics")

class_metrics_levels_stable("", "Distribution/Class_Metrics", yticks=y_ticks, metrics=CLASS_ATTRIBUTES_QTY_Fields,
                            title="Class Attributes: Stable Instances Levels",
                            file_descriptor="Stable_ClassAttributes")

class_metrics_levels_stable("", "Distribution/Class_Metrics", yticks=y_ticks, metrics=CLASS_METRICS_Fields,
                            title="Class Metrics: Stable Instances Levels",
                            file_descriptor="Stable_ClassMetrics")

log('Generating Statistics took %s seconds.' % (time.time() - start_time))
log_close()
close_connection()

exit()