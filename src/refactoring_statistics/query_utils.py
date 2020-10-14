from configs import CACHE_DIR_PATH
from db.DBConnector import execute_query
from db.QueryBuilder import get_level_stable, get_level_refactorings
from utils.log import log
from os import path
import pandas as pd
import hashlib


def get_metrics_refactoring_level(level, dataset, refactorings,  metrics, samples=-1):
    combined_refactoring_metrics = pd.DataFrame()
    for refactoring_name in refactorings:
        metric_data = retrieve_columns(get_level_refactorings(int(level), refactoring_name, dataset), metrics, samples)
        combined_refactoring_metrics = combined_refactoring_metrics.append(metric_data)
    log(f"Extracted refactorings metrics of level {level}")
    return combined_refactoring_metrics


def get_metrics_refactorings(level, dataset, refactorings,  metrics, samples=-1):
    combined_refactoring_metrics = pd.DataFrame()
    for refactoring_name in refactorings:
        metric_data = retrieve_columns(get_level_refactorings(int(level), refactoring_name, dataset), metrics, samples)
        metric_data['refactoring'] = refactoring_name
        combined_refactoring_metrics = combined_refactoring_metrics.append(metric_data)
    log(f"Extracted refactorings metrics of level {level}")
    return combined_refactoring_metrics


def get_metrics_stable_level(level, k, dataset, metrics, samples=-1):
    metric_data = retrieve_columns(get_level_stable(int(level), k, dataset), metrics, samples)
    log(f"Extracted metrics of level {level} for K={k}")
    return metric_data


def get_metrics_stable_level_unique_metrics(level, k, metrics, samples=-1):
    query = f"SELECT classmetric.* FROM classmetric INNER JOIN (SELECT DISTINCT classMetrics_id FROM stablecommit WHERE isTest = FALSE AND LEVEL = {int(level)} AND commitThreshold = {k}) unique_metrics ON unique_metrics.classMetrics_id = classmetric.id;"
    metric_data = retrieve_columns(query, metrics, samples)
    log(f"Extracted metrics of level {level} at {k}")
    return metric_data


def get_metrics_stable_all(k, dataset, levels, metrics, samples=-1):
    combined_stable_metrics = pd.DataFrame()
    for level in levels:
        metric_data = get_metrics_stable_level(level, k, dataset, metrics, samples)
        combined_stable_metrics = combined_stable_metrics.append(metric_data)
    return combined_stable_metrics


def get_last_refactored_instance(metrics, level, refactoring="", samples=-1):
    refactoring_condition = ""
    if len(refactoring) > 0:
        refactoring_condition = f"AND refactoring LIKE \"{refactoring}\""
    query = f"SELECT classmetric.*, processmetrics.* FROM (SELECT project_id, filePath, max(processMetrics_id) AS processMetrics_id, max(classmetrics_id) AS classmetrics_id FROM refactoringcommit WHERE isValid = True AND isTest = FALSE AND `level`={int(level)} {refactoring_condition} GROUP BY project_id, filePath, className) latest INNER JOIN classmetric ON classmetric.id = latest.classmetrics_id INNER JOIN processmetrics  ON processmetrics.id = latest.processMetrics_id;"
    metric_data = retrieve_columns(query, metrics, samples)
    return metric_data


def get_last_refactored_instance_all(metrics, samples=-1):
    query = f"SELECT classmetric.*, processmetrics.* FROM (SELECT max(processMetrics_id) AS processMetrics_id, max(classmetrics_id) AS classmetrics_id FROM refactoringcommit WHERE isValid = True AND isTest = FALSE GROUP BY project_id, filePath) latest INNER JOIN classmetric ON classmetric.id = latest.classmetrics_id INNER JOIN processmetrics  ON processmetrics.id = latest.processMetrics_id;"
    metric_data = retrieve_columns(query, metrics, samples)
    return metric_data


def retrieve_columns(sql_query, columns, samples=-1):
    # Hash the query
    query_hash = hashlib.sha1(sql_query.encode()).hexdigest()

    # Create the filepath
    cache_dir = path.join(CACHE_DIR_PATH, "_cache")
    file_path = path.join(cache_dir, f"{query_hash}.csv")

    if path.exists(file_path):
        data = pd.read_csv(file_path, usecols=columns)
        if samples < 0 or len(data) < samples:
            return data
        else:
            return data.sample(samples)
    else:
        return execute_query(sql_query)