import json
from pathlib import Path
import pandas as pd
from os import path
from collections import Counter
from configs import Level, LEVEL_MAP


DIRECTORY = "results/predictions/"


# import all json files in the given directory and return them as pd dataframe
def import_evaluation(dir_path: str):
    path_list = Path(dir_path).glob('**/*.json')
    data = pd.DataFrame()
    for file_path in path_list:
        with open(str(file_path), 'r') as file:
            current_data = json.load(file)
            current_evaluation = json.loads(current_data["test_scores"])
            data = data.append(current_evaluation, ignore_index=True)
    return data


# extract all test scores from the given data
def extract_columns(data, scores):
    return data[["model_name", "refactoring type", "validation_sets", "level"] + scores]


def get_top_k(dict, k):
    if len(dict.items()) > 0:
        k = min(len(dict.items()), k)
        top_k = sorted(dict.items(), key=lambda x: abs(x[1]) if not isinstance(x[1], list) else abs(x[1][0]), reverse=True)[:k]
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


# data import
data = import_evaluation(DIRECTORY)

# data preparation
data['level'] = list(map(get_refactoring_level, data["refactoring type"]))
test_scores = extract_columns(data, ["f1_scores", "precision_scores", "recall_scores", "accuracy_scores", "confusion_matrix"])
feature_importances = add_feature_importances(data, ["feature_importance", "feature_coefficients", "permutation_importance"])
feature_importances_statistics = extract_feature_importances_statistic(feature_importances, ["feature_importance", "feature_coefficients", "permutation_importance"])

Path(path.dirname("results/Evaluation/")).mkdir(parents=True, exist_ok=True)
test_scores.to_excel("results/Evaluation/test_scores_all.xlsx", index=False)
feature_importances.to_excel("results/Evaluation/feature_importances_all.xlsx", index=False)
feature_importances_statistics.to_excel("results/Evaluation/feature_importances_statistics.xlsx")
exit()