from dataclasses import dataclass, field

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

TEST_MODELS = {
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
             "ratio_ext_flex",
             ],
    "freq": ["max_freq",
             "sum_freq",
             "mean_freq",
             "var_freq",
             "skew_freq",
             "kurtosis_freq",
             ],
}

@dataclass
class model_config:
    model_name: str = "lda"
    model_type: str = "supervised"
    trim: int = 50
    min_len: int  = 300
    win: int = 100
    step: int = 50
    features: list | dict = field(default_factory=FEATURE_SETS)