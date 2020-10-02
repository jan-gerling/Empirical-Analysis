from db.DBConnector import execute_query
from utils.log import log_init, log_close, log
import time
from os import path
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# the ids are not included as they are the same for every table: id : long
classMetricsEntities = ["classAnonymousClassesQty",
                        "classAssignmentsQty",
                        "classComparisonsQty",
                        "classLambdasQty",
                        "classLoopQty",
                        "classMathOperationsQty",
                        "classMaxNestedBlocks",
                        "classNosi",
                        "classNumberOfAbstractMethods",
                        "classNumberOfDefaultFields",
                        "classNumberOfDefaultMethods",
                        "classNumberOfFields",
                        "classNumberOfFinalFields",
                        "classNumberOfFinalMethods",
                        "classNumberOfMethods",
                        "classNumberOfPrivateFields",
                        "classNumberOfPrivateMethods",
                        "classNumberOfProtectedFields",
                        "classNumberOfProtectedMethods",
                        "classNumberOfPublicMethods",
                        "classNumberOfStaticFields",
                        "classNumberOfStaticMethods",
                        "classNumberOfSynchronizedMethods",
                        "classNumbersQty",
                        "classParenthesizedExpsQty",
                        "classReturnQty",
                        "classStringLiteralsQty",
                        "classSubClassesQty",
                        "classTryCatchQty",
                        "classVariablesQty"]
classMetricsComplex = ["classCbo",
                       "classLcom",
                       "classLoc",
                       "classRfc",
                       "classWmc",
                       "classTCC",
                       "classLCC"]
processMetricsFields = ["bugFixCount",
                        "qtyMajorAuthors",
                        "qtyMinorAuthors",
                        "qtyOfAuthors",
                        "qtyOfCommits"]
methodMetricsSize = ["methodLoc",
                     "methodUniqueWordsQty"]
methodMetrics = ["methodAnonymousClassesQty",
                       "methodAssignmentsQty",
                       "methodCbo",
                       "methodComparisonsQty",
                       "methodLambdasQty",
                       "methodLoopQty",
                       "methodMathOperationsQty",
                       "methodMaxNestedBlocks",
                       "methodNumbersQty",
                       "methodParametersQty",
                       "methodParenthesizedExpsQty",
                       "methodReturnQty",
                       "methodRfc",
                       "methodStringLiteralsQty",
                       "methodSubClassesQty",
                       "methodTryCatchQty",
                       "methodVariablesQty",
                       "methodWmc"]


def plot_bar(data, x_labels, group_labels, scale: str = "linear", title: str = ""):
    fig, ax = plt.subplots(figsize=(max(len(x_labels), 6), 12), dpi=120)
    barWidth = 1 / (len(group_labels) + 1)
    x = np.arange(len(x_labels))
    for index, row in data.iterrows():
        ax.bar(x + index * barWidth, row, width=barWidth, edgecolor='white', label=group_labels[index])

    plt.xticks(x, x_labels, rotation='30')
    ax.set_ylabel('AVG')
    ax.set_title(title)
    plt.yscale(scale)
    ax.legend()
    fig_path = f"results/Metrics/{title}_{scale}_mean.png"
    plt.savefig(fig_path)


def plot_box(data, label, title, scale: str = "log"):
    fig, ax = plt.subplots(figsize=(max(len(label), 32), 12), dpi=120)
    ax.set_title(f"{title}")
    ax.boxplot(data, showfliers=False)
    plt.xticks(np.arange(1, len(label) + 1), label, rotation=30)
    plt.yscale(scale)
    plt.xlabel("Metrics")
    fig_path = f"results/Metrics/{title}_{scale}_box_plot.png"
    plt.savefig(fig_path)
    log(f"Saved box plot to {fig_path}")


