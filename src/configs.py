from enum import IntEnum, Enum
class FileType(Enum):
    only_production = 0
    only_test = 1
    test_and_production = 2

FILE_TYPE = 0

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
CLASS_LEVEL_REFACTORINGS = ["Extract Class",
                            "Extract Interface",
                            "Extract Subclass",
                            "Extract Superclass",
                            "Move And Rename Class",
                            "Move Class",
                            "Rename Class",
                            #"Introduce Polymorphism",
                            "Move And Rename Class",
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
                               "Merge Variable"]

FIELD_LEVEL_REFACTORINGS = ["Move Attribute",
                            "Pull Up Attribute",
                            "Move And Rename Attribute",
                            "Push Down Attribute",
                            "Replace Attribute",
                            "Rename Attribute",
                            "Extract Attribute",
                            "Change Attribute Type"]

OTHER_LEVEL_REFACTORINGS = ["Move Source Folder",
                            "Change Package"]

LEVEL_MAP = {Level.NONE: [],
             Level.Class: CLASS_LEVEL_REFACTORINGS,
             Level.Method: METHOD_LEVEL_REFACTORINGS,
             Level.Field: FIELD_LEVEL_REFACTORINGS,
             Level.Variable: VARIABLE_LEVEL_REFACTORINGS,
             Level.Other: OTHER_LEVEL_REFACTORINGS}
