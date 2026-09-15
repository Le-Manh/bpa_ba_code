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

    scaler =  pickle.load(open("python/models/scaler_features_default_tsfel_r.pkl", "rb"))
    model = Interpreter(model_path="python/models/EMG-MLP-default_tsfel-r.tflite")
    model.allocate_tensors()

    in_details = model.get_input_details()
    out_details = model.get_output_details()

    if CHECK_MODEL_DETAILS:
        # Debug: Anzahl Inputs prüfen
        print("num_inputs:", len(in_details))
        for i, d in enumerate(in_details):
            print("input", i, "shape", d["shape"], "dtype", d["dtype"], "index", d["index"])

        for i, d in enumerate(out_details):
            print("output", i, "shape", d["shape"], "dtype", d["dtype"], "index", d["index"])
   

def get_prediction(df_feat: pd.DataFrame) -> np.ndarray:
    global scaler, model, in_details, out_details

    # Features: 1x624 (für alle Fenster gleich)
    #X_feat = np.asarray(df_feat, dtype=np.float32)          # shape (1,624) oder (624,)
    #if X_feat.ndim == 1:
    #    X_feat = X_feat[None, :]
    X_feat = scaler.transform(df_feat.to_numpy()).astype(np.float32)    # (1,624)

    model.set_tensor(in_details[0]["index"], X_feat)    # (1,624)
    model.invoke()

    probs = model.get_tensor(out_details[0]["index"])  # (5,)
    #print(probs)
    return probs

def predict_block(df_feat):
    probs = get_prediction(df_feat)   # (N,5)
    #print(np.argmax(probs, axis=1))
    return int(np.argmax(probs, axis=1)[0])
