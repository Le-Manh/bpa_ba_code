from __future__ import annotations

import json
from collections import Counter, deque # Counter is a hashable dict and deque a "faster list" at least for my usecase

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.base import clone
from sklearn.model_selection import GroupKFold, GridSearchCV

from auswertung_features.build_models import make_clustering_model, make_supervised_model

def sliding_vote_cm_from_dfpred(df_pred: pd.DataFrame, K: int, classes) -> np.ndarray:
    gcols = ["subject_id", "session", "trial_id"] # TODO doppelter Code
    y_true_all, y_pred_all = [], []

    for _, g in df_pred.groupby(gcols, sort=False):
        g = g.sort_values("widx")
        y_true = g["label"].to_numpy(int)
        y_hat  = g["pred"].to_numpy(int)

        y_hat_v = sliding_majority_vote(y_hat, K=K)
        if len(y_hat_v) == 0:
            continue
        y_true_v = y_true[K-1:]

        y_true_all.append(y_true_v)
        y_pred_all.append(y_hat_v)

    if not y_true_all:
        return np.zeros((len(classes), len(classes)), dtype=int)

    y_true_all = np.concatenate(y_true_all)
    y_pred_all = np.concatenate(y_pred_all)
    return confusion_matrix(y_true_all, y_pred_all, labels=list(classes))

def effective_latency_s(win: int, step: int, K: int, fs: int = 500) -> float:
    return win/fs + (K-1)*step/fs

def sliding_majority_vote(labels: np.ndarray, K: int) -> np.ndarray:
    if K <= 1:
        return labels.astype(int, copy=True)
    buf = deque(maxlen=K)
    out = []
    for y in labels:
        buf.append(int(y))
        if len(buf) == K:
            out.append(Counter(buf).most_common(1)[0][0])
    return np.asarray(out, dtype=int)

def sliding_vote_f1_from_dfpred(df_pred: pd.DataFrame, K: int, average="macro") -> float:
    gcols = ["subject_id", "session", "trial_id"] # TODO doppelter Code
    y_true_all, y_pred_all = [], []

    for _, g in df_pred.groupby(gcols, sort=False):
        g = g.sort_values("widx")
        y_true = g["label"].to_numpy(int)
        y_hat  = g["pred"].to_numpy(int)

        y_hat_v = sliding_majority_vote(y_hat, K=K)
        if len(y_hat_v) == 0:
            continue
        y_true_v = y_true[K-1:]

        y_true_all.append(y_true_v)
        y_pred_all.append(y_hat_v)

    if not y_true_all:
        return float("nan")

    y_true_all = np.concatenate(y_true_all)
    y_pred_all = np.concatenate(y_pred_all)
    return float(f1_score(y_true_all, y_pred_all, average=average, zero_division=0))

def outer_eval(feature_df, train_subjects, test_subjects, hand, base_cfg, params_prefixed, vote_K, classes=(0,1,2,3,4), return_cm = True):
    df = feature_df[feature_df["hand"] == hand]
    df_tr = df[df["subject_id"].isin(train_subjects)]
    df_te = df[df["subject_id"].isin(test_subjects)]
    if df_tr.empty or df_te.empty:
        return {"outer_window_f1": np.nan, "outer_sliding_f1": np.nan}

    feat_cols = [c for c in df.iloc[:,6:].columns]

    X_tr = df_tr[feat_cols].to_numpy(np.float32)
    y_tr = df_tr["label"].to_numpy(int)
    X_te = df_te[feat_cols].to_numpy(np.float32)
    y_te = df_te["label"].to_numpy(int)

    est = clone(make_supervised_model(base_cfg))
    est.set_params(**params_prefixed)   # params_prefixed enthält ggf. clf__...
    est.fit(X_tr, y_tr)
    y_hat = est.predict(X_te)

    outer_window_f1 = float(f1_score(y_te, y_hat, average="macro", zero_division=0))

    df_pred = df_te[["subject_id","session","trial_id","widx","label"]].copy()
    df_pred["pred"] = y_hat
    outer_sliding_f1 = float(sliding_vote_f1_from_dfpred(df_pred, K=vote_K))

    out = {"outer_window_f1": outer_window_f1, "outer_sliding_f1": outer_sliding_f1}

    if return_cm:
        cm = sliding_vote_cm_from_dfpred(df_pred, K=vote_K, classes=classes)
        out["cm_json"] = json.dumps(cm.tolist())

    return out

