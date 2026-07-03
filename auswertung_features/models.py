from typing import Callable, Dict, Any

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

ModelFn = Callable[...,Any]

MODELS_SUPERVISED : Dict[str, ModelFn] = {}

def register_model_supervised(name: str):
    def deco(fn: ModelFn):
        MODELS_SUPERVISED[name] = fn
        return fn
    return deco

# =========================================================
# ===                supervised models                  ===
# =========================================================

@register_model_supervised('lda')
def model_lda(**kwargs):
    return LinearDiscriminantAnalysis()

@register_model_supervised('linear-svm')
def model_linear_svm(**kwargs):
    return LinearSVC()

@register_model_supervised('decision-tree')
def model_decision_tree(**kwargs):
    return DecisionTreeClassifier()

@register_model_supervised('log-reg')
def model_logistic_regression(**kwargs):
    return LogisticRegression()

@register_model_supervised('knn')
def model_knn(**kwargs):
    return KNeighborsClassifier()

@register_model_supervised('randomforest')
def model_random_forest(**kwargs):
    return RandomForestClassifier()