PARAM_GRID = [
    {"trim": 50, "min_len": 300, "win": 200, "step": 50},
    {"trim": 50, "min_len": 300, "win": 300, "step": 100},
    {"trim": 25, "min_len": 300, "win": 300, "step": 50},
]
FEATURE_SETS = {
    "basic": ["rms", "wl", "ratio_ext_flex"],
    "basic_plus": ["rms", "wl", "ratio_ext_flex", "..."],
}