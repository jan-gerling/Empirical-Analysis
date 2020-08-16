from enum import Enum
from db.DBConnector import execute_query
from utils.log import log
from os import path
import pandas as pd
from pathlib import Path


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


def query_evolution(table_name: str, count: str, aggregated: bool, refactorings = None, level = None):
    data = []
    for refactoring_name in refactorings:
        if not aggregated and
            if refactorings is not None:
                query = f"SELECT {count} FROM {table_name} WHERE refactoring LIKE \"{refactoring_name}\""
            elif not aggregated and refactorings is None and level is not None:
                query = f"SELECT {count} FROM {table_name} INNER JOIN RefactoringCommit WHERE refactoring LIKE \"{refactoring_name}\""
            commit_count = execute_query(query)
        elif aggregated and refactorings is not None:
            query = f"SELECT {count}, COUNT({count}) AS \"refactoring_count\" FROM {table_name} WHERE refactoring LIKE \"{refactoring_name}\" GROUP BY {count}"
            commit_count = execute_query(query)
            commit_count[f"{count}_total"] = sum(commit_count["refactoring_count"])
        data.append(commit_count)
    log(f"Got {count} from {table_name} for these refactorings: {refactorings}.")
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