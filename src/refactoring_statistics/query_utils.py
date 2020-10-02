from enum import Enum

from configs import CACHE_DIR_PATH
from db.DBConnector import execute_query
from db.QueryBuilder import get_level_stable, get_level_refactorings
from utils.log import log
from os import path
import pandas as pd
from pathlib import Path
import hashlib


class Statistics(Enum):
    """
    1. "likelihood": total sum of windows in which a refactoring type occurs
            and divide it by the total window count in which the current refactoring type occurs
    2. "frequency": total sum of the occurrences in a window of a refactoring
            divided by the total window count in which the current refactoring type occurs
    """
    likelihood = 1
    frequency = 2


def query_count(table_name: str, refactorings):
    data = []
    for refactoring_name in refactorings:
        if table_name == "refactoringspercommit":
            query = f"SELECT `{refactoring_name}` FROM {table_name} WHERE `{refactoring_name}` > 0"
        elif table_name == "refactoringsperclass" or "RefactoringsWindow" in table_name:
            query = f"SELECT refactoring_count FROM {table_name} WHERE refactoring LIKE \"{refactoring_name}\""

        refactoring_counts = execute_query(query).values
        data.append(refactoring_counts)
    log(f"Got the raw data from {table_name} for these refactorings: {refactorings}.")
    return data


def query_aggregate(table_name: str, function: str, refactorings, descriptor: str = ""):
    dataframe = pd.DataFrame()
    file_path = f"results/Aggregate/{table_name}_{function}_{descriptor}_raw.csv"
    Path(path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
    if not path.exists(file_path):
        for refactoring_name in refactorings:
            if table_name == "refactoringspercommit" or "RefactoringsWindow" in table_name:
                query = f"SELECT {function}(CASE WHEN `{refactoring_name}` > 0 THEN `{refactoring_name}` ELSE NULL END) AS \"{function}\" FROM {table_name}"
            elif table_name == "refactoringsperclass":
                query = f"SELECT {function}(refactoring_count) AS \"{function}\" FROM {table_name} WHERE refactoring LIKE \"{refactoring_name}\" AND refactoring_count > 0"
            refactoring_aggregate = execute_query(query)
            refactoring_aggregate[""] = refactoring_name
            dataframe = pd.concat([dataframe, refactoring_aggregate])
        #store the dataframe to have the raw data
        dataframe.to_csv(file_path, index=False)
        log(f"Got the raw data from {table_name} for these refactorings: {refactorings} for the aggregate function: {function}.")
    else:
        dataframe = pd.read_csv(file_path)
    labels = dataframe["Refactoring Type"].values
    dataframe = dataframe.drop(["Refactoring Type"], axis=1)
    return dataframe, labels


def query_evolution(table_name: str, count: str, aggregated: bool, refactorings):
    data = []
    for refactoring_name in refactorings:
        if not aggregated:
            query = f"SELECT {count} FROM {table_name} WHERE refactoring LIKE \"{refactoring_name}\""
            commit_count = execute_query(query)
        else:
            query = f"SELECT {count}, COUNT({count}) AS \"refactoring_count\" FROM {table_name} WHERE refactoring LIKE \"{refactoring_name}\" GROUP BY {count}"
            commit_count = execute_query(query)
            commit_count[f"{count}_total"] = sum(commit_count["refactoring_count"])
        data.append(commit_count)
    log(f"Got {count} from {table_name} for these refactorings: {refactorings}.")
    return data


def query_evolution_level(table_name: str, count: str, aggregated: bool, levels):
    data = []
    for level in levels:
        if not aggregated:
            query = f"SELECT {count} FROM {table_name} WHERE refactoring_level = {level}"
            commit_count = execute_query(query)
        else:
            query = f"SELECT {count}, COUNT({count}) AS \"refactoring_count\" FROM {table_name} WHERE refactoring_level = {level} GROUP BY {count}"
            commit_count = execute_query(query)
            commit_count[f"{count}_total"] = sum(commit_count["refactoring_count"])
        data.append(commit_count)
    log(f"Got {count} from {table_name} for these level: {levels}.")
    return data


def query_co_occurrence(table_name: str, entity_name: str, refactorings, statistic = Statistics.likelihood, descriptor: str = ""):
    dataframe = pd.DataFrame()
    file_path = f"results/Co-occurrence/{table_name}_{statistic}_{descriptor}_raw.csv"
    Path(path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
    if not path.exists(file_path):
        for refactoring_name in refactorings:
            query = "SELECT "
            if statistic == Statistics.likelihood:
                query += ", ".join([f"SUM(IF(`{refactoring_type}` > 0, 1, 0)) AS `{refactoring_type}`" for refactoring_type in refactorings])
            elif statistic == Statistics.frequency:
                query += ", ".join([f"SUM(`{refactoring_type}`) AS `{refactoring_type}`" for refactoring_type in refactorings])

            query += f",COUNT(*) AS `{entity_name} Count Total` "
            query += f"FROM {table_name} WHERE `{refactoring_name}` > 0"
            refactoringspercommit = execute_query(query)
            refactoringspercommit["Refactoring Type"] = refactoring_name
            dataframe = pd.concat([dataframe, refactoringspercommit])
        #store the dataframe to have the raw data
        dataframe.to_csv(file_path, index=False)
        log(f"Got the raw data from Refactorings_window_{table_name} and stored it in: {file_path}.")
    else:
        dataframe = pd.read_csv(file_path)

    # extract the labels for the plot and remove un-plotted data
    labels = dataframe["Refactoring Type"].values
    count = dataframe[f"{entity_name} Count Total"].values
    dataframe = dataframe.drop(["Refactoring Type", f"{entity_name} Count Total"], axis=1)
    return dataframe, labels, count


def get_metrics_refactoring_level(level, dataset, refactorings,  metrics, samples=-1):
    combined_refactoring_metrics = pd.DataFrame()
    for refactoring_name in refactorings:
        metric_data = retrieve_columns(get_level_refactorings(int(level), refactoring_name, dataset), metrics, samples)
        combined_refactoring_metrics = combined_refactoring_metrics.append(metric_data)
    log(f"Extracted refactorings metrics of level {level}")
    return combined_refactoring_metrics


def get_metrics_stable_level(level, k, dataset, metrics, samples=-1):
    metric_data = retrieve_columns(get_level_stable(int(level), k, dataset), metrics, samples)
    log(f"Extracted metrics of level {level} for K={k}")
    return metric_data


def get_metrics_stable_all(k, dataset, levels, metrics, samples=-1):
    combined_stable_metrics = pd.DataFrame()
    for level in levels:
        metric_data = get_metrics_stable_level(level, k, dataset, metrics, samples)
        combined_stable_metrics = combined_stable_metrics.append(metric_data)
    return combined_stable_metrics


def retrieve_columns(sql_query, columns, samples=-1):
    # Hash the query
    query_hash = hashlib.sha1(sql_query.encode()).hexdigest()

    # Create the filepath
    cache_dir = path.join(CACHE_DIR_PATH, "_cache")
    file_path = path.join(cache_dir, f"{query_hash}.csv")

    data = pd.read_csv(file_path, usecols=columns).apply(pd.to_numeric, downcast='float')
    if samples < 0 or len(data) < samples:
        return data
    else:
        return data.sample(samples)