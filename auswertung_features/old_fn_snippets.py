import pandas as pd
import numpy as np

from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GroupKFold
from sklearn.base import clone

from parameterraum import ModelConfig, DataConfig
from build_features import build_feature_table
from plot_fn import plot_cm
from build_models import make_clustering_model, make_supervised_model


def majority_mapping(cluster_ids: np.ndarray, y: np.ndarray) -> dict[int, int]:
    mapping = {}
    for cid in np.unique(cluster_ids):
        ys = y[cluster_ids == cid]
        mapping[int(cid)] = int(Counter(ys).most_common(1)[0][0])
    return mapping

def map_clusters(cluster_ids: np.ndarray, mapping: dict[int,int]) -> np.ndarray:
    default = next(iter(mapping.values()))
    return np.array([mapping.get(int(c), default) for c in cluster_ids], dtype=int)

def validate_model_cfg(cfg: ModelConfig):
    if cfg.model_type in ("supervised", "ann"):
        if cfg.model_name not in MODELS_SUPERVISED:
            raise KeyError(f"Unknown supervised/ann model: {cfg.model_name}")
    elif cfg.model_type == "clustering":
        if cfg.model_name not in MODELS_CLUSTERING:
            raise KeyError(f"Unknown clustering model: {cfg.model_name}")
    else:
        raise KeyError(f"Unknown model_type: {cfg.model_type}")

def trial_level_vote(df_pred: pd.DataFrame) -> pd.DataFrame:
    """
    df_pred enthält: subject_id, session, trial_id, label (true), pred (window)
    Gibt trial-level Pred via Majority Vote zurück.
    """
    gcols = ["subject_id", "session", "trial_id"]
    out = []
    for k, g in df_pred.groupby(gcols, sort=False):
        true_label = int(g["label"].iloc[0])
        # Majority vote
        pred_label = int(g["pred"].value_counts().idxmax())
        out.append({
            "subject_id": k[0],
            "session": k[1],
            "trial_id": k[2],
            "true": true_label,
            "pred": pred_label
        })
    return pd.DataFrame(out)

def eval_holdout(feature_df: pd.DataFrame,
                 train_subjects: set[str],
                 test_subjects: set[str],
                 hand: str,
                 model_cfg: ModelConfig,
                 return_trials: bool = False) -> float | tuple[float, pd.DataFrame]:
    df = feature_df[feature_df["hand"] == hand].copy()
    df_tr = df[df["subject_id"].isin(train_subjects)]
    df_te = df[df["subject_id"].isin(test_subjects)]

    if df_tr.empty or df_te.empty:
        if return_trials:
            return float("nan"), pd.DataFrame(columns=["subject_id", "session", "trial_id", "true", "pred"])
        return float("nan")

    feat_cols = [c for c in df.columns if c.startswith("t_") or c.startswith("f_")]

    X_tr = df_tr[feat_cols].to_numpy(np.float32)
    y_tr = df_tr["label"].to_numpy(int)
    X_te = df_te[feat_cols].to_numpy(np.float32)

    # ---- supervised / ann ----
    if model_cfg.model_type in ("supervised", "ann"):
        model = clone(make_supervised_model(model_cfg))
        # print(f"Training model: {model_cfg.model_name} mit {model_cfg.params}")
        model.fit(X_tr, y_tr)
        y_pred_win = model.predict(X_te)

    # ---- clustering ----
    elif model_cfg.model_type == "clustering":
        spec = MODELS_CLUSTERING[model_cfg.model_name]
        # print(f"Training: {model_cfg.model_name} mit {model_cfg.params}")
        clusterer = clone(make_clustering_model(model_cfg))

        if spec.needs_scaling:
            scaler = StandardScaler()
            X_tr_s = scaler.fit_transform(X_tr)  # fit nur auf train!
            X_te_s = scaler.transform(X_te)
        else:
            X_tr_s, X_te_s = X_tr, X_te

        # cluster fit
        clusterer.fit(X_tr_s)

        # train cluster ids (für mapping)
        if hasattr(clusterer, "predict"):
            cl_tr = clusterer.predict(X_tr_s)
            cl_te = clusterer.predict(X_te_s)
        else:
            # Fallback (bei manchen Clusterern gibt es kein predict)
            cl_tr = clusterer.fit_predict(X_tr_s)
            cl_te = clusterer.fit_predict(X_te_s)

        mapping = majority_mapping(cl_tr, y_tr)
        y_pred_win = map_clusters(cl_te, mapping)

    else:
        raise ValueError(f"Unknown model_type: {model_cfg.model_type}")

    # ---- window -> trial aggregation ----
    df_pred = df_te[["subject_id", "session", "trial_id", "label"]].copy()
    df_pred["pred"] = y_pred_win

    trial_df = trial_level_vote(df_pred)    # columns: subject_id, session, trial_id, true, pred
    score = float(f1_score(trial_df["true"], trial_df["pred"], average="macro", zero_division=0))
    if return_trials:
        return score, trial_df
    return score

