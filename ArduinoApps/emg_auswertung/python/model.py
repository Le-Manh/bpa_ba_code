import pickle
from ai_edge_litert.interpreter import Interpreter
import pandas as pd
import numpy as np

scaler = None
model = None
in_details = None
out_details = None

CHECK_MODEL_DETAILS =  False

def load_model():
    global scaler, model, in_details, out_details

    scaler =  pickle.load(open("python/models/scaler_features.pkl", "rb"))
    model = Interpreter(model_path="python/models/EMG-CNN.tflite")
    model.allocate_tensors()

    in_details = model.get_input_details()
    out_details = model.get_output_details()

    if CHECK_MODEL_DETAILS:
        # Debug: Anzahl Inputs prüfen (du erwartest 2)
        print("num_inputs:", len(in_details))
        for i, d in enumerate(in_details):
            print("input", i, "shape", d["shape"], "dtype", d["dtype"], "index", d["index"])

        for i, d in enumerate(out_details):
            print("output", i, "shape", d["shape"], "dtype", d["dtype"], "index", d["index"])
   

def get_prediction_windows(X_ts_N: np.ndarray, df_feat: pd.DataFrame) -> np.ndarray:
    global scaler, model, in_details, out_details

    N = X_ts_N.shape[0] # X_ts is (N, 500, 4) --> N is bc of the stack of 

    # Features: 1x624 (für alle Fenster gleich)
    X_feat = np.asarray(df_feat, dtype=np.float32)          # shape (1,624) oder (624,)
    if X_feat.ndim == 1:
        X_feat = X_feat[None, :]
    X_feat = scaler.transform(X_feat).astype(np.float32)    # (1,624)

    probs = np.zeros((N, 5), dtype=np.float32)

    for i in range(N):
        x_ts = X_ts_N[i:i+1, :, :].astype(np.float32)       # (1,500,4)

        model.set_tensor(in_details[0]["index"], X_feat)    # (1,624)
        model.set_tensor(in_details[1]["index"], x_ts)      # (1,500,4)
        model.invoke()

        probs[i] = model.get_tensor(out_details[0]["index"])[0]  # (5,)

    return probs

def predict_block_from_windows(X_ts_N, df_feat):
    probs = get_prediction_windows(X_ts_N, df_feat)   # (N,5)
    prob_block = probs.mean(axis=0)                   # (5,)
    return int(np.argmax(prob_block))