def query_avg(table_name: str, function: str, metrics, descriptor: str, group: bool):
    file_path = f"results/Metrics/{table_name}_{function}_{descriptor}.csv"
    Path(path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
    if not path.exists(file_path):
        metrics_query = ', '.join([f"{function}({metric}) AS \"{metric}\"" for metric in metrics])
        if group:
            query = f"SELECT {metrics_query} FROM {table_name} group by level"
        else:
            query = f"SELECT {metrics_query} FROM {table_name}"
        dataframe = execute_query(query)
        dataframe.to_csv(file_path, index=False)
        log(f"Got the data from {table_name} for these metrics: {metrics} for the aggregate function: {function}.")
    else:
        dataframe = pd.read_csv(file_path)
    return dataframe


def query_raw(table_name: str,  metrics, descriptor: str):
    file_path = f"results/Metrics/{table_name}_{descriptor}_raw.csv"
    Path(path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
    if not path.exists(file_path):
        metrics_query = ', '.join([f"{metric}" for metric in metrics])
        query = f"SELECT {metrics_query} FROM {table_name}"
        dataframe = execute_query(query)
        dataframe.to_csv(file_path, index=False)
        log(f"Got the raw data from {table_name} for these metrics: {metrics}.")
    else:
        dataframe = pd.read_csv(file_path)
    return dataframe


log_init(f"")
log('Begin Statistics')
start_time = time.time()

Path(path.dirname("results/Metrics/")).mkdir(parents=True, exist_ok=True)

group_labels = ["Stable", "Class", "Method", "Variable", "Field", "Other"]
# class entities
avg_stable_class = query_avg("unique_class_metrics_stable", "AVG", classMetricsEntities, "class_entities", False)
avg_refactorings_class = query_avg("Unique_Metrics_Refactorings", "AVG", classMetricsEntities, "class_entities", True)
avg_combined_class = pd.concat([avg_stable_class, avg_refactorings_class], ignore_index=True)
plot_bar(avg_combined_class, avg_combined_class.columns.values, group_labels, "linear", "class_entities_count_comparison")

# class metrics
avg_stable_class = query_avg("unique_class_metrics_stable", "AVG", classMetricsComplex, "class_metrics", False)
avg_refactorings_class = query_avg("Unique_Metrics_Refactorings", "AVG", classMetricsComplex, "class_metrics", True)
avg_combined_class = pd.concat([avg_stable_class, avg_refactorings_class], ignore_index=True)
plot_bar(avg_combined_class, avg_combined_class.columns.values, group_labels, "log", "class_metrics_comparison")

# process
avg_stable_process = query_avg("unique_class_metrics_stable", "AVG", processMetricsFields, "process", False)
avg_refactoring_process = query_avg("Unique_Metrics_Refactorings", "AVG", processMetricsFields, "process", True)
avg_combined_process = pd.concat([avg_stable_process, avg_refactoring_process], ignore_index=True)
plot_bar(avg_combined_process, avg_combined_process.columns.values, group_labels, "log", "process_metrics_comparison")

# methods size
avg_refactoring_process = query_avg("UniqueMethodMetrics_Refactoring", "AVG", methodMetricsSize, "method_size_metrics", True)
avg_stable_process = query_avg("unique_method_metrics_stable", "AVG", methodMetricsSize, "method_size_metrics", False)
avg_combined_process = pd.concat([avg_stable_process, avg_refactoring_process], ignore_index=True)
plot_bar(avg_combined_process, avg_combined_process.columns.values, ["Stable", "Method", "Variable"], "linear", "method_metrics_size_comparison")

# methods size
avg_refactoring_process = query_avg("UniqueMethodMetrics_Refactoring", "AVG", methodMetrics, "method", True)
avg_stable_process = query_avg("unique_method_metrics_stable", "AVG", methodMetrics, "method", False)
avg_combined_process = pd.concat([avg_stable_process, avg_refactoring_process], ignore_index=True)
plot_bar(avg_combined_process, avg_combined_process.columns.values, ["Stable", "Method", "Variable"], "linear", "method_metrics_comparison")

# raw process
raw_stable_process = query_raw("unique_class_metrics_stable", processMetricsFields, "process")
raw_stable_process_reduced = raw_stable_process.sample(frac=0.001, random_state=42)
plot_box(raw_stable_process_reduced.to_numpy(), processMetricsFields, "Stable process metrics")


log(f"Processing statistics took {time.time() - start_time:.2f} seconds.")
log_close()

exit(0)