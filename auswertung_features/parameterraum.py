from dataclasses import dataclass, field
from features import FeatureFn

PARAM_GRID = [
    {"trim": 25, "min_len": 300, "win": 100, "step": 25},
    {"trim": 25, "min_len": 300, "win": 100, "step": 50},
    {"trim": 50, "min_len": 300, "win": 100, "step": 100},
    {"trim": 50, "min_len": 300, "win": 200, "step": 50},
    {"trim": 50, "min_len": 300, "win": 200, "step": 100},
    {"trim": 50, "min_len": 300, "win": 250, "step": 50},
    {"trim": 50, "min_len": 300, "win": 250, "step": 100},
    {"trim": 50, "min_len": 300, "win": 300, "step": 100},
    {"trim": 25, "min_len": 300, "win": 300, "step": 50},
]

TEST_MODELS = { # vllt 10?
    "supervised" : ["lda",
                    "randomForest",
                    "knn",
                    "linear-svm",
                    "decisionTree",
                    "log-reg",
                    ],
    "unsupervised" : [""], # TODO implement unsupervised
    "ANN" : ["CNN"] # TODO wenn man mal Zeit hat
}

FEATURE_SETS = { # 3 Feature Sets
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
    "time_only": {"time": FEATURE_SETS["time"], "freq": []},
    "freq_only": {"time": [], "freq": FEATURE_SETS["freq"]},
    "time+freq": {"time": FEATURE_SETS["time"], "freq": FEATURE_SETS["freq"]},
}

@dataclass(frozen=True)
class model_config:
    model_name: str = "lda"
    model_type: str = "supervised"
    trim: int = 50
    min_len: int  = 300
    win: int = 100
    step: int = 50
    feature_set_name: str = "time+freq"
    time_feature_names: tuple[str, ...] = ("rms", "mav", "wl")
    freq_feature_names: tuple[str,...] = ("mean_freq","sum_freq")