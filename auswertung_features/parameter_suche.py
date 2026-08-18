from __future__ import annotations

from collections import Counter, deque # Counter is a hashable dict and deque a "faster list" at least for my usecase
from pathlib import Path
import numpy as np
import pandas as pd
import json
import time
import tsfel
import os

from parameterraum import MODEL_SPACE, DATA_PARAM_LIST, ModelConfig, DataConfig, FEATURE_SET_LIBRARY

from plot_fn import plot_cm
from build_features import build_feature_table
from evaluation import effective_latency_s, topN_params_by_gridsearch, inner_select_params_and_K_sliding, outer_eval, sliding_majority_vote

from sklearn.model_selection import GroupKFold

# Sensor 2 ist Gegenseite (Extensor-Seite)
EXT_IDX = 2
FLEX_IDXS = [0, 1, 3]

def data_cfg_key(dcfg: DataConfig) -> str:
    return (f"trim={dcfg.trim}|minlen={dcfg.min_len}|win={dcfg.win}|step={dcfg.step}"
            f"|fs={dcfg.feature_set_name}|t={','.join(dcfg.time_feature_names)}|f={','.join(dcfg.freq_feature_names)}")

def build_data_cfgs(data_param_list, feature_set_library) -> list[DataConfig]:
    out: list[DataConfig] = []

    # param_list stabil sortieren, falls sie aus Filtern kommt
    data_param_list = sorted(
        data_param_list,
        key=lambda p: (p["trim"], p["min_len"], p["win"], p["step"])
    )

    # feature sets stabil sortieren nach Name
    for p in data_param_list:
        for fs_name in sorted(feature_set_library.keys()):
            fs = feature_set_library[fs_name]

            # Kanonisierung, damit Cache-Key stabil ist
            time_feats = tuple(sorted(fs.get("time", [])))
            freq_feats = tuple(sorted(fs.get("freq", [])))

            out.append(DataConfig(
                trim=p["trim"],
                min_len=p["min_len"],
                win=p["win"],
                step=p["step"],
                feature_set_name=fs_name,
                time_feature_names=time_feats,
                freq_feature_names=freq_feats,
            ))
    return out

