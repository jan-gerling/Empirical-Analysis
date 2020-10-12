import math

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import DBSCAN, KMeans
from configs import Level, LEVEL_MAP
from db.QueryBuilder import get_level_refactorings
from refactoring_statistics.query_utils import retrieve_columns
import pandas as pd
from pathlib import Path
from os import path
import numpy as np


REFACTORING_SAMPLES = 50000
STABLE_SAMPLES = 50000
REFACTORING_LEVELS = [Level.Class, Level.Method, Level.Variable, Level.Field, Level.Other]
STABLE_LEVELS = [Level.Class, Level.Method, Level.Variable, Level.Field]
STABLE_Ks = [15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]
IMG_FORMAT = "svg"
DATASET = ""

CLASS_METRICS_Fields = ["classCbo",
                        "classLcom",
                        "classLCC",
                        "classTCC",
                        "classRfc",
                        "classWmc"]

CLASS_ATTRIBUTES_QTY_Fields = ["classLoc", "classUniqueWordsQty", "classNumberOfMethods", "classStringLiteralsQty",
                               "classNumberOfPublicFields", "classVariablesQty"]

PROCESS_METRICS_FIELDS = ["qtyOfCommits",
                          "bugFixCount",
                          "refactoringsInvolved"]

OWNERSHIP_METRICS_FIELDS = ["authorOwnership",
                            "qtyMajorAuthors",
                            "qtyMinorAuthors",
                            "qtyOfAuthors"]


# plot all refactoring for each level
def retrieve_aggr_refactorings(dataset, metrics, metrics_description: str, aggregate_function: str = "median"):
    Path(path.dirname(SAVE_DIR_METRICS)).mkdir(parents=True, exist_ok=True)
    data_path = f"{SAVE_DIR_METRICS}refactoring_{metrics_description}_{aggregate_function}.csv"
    if not path.exists(data_path):
        # refactoring metrics per level
        combined_refactoring_metrics_agg = pd.DataFrame(columns=["refactoring", "level"] + metrics)
        for level in REFACTORING_LEVELS:
            for refactoring_name in LEVEL_MAP[level]:
                refactoring_metrics = retrieve_columns(get_level_refactorings(int(level), refactoring_name, dataset),
                                                       metrics, REFACTORING_SAMPLES)
                refactoring_metrics_agg = pd.DataFrame(columns=["refactoring", "level"] + metrics)
                meta_data = [refactoring_name, int(level)]
                if aggregate_function == "mean":
                    refactoring_metrics_agg.loc[0] = meta_data + refactoring_metrics[metrics].mean(axis=0).tolist()
                elif aggregate_function == "median":
                    refactoring_metrics_agg.loc[0] = meta_data + refactoring_metrics[metrics].median(axis=0).tolist()
                else:
                    raise ValueError(f"{aggregate_function} is not supported.")
                combined_refactoring_metrics_agg = combined_refactoring_metrics_agg.append(refactoring_metrics_agg)
        combined_refactoring_metrics_agg.to_csv(data_path)
        print(
            f"Finished computation of the {aggregate_function} of the {metrics_description} metrics for all refactoring levels and stored it at {data_path}.")
        return combined_refactoring_metrics_agg
    else:
        return pd.read_csv(data_path)


def dbscan_cluster(data, eps):
    return DBSCAN(eps=eps, min_samples=5).fit(data)


def kmeans_cluster(data, k):
    return KMeans(n_clusters=k).fit(data)


def cluster(data, metrics, metrics_description: str, aggregate_function: str = "median", clustering: str = "DBScan",
            clustering_description: str = "DBScan",
            eps: int = 18, k: int = 3):
    Path(path.dirname(f"{SAVE_DIR_RESULTS}Results/")).mkdir(parents=True, exist_ok=True)
    result_path = f"{SAVE_DIR_RESULTS}Results/refactoring_{metrics_description}_{aggregate_function}_{clustering}_{clustering_description}.csv"
    if not path.exists(result_path):
        if clustering == "DBScan":
            model = dbscan_cluster(data[metrics].to_numpy(), eps=eps)
        elif clustering == "KMeans":
            model = kmeans_cluster(data[metrics].to_numpy(), k=k)
        else:
            raise ValueError(f"{clustering} is not supported.")

        data = {"refactoring": data["refactoring"].to_list(),
                "level": data["level"].to_list(),
                "cluster": list(model.labels_)}
        results = pd.DataFrame(data=data)
        results.to_csv(result_path)
        print(
            f"Finished clustering with {clustering} of the refactoring with the {aggregate_function} of the {metrics_description} metrics types of all levels "
            f"and stored the results at {result_path}.")
        return results
    else:
        return pd.read_csv(result_path)


