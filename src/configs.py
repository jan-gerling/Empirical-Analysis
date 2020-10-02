from enum import IntEnum, Enum


class FileType(Enum):
    only_production = 0
    only_test = 1
    test_and_production = 2


FILE_TYPE = 0

USE_CACHE = True
DB_AVAILABLE = False
CACHE_DIR_PATH = "C:/Users/jange/Desktop/Machine-Learning/"

# --------------------------------
# Datasets
# --------------------------------

# Empty dataset means 'all datasets'
DATASETS = ["github"]

VALIDATION_DATASETS = ["test set github", "validation set github"]


# --------------------------------
# Refactorings
# --------------------------------

# refactoring levels
class Level(IntEnum):
    NONE = 0
    Class = 1
    Method = 2
    Variable = 3
    Field = 4
    Other = 5


# Refactorings to study
# Refactorings to study
CLASS_LEVEL_REFACTORINGS = ["Extract Class",
                            "Extract Interface",
                            "Extract Subclass",
                            "Extract Superclass",
                            "Move And Rename Class",
                            "Move Class",
                            "Rename Class",
                            #"Introduce Polymorphism",
                            #"Convert Anonymous Class To Type"
                            ]

METHOD_LEVEL_REFACTORINGS = ["Extract And Move Method",
                             "Extract Method",
                             "Inline Method",
                             "Move Method",
                             "Pull Up Method",
                             "Push Down Method",
                             "Rename Method",
                             "Extract And Move Method",
                             "Change Return Type",
                             "Move And Inline Method",
                             "Move And Rename Method",
                             "Change Parameter Type",
                             "Split Parameter",
                             "Merge Parameter"]

VARIABLE_LEVEL_REFACTORINGS = ["Extract Variable",
                               "Inline Variable",
                               "Parameterize Variable",
                               "Rename Parameter",
                               "Rename Variable",
                               "Replace Variable With Attribute",
                               "Change Variable Type",
                               "Split Variable",
                               "Merge Variable"
                               ]

FIELD_LEVEL_REFACTORINGS = ["Move Attribute",
                            "Pull Up Attribute",
                            "Move And Rename Attribute",
                            "Push Down Attribute",
                            "Replace Attribute",
                            "Rename Attribute",
                            "Extract Attribute",
                            "Change Attribute Type"
                            ]

OTHER_LEVEL_REFACTORINGS = ["Move Source Folder",
                            "Change Package"]

# region metrics fields
# the ids are not included as they are the same for every table: id : long
CLASS_METRICS_Fields = ["classAnonymousClassesQty",
                        "classAssignmentsQty",
                        "classCbo",
                        "classComparisonsQty",
                        "classLambdasQty",
                        "classLcom",
                        "classLoc",
                        "classLCC",
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
                        "classNumberOfPublicFields",
                        "classNumberOfPublicMethods",
                        "classNumberOfStaticFields",
                        "classNumberOfStaticMethods",
                        "classNumberOfSynchronizedFields",
                        "classNumberOfSynchronizedMethods",
                        "classNumbersQty",
                        "classParenthesizedExpsQty",
                        "classReturnQty",
                        "classRfc",
                        "classStringLiteralsQty",
                        "classSubClassesQty",
                        "classTryCatchQty",
                        "classUniqueWordsQty",
                        "classVariablesQty",
                        "classWmc",
                        "classTCC",
                        "isInnerClass"]
METHOD_METRICS_FIELDS = [#"fullMethodName", ToDo: decide if and how to include string objects
    "methodAnonymousClassesQty",
    "methodAssignmentsQty",
    "methodCbo",
    "methodComparisonsQty",
    "methodLambdasQty",
    "methodLoc",
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
    "methodUniqueWordsQty",
    "methodVariablesQty",
    "methodWmc",
    #"shortMethodName", ToDo: decide if and how to include string objects
    "startLine"]
