from configs import Level, LEVEL_MAP, PROCESS_METRICS_FIELDS
from db.QueryBuilder import get_level_refactorings, get_level_stable
from refactoring_statistics.plot_utils import  box_plot_seaborn_simple
from refactoring_statistics.query_utils import retrieve_columns, get_last_refactored_instance_all
from utils.log import log_init, log_close, log
import time
import datetime
import pandas as pd
from pathlib import Path
from os import path
from scipy import stats


# metrics
CLASS_METRICS_Fields = ["classCbo",
                        "classLcom",
                        "classLCC",
                        "classTCC",
                        "classRfc",
                        "classWmc"]

CLASS_ATTRIBUTES_QTY_Fields = ["classUniqueWordsQty", "classNumberOfMethods", "classStringLiteralsQty",
                               "classNumberOfPublicFields", "classVariablesQty", "classLoc"]
METRIC_SETS = {"CLASS_METRICS_Fields": CLASS_METRICS_Fields, "CLASS_ATTRIBUTES_QTY_Fields": CLASS_ATTRIBUTES_QTY_Fields, "PO_METRIC_SETS": PROCESS_METRICS_FIELDS}.items()


REFACTORING_SAMPLES = 100000
STABLE_Ks = [15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]
STABLE_SAMPLES = 50000
REFACTORING_LEVELS = [Level.Class, Level.Method, Level.Variable, Level.Field, Level.Other]
STABLE_LEVELS = [Level.Class, Level.Method, Level.Variable, Level.Field]


def compute_statistics(metric_data, level, metric, extra_field=""):
    stat, p = stats.shapiro(metric_data)
    alpha = 0.05
    is_non_normal = p < alpha
    skew = stats.skew(metric_data.to_numpy())[0]
    extra_field_name = 'refactoring_name'
    if len(extra_field) <= 3:
        extra_field_name = 'k'
    return {
        f"{extra_field_name}": extra_field,
        'level': str(level),
        'metric': metric,
        'skew': skew,
        'mean': metric_data.mean().iloc[0],
        'std': metric_data.std().iloc[0],
        'min': metric_data.min().iloc[0],
        '5%': metric_data.quantile(.05).iloc[0],
        '25%': metric_data.quantile(.25).iloc[0],
        '50%': metric_data.quantile(.50).iloc[0],
        '75%': metric_data.quantile(.75).iloc[0],
        '95%': metric_data.quantile(.95).iloc[0],
        'max': metric_data.max().iloc[0],
        'Shapiro-Wilk-test': f"Statistics={stat}, p={p}",
        'non-normal_distribution': is_non_normal
    }


def refactoring_statistics(dataset, save_dir, levels, metrics, file_descriptor, refactorings=False):
    statistics = pd.DataFrame(
        columns=['refactoring_name', 'level', 'metric', 'descriptive_statistics', 'skew', 'Shapiro-Wilk-test',
                 'non-normal_distribution'])

    for level in levels:
        statistics_path = f"{save_dir}{file_descriptor}{str(level)}_{dataset}.csv"
        if not path.exists(statistics_path):
            for metric in metrics:
                if refactorings:
                    for refactoring_name in LEVEL_MAP[level]:
                        metric_data = retrieve_columns(get_level_refactorings(int(level), refactoring_name, dataset), [metric], samples=REFACTORING_SAMPLES)
                        statistics = statistics.append(compute_statistics(metric_data, level, metric, extra_field=refactoring_name), ignore_index=True)
                else:
                    for k in STABLE_Ks:
                        metric_data = retrieve_columns(get_level_stable(int(level), k, dataset), metrics, STABLE_SAMPLES)
                        statistics = statistics.append(compute_statistics(metric_data, level, metric, extra_field=f"{k}"), ignore_index=True)
            statistics.to_csv(statistics_path, index=False, header=True)
            log(f"Collected all statistics for {str(level)} and stored them at: {statistics_path}.")
        else:
            statistics = statistics.append(pd.read_csv(statistics_path), ignore_index=True)

    grouped = statistics.groupby(["metric", "level"], as_index=False).mean()
    excel_path = f"{save_dir}{file_descriptor}_{dataset}.xlsx"
    grouped.to_excel(excel_path, index=False)
    return statistics


SAVE_DIR = f"results/Distribution/Statistics/"
log_init(f"{SAVE_DIR}feature_statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt")
start_time = time.time()

Path(path.dirname(SAVE_DIR)).mkdir(parents=True, exist_ok=True)
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    # for metric_description, metrics in METRIC_SETS:
    #     statistics = pd.DataFrame()
    #     metrics_data = pd.DataFrame()
    #     for metric in metrics:
    #         metrics = get_last_refactored_instance_all([metric], REFACTORING_SAMPLES * 5)
    #         statistics_metric = compute_statistics(metrics, Level.NONE, metric, extra_field="all")
    #         statistics = statistics.append(statistics_metric, ignore_index=True)
    #         metrics_data = metrics_data.append(metrics)
    #         log(f"Extract {metric}")
    #
    #     if metric_description == "CLASS_METRICS_Fields":
    #         yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 35, 50, 100, 150, 250, 500, 650, 1000]
    #     elif metric_description == "CLASS_ATTRIBUTES_QTY_Fields":
    #         yticks=[0.5, 0.75, 1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 35, 50, 75, 100, 150, 200]
    #     else:
    #         yticks=[0.1, 0.15, 0.25, 0.5, 0.75, 1, 1.5, 2.0, 2.5, 3.5, 5, 6, 7.5, 9, 10, 15, 20]
    #
    #     fig_path = f"{SAVE_DIR}last_refactored_class_{metric_description}_plot.svg"
    #     box_plot_seaborn_simple(metrics_data, f"{metric_description}", fig_path, "log", yticks=yticks)
    #
    #     grouped = statistics.groupby(["metric", "level"], as_index=False).mean()
    #     excel_path = f"{SAVE_DIR}last_refactored_class_{metric_description}.xlsx"
    #     grouped.to_excel(excel_path, index=False)
    #     log(f"Stored statistics for {metric_description}")

    for refactorings in [True, False]:
        for metric_description, metrics in METRIC_SETS:
            log(f"{refactorings} {metric_description}")
            if refactorings:
                refactoring_statistics("", SAVE_DIR, REFACTORING_LEVELS, metrics, f"refactoring_{metric_description}", refactorings)
            else:
                refactoring_statistics("", SAVE_DIR, STABLE_LEVELS, metrics, f"stable_{metric_description}", refactorings)

log('Generating Statistics took %s seconds.' % (time.time() - start_time))
log_close()

exit()