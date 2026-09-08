import pandas as pd
import numpy as np
from sklearn.model_selection import LeaveOneGroupOut
from loso_windowed_blockfeat import block_to_windows_postpad
import tsfel
import os
from LOSO_Run_2_input import build_model_feat, build_model
import tensorflow as tf
from auswertung_features.build_features import split_into_label_blocks, load_session
from sklearn.preprocessing import StandardScaler
import random
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

meta = pd.read_csv("../auswertung_features/meta.csv")
dict_blocks = {}
meta_blocks = {"subject_id":[], "hand": [], "rel_path":[], "block_id":[]}
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
        meta_blocks["rel_path"].append(r["rel_path"])
        meta_blocks["block_id"].append(len(dict_blocks))
        dict_blocks[len(dict_blocks)] = block
meta_blocks = pd.DataFrame(meta_blocks)
meta_blocks_r = meta_blocks[meta_blocks["hand"]=="r"].reset_index(drop=True)
meta_blocks_l = meta_blocks[meta_blocks["hand"]=="l"].reset_index(drop=True)

feature_cache: dict[str, pd.DataFrame] = {}
def tsfel_feature_read(dict_blocks, tsfel_cfg, feature_set_name = "default_tsfel", fs = 500, b_pad = True):
    k = feature_set_name
    if b_pad:
        k = k + "_pad"
    feature_list = []
    if k not in feature_cache:
        if os.path.isfile(f"../auswertung_features/cache/feature_{k}.csv"):
            feature_cache[k] = pd.read_csv(f"../auswertung_features/cache/feature_{k}.csv", index_col=0)
        else:
            for win, label in dict_blocks.values():
                if b_pad:
                    X = block_to_windows_postpad(win, T=2000, stride=2000)
                else:
                    X = win
                feats_df= tsfel.time_series_features_extractor(tsfel_cfg, X, fs=fs)
                feature_list.append(feats_df.iloc[0].to_dict())
            feature_cache[k] = pd.DataFrame(feature_list)
            feature_cache[k].to_csv(f"../auswertung_features/cache/feature_{k}.csv")
    return feature_cache[k]