def compute_similarity_matrix(data):
    # data preparation
    refactorings = data["refactoring"]
    data = data.drop(["level", "refactoring"], 1).replace(-1, np.nan)

    n = len(data.index)
    similarity_matrix=np.zeros(shape=(n, n), dtype=float)

    for column in data.columns:
        for x in range(0, n, 1):
            current_cluster = data[column][x]
            for y in range(0, n, 1):
                # in case x and y are nan, nothing is counted, also on the diagonal
                if x == y:
                    similarity_matrix[x, y] += 1
                else:
                    similarity_matrix[x, y] += math.isclose(data[column][y], current_cluster, rel_tol=1e-5)

    similarity_matrix *= 1.0/float(len(data.columns))
    return pd.DataFrame(data=similarity_matrix, index=refactorings, columns=refactorings)


SAVE_DIR_METRICS = "results/Distribution/Cluster/Metrics/"
SAVE_DIR_RESULTS = "results/Distribution/Cluster/"

CLASS_METRIC_SETS = {"CLASS_METRICS": CLASS_METRICS_Fields,
                     "CLASS_ATTRIBUTES": CLASS_ATTRIBUTES_QTY_Fields,
                     "CLASS_All": CLASS_METRICS_Fields + CLASS_ATTRIBUTES_QTY_Fields}.items()

PO_METRIC_SETS = {"PROCESS_METRICS": PROCESS_METRICS_FIELDS,
                  "OWNERSHIP_METRICS": OWNERSHIP_METRICS_FIELDS,
                  "PO_Metrics": PROCESS_METRICS_FIELDS + OWNERSHIP_METRICS_FIELDS}.items()

METRIC_SETS = {"CLASS_METRIC_SETS": CLASS_METRIC_SETS, "PO_METRIC_SETS": PO_METRIC_SETS}.items()


def heatmap(similarity_matrix, figpath):
    plt.figure(figsize=(16, 16))
    sns.heatmap(similarity_matrix, cmap="rocket_r", cbar_kws={'orientation': 'horizontal', "shrink": 0.85})
    plt.savefig(figpath)
    plt.close()


with pd.option_context('display.max_rows', 2, 'display.max_columns', 2):
    for metric_set_description, metric_set in METRIC_SETS:
        print(f"\nDBScan Clustering: {metric_set_description}")
        for eps in [0.1, 0.2, 0.25, 0.3, 0.5, 0.75, 1, 2, 3, 5, 6, 8, 10, 12.5, 15, 18, 23, 28, 33, 38, 43, 50]:
            combined_results = pd.DataFrame()
            for aggregate_function in ["median", "mean"]:
                for metrics_description, metrics in metric_set:
                    current_metrics = retrieve_aggr_refactorings(DATASET, metrics=metrics,
                                                                 metrics_description=metrics_description,
                                                                 aggregate_function=aggregate_function)
                    dbscan_results_mean = cluster(data=current_metrics, metrics=metrics,
                                                  metrics_description=metrics_description,
                                                  aggregate_function=aggregate_function, clustering="DBScan",
                                                  clustering_description=f"eps={eps}", eps=eps)
                    combined_results["refactoring"] = dbscan_results_mean["refactoring"]
                    combined_results["level"] = dbscan_results_mean["level"]
                    combined_results[f"{aggregate_function} {metrics_description}"] = dbscan_results_mean["cluster"]
            print(f"--eps={eps}")
            combined_results.to_csv(f"{SAVE_DIR_RESULTS}DBScan_{metric_set_description}_eps={eps}.csv")
            similarity_matrix = compute_similarity_matrix(combined_results)
            similarity_matrix.to_csv(f"{SAVE_DIR_RESULTS}DBScan_{metric_set_description}_eps={eps}_similarity.csv")
            figpath = f"{SAVE_DIR_RESULTS}DBScan_{metric_set_description}_eps={eps}_similarity_heatmap.{IMG_FORMAT}"
            heatmap(similarity_matrix, figpath)

        print(f"\nKMeans Clustering: {metric_set_description}")
        for k in [3, 4, 5, 7]:
            combined_results = pd.DataFrame()
            for aggregate_function in ["median", "mean"]:
                for metrics_description, metrics in metric_set:
                    current_metrics = retrieve_aggr_refactorings(DATASET, metrics=metrics,
                                                                 metrics_description=metrics_description,
                                                                 aggregate_function=aggregate_function)
                    kmeans_results_mean = cluster(data=current_metrics, metrics=metrics,
                                                  metrics_description=metrics_description,
                                                  aggregate_function=aggregate_function, clustering="KMeans",
                                                  clustering_description=f"k={k}", k=k)
                    combined_results["refactoring"] = kmeans_results_mean["refactoring"]
                    combined_results["level"] = kmeans_results_mean["level"]
                    combined_results[f"{aggregate_function} {metrics_description}"] = kmeans_results_mean["cluster"]
            print(f"--k={k}")
            combined_results.to_csv(f"{SAVE_DIR_RESULTS}KMeans_{metric_set_description}_k={k}.csv")
            similarity_matrix = compute_similarity_matrix(combined_results)
            similarity_matrix.to_csv(f"{SAVE_DIR_RESULTS}KMeans_{metric_set_description}_k={k}_similarity.csv")
            figpath = f"{SAVE_DIR_RESULTS}KMeans_{metric_set_description}_k={k}_similarity_heatmap.{IMG_FORMAT}"
            heatmap(similarity_matrix, figpath)
exit()