def nested_cv_sliding_hybrid(
    meta: pd.DataFrame,
    data_cfgs: list[DataConfig],
    model_space_grids: dict,          # your NEW MODEL_SPACE with raw grids
    hands=("l", "r"),
    outer_splits=5,
    inner_splits=4,
    classes = (0,1,2,3,4),
    K_candidates=(1,3,5,7,9,11,13,15,17,19),
    fs: int = 500,
    max_latency_s: float = 1.0,
    topN: int = 5,
    n_jobs: int = -1,
    plot_per_outer_fold: bool = False,
):
    subjects_all = np.array(sorted(meta["subject_id"].astype(str).unique()))
    outer_cv = GroupKFold(n_splits=outer_splits)

    # Cache features per DataConfig
    tsfel_cfg = tsfel.get_features_by_domain(json_path="tsfel_conf.json")
    feature_cache: dict[str, pd.DataFrame] = {}

    results = []
    t0_all = time.perf_counter()
    units_total = outer_splits * len(hands)
    units_done = 0
    durations = []

    for outer_fold, (tr_idx, te_idx) in enumerate(outer_cv.split(subjects_all, groups=subjects_all), start=0):
        outer_train_sub = subjects_all[tr_idx].tolist()
        outer_test_sub  = subjects_all[te_idx].tolist()

        outer_train_set = set(outer_train_sub)
        outer_test_set  = set(outer_test_sub)
        t0_unit = time.perf_counter()
        for hand in hands:
            best = None
            best_score = -np.inf

            # ---- inner selection over data_cfg + model ----
            for dcfg in data_cfgs:
                k = data_cfg_key(dcfg)
                if k not in feature_cache:
                    if os.path.isfile(f"cache/feature_{k}.csv"):
                        feature_cache[k] = pd.read_csv(f"cache/feature_{k}.csv", index_col = 0,
                                                       dtype={"subject_id":str})
                    else:
                        feature_cache[k] = build_feature_table(meta=meta, data_cfg=dcfg, b_TSFEL=True,
                                                               tsfel_cfg=tsfel_cfg)
                        feature_cache[k].to_csv(f"cache/feature_{k}.csv")

                feat_df = feature_cache[k]
                df_tr_hand = feat_df[(feat_df["hand"] == hand) & (feat_df["subject_id"].isin(outer_train_set))]
                if df_tr_hand.empty:
                    continue

                feat_cols = [c for c in feat_df.iloc[:,6:].columns]

                # iterate model grids (supervised + ann)
                for model_type, models in model_space_grids.items():
                    if model_type not in ("supervised", "ann"):
                        continue

                    for model_name, param_grid in models.items():
                        # base cfg without params; params come from gs
                        base_cfg = ModelConfig(model_name=model_name, model_type=model_type, params=tuple())

                        # 1) GridSearchCV prescreen (window-level)
                        top_params = topN_params_by_gridsearch(
                            df_tr_hand, feat_cols, base_cfg, param_grid,
                            inner_splits=inner_splits, topN=topN, n_jobs=n_jobs
                        )

                        if not top_params:
                            continue

                        # 2) true inner selection by sliding-vote (A) over K
                        inner_sel = inner_select_params_and_K_sliding(
                            feature_df=feat_df,
                            subjects_train_outer=outer_train_sub,
                            hand=hand,
                            base_cfg=base_cfg,
                            top_paramsets=top_params,
                            dcfg=dcfg,
                            K_candidates=list(K_candidates),
                            inner_splits=inner_splits,
                            fs=fs,
                            max_latency_s=max_latency_s
                        )
                        if inner_sel is None:
                            continue

                        score = inner_sel["inner_best_ok_score"]
                        if score > best_score:
                            best_score = score
                            best = (dcfg, base_cfg, inner_sel)

            if best is None:
                results.append({
                    "outer_fold": outer_fold,
                    "hand": hand,
                    "outer_window_f1": np.nan,
                    "outer_sliding_f1": np.nan,
                    "best_inner_score": np.nan,
                    "best_model_name": None,
                })
                continue

            # ---- outer evaluation with best ----
            best_dcfg, best_base_cfg, inner_sel = best
            feat_df_best = feature_cache[data_cfg_key(best_dcfg)]

            params_ok = json.loads(inner_sel["inner_best_ok_params_json"])
            vote_K = int(inner_sel["inner_best_ok_K"])

            outer_scores = outer_eval(
                feature_df=feat_df_best,
                train_subjects=outer_train_set,
                test_subjects=outer_test_set,
                hand=hand,
                base_cfg=best_base_cfg,
                params_prefixed=params_ok,
                vote_K=vote_K,
                classes=classes
            )
            if plot_per_outer_fold:
                cm = np.array(json.loads(outer_scores["cm_json"]), dtype=int)
                title = (f"Winner outer{outer_fold} {hand} | {best_base_cfg.model_name} | "
                         f"{best_dcfg.feature_set_name} win{best_dcfg.win} step{best_dcfg.step} | "
                         f"K={vote_K}")

                out_path = (f"result_plots/winner_outer_folds/{hand}/"
                            f"outer{outer_fold}_{best_base_cfg.model_name}_{best_dcfg.feature_set_name}_K{vote_K}.svg")

                plot_cm(cm, classes=classes, out_path=out_path, title=title)

            results.append({
                "outer_fold": outer_fold,
                "hand": hand,

                "train_subjects": "|".join(sorted(map(str, outer_train_sub))),
                "test_subjects":  "|".join(sorted(map(str, outer_test_sub))),

                # selected data cfg
                "best_feature_set": best_dcfg.feature_set_name,
                "best_win": best_dcfg.win,
                "best_step": best_dcfg.step,
                "best_trim": best_dcfg.trim,
                "best_min_len": best_dcfg.min_len,

                # selected model
                "best_model_type": best_base_cfg.model_type,
                "best_model_name": best_base_cfg.model_name,

                # inner diag
                "best_inner_score": float(best_score),
                **inner_sel,  # includes K, latency, best_any, K-curve JSON, params JSON

                # outer scores
                **outer_scores,

                # helpful to log the operational latency
                "best_ok_latency_s": float(effective_latency_s(best_dcfg.win, best_dcfg.step, vote_K, fs=fs)),
            })
            units_done += 1
            dt = time.perf_counter() - t0_unit
            durations.append(dt)

            avg = sum(durations) / len(durations)
            eta = avg * (units_total - units_done)
            elapsed = time.perf_counter() - t0_all

            print(f"[Progress] fold {outer_fold + 1}/{outer_splits}, hand={hand} | "
                  f"unit {units_done}/{units_total} | "
                  f"dt={dt / 60:.1f} min | elapsed={elapsed / 60:.1f} min | ETA≈{eta / 60:.1f} min")

    return pd.DataFrame(results)

