import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import pickle # is not secure, bit supports a lot: https://scikit-learn.org/stable/model_persistence.html

from ANN.LOSO_Run_2_input import build_model, make_xy_from_meta
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

    Xts_tr, Xf_tr, y_tr, subj_tr = make_xy_from_meta(meta_blocks, dict_blocks, pad_to=None)

    # Scale Features
    scaler = StandardScaler()
    Xf_tr = scaler.fit_transform(Xf_tr).astype(np.float32)
    pickle.dump(scaler, open("models/scaler_rightHand.pkl", "wb"), protocol=5)

    es = tf.keras.callbacks.EarlyStopping(
        monitor="loss", patience=15, restore_best_weights=True
    )
    rlr = tf.keras.callbacks.ReduceLROnPlateau(
        monitor="loss", factor=0.5, patience=5, min_lr=1e-6
    )

    model = build_model()
    hist = model.fit(
        {"ts": Xts_tr, "feat": Xf_tr}, y_tr,
        epochs=200,
        batch_size=32,
        callbacks=[es, rlr],
        verbose=0,
        shuffle=True
    )

    model.save("models/EMG-CNN-Model-rightHand.keras")

    #model = tf.keras.models.load_model("models/EMG-CNN-Model-rightHand.keras")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    with open("models/EMG-rightHand.tflite", "wb") as f:
        f.write(tflite_model)

if __name__ == "__main__":
    main()