from typing import Callable, Dict, Any
from dataclasses import dataclass

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC, SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from sklearn.cluster import KMeans, AgglomerativeClustering

from sklearn.neural_network import MLPClassifier

from sklearn.pipeline import Pipeline

# supervised registry and ANN registry
ModelFn = Callable[...,Any]

@dataclass(frozen=True)
class ModelSpec:
    make: ModelFn
    needs_scaling: bool = False

MODELS_SUPERVISED: Dict[str, ModelSpec] = {}

def register_model_supervised(name: str, *, needs_scaling: bool = False):
    def deco(fn: ModelFn):
        MODELS_SUPERVISED[name] = ModelSpec(make=fn, needs_scaling=needs_scaling)
        return fn
    return deco

# unsupervised/clustering registry
ClusterFn = Callable[..., Any]

MODELS_CLUSTERING: Dict[str, ModelSpec] = {}

def register_model_clustering(name: str, *, needs_scaling: bool = False):
    def deco(fn: ClusterFn):
        MODELS_CLUSTERING[name] = ModelSpec(make=fn, needs_scaling=needs_scaling)
        return fn
    return deco

# =========================================================
# ===                supervised models                  ===
# =========================================================

@register_model_supervised('lda', needs_scaling=True)
def model_lda(**kwargs):
    return LinearDiscriminantAnalysis(**kwargs)

@register_model_supervised('linear-svm', needs_scaling=True)
def model_linear_svm(**kwargs):
    return LinearSVC(**kwargs)

@register_model_supervised('svc', needs_scaling=True)
def model_svc(**kwargs):
    return SVC(**kwargs)

@register_model_supervised('decision-tree', needs_scaling=False)
def model_decision_tree(**kwargs):
    return DecisionTreeClassifier(**kwargs)

@register_model_supervised('log-reg', needs_scaling=True)
def model_logistic_regression(**kwargs):
    return LogisticRegression(**kwargs)

@register_model_supervised('knn', needs_scaling=True)
def model_knn(**kwargs):
    return KNeighborsClassifier(**kwargs)

@register_model_supervised('randomforest', needs_scaling=False)
def model_random_forest(**kwargs):
    return RandomForestClassifier(**kwargs)

# This is a model which uses lda as dimension reduction and svc as model
@register_model_supervised("lda-svm", needs_scaling=True)
def model_lda_svm(**kwargs):
    return Pipeline([("dim-red",LinearDiscriminantAnalysis()),("base",SVC(**kwargs))])

# =========================================================
# ===              unsupervised models                  ===
# =========================================================
@register_model_clustering("kmeans", needs_scaling=True)
def cluster_kmeans(**kwargs):
    return KMeans(**kwargs)

@register_model_clustering("agglo", needs_scaling=True)
def cluster_agglo(**kwargs):
    return AgglomerativeClustering(**kwargs)

# =========================================================
# ===                 Neural Networks                   ===
# =========================================================
@register_model_supervised("mlp", needs_scaling=True)
def model_mlp(**kwargs):
    return MLPClassifier(
        **kwargs
    )