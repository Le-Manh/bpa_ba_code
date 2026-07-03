from typing import Callable, Dict, List
import numpy as np

FeatureFn = Callable[[np.ndarray], np.ndarray]

FEATURES: Dict[str, FeatureFn] = {}

def register_feature(name: str):
    def deco(fn: FeatureFn):
        FEATURES[name] = fn
        return fn
    return deco

@register_feature("rms")
def feat_rms(w):
    eps = 1e-8
    return np.sqrt(np.mean(w*w, axis=0) + eps)

@register_feature("wl")
def feat_wl(w):
    return np.sum(np.abs(np.diff(w, axis=0)), axis=0)

@register_feature("ratio_ext_flex")
def feat_ratio(w):
    eps = 1e-8
    rms = np.sqrt(np.mean(w*w, axis=0) + eps)
    EXT_IDX = 2
    FLEX_IDXS = [0,1,3]
    return np.array([rms[EXT_IDX] / (np.sum(rms[FLEX_IDXS]) + eps)], dtype=np.float32)