def logo_mlp(model, meta_block, dict_blocks, tsfel_cfg, feature_set_name = "default_tsfel", b_CNN = False, b_pad = True):
    logo = LeaveOneGroupOut()
    groups = meta_block["subject_id"].to_numpy()
    fold_metrics = []
    feat_global = tsfel_feature_read(dict_blocks, tsfel_cfg, feature_set_name= feature_set_name, b_pad=b_pad)

    for fold, (train_idx, val_idx) in enumerate(logo.split(meta_block, groups=groups)):
        y_list_tr = []
        y_list_va = []
        xts_list_tr = []
        xts_list_va = []
        meta_tr = meta_block.iloc[train_idx].reset_index(drop=True)
        meta_va = meta_block.iloc[val_idx].reset_index(drop=True)

        #Xf_va = feat_global.loc[meta_va["block_id"].astype(int), feat_cols].to_numpy()
        for i, bid in enumerate(meta_tr["block_id"].to_numpy()):
            x_tr_raw, y_i = dict_blocks[int(bid)]
            y_list_tr.append(int(y_i))
            #random.shuffle(y_list_tr) # used to test label leakage
            xts_list_tr.append(block_to_windows_postpad(x_tr_raw, T = 2000, stride=2000)[0])

        for i, bid in enumerate(meta_va["block_id"].to_numpy()):
            x_va_raw, y_i = dict_blocks[int(bid)]
            y_list_va.append(int(y_i))
            #random.shuffle(y_list_va)
            xts_list_va.append(block_to_windows_postpad(x_va_raw, T = 2000, stride=2000)[0])

        y_tr = np.array(y_list_tr, dtype=np.int32)
        y_va = np.array(y_list_va, dtype=np.int32)

        X_all = feat_global
        X_tr = X_all.iloc[train_idx].reset_index(drop=True).to_numpy(np.float32)
        X_va = X_all.iloc[val_idx].reset_index(drop=True).to_numpy(np.float32)

        scaler = StandardScaler()
        #X_tr = scaler.fit_transform(X_tr)
        #X_va = scaler.transform(X_va)

        es = tf.keras.callbacks.EarlyStopping(
            monitor="loss", patience=10, restore_best_weights=True
        )
        rlr = tf.keras.callbacks.ReduceLROnPlateau(
            monitor="loss", factor=0.5, patience=max(2, 10 // 2), min_lr=1e-6
        )
        if b_CNN:
            xts_tr = np.stack(xts_list_tr, axis=0).astype(np.float32)
            xts_va = np.stack(xts_list_va, axis=0).astype(np.float32)
            hist = model.fit({"ts":xts_tr, "feat":X_tr}, y_tr, batch_size=32, epochs=200, callbacks=[es, rlr], shuffle=True)
            y_prob = model.predict({"ts":xts_va, "feat":X_va})
        else:
            hist = model.fit(X_tr, y_tr,
                         validation_data=(X_va, y_va), callbacks=[es, rlr],
                         epochs = 200, shuffle = True, batch_size=32)
            y_prob = model.predict(X_va)

        y_pred = y_prob.argmax(axis=1)

        # Metrics
        acc = accuracy_score(y_va, y_pred)
        f1m = f1_score(y_va, y_pred, average="macro")
        cm = confusion_matrix(y_va, y_pred)

        # subject id in this fold is single subject
        subject_left_out = meta_va["subject_id"].unique()
        subject_left_out = int(subject_left_out[0]) if len(subject_left_out) == 1 else subject_left_out.tolist()

        fold_metrics.append({
            "fold": fold,
            "left_out_subject": subject_left_out,
            "n_val_blocks": int(len(meta_va)),
            "best_epoch": int(np.argmin(hist.history["loss"]) + 1) if "loss" in hist.history else None,
            "n_val": len(y_va),
            "val_acc": float(acc),
            "val_macro_f1": float(f1m),
            "cm_pro_": cm,
        })

    return fold_metrics

feature_set = "tsfel"

if feature_set == "default_tsfel":
    tsfel_cfg = tsfel.get_features_by_domain()
    F = 624
elif feature_set == "tsfel_wOut_time":
    tsfel_cfg = tsfel.get_features_by_domain(json_path="tsfel_conf_without_TimeVar.json")
    F = 352
else:
    tsfel_cfg = tsfel.get_features_by_domain(json_path="../auswertung_features/tsfel_conf.json")
    F = 260
#tf_model = build_model(2000,F)
#results_mlp = logo_mlp(tf_model, meta_blocks ,dict_blocks, feature_set_name = feature_set, tsfel_cfg = tsfel_cfg, b_CNN=True)

hidden_units_list = [(64,) ]
wd_list = [1e-4]
dropout_list = [0.0]
learning_rate_list = [3e-4]
norms = ["layernorm"]
hand_list = ["both","r","l"]

for hidden_unit in hidden_units_list:
    for wd in wd_list:
        for dropout in dropout_list:
            for learning_rate in learning_rate_list:
                for norm in norms:
                    tf_model = build_model_feat(F, hidden_units=hidden_unit, wd=wd, lr=learning_rate, norm=norm, dropout=dropout)
                    for hand in hand_list:
                        if hand == "r":
                            data = meta_blocks_r
                        elif hand == "l":
                            data = meta_blocks_l
                        else:
                            data = meta_blocks
                        results_mlp = logo_mlp(tf_model, data, dict_blocks, feature_set_name = feature_set,tsfel_cfg = tsfel_cfg, b_pad = False)
                        path = "../auswertung_features/results/mlp-logo/"
                        filename = f"results_logo_mlp_{feature_set}_hu-{hidden_unit}_wd-{wd}_drop-{dropout}_lr-{learning_rate}_norm-{norm}_scaler-no_{hand}.csv"
                        pd.DataFrame(results_mlp).to_csv(path+filename)