def inner_cv_score(feature_df: pd.DataFrame,
                   subjects_train_outer: list[str],
                   hand: str,
                   model: ModelConfig,
                   n_splits: int = 4) -> float:
    subjects = np.array(subjects_train_outer)
    cv = GroupKFold(n_splits=n_splits)

    scores = []
    for tr_idx, va_idx in cv.split(subjects, groups=subjects):
        tr_sub = set(subjects[tr_idx])
        va_sub = set(subjects[va_idx])

        s = eval_holdout(feature_df, tr_sub, va_sub, hand=hand, model_cfg=model)
        scores.append(s)

    return float(np.nanmean(scores))

def nested_cv(meta: pd.DataFrame,
              model_cfgs: list[ModelConfig],
              data_cfgs: list[DataConfig],
              hands=("l","r"),
              outer_splits=5,
              inner_splits=4,
              classes = (0, 1, 2, 3, 4),
              plot_per_outer_fold: bool = False):

    subjects_all = np.array(sorted(meta["subject_id"].astype(str).unique()))
    outer_cv = GroupKFold(n_splits=outer_splits)

    results = []

    # Cache: pro data_cfg die Feature-Tabelle einmal bauen
    feature_cache: dict[DataConfig, pd.DataFrame] = {}
    # Aggregierte CMs pro Hand über alle Outer-Folds
    cm_total = {hand: np.zeros((len(classes), len(classes)), dtype=int) for hand in hands}

    for outer_fold, (tr_idx, te_idx) in enumerate(outer_cv.split(subjects_all, groups=subjects_all)):
        outer_train_sub = subjects_all[tr_idx].tolist()
        outer_test_sub  = subjects_all[te_idx].tolist()

        outer_train_set = set(outer_train_sub)
        outer_test_set  = set(outer_test_sub)

        for hand in hands:
            # 1) Inner selection: best (data_cfg, model) on outer-train
            best = None
            best_score = -1.0

            for dcfg in data_cfgs:
                if dcfg not in feature_cache:
                    feature_cache[dcfg] = build_feature_table(meta=meta, data_cfg=dcfg)

                feat_df = feature_cache[dcfg]

                for model in model_cfgs:
                    score = inner_cv_score(
                        feat_df,
                        subjects_train_outer=outer_train_sub,
                        hand=hand,
                        model=model,
                        n_splits=inner_splits
                    )

                    if score > best_score:
                        best_score = score
                        best = (dcfg, model)

            if best is None:
                # sollte praktisch nicht passieren, aber robust bleiben
                results.append({
                    "outer_fold": outer_fold,
                    "hand": hand,
                    "best_model": None,
                    "best_feature_set": None,
                    "best_win": None,
                    "best_step": None,
                    "best_trim": None,
                    "best_min_len": None,
                    "best_inner_score": None,
                    "outer_score": None,
                })
                continue

            # 2) Outer evaluation: evaluate best on outer-test
            best_dcfg, best_model = best
            feat_df_best = feature_cache[best_dcfg]
            outer_score, trial_df = eval_holdout(
                feat_df_best,
                train_subjects=outer_train_set,
                test_subjects=outer_test_set,
                hand=hand,
                model_cfg=best_model,
                return_trials = True
            )

            planned_test = list(map(str, outer_test_sub))
            planned_train = list(map(str, outer_train_sub))
            effective_test = sorted(trial_df["subject_id"].astype(str).unique().tolist())

            missing = sorted(set(planned_test) - set(effective_test))  # Test-Subjects ohne Trials (für diese Hand/Config)

            cm = confusion_matrix(trial_df["true"], trial_df["pred"], labels=list(classes))
            cm_total[hand] += cm

            if plot_per_outer_fold:
                title = (f"NestedCV outer{outer_fold} {hand} | {best_model} | "
                         f"{best_dcfg.feature_set_name} win{best_dcfg.win} step{best_dcfg.step} "
                         f"trim{best_dcfg.trim} minlen{best_dcfg.min_len}")
                out_path = (f"result_plots/nested/outer_folds/"
                            f"{hand}/outer{outer_fold}_{best_model}_{best_dcfg.feature_set_name}_"
                            f"win{best_dcfg.win}_step{best_dcfg.step}.svg")
                plot_cm(cm, classes, out_path, title)

            results.append({
                "outer_fold": outer_fold,
                "hand": hand,
                "test_subjects":"|".join(sorted(planned_test)),
                "train_subjects":"|".join(sorted(planned_train)),
                "best_model": best_model,
                "best_feature_set": best_dcfg.feature_set_name,
                "best_win": best_dcfg.win,
                "best_step": best_dcfg.step,
                "best_trim": best_dcfg.trim,
                "best_min_len": best_dcfg.min_len,
                "best_inner_score": best_score,
                "outer_score": outer_score,
                "n_trials_outer": int(len(trial_df)),
                "test_subjects_missing": ";".join(sorted(missing)),
                "n_test_subjects_missing": len(missing),
            })
    results_df = pd.DataFrame(results)
    # Gesamt-CM plotten
    for hand in hands:
        out_path = f"result_plots/cm_total_{hand}.svg"
        title = f"NestedCV total CM ({hand}) | outer_splits={outer_splits}"
        plot_cm(cm_total[hand], classes, out_path, title)

    return results_df