VARIABLE_METRICS_FIELDS = ["variableAppearances",
                           #"variableName" ToDo: decide if and how to include string objects
                           ]
FIELD_METRICS_FIELDS = ["fieldAppearances",
                        #"fieldName" ToDo: decide if and how to include string objects
                        ]
PROCESS_METRICS_FIELDS = ["authorOwnership",
                          "bugFixCount",
                          "qtyMajorAuthors",
                          "qtyMinorAuthors",
                          "qtyOfAuthors",
                          "qtyOfCommits",
                          "refactoringsInvolved"]
COMMIT_METADATA_FIELDS = ["commitDate",
                          "commitId",
                          "commitMessage",
                          "commitUrl",
                          "parentCommitId"]
PROJECT_FIELDS = ["commitCountThresholds",
                  "commits",
                  "datasetName",
                  "dateOfProcessing",
                  "exceptionsCount",
                  "finishedDate",
                  "gitUrl",
                  "isLocal",
                  "javaLoc",
                  "lastCommitHash",
                  "numberOfProductionFiles",
                  "numberOfTestFiles",
                  "productionLoc",
                  "projectName",
                  "projectSizeInBytes",
                  "testLoc"]
REFACTORING_COMMIT_FIELDS = ["className",
                             "filePath",
                             "isTest",
                             "level",
                             # "refactoring", this two fields are not used for the training
                             # "refactoringSummary"
                             ]
STABLE_COMMIT_FIELDS = ["className",
                        "filePath",
                        "isTest",
                        "level"]
# endregion

LEVEL_METRIC_MAP = {
                 Level.NONE: [],
                 Level.Class: CLASS_METRICS_Fields + PROCESS_METRICS_FIELDS,
                 Level.Method:  CLASS_METRICS_Fields + METHOD_METRICS_FIELDS + PROCESS_METRICS_FIELDS,
                 Level.Field:  CLASS_METRICS_Fields + FIELD_METRICS_FIELDS + PROCESS_METRICS_FIELDS,
                 Level.Variable:  CLASS_METRICS_Fields + METHOD_METRICS_FIELDS + VARIABLE_METRICS_FIELDS + PROCESS_METRICS_FIELDS,
                 Level.Other:  CLASS_METRICS_Fields + PROCESS_METRICS_FIELDS,
}

LEVEL_METRIC_SET_MAP = {
    Level.NONE: [],
    Level.Class: [("CLASS_METRICS", CLASS_METRICS_Fields), ("PROCESS_METRICS", PROCESS_METRICS_FIELDS)],
    Level.Method:  [("CLASS_METRICS", CLASS_METRICS_Fields), ("METHOD_METRICS", METHOD_METRICS_FIELDS), ("PROCESS_METRICS", PROCESS_METRICS_FIELDS)],
    Level.Field:  [("CLASS_METRICS", CLASS_METRICS_Fields), ("FIELD_METRICS", FIELD_METRICS_FIELDS), ("PROCESS_METRICS", PROCESS_METRICS_FIELDS)],
    Level.Variable:  [("CLASS_METRICS", CLASS_METRICS_Fields), ("METHOD_METRICS", METHOD_METRICS_FIELDS), ("VARIABLE_METRICS", VARIABLE_METRICS_FIELDS), ("PROCESS_METRICS", PROCESS_METRICS_FIELDS)],
    Level.Other:  [("CLASS_METRICS", CLASS_METRICS_Fields), ("PROCESS_METRICS", PROCESS_METRICS_FIELDS)],
}


LEVEL_MAP = {Level.NONE: [],
             Level.Class: CLASS_LEVEL_REFACTORINGS,
             Level.Method: METHOD_LEVEL_REFACTORINGS,
             Level.Field: FIELD_LEVEL_REFACTORINGS,
             Level.Variable: VARIABLE_LEVEL_REFACTORINGS,
             Level.Other: OTHER_LEVEL_REFACTORINGS}
