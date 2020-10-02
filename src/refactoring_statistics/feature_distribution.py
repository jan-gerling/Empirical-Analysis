from configs import Level, LEVEL_MAP, CACHE_DIR_PATH, LEVEL_METRIC_MAP, LEVEL_METRIC_SET_MAP, PROCESS_METRICS_FIELDS
from db.QueryBuilder import get_level_refactorings, get_level_stable
from db.DBConnector import close_connection
from refactoring_statistics.plot_utils import box_plot
from utils.log import log_init, log_close, log
import time
import datetime
import pandas as pd
import hashlib
import os.path
from pathlib import Path
from os import path
import matplotlib.pyplot as plt
import numpy as np


def refactoring_statistics(dataset, save_dir):
    statistics = pd.DataFrame(columns=['refactoring_name', 'level', 'metric', 'descriptive_statistics'])
    for level in [Level.Class, Level.Method, Level.Variable, Level.Field, Level.Other]:
        for refactoring_name in LEVEL_MAP[level]:
            # for metric in LEVEL_METRIC_MAP[level]:
            #     metric_data = retrieve_columns(get_level_refactorings(int(level), refactoring_name, dataset), [metric])
            #     new_statistics = {
            #         'refactoring_name': refactoring_name,
            #         'level': str(level),
            #         'metric': metric,
            #         'descriptive_statistics': f"{metric_data.describe()}"}
            #     statistics.append(new_statistics, ignore_index=True)
            # log(f"Collected all statistics for {refactoring_name} of the Level {str(level)}")
            for name, metrics in [("PROCESS_METRICS", PROCESS_METRICS_FIELDS)]:
                title = f"{name}_{str(level)}_{refactoring_name}"
                fig_path = f"results/{save_dir}/{title}_log_box_plot.svg"
                if not path.exists(fig_path):
                    metric_data = retrieve_columns(get_level_refactorings(int(level), refactoring_name, dataset), metrics)
                    box_plot(metric_data.to_numpy(), metrics, title, fig_path)
                else:
                    log(f"--Skipped box plot at {fig_path}, because it already exists.")
        # for name, metrics in [("PROCESS_METRICS", PROCESS_METRICS_FIELDS)]:
        #     metric_data = retrieve_columns(get_level_refactorings(int(level), "", dataset), metrics)
        #     box_plot(metric_data.to_numpy(), metrics, f"{name}_{str(level)}", "Distribution/Refactoring")
    statistics.to_csv(f"results/Distribution/Refactoring/refactoring_statistics_{dataset}.csv", index=False, header=True)


def stable_statistics(dataset, save_dir):
    statistics = pd.DataFrame(columns=['refactoring_name', 'level', 'metric', 'descriptive_statistics'])
    for level in [Level.Class, Level.Method, Level.Variable, Level.Field]:
        for k in [15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]:
            # for metric in LEVEL_METRIC_MAP[level]:
            #     metric_data = retrieve_columns(get_level_stable(int(level), k, dataset), [metric])
            #     new_statistics = {
            #         'k': k,
            #         'level': level,
            #         'metric': metric,
            #         'descriptive_statistics': f"{metric_data.describe()}"}
            #     statistics.append(new_statistics, ignore_index=True)
            # log(f"Collected all statistics for K={k} for the Level {level}")
            # for name, metrics in LEVEL_METRIC_SET_MAP[level]:
            for name, metrics in [("PROCESS_METRICS", PROCESS_METRICS_FIELDS)]:
                title = f"{name}_{str(level)}_K={k}"
                fig_path = f"results/{save_dir}/{title}_log_box_plot.svg"
                if not path.exists(fig_path):
                    metric_data = retrieve_columns(get_level_stable(int(level), k, dataset), metrics)
                    box_plot(metric_data.to_numpy(), metrics, title, fig_path)
                else:
                    log(f"--Skipped box plot at {fig_path}, because it already exists.")
    statistics.to_csv(f"results/Distribution/Stable/statistics_{dataset}.csv", index=False, header=True)


def process_metrics(dataset, save_dir):
    for k in [100, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]:
        fig_path = f"results/{save_dir}/Process_Ownership_Metrics_K={k}_log_box_plot.svg"
        if not path.exists(fig_path):
            combined_stable_metrics = get_metrics_stable_all(k, dataset, PROCESS_METRICS_FIELDS)

            # box plot
            fig, ax = plt.subplots()
            ax.set_title(f"Process- and ownership metrics for K={k}")
            ax.boxplot(combined_stable_metrics.to_numpy(), showmeans=True, meanline=True, showfliers=False, notch=True, patch_artist=True, label=f"Stable K=15")

            # plot refactorings
            for level in [Level.Class, Level.Method, Level.Variable, Level.Field]:
                refactoring_metrics_level = get_metrics_refactoring_level(level, dataset, PROCESS_METRICS_FIELDS)
                ax.boxplot(refactoring_metrics_level, showmeans=True, meanline=True, showfliers=False, notch=True, patch_artist=True, label=f"{str(level)}")

            plt.xticks(np.arange(1, len(PROCESS_METRICS_FIELDS) + 1), PROCESS_METRICS_FIELDS, rotation=30)
            plt.yscale("log")
            ax.set_yticks([0.1, 1, 10, 50, 100])
            plt.xlabel("Metrics")
            plt.legend()
            plt.savefig(fig_path)
            log(f"Saved box plot to {fig_path}")
            plt.close(fig)
        else:
            log(f"--Skipped box plot at {fig_path}, because it already exists.")


def get_metrics_refactoring_level(level, dataset, metrics):
    combined_refactoring_metrics = pd.DataFrame()
    for refactoring_name in LEVEL_MAP[level]:
        metric_data = retrieve_columns(get_level_refactorings(int(level), refactoring_name, dataset), metrics)
        combined_refactoring_metrics = combined_refactoring_metrics.append(metric_data)
    log(f"Extracted refactorings metrics of level {level}")
    return combined_refactoring_metrics


def get_metrics_stable_all(k, dataset, metrics):
    combined_stable_metrics = pd.DataFrame()
    for level in [Level.Class, Level.Method, Level.Variable, Level.Field]:
        metric_data = retrieve_columns(get_level_stable(int(level), k, dataset), PROCESS_METRICS_FIELDS)
        combined_stable_metrics = combined_stable_metrics.append(metric_data)
        log(f"Extracted metrics of level {level} for K={k}")
    return combined_stable_metrics


def retrieve_columns(sql_query, columns):
    # Hash the query
    query_hash = hashlib.sha1(sql_query.encode()).hexdigest()

    # Create the filepath
    cache_dir = os.path.join(CACHE_DIR_PATH, "_cache")
    file_path = os.path.join(cache_dir, f"{query_hash}.csv")
    return pd.read_csv(file_path, usecols=columns).apply(pd.to_numeric, downcast='float')


log_init(f"results/Distribution/feature_distribution_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt")
start_time = time.time()

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    # Path(path.dirname(f"results/Distribution/Refactoring/")).mkdir(parents=True, exist_ok=True)
    # refactoring_statistics("", "Distribution/Refactoring")
    Path(path.dirname(f"results/Distribution/Stable/")).mkdir(parents=True, exist_ok=True)
    # stable_statistics("", "Distribution/Stable")
    process_metrics("", "Distribution/Stable")


log('Generating Statistics took %s seconds.' % (time.time() - start_time))
log_close()
close_connection()

exit()