import json
from pathlib import Path
import pandas as pd
from os import path
from collections import Counter
from configs import Level, LEVEL_MAP, PROCESS_METRICS_FIELDS
from db.QueryBuilder import get_level_refactorings
from refactoring_statistics.plot_utils import box_plot_seaborn
from refactoring_statistics.query_utils import retrieve_columns, get_metrics_stable_level
from utils.log import log_init, log_close, log
import datetime
import time

INPUT_DIRECTORY = "results/predictions/reproduction/"
SAVE_DIRECTORY = "results/Evaluation/reproduction/"

# metrics
CLASS_METRICS_Fields = ["classCbo",
                        # "classLcom", to large for plotting
                        "classLCC",
                        "classTCC",
                        "classRfc",
                        "classWmc"]
CLASS_ATTRIBUTES_QTY_Fields = ["classUniqueWordsQty",
                               "classNumberOfMethods",
                               "classStringLiteralsQty",
                               "classNumberOfPublicFields",
                               "classVariablesQty",
                               # "classLoc" to large for plotting
                               ]
ALL_METRICS = CLASS_METRICS_Fields + CLASS_ATTRIBUTES_QTY_Fields + PROCESS_METRICS_FIELDS


# import all json files in the given directory and return them as pd dataframe
def import_evaluation(dir_path: str):
    path_list = Path(dir_path).glob('**/*.json')
    evaluation_data = pd.DataFrame()
    prediction_data = pd.DataFrame()
    for file_path in path_list:
        with open(str(file_path), 'r') as file:
            current_data = json.load(file)
            current_evaluation = json.loads(current_data["test_scores"])
            current_predictions = json.loads(current_data["test_results"])
            current_predictions["model_name"] = current_evaluation["model_name"]
            current_predictions["refactoring_name"] = current_evaluation["refactoring type"]
            current_evaluation['level'] = get_refactoring_level(current_evaluation["refactoring type"])
            current_predictions['level'] = get_refactoring_level(current_evaluation["refactoring type"])
            prediction_data = prediction_data.append(current_predictions, ignore_index=True)
            evaluation_data = evaluation_data.append(current_evaluation, ignore_index=True)
    return evaluation_data, prediction_data


def extract_predictions(current_prediction_raw):
    return list(zip(current_prediction_raw["db_id"].values(), current_prediction_raw["label"].values(),
                    current_prediction_raw["prediction"].values()))


# extract all test scores from the given data
def extract_columns(data, scores):
    return data[["model_name", "refactoring type", "validation_sets", "level"] + scores]


def get_top_k(dict, k):
    if len(dict.items()) > 0:
        k = min(len(dict.items()), k)
        top_k = sorted(dict.items(), key=lambda x: abs(x[1]) if not isinstance(x[1], list) else abs(x[1][0]),
                       reverse=True)[:k]
        return top_k
    else:
        return []


def extract_top_k_feature_importance(data_features, k):
    features = data_features["feature_importance"]
    features_top_k = []
    for index, value in features.items():
        current_features = json.loads(value)
        current_top_k = get_top_k(current_features, k)
        features_top_k.append(current_top_k)
    return features_top_k


def extract_top_k_permutation_importance(data_features, k):
    features = data_features["permutation_importance"]
    features_top_k = []
    for index, value in features.items():
        current_features = json.loads(value)
        for key, current_validation in current_features.items():
            current_top_k = get_top_k(current_validation, k)
            features_top_k.append(current_top_k)
    return features_top_k


def extract_top_k_coef(data_features, k):
    features = data_features["feature_coefficients"]
    features_top_k = []
    for index, value in features.items():
        current_features = json.loads(value)
        current_top_k = get_top_k(current_features, k)
        features_top_k.append(current_top_k)
    return features_top_k


def get_refactoring_level(refactoring_name):
    for level in Level:
        refactorings = LEVEL_MAP[level]
        if refactoring_name in refactorings:
            return level
    return Level.NONE


