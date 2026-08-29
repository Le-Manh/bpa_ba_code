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

    scaler =  pickle.load(open("python/models/scaler_rightHand.pkl", "rb"))
    model = Interpreter(model_path="python/models/EMG-rightHand.tflite")
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

        
def get_prediction(df_ts: pd.DataFrame, df_feat: pd.DataFrame) -> int:
    global scaler, model, in_details, out_details
    
    X_feat = np.asarray(df_feat, dtype=np.float32)
    X_feat = scaler.transform(X_feat).astype(np.float32)
    X_ts = np.asarray(df_ts, dtype=np.float32)
    X_ts = np.reshape(X_ts, (1, 1, 4)).astype(np.float32)
    print(X_ts.shape)

    model.set_tensor(in_details[0]["index"], X_feat)
    model.set_tensor(in_details[1]["index"], X_ts)

    model.invoke()

    pred = model.get_tensor(out_details[0]["index"])
    print(pred)
    y = int(np.argmax(pred,axis=1)[0])
    return y