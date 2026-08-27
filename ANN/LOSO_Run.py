# LOSO cross-validation template for Keras (2-input model) + subject-wise reporting
# Assumptions:
# - meta: pandas DataFrame with columns: subject_id, hand, block_id (one row = one sample/block)
# - dict_block[block_id] -> (x_ts, y_label) where
#     x_ts has shape (T, 4) (T may vary per sample)
#     y_label is int in {0,1,2,3,4}
# - You already have a working build_model() that returns a compiled Keras model
#
# Notes:
# - If T varies, simplest is padding + Masking OR use ragged tensors.
#   Below uses padding to max length inside each fold for simplicity.

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import tsfel
import os

from auswertung_features.build_features import split_into_label_blocks, load_session
from auswertung_features.parameterraum import DataConfig
from auswertung_features.build_features import build_feature_table
from auswertung_features.parameter_suche import data_cfg_key

# -----------------------------
# 1) Helpers: data extraction
# -----------------------------
def make_xy_from_meta(meta_df, dict_block, pad_to=None):
    """Returns (X_ts, X_feat, y, subjects) for a given meta_df.
       If you don't use X_feat here, adapt accordingly.

       pad_to: int or None. If int, pad all time series to pad_to length.
               If None, pad to max length in meta_df.
    """
    X_ts_list = []
    X_feat_list = []
    y_list = []
    subjects = meta_df["subject_id"].to_numpy()
    X_feat = tsfel_feature()

    # Collect ts + labels
    lengths = []
    for bid in meta_df["block_id"].to_numpy():
        x_ts, y = dict_block[int(bid)]
        X_ts_list.append(x_ts.astype(np.float32))
        fb = X_feat.iloc[int(bid),6:]
        X_feat_list.append(np.asarray(fb, dtype=np.float32))
        y_list.append(int(y))
        lengths.append(x_ts.shape[0])

    y = np.array(y_list, dtype=np.int64)

    # Pad sequences (T may vary)
    if pad_to is None:
        pad_to = int(np.max(lengths))

    # Pad with zeros at end
    X_ts = np.zeros((len(X_ts_list), pad_to, 4), dtype=np.float32)
    for i, x in enumerate(X_ts_list):
        T = min(x.shape[0], pad_to)
        X_ts[i, :T, :] = x[:T, :]

    X_feat = np.stack(X_feat_list, axis=0).astype(np.float32)

    return X_ts, X_feat, y, subjects

feature_cache: dict[str, pd.DataFrame] = {} # global as cache

def tsfel_feature(win: int=0, step: int=50, feature_set_name="default_tsfel"):
    tsfel_cfg = tsfel.get_features_by_domain()#json_path="../auswertung_features/tsfel_conf.json")
    dcfg = DataConfig(
        trim=0,
        min_len=win,
        win=win, # feeding the feature table the whole sequence if win = 0. To feed sth different win should be the same as min_len. TSFEL can't work with different win lengths
        step=step, # arbitrary value. It should be the same as stride but if we take the whole sequence, stride may be not defined even though we wouldn't use it
        feature_set_name= feature_set_name
    )

    k = data_cfg_key(dcfg)
    if k not in feature_cache:
        if os.path.isfile(f"../auswertung_features/cache/feature_{k}.csv"):
            feature_cache[k] = pd.read_csv(f"../auswertung_features/cache/feature_{k}.csv", index_col = 0, dtype={"subject_id":str})
        else:
            feature_cache[k] = build_feature_table(meta=meta, data_cfg=dcfg, tsfel_cfg=tsfel_cfg)
            feature_cache[k].to_csv(f"../auswertung_features/cache/feature_{k}.csv")
    return feature_cache[k]

# -----------------------------
# 2) Model factory
# -----------------------------
def build_model(F=624, wd=1e-3, initializer="he_normal", lr=1e-3):
    init = tf.keras.initializers.get(initializer)

    ts_inputs = tf.keras.layers.Input(shape=(None, 4), name="ts")
    x = tf.keras.layers.Conv1D(
        8, 7, padding="same", activation="leaky_relu",
        kernel_initializer=init,
        kernel_regularizer=tf.keras.regularizers.l2(wd)
    )(ts_inputs)
    x = tf.keras.layers.SpatialDropout1D(0.2)(x)
    x = tf.keras.layers.Conv1D(
        16, 5, padding="same", activation="relu",
        kernel_regularizer=tf.keras.regularizers.l2(wd)
    )(x)
    x = tf.keras.layers.GlobalAveragePooling1D()(x)
    x = tf.keras.layers.Dropout(0.5)(x)

    feat_in = tf.keras.layers.Input(shape=(F,), name="feat")
    f = tf.keras.layers.LayerNormalization()(feat_in)
    f = tf.keras.layers.Dropout(0.3)(f)
    f = tf.keras.layers.Dense(
        128, kernel_initializer=init,
        kernel_regularizer=tf.keras.regularizers.l2(wd),
        activation="leaky_relu"
    )(f)
    f = tf.keras.layers.Dropout(0.5)(f)
    f = tf.keras.layers.Dense(
        64, kernel_initializer=init,
        kernel_regularizer=tf.keras.regularizers.l2(wd),
        activation="leaky_relu"
    )(f)

    h = tf.keras.layers.Concatenate()([x, f])
    h = tf.keras.layers.Dense(
        128, kernel_initializer=init,
        kernel_regularizer=tf.keras.regularizers.l2(wd),
        activation="leaky_relu"
    )(h)
    h = tf.keras.layers.Dropout(0.3)(h)
    outputs = tf.keras.layers.Dense(5, activation="softmax")(h)

    model = tf.keras.Model(inputs=[ts_inputs, feat_in], outputs=outputs)

    loss = tf.keras.losses.SparseCategoricalCrossentropy()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(lr),
        loss=loss,
        metrics=["accuracy", tf.keras.metrics.SparseCategoricalCrossentropy(name="ce")]
    )
    return model