# extract all feature importances from the given data
# Also enrich the feature importance by filtering for the top 1, 5 and 10 features and filtering for > 1.% features
def add_feature_importances(data, feature_importances):
    data_features = extract_columns(data, feature_importances)
    # extract top k
    for k in [1, 5, 10]:
        data_features[f"feature_importance Top-{k}"] = extract_top_k_feature_importance(data_features, k)
        data_features[f"feature_coefficients Top-{k}"] = extract_top_k_coef(data_features, k)
        data_features[f"permutation_importance Top-{k}"] = extract_top_k_permutation_importance(data_features, k)
    return data_features


def extract_feature_importances_statistic(data_features, feature_importances):
    columns = []
    for k in [1, 5, 10]:
        for importance in feature_importances:
            columns += [f"{importance} Top-{k}"]
    grouped_importances_model_level = data_features.groupby(['model_name', 'level'])[columns].agg(count_appearances)
    grouped_importances_model = data_features.groupby(['model_name'])[columns].agg(count_appearances)
    return pd.concat([grouped_importances_model_level, grouped_importances_model])


def count_appearances(column):
    values = []
    for index, value in column.items():
        values += [i[0] for i in value]
    return Counter(values).most_common()


def extract_ids(all_predictions, condition):
    filtered = list(filter(condition, all_predictions))
    return list(map(lambda x: x[0], filtered))


def get_refactoring_instances(dataset, level, refactoring_name):
    refactoring_metrics = retrieve_columns(get_level_refactorings(int(level), refactoring_name, dataset),
                                           ["db_id"] + ALL_METRICS, -1)
    refactoring_metrics["refactoring"] = refactoring_name
    refactoring_metrics["level"] = level.name
    return refactoring_metrics


def get_stable_instances(dataset, level, k):
    stable_metrics = get_metrics_stable_level(level, k, dataset, ["db_id"] + ALL_METRICS, -1)
    stable_metrics['level'] = level.name
    stable_metrics['k'] = k
    stable_metrics['refactoring'] = f"Stable-{str(level)}"
    return stable_metrics


def extract_false_negatives(data, dataset, level, refactoring_name):
    refactoring_metrics = get_refactoring_instances(dataset, level, refactoring_name)
    predictions = extract_predictions(data)
    false_negatives_ids = extract_ids(predictions, lambda x: x[1] == 1 and x[2] == 0)
    return refactoring_metrics[refactoring_metrics.db_id.isin(false_negatives_ids)]


def extract_true_positives(data, dataset, level, refactoring_name):
    refactoring_metrics = get_refactoring_instances(dataset, level, refactoring_name)
    predictions = extract_predictions(data)
    true_positives_ids = extract_ids(predictions, lambda x: x[1] == 1 and x[2] == 1)
    return refactoring_metrics[refactoring_metrics.db_id.isin(true_positives_ids)]


def extract_false_positives(data, dataset, level, k):
    stable_metrics = get_stable_instances(dataset, level, k)
    predictions = extract_predictions(data)
    false_positives_ids = extract_ids(predictions, lambda x: x[1] == 0 and x[2] == 1)
    return stable_metrics[stable_metrics.db_id.isin(false_positives_ids)]


def extract_true_negatives(data, dataset, level, k):
    stable_metrics = get_stable_instances(dataset, level, k)
    predictions = extract_predictions(data)
    true_negatives_ids = extract_ids(predictions, lambda x: x[1] == 0 and x[2] == 0)
    return stable_metrics[stable_metrics.db_id.isin(true_negatives_ids)]


# plot all refactorings
def plot_refactoring_metrics(refactoring_metrics, level, dataset, hue, yticks, metrics, title, file_descriptor):
    fig_path_box = f"{SAVE_DIRECTORY}{file_descriptor}_{level.name}_log_box_plot_{dataset}.svg"
    if not path.exists(fig_path_box):
        refactoring_metrics = pd.melt(refactoring_metrics, id_vars=hue, var_name="Metric", value_vars=metrics,
                                      value_name="values")
        box_plot_seaborn(refactoring_metrics, f"{title}", fig_path_box, scale="log", yticks=yticks, hue=hue)
    else:
        log(f"--Skipped box plot at {fig_path_box}, because it already exists.")


