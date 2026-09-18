import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import tsfel
import pickle # is not secure, bit supports a lot: https://scikit-learn.org/stable/model_persistence.html

from ANN.build_model_mlp import build_model_feat
from ANN.gridsearch_mlp import tsfel_feature_read
from auswertung_features.build_features import split_into_label_blocks, load_session

def main():
    hidden_unit = (128,64)
    wd = 1e-4
    dropout = 0.0
    learning_rate = 1e-3
    norm = "layernorm"
    hand = "l"
    feature_set = "default_tsfel"

    if feature_set == "default_tsfel":
        tsfel_cfg = tsfel.get_features_by_domain()
        F = 624
    else:
        tsfel_cfg = tsfel.get_features_by_domain(json_path="../auswertung_features/tsfel_conf.json")
        F = 260

    meta = pd.read_csv("../auswertung_features/meta.csv")

    dict_blocks = {}
    meta_blocks = {"subject_id":[], "hand": [],"rel_path":[], "block_id":[]}
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

    y_list = []
    X_list = []

    if hand == "r":
        data = meta_blocks_r
    elif hand == "l":
        data = meta_blocks_l
    else:
        data = meta_blocks

    # global feature table
    feat_global = tsfel_feature_read(dict_blocks,tsfel_cfg, feature_set_name=feature_set, b_pad=False)

    for bid in data["block_id"].to_numpy():
        x_tr_raw, y_i = dict_blocks[int(bid)]
        y_list.append(int(y_i))
        X_list.append(feat_global.iloc[int(bid)].reset_index(drop=True).to_numpy(np.float32))

    X_tr = np.array(X_list)

    # Scale Features
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_tr)
    y_tr = np.array(y_list, dtype=np.int32)

    pickle.dump(scaler, open(f"models/scaler_features_{hand}.pkl", "wb"), protocol=5)

    model = build_model_feat(F, hidden_units=hidden_unit, wd=wd, lr=learning_rate, norm=norm, dropout=dropout)
    model.fit(X_tr, y_tr ,
        epochs=38,
        batch_size=32,
        verbose=0,
        shuffle=True
    )

    model.save(f"models/EMG-Model-{hand}.keras")

    print(model.summary())
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,
        tf.lite.OpsSet.SELECT_TF_OPS
    ]
    converter._experimental_lower_tensor_list_ops = False

    tflite_model = converter.convert()

    with open(f"models/EMG-MLP-{hand}.tflite", "wb") as f:
        f.write(tflite_model)

if __name__ == "__main__":
    main()