# -----------------------------
# 3) LOSO CV loop
# -----------------------------
def run_loso(meta, dict_block, epochs=200, batch_size=32, verbose=0, seed=42):
    tf.keras.utils.set_random_seed(seed)

    groups = meta["subject_id"].to_numpy()
    logo = LeaveOneGroupOut()

    fold_metrics = []
    all_y_true = []
    all_y_pred = []
    all_subjects = []

    for fold, (train_idx, val_idx) in enumerate(logo.split(meta, groups=groups)):
        meta_tr = meta.iloc[train_idx]
        meta_va = meta.iloc[val_idx]

        # pad length based on training fold (avoid using val stats)
        Xts_tr, Xf_tr, y_tr, subj_tr = make_xy_from_meta(meta_tr, dict_block, pad_to=None)
        pad_to = Xts_tr.shape[1]
        Xts_va, Xf_va, y_va, subj_va = make_xy_from_meta(meta_va, dict_block, pad_to=pad_to)

        model = build_model(F=Xf_tr.shape[1])

        es = tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=15, restore_best_weights=True
        )
        rlr = tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=5, min_lr=1e-6
        )

        hist = model.fit(
            {"ts": Xts_tr, "feat": Xf_tr}, y_tr,
            validation_data=({"ts": Xts_va, "feat": Xf_va}, y_va),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[es, rlr],
            verbose=verbose,
            shuffle=True
        )

        # Predict on val fold
        prob = model.predict({"ts": Xts_va, "feat": Xf_va}, verbose=0)
        y_pred = np.argmax(prob, axis=1)

        # Metrics
        acc = accuracy_score(y_va, y_pred)
        f1m = f1_score(y_va, y_pred, average="macro")

        # keep for global summary
        all_y_true.append(y_va)
        all_y_pred.append(y_pred)
        all_subjects.append(subj_va)

        # subject id in this fold is single subject
        subject_left_out = meta_va["subject_id"].unique()
        subject_left_out = int(subject_left_out[0]) if len(subject_left_out) == 1 else subject_left_out.tolist()

        fold_metrics.append({
            "fold": fold,
            "left_out_subject": subject_left_out,
            "n_val": len(y_va),
            "best_epoch": int(np.argmin(hist.history["val_loss"]) + 1),
            "val_acc": float(acc),
            "val_macro_f1": float(f1m),
            "val_loss_best": float(np.min(hist.history["val_loss"]))
        })

        print(f"Fold {fold:02d} | subj {subject_left_out} | n={len(y_va)} "
              f"| acc={acc:.3f} | macroF1={f1m:.3f} | best_val_loss={np.min(hist.history['val_loss']):.3f}")

    # Aggregate results
    y_true = np.concatenate(all_y_true)
    y_pred = np.concatenate(all_y_pred)
    subjects = np.concatenate(all_subjects)

    overall_acc = accuracy_score(y_true, y_pred)
    overall_f1m = f1_score(y_true, y_pred, average="macro")
    cm = confusion_matrix(y_true, y_pred)

    df_folds = pd.DataFrame(fold_metrics).sort_values("left_out_subject")

    print("\n ## LOSO summary \n")
    print(df_folds[["left_out_subject", "n_val", "val_acc", "val_macro_f1", "val_loss_best", "best_epoch"]].to_markdown())

    print("\nMean/Std across subjects: \n")
    print("val_acc     :", df_folds["val_acc"].mean(), "+/-", df_folds["val_acc"].std(), "\n")
    print("val_macro_f1:", df_folds["val_macro_f1"].mean(), "+/-", df_folds["val_macro_f1"].std())

    print("\nOverall (micro over all left-out samples):")
    print("\noverall_acc     :", overall_acc)
    print("\noverall_macro_f1:", overall_f1m)
    print("\nConfusion matrix:\n", cm)

    return df_folds, {"overall_acc": overall_acc, "overall_macro_f1": overall_f1m, "cm": cm}


# -----------------------------
# Usage
# -----------------------------
meta = pd.read_csv("../auswertung_features/meta.csv")
meta_tr: dict[int, pd.DataFrame] = {}
meta_te: dict[int, pd.DataFrame] = {}

dict_blocks = {}
meta_blocks = {"subject_id":[], "hand": [], "block_id":[]}
for i, r in meta.iterrows():
        csv_path = r["rel_path"]
        df_session = load_session(csv_path)

        #Error Handling für leere dfs
        if df_session is None:
            continue

        blocks = split_into_label_blocks(df_session)
        for block in blocks:
            meta_blocks["subject_id"].append(r["subject_id"])
            meta_blocks["hand"].append(r["hand"])
            meta_blocks["block_id"].append(len(dict_blocks))
            dict_blocks[len(dict_blocks)] = block
meta_blocks = pd.DataFrame(meta_blocks)

df_folds, summary = run_loso(meta_blocks, dict_blocks, epochs=200, batch_size=32, verbose=0)