def plot_metrics(metrics, level, title, file_descriptor, hue):
    plot_refactoring_metrics(metrics, level, "test_set_github", hue,
                             yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 50, 75, 100, 125, 150, 200],
                             metrics=CLASS_ATTRIBUTES_QTY_Fields,
                             title=f"Class Attributes: {title} at {level.name}",
                             file_descriptor=f"{file_descriptor}_Class_Attributes")
    plot_refactoring_metrics(metrics, level, "test_set_github", hue,
                             yticks=[1, 2.5, 3.5, 5, 7.5, 10, 15, 20, 25, 50, 100, 150, 250, 350, 500, 750, 1000],
                             metrics=CLASS_METRICS_Fields,
                             title=f"Class Metrics: {title} at {level.name}",
                             file_descriptor=f"{file_descriptor}_Class_Metrics")
    plot_refactoring_metrics(metrics, level, "test_set_github", hue,
                             yticks=[0.1, 0.15, 0.25, 0.5, 0.75, 1, 1.5, 2.0, 2.5, 5, 6, 7.5, 10, 15, 20, 25, 50, 75,
                                     100, 125, 150], metrics=PROCESS_METRICS_FIELDS,
                             title=f"Process- and Ownership Metrics: {title} at {level.name}",
                             file_descriptor=f"{file_descriptor}_Process_Ownership_Metrics")


log_init(f"{SAVE_DIRECTORY}evaluation_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt")
start_time = time.time()
# data import and preparation
evaluation_data, prediction_data = import_evaluation(INPUT_DIRECTORY)

false_negatives_metrics_all = pd.DataFrame()
false_positives_metrics_all = pd.DataFrame()
true_negatives_metrics_all = pd.DataFrame()
true_positives_metrics_all = pd.DataFrame()

for index, row in prediction_data.iterrows():
    refactoring_name = row["refactoring_name"]
    level = get_refactoring_level(refactoring_name)
    false_negatives_metrics_all = false_negatives_metrics_all.append(extract_false_negatives(row, "test set github", level, refactoring_name))
    false_positives_metrics_all = false_positives_metrics_all.append(extract_false_positives(row, "test set github", level, 50))
    true_negatives_metrics_all = true_negatives_metrics_all.append(extract_true_negatives(row, "test set github", level, 50))
    true_positives_metrics_all = true_positives_metrics_all.append(extract_true_positives(row, "test set github", level, refactoring_name))

for level in [Level.Class, Level.Method, Level.Variable]:
    false_negatives_metrics_level = false_negatives_metrics_all[false_negatives_metrics_all['level'] == level.name]
    false_positives_metrics_level = false_positives_metrics_all[false_positives_metrics_all['level'] == level.name]
    true_negatives_metrics_level = true_negatives_metrics_all[true_negatives_metrics_all['level'] == level.name]
    true_positives_metrics_level = true_positives_metrics_all[true_positives_metrics_all['level'] == level.name]
    if false_negatives_metrics_level.shape[0] > 0 and false_positives_metrics_level.shape[0] > 0:
        plot_metrics(pd.concat([false_positives_metrics_level, true_positives_metrics_level]), level,
                     "False Positives vs True Positives", "false_positives_true_positives", "refactoring")
        plot_metrics(pd.concat([false_negatives_metrics_level, true_negatives_metrics_level]), level,
                     "False Negatives vs True Negatives", "false_negatives_true_negatives", "refactoring")
        plot_metrics(pd.concat([false_negatives_metrics_level, false_positives_metrics_level]), level,
                     "False Negatives vs False Positives", "false_negatives_false_positives", "refactoring")

test_scores = extract_columns(evaluation_data, ["f1_scores", "precision_scores", "recall_scores", "accuracy_scores", "confusion_matrix"])
feature_importances = add_feature_importances(evaluation_data, ["feature_importance", "feature_coefficients", "permutation_importance"])
feature_importances_statistics = extract_feature_importances_statistic(feature_importances,
                                                                       ["feature_importance", "feature_coefficients",
                                                                        "permutation_importance"])

Path(path.dirname(SAVE_DIRECTORY)).mkdir(parents=True, exist_ok=True)
test_scores.to_excel(f"{SAVE_DIRECTORY}test_scores_all.xlsx", index=False)
feature_importances.to_excel(f"{SAVE_DIRECTORY}feature_importances_all.xlsx", index=False)
feature_importances_statistics.to_excel(f"{SAVE_DIRECTORY}feature_importances_statistics.xlsx")

log_close()
exit()
