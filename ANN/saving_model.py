import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import pickle # is not secure, bit supports a lot: https://scikit-learn.org/stable/model_persistence.html

from ANN.loso_windowed_blockfeat import make_xy_from_meta_windowed_blockfeat
from ANN.LOSO_Run_2_input import build_model, tsfel_feature
from auswertung_features.build_features import split_into_label_blocks, load_session

def main():

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

    # global feature table
    feat_table = tsfel_feature(meta_blocks, win= 0, step=0)

    # Window-Parameter
    T = 500
    stride = 250

    X_ts, X_f, y, subj, bid = make_xy_from_meta_windowed_blockfeat(meta_blocks, dict_blocks,feat_table, T=T, stride=stride)

    # Scale Features
    scaler = StandardScaler()
    X_f = scaler.fit_transform(X_f).astype(np.float32)
    pickle.dump(scaler, open("models/scaler_features.pkl", "wb"), protocol=5)

    es = tf.keras.callbacks.EarlyStopping(
        monitor="loss", patience=15, restore_best_weights=True
    )
    rlr = tf.keras.callbacks.ReduceLROnPlateau(
        monitor="loss", factor=0.5, patience=5, min_lr=1e-6
    )

    model = build_model(T=T, F=X_f.shape[1])
    model.fit(
        {"ts": X_ts, "feat": X_f}, y,
        epochs=200,
        batch_size=32,
        callbacks=[es, rlr],
        verbose=0,
        shuffle=True
    )

    model.save("models/EMG-CNN-Model.keras")

    #model = tf.keras.models.load_model("models/EMG-CNN-Model-rightHand.keras")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    with open("models/EMG-CNN.tflite", "wb") as f:
        f.write(tflite_model)

if __name__ == "__main__":
    main()