from dataclasses import dataclass, field
from typing import Tuple, Any
from sklearn.model_selection import ParameterGrid

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

MODEL_SPACE = {
  "supervised": {
    "linear-svm": ParameterGrid({"C": [0.1, 1.0, 10.0]}),
    "knn": ParameterGrid({"n_neighbors": [3,5,7]}),
  },
  "clustering": {
    "kmeans": ParameterGrid({"n_clusters":[5], "random_state":[0,1], "n_init":["auto"]}),
  }
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
class DataConfig:
    trim: int
    min_len: int
    win: int
    step: int
    feature_set_name: str
    time_feature_names: Tuple[str, ...]
    freq_feature_names: Tuple[str, ...]

@dataclass(frozen=True)
class ModelConfig:
    model_name: str
    model_type: str
    params: tuple[tuple[str, Any], ...] = field(default_factory=tuple)

    def params_dict(self) -> dict[str, Any]:
        return dict(self.params)