def main():
    meta_path = Path("meta.csv")                # bleibt im repo/arbeitspfad

    meta = pd.read_csv(meta_path) # Einlesen von den metadaten
    # Minimale Checks
    for col in ["rel_path", "subject_id", "hand"]: #Kontrolle ob rel_path, subject_id und hand existiert
        if col not in meta.columns:
            raise ValueError(f"meta.csv missing column: {col}")

    #MODEL_CFGS = build_model_cfgs(MODEL_SPACE)

    DATA_CFGS = list(dict.fromkeys(build_data_cfgs(DATA_PARAM_LIST, FEATURE_SET_LIBRARY)))
    #df_nested = nested_cv(meta, MODEL_CFGS,DATA_CFGS, outer_splits=5, inner_splits=4, plot_per_outer_fold=False)
    df_nested = nested_cv_sliding_hybrid(
        meta=meta,
        data_cfgs=DATA_CFGS,
        model_space_grids=MODEL_SPACE,  # now raw grid dicts
        outer_splits=5,
        inner_splits=4,
        classes=(0, 1, 2, 3, 4),
        topN=5,
        n_jobs=-1,
        K_candidates=(1, 3, 5, 7, 9, 11, 13, 15, 17, 19),
        plot_per_outer_fold=True,
    )
    df_nested.to_csv("results/sliding/results_sliding.csv", index=False)

    #zusammenfassen
    df_nested_summary = (df_nested
                         .dropna(subset=["outer_sliding_f1"])
                         .groupby(["hand"])["outer_sliding_f1"]
                         .agg(["mean", "std", "count"])
                         .reset_index())
    df_nested_summary.to_csv("results/sliding/results_sliding_summary.csv", index=False)

    # Gewinner-Häufigkeiten
    model_freq = (df_nested
                  .groupby("hand")["best_model_name"]
                  .value_counts()
                  .rename("n") # wie oft das Model mit der Configuration vorkommt
                  .reset_index())
    model_freq.to_csv("results/sliding/results_sliding_winner_models.csv", index=False)

    ''' not used
    fs_freq = (df_nested
               .groupby("hand")["best_feature_set"]
               .value_counts()
               .rename("n") # wie oft das Featureset in jeder Hand vorkommt
               .reset_index())
    fs_freq.to_csv("results_nested_winner_featuresets.csv", index=False)
    '''

    # Parameterhäufigkeiten (Window/Step/Trim/MinLen)
    param_freq = (df_nested
                  .groupby(["hand", "best_win", "best_step", "best_trim", "best_min_len"])
                  .size()
                  .rename("n")
                  .reset_index()
                  .sort_values(["hand", "n"], ascending=[True, False]))
    param_freq.to_csv("results/sliding/results_sliding_winner_params.csv", index=False)


if __name__ == "__main__":
    main()