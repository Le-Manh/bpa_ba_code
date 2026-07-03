from typing import Callable, Dict, List
import numpy as np
from scipy.stats import skew, kurtosis

FeatureFn = Callable[[np.ndarray], np.ndarray]

FEATURES_TIME: Dict[str, FeatureFn] = {}
FEATURES_FREQ: Dict[str, FeatureFn] = {}

def register_feature_time(name: str):
    def deco(fn: FeatureFn):
        FEATURES_TIME[name] = fn
        return fn
    return deco

def register_feature_freq(name: str):
    def deco(fn: FeatureFn):
        FEATURES_FREQ[name] = fn
        return fn

    return deco

# =========================================================
# ===                  TIME FEATURES                    ===
# =========================================================
@register_feature_time("rms")
def feat_rms(w, eps = 1e-8, **kwargs):
    return np.sqrt(np.mean(w*w, axis=0) + eps)

@register_feature_time("wl")
def feat_wl(w, **kwargs):
    return np.sum(np.abs(np.diff(w, axis=0)), axis=0)

@register_feature_time("p")
def feat_p(w, eps=1e-8, **kwargs):
    rms = feat_rms(w, eps)
    return rms / (np.sum(rms) + eps)

@register_feature_time("min")
def feat_min(w, **kwargs):
    return np.min(w, axis=0)

@register_feature_time("max")
def feat_max(w, **kwargs):
    return np.max(w, axis=0)

@register_feature_time("mean")
def feat_mean(w, **kwargs):
    return np.mean(w, axis=0)

@register_feature_time("std")
def feat_std(w, **kwargs):
    return np.std(w, axis=0)

@register_feature_time("var")
def feat_var(w, **kwargs):
    return np.var(w, axis=0)

@register_feature_time("mav")
def feat_mav(w, **kwargs):
    return np.mean(np.abs(w), axis=0)

@register_feature_time("peak")
def feat_peak(w, **kwargs):
    return np.max(np.abs(w), axis=0)

@register_feature_time("ptp")
def feat_ptp(w, **kwargs):
    return np.ptp(w, axis=0)

@register_feature_time("crest")
def feat_crest(w, eps=1e-8, **kwargs):
    peak = feat_peak(w)
    rms = feat_rms(w, eps)
    return peak / (rms + eps)

@register_feature_time("skew")
def feat_skew(w, **kwargs):
    return skew(w, axis=0)

@register_feature_time("kurtosis")
def feat_kurtosis(w, **kwargs):
    return kurtosis(w, axis=0)

# =========================================================
# ===                FREQUENCY FEATURES                 ===
# =========================================================

@register_feature_freq("max_freq")
def feat_max_freq(s, **kwargs):
    return np.max(s, axis=0)

@register_feature_freq("sum_freq")
def feat_sum_freq(s, **kwargs):
    return np.sum(s, axis=0)

@register_feature_freq("mean_freq")
def feat_mean_freq(s, **kwargs):
    return np.mean(s, axis=0)

@register_feature_freq("var_freq")
def feat_var_freq(s, **kwargs):
    return np.var(s, axis=0)

@register_feature_freq("skew_freq")
def feat_skew_freq(s, **kwargs):
    return skew(s, axis=0)

@register_feature_freq("kurtosis_freq")
def feat_kurtosis_freq(s, **kwargs):
    return kurtosis(s, axis=0)

# =============================================
# ===   Beachtung der Sensorenplatzierung   ===
# =============================================
@register_feature_time("ratio_ext_flex")
def feat_ratio(w, **kwargs):
    eps = 1e-8
    rms = np.sqrt(np.mean(w*w, axis=0) + eps)
    EXT_IDX = 2
    FLEX_IDXS = [0,1,3]
    return np.array([rms[EXT_IDX] / (np.sum(rms[FLEX_IDXS]) + eps)], dtype=np.float32)