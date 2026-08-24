from dataclasses import dataclass, field
from typing import Tuple, Any
from sklearn.model_selection import ParameterGrid

PARAM_GRID = ParameterGrid({
    "trim":    [0],
    "min_len": [500],
    "win":     [500],
    "step":    [50],
})
def valid_data_params(p: dict) -> bool:
    # Schrittweite sollte nicht größer als Fenster sein
    if p["step"] > p["win"]:
        return False
    # sinnvoll: min_len muss mindestens ein Fenster nach trim erlauben
    # (hier eher konservativ)
    if p["min_len"] != 0 and p["min_len"] < p["win"]:
        return False
    return True

DATA_PARAM_LIST = [p for p in PARAM_GRID if valid_data_params(p)]

MODEL_SPACE = {
    "supervised": {
        "linear-svm": {"random_state":[0],"C": [0.01, 0.1, 1.0, 10.0], "max_iter":[2000]},
        "svc": {"random_state": [0], "C": [0.01, 0.1, 1.0, 10.0], "max_iter":[2000]},
        #"knn": {"n_neighbors": [1, 3, 5, 7, 9]},
        #"logs-reg": {"C": [0.1, 1.0, 10.0], "max_iter": [2000]},
        #"randomforest": {
        #    "n_estimators": [300, 600],
        #    "max_depth": [None, 10, 20],
        #    "random_state": [0],
        #},
        "lda": {},
        "lda-svm":{"random_state" : [0], "max_iter":[2000]}
    },
    #"ann": {
    #    "mlp":{
    #        "solver": ["lbfgs","sgd", "adam"],
    #        "activation": ["identity", "logistic", "tanh", "relu"],
    #        "hidden_layer_sizes": [(50,), (100,), (200,)],
    #        "alpha": [1e-4, 1e-3],
    #        "max_iter": [10000],
    #        "early_stopping":[True],
    #        "random_state":[0],
    #    }
    #}
}
''' not used for now
    "clustering": { # TODO vllt eher Dimensionsreduktion und plotten
        "kmeans": ParameterGrid({ # ParameterGrid will be not used if I GridSearchCV is used
            "n_clusters": [5],
            "random_state": [0, 1, 2],
            "n_init": ["auto"],
        })
    }
'''


FEATURE_SETS = {
    "time": ["rms",
             "wl",
             "p",
             "min",
             "max",
             "mean",
             "std",
             "var",
             "mav",
             "peak",
             "ptp",
             "crest",
             "skew",
             "kurtosis",
             #"ratio_ext_flex",
             ],
    "freq": ["max_freq",
             "sum_freq",
             "mean_freq",
             "var_freq",
             "skew_freq",
             "kurtosis_freq",
             ],
}

FEATURE_SET_LIBRARY = {
    #"time_only": {"time": FEATURE_SETS["time"], "freq": []},
    #"freq_only": {"time": [], "freq": FEATURE_SETS["freq"]},
    "time+freq": {"time": FEATURE_SETS["time"], "freq": FEATURE_SETS["freq"]}, # in the first run wa sthis the best
}

@dataclass(frozen=True)
class DataConfig:
    trim: int
    min_len: int
    win: int
    step: int
    feature_set_name: str = "tsfel"
    time_feature_names: Tuple[str, ...] = ("rms", "wl")
    freq_feature_names: Tuple[str, ...] = ("max_feq", "sum_freq")

@dataclass(frozen=True)
class ModelConfig:
    model_name: str
    model_type: str
    params: tuple[tuple[str, Any], ...] = field(default_factory=tuple)

    def params_dict(self) -> dict[str, Any]:
        return dict(self.params)