# loso_windowed_blockfeat.py
# Windowed LOSO evaluation:
# - TS is windowed to fixed length T with stride
# - features are block-global (from your TSFEL table) and replicated for each window
# - evaluation is block-level via mean-softmax aggregation

import os
import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix


# ----------------------------
# 0) Your feature function hook
# ----------------------------
# You already have tsfel_feature(meta_df, step=0) in your project.
# Import it here or paste your implementation.
#
# Example:
# from ANN.LOSO_Run_2_input import tsfel_feature
#
# For this template, we assume it's in scope as tsfel_feature(meta_df, step=0).


# ----------------------------
# 1) Windowing
# ----------------------------
def block_to_windows_postpad(x_ts: np.ndarray, T: int, stride: int):
    """
    x_ts: (L,4)
    Returns list of windows (T,4).
    Behavior matches your earlier padding style:
      - if L < T: post-pad with zeros
      - if L >= T: sliding windows of length T
      - optional: last window is forced to include the end of the block
    """
    x_ts = np.asarray(x_ts, np.float32)
    L = x_ts.shape[0]

    if L <= T:
        w = np.zeros((T, 4), np.float32)
        w[:L, :] = x_ts
        return [w]

    wins = []
    for start in range(0, L - T + 1, stride):
        wins.append(x_ts[start:start + T, :])
        last_added = start

    # force last window to not "miss" the end
    last_start = L - T
    if last_added != last_start:
        wins.append(x_ts[last_start:last_start + T])

    return wins


# ----------------------------
# 2) Dataset builder: windowed TS + block features replicated
# ----------------------------
def windows_to_fixed_tensor(windows, W_max: int, T: int):
    """windows: list of (T,4)"""
    wlen = len(windows)
    if wlen > W_max:
        windows = windows[:W_max]   # oder smarter auswählen
        wlen = W_max

    out = np.zeros((W_max, T, 4), np.float32)
    if wlen > 0:
        out[:wlen] = np.stack(windows, axis=0).astype(np.float32)

    return out, np.int32(wlen)

def compute_W_max(L_max: int, T: int, stride: int):
    """maximale Fensterzahl für deine 'force last window'-Logik"""
    if L_max <= T:
        return 1
    starts = list(range(0, L_max - T + 1, stride))
    last_start = L_max - T
    if starts[-1] != last_start:
        return len(starts) + 1
    return len(starts)

def make_xy_from_meta_windowed_blockfeat(meta_df, dict_block, feat_table, T: int, stride: int):
    """
    meta_df: DataFrame with columns at least: subject_id, block_id
    dict_block[block_id] -> (x_ts, y_label), x_ts shape (L,4)
    feat_table: DataFrame such that feat_table.iloc[block_id, 6:] returns 1D features for that block

    Returns:
      X_ts_win: (Nwin, T, 4)
      X_feat_win: (Nwin, F)
      y_win: (Nwin,)
      subjects_win: (Nwin,)
      block_ids_win: (Nwin,)
    """
    X_ts_list, X_feat_list, y_list, subjects_list, block_ids_list = [], [], [], [], []

    bids = meta_df["block_id"].to_numpy()
    subjs = meta_df["subject_id"].to_numpy()

    for bid, subj in zip(bids, subjs):
        x_ts, y = dict_block[int(bid)]
        x_ts = np.asarray(x_ts, dtype=np.float32)

        # block-global features (replicated per window)
        fb = feat_table.iloc[int(bid), 6:]
        x_feat = np.asarray(fb, dtype=np.float32)

        windows = block_to_windows_postpad(x_ts, T=T, stride=stride)

        for w in windows:
            X_ts_list.append(w)
            X_feat_list.append(x_feat)
            y_list.append(int(y))
            subjects_list.append(subj)
            block_ids_list.append(int(bid))

    X_ts = np.stack(X_ts_list, axis=0).astype(np.float32)
    X_feat = np.stack(X_feat_list, axis=0).astype(np.float32)
    y = np.array(y_list, dtype=np.int64)
    subjects = np.array(subjects_list)
    block_ids = np.array(block_ids_list, dtype=np.int64)

    return X_ts, X_feat, y, subjects, block_ids

def gen_meta_windowed_blocks(meta_df, dict_block, feat_table, T: int, stride: int, W_max: int):
    bids = meta_df["block_id"].to_numpy()
    subjs = meta_df["subject_id"].to_numpy()

    for bid, subj in zip(bids, subjs):
        bid_i = int(bid)
        x_ts, y = dict_block[bid_i]
        x_ts = np.asarray(x_ts, dtype=np.float32)

        fb = feat_table.iloc[bid_i, 6:]              # block-globale Features
        x_feat = np.asarray(fb, dtype=np.float32)

        windows = block_to_windows_postpad(x_ts, T=T, stride=stride)
        ts_win, wlen = windows_to_fixed_tensor(windows, W_max=W_max, T=T)

        # Output: (inputs_dict, label) – optional kannst du subj/bid extra ausgeben
        yield (
            {
                "ts": ts_win,                        # (W_max, T, 4)
                "feat": x_feat,                      # (F,)
                "wlen": wlen,                        # scalar
            },
            np.int32(y)
        )

# ----------------------------
# 3) Mean-Softmax aggregation per block (offline button use-case)
# ----------------------------
def aggregate_mean_softmax(prob_win: np.ndarray, block_ids_win: np.ndarray):
    """
    prob_win: (Nwin, C) softmax outputs
    block_ids_win: (Nwin,) block id for each window sample

    Returns:
      uniq_bids: (Nb,)
      prob_block: (Nb, C) mean-softmax
      y_pred_block: (Nb,) argmax over mean-softmax
    """
    prob_win = np.asarray(prob_win)
    block_ids_win = np.asarray(block_ids_win)

    uniq_bids = np.unique(block_ids_win)
    prob_block = np.zeros((len(uniq_bids), prob_win.shape[1]), dtype=np.float32)

    for i, bid in enumerate(uniq_bids):
        mask = (block_ids_win == bid)
        prob_block[i] = prob_win[mask].mean(axis=0)

    y_pred_block = np.argmax(prob_block, axis=1).astype(np.int64)
    return uniq_bids, prob_block, y_pred_block


# ----------------------------
# 4) Runtime estimator: estimate number of windows (cheap preview)
# ----------------------------
def estimate_windows_for_lengths(lengths, T: int, stride: int, force_last=True):
    """
    lengths: list/array of L for each block
    Returns total windows, avg windows per block, and per-block window counts
    """
    counts = []
    for L in lengths:
        L = int(L)
        if L <= T:
            counts.append(1)
            continue

        n = 1 + (L - T) // stride  # windows hit by regular stepping
        if force_last:
            last_start = L - T
            if (last_start % stride) != 0:
                n += 1
        counts.append(n)

    counts = np.array(counts, dtype=np.int64)
    return int(counts.sum()), float(counts.mean()), counts


def estimate_fold_window_counts(meta_df, dict_block, T: int, stride: int):
    lengths = [dict_block[int(bid)][0].shape[0] for bid in meta_df["block_id"].to_numpy()]
    total, avg, counts = estimate_windows_for_lengths(lengths, T=T, stride=stride, force_last=True)
    return {
        "n_blocks": len(lengths),
        "total_windows_est": total,
        "avg_windows_per_block_est": avg,
        "min_L": int(np.min(lengths)) if lengths else None,
        "max_L": int(np.max(lengths)) if lengths else None,
    }


# ----------------------------
# 5) LOSO for one (T,stride)
# ----------------------------
def run_loso_windowed(
    meta, dict_block, tsfel_feature_fn, build_model_fn,
    T=500, stride=500, L_max = 2000,
    epochs=120, batch_size=32, verbose=0, seed=42,
    patience=10
):
    """
    tsfel_feature_fn(meta_df, step=0) -> feature table (DataFrame)
    build_model_fn(T=..., F=...) -> compiled keras model
      IMPORTANT: build_model_fn must use Input(shape=(T,4)).

    Returns df_folds with block-level metrics per fold.
    """
    tf.keras.utils.set_random_seed(seed)
    groups = meta["subject_id"].to_numpy()
    logo = LeaveOneGroupOut()

    fold_metrics = []
    W_max = compute_W_max(L_max, T, stride)

    for fold, (train_idx, val_idx) in enumerate(logo.split(meta, groups=groups)):
        tf.keras.backend.clear_session()

        meta_tr = meta.iloc[train_idx].reset_index(drop=True)
        meta_va = meta.iloc[val_idx].reset_index(drop=True)

        # Feature tables global
        feat_global = tsfel_feature_fn(meta)

        feat_cols = feat_global.columns[6:]
        Xf_tr = feat_global.loc[meta_tr["block_id"].astype(int), feat_cols].to_numpy()

        # Scale features (fit only on training windows)
        scaler = StandardScaler()
        Xf_tr = scaler.fit(Xf_tr)

        X_all = feat_global.loc[:, feat_cols].to_numpy(np.float32)
        X_all_scaled = scaler.transform(X_all)
        feat_table_scaled = feat_global.copy()
        feat_table_scaled.loc[:, feat_cols] = X_all_scaled

        output_signature = (
            {
                "ts": tf.TensorSpec(shape=(W_max, T, 4), dtype=tf.float32),
                "feat": tf.TensorSpec(shape=(Xf_tr.shape[1],), dtype=tf.float32),
                "wlen": tf.TensorSpec(shape=(), dtype=tf.int32),
            },
            tf.TensorSpec(shape=(), dtype=tf.int32)  # sparse label
        )

        ds_tr = tf.data.Dataset.from_generator(
            lambda: gen_meta_windowed_blocks(meta_tr, dict_block, feat_table_scaled, T, stride, W_max),
            output_signature=output_signature
        )

        ds_tr = ds_tr.shuffle(2048).batch(32).prefetch(tf.data.AUTOTUNE)
        # Build model with fixed T
        model = build_model_fn(W=W_max,T=T,F=Xf_tr.shape[1])

        es = tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=patience, restore_best_weights=True
        )
        rlr = tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=max(2, patience // 2), min_lr=1e-6
        )

        hist = model.fit(ds_tr,
            validation_data=({"ts": Xts_va, "feat": Xf_va}, y_va),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[es, rlr],
            verbose=verbose,
            shuffle=True
        )
        """"
        Nva_shape = Xf_va.shape
        zero_ts = np.zeros(Nva_shape, dtype=np.float32)
        """
        prob_win = model.predict({"ts": Xts_va, "feat": Xf_va}, verbose=0)  # (Nwin, C)

        # Aggregate to block-level
        uniq_bids, prob_block, y_pred_block = aggregate_mean_softmax(prob_win, bid_va)
        y_true_block = np.array([int(dict_block[int(bid)][1]) for bid in uniq_bids], dtype=np.int64)

        acc = accuracy_score(y_true_block, y_pred_block)
        f1m = f1_score(y_true_block, y_pred_block, average="macro")
        cm = confusion_matrix(y_true_block, y_pred_block)

        subject_left_out = meta_va["subject_id"].unique()
        subject_left_out = subject_left_out[0] if len(subject_left_out) == 1 else subject_left_out.tolist()

        fold_metrics.append({
            "fold": fold,
            "left_out_subject": subject_left_out,
            "T": int(T),
            "stride": int(stride),
            "n_val_blocks": int(len(uniq_bids)),
            "n_val_windows": int(len(y_va)),
            "best_epoch": int(np.argmin(hist.history["val_loss"]) + 1) if "val_loss" in hist.history else None,
            "val_acc_block": float(acc),
            "val_macro_f1_block": float(f1m),
            "confusion_matrix": cm,  # keep if you want; else remove (not JSON-friendly)
        })

        print(f"Fold {fold:02d} | subj {subject_left_out} | "
              f"blocks={len(uniq_bids)} windows={len(y_va)} | "
              f"acc_block={acc:.3f} | macroF1_block={f1m:.3f}")

    return pd.DataFrame(fold_metrics)


# ----------------------------
# 6) Grid search runner + summary
# ----------------------------
def summarize_results(df_runs: pd.DataFrame):
    g = df_runs.groupby(["T", "stride"], as_index=False).agg(
        f1_mean=("val_macro_f1_block", "mean"),
        f1_std =("val_macro_f1_block", "std"),
        acc_mean=("val_acc_block", "mean"),
        acc_std =("val_acc_block", "std"),
        n_blocks_mean=("n_val_blocks", "mean"),
        n_windows_mean=("n_val_windows", "mean"),
        best_epoch_mean=("best_epoch", "mean"),
    )
    g = g.sort_values(["f1_mean", "acc_mean"], ascending=False).reset_index(drop=True)
    return g


def run_window_grid_loso(
    meta, dict_block, tsfel_feature_fn, build_model_fn,
    grid, L_max=2000,
    epochs=120, batch_size=32, verbose=0, seed=42, patience=10
):
    all_runs = []
    for (T, stride) in grid:
        print(f"\n=== Running LOSO for T={T}, stride={stride} (opt: macroF1_block) ===")
        df_folds = run_loso_windowed(
            meta, dict_block,
            tsfel_feature_fn=tsfel_feature_fn,
            build_model_fn=build_model_fn,
            L_max=L_max,
            T=T, stride=stride,
            epochs=epochs, batch_size=batch_size, verbose=verbose,
            seed=seed, patience=patience
        )
        all_runs.append(df_folds)

    df_folds_all = pd.concat(all_runs, axis=0, ignore_index=True)
    df_summary = summarize_results(df_folds_all)
    return df_folds_all, df_summary


# ----------------------------
# 7) Suggested grids for your scenario (500 Hz, 1-2 s blocks)
# ----------------------------
def suggested_grids():
    grid_round1 = [
        (250, 250),  # 0.5s, no overlap
        (500, 500),  # 1.0s, no overlap
        (750, 750),  # 1.5s, no overlap
    ]
    # second round: Testing if teh amount of windows is part of why it works so well
    grid_round2_ensembleeffect = [
        (500, 250),
        (750, 375),  # 50% overlap
    ]
    grid_round_feat_ts_test = [
        (500, 250),
    ]
    grid_round2_compute = [
        (250, 250),
        (500, 250),
        (500, 500),
    ]
    return grid_round1, grid_round_feat_ts_test, grid_round2_ensembleeffect, grid_round2_compute


# ----------------------------
# 8) Notes on build_model
# ----------------------------
"""
Your build_model MUST accept T and use fixed input shape:

def build_model(T, F=624, ...):
    ts_inputs = tf.keras.layers.Input(shape=(T,4), name="ts")  # fixed T
    ...
    model = tf.keras.Model(inputs=[ts_inputs, feat_in], outputs=outputs)
    ...

Then pass build_model as build_model_fn.
"""