def topN_params_by_gridsearch(df_tr_hand, feat_cols, base_cfg, param_grid,
                              inner_splits=4, topN=5, n_jobs=-1):
    X = df_tr_hand[feat_cols].to_numpy(np.float32)
    y = df_tr_hand["label"].to_numpy(int)
    groups = df_tr_hand["subject_id"].astype(str).to_numpy()

    est = make_supervised_model(base_cfg)
    # Pipeline? -> clf__
    if isinstance(est, Pipeline):
        grid = {f"clf__{k}": v for k, v in param_grid.items()}
    else:
        grid = dict(param_grid)

    cv = GroupKFold(n_splits=inner_splits)
    gs = GridSearchCV(est, grid, scoring="f1_macro",
                      cv=cv, n_jobs=n_jobs, refit=False, verbose=0,
                      return_train_score=False)
    gs.fit(X, y, groups=groups)

    res = gs.cv_results_
    order = np.argsort(-np.asarray(res["mean_test_score"], float))

    top = []
    for idx in order[:min(topN, len(order))]:
        top.append({
            "params_prefixed": res["params"][idx],
            "mean_test_score": float(res["mean_test_score"][idx]),
            "std_test_score": float(res["std_test_score"][idx]),
        })
    return top

def inner_select_params_and_K_sliding(feature_df, subjects_train_outer, hand,
                                      base_cfg, top_paramsets, dcfg,
                                      K_candidates, inner_splits=4,
                                      fs=500, max_latency_s=1.0):

    df = feature_df[feature_df["hand"] == hand]
    df = df[df["subject_id"].isin(subjects_train_outer)]
    if df.empty:
        return None

    feat_cols = [c for c in df.iloc[:, 6:].columns]

    subjects = np.array(sorted(df["subject_id"].astype(str).unique()))
    cv = GroupKFold(n_splits=inner_splits)

    allowed_K = [K for K in K_candidates
                 if effective_latency_s(dcfg.win, dcfg.step, K, fs=fs) <= max_latency_s + 1e-12]
    if not allowed_K:
        allowed_K = [min(K_candidates)]

    best_ok = None  # (score, params_prefixed, K, mean_by_K)
    best_any = None

    for cand in top_paramsets:
        params_pref = cand["params_prefixed"]
        fold_scores_by_K = {K: [] for K in K_candidates}

        for tr_idx, va_idx in cv.split(subjects, groups=subjects):
            tr_sub = set(subjects[tr_idx]); va_sub = set(subjects[va_idx])

            df_tr = df[df["subject_id"].isin(tr_sub)]
            df_va = df[df["subject_id"].isin(va_sub)]
            if df_tr.empty or df_va.empty:
                continue

            X_tr = df_tr[feat_cols].to_numpy(np.float32)
            y_tr = df_tr["label"].to_numpy(int)
            X_va = df_va[feat_cols].to_numpy(np.float32)

            est = clone(make_supervised_model(base_cfg))
            est.set_params(**params_pref)
            est.fit(X_tr, y_tr)
            y_hat = est.predict(X_va)

            df_pred = df_va[["subject_id","session","trial_id","widx","label"]].copy()
            df_pred["pred"] = y_hat

            for K in K_candidates:
                fold_scores_by_K[K].append(sliding_vote_f1_from_dfpred(df_pred, K=K))

        mean_by_K = {K: float(np.nanmean(v)) if v else np.nan for K, v in fold_scores_by_K.items()}

        # best_any
        for K, s in mean_by_K.items():
            if np.isnan(s):
                continue
            if best_any is None or s > best_any[0]:
                best_any = (s, params_pref, K, mean_by_K)

        # best_ok
        for K in allowed_K:
            s = mean_by_K.get(K, np.nan)
            if np.isnan(s):
                continue
            if best_ok is None or s > best_ok[0]:
                best_ok = (s, params_pref, K, mean_by_K)

    if best_ok is None:
        best_ok = best_any
    if best_ok is None:
        return None

    s_ok, params_ok, K_ok, mean_ok = best_ok
    s_any, params_any, K_any, _ = best_any

    return {
        "inner_best_ok_score": float(s_ok),
        "inner_best_ok_K": int(K_ok),
        "inner_best_ok_latency_s": float(effective_latency_s(dcfg.win, dcfg.step, K_ok, fs=fs)),
        "inner_best_ok_params_json": json.dumps(params_ok),

        "inner_best_any_score": float(s_any),
        "inner_best_any_K": int(K_any),
        "inner_best_any_latency_s": float(effective_latency_s(dcfg.win, dcfg.step, K_any, fs=fs)),
        "inner_best_any_params_json": json.dumps(params_any),

        "inner_scores_by_K_json": json.dumps({str(k): float(v) for k, v in mean_ok.items()}),
    }