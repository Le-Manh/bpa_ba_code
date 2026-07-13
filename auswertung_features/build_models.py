from typing import Any, Iterable


from parameterraum import ModelConfig
from models import MODELS_SUPERVISED, MODELS_CLUSTERING

from sklearn.model_selection import ParameterGrid
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

def make_supervised_model(model_cfg: ModelConfig):
    spec = MODELS_SUPERVISED[model_cfg.model_name]
    base = spec.make(**model_cfg.params_dict())
    if spec.needs_scaling:
        return Pipeline([("scaler", StandardScaler()), ("clf", base)])
    return base

def make_clustering_model(model_cfg: ModelConfig):
    spec = MODELS_CLUSTERING[model_cfg.model_name]
    return spec.make(**model_cfg.params_dict())

def build_model_cfgs(model_space: dict,
                    *,
                    validate_names: bool = True,
                    validate_params_by_instantiation: bool = False) -> list[ModelConfig]:
    allowed_types = {"supervised", "ann", "clustering"}
    cfgs: list[ModelConfig] = []

    for model_type, models in model_space.items():
        if model_type not in allowed_types:
            raise ValueError(f"Unknown model_type '{model_type}'. Allowed: {sorted(allowed_types)}")
        for model_name, params_obj in models.items():
            # --- name validation against registries ---
            if validate_names:
                if model_type in ("supervised", "ann"):
                    if model_name not in MODELS_SUPERVISED:
                        raise KeyError(f"Unknown model '{model_name}' for type '{model_type}'")
                elif model_type == "clustering":
                    if model_name not in MODELS_CLUSTERING:
                        raise KeyError(f"Unknown clustering model '{model_name}'")
            for params in iter_param_dicts(params_obj):
                cfg = ModelConfig(
                    model_name=model_name,
                    model_type=model_type,
                    params=params_to_tuple(params),
                )
                # --- check param names by instantiating model object ---
                if validate_params_by_instantiation:
                    try:
                        if model_type in ("supervised", "ann"):
                            _ = make_supervised_model(cfg)
                        else:
                            _ = make_clustering_model(cfg)
                    except TypeError as e:
                        raise TypeError(
                            f"Bad params for {model_type}/{model_name}: {params}\nOriginal: {e}"
                        ) from e

                cfgs.append(cfg)

    return cfgs

def iter_param_dicts(obj) -> Iterable[dict[str, Any]]:
    # erlaubt: list[dict], ParameterGrid, tuple/list leere dicts, etc.
    if obj is None:
        yield {}
    elif isinstance(obj, ParameterGrid):
        yield from obj
    else:
        # z.B. list[dict]
        yield from obj

def params_to_tuple(params: dict[str, Any]) -> tuple[tuple[str, Any], ...]:
    return tuple(sorted(params.items(), key=lambda kv: kv[0]))