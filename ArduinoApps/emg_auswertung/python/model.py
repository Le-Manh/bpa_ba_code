import pickle
from ai_edge_litert.interpreter import Interpreter
import pandas as pd
import numpy as np

scaler = None
model = None

def load_model():
    global scaler, model

    scaler =  pickle.load(open("python/models/scaler_rightHand.pkl", "rb"))
    model = Interpreter(model_path="python/models/EMG-rightHand.tflite")


def get_prediction(df_ts: pd.DataFrame, df_feat: pd.DataFrame) -> int:
    global scaler, model
    
    X_feat = np.asarray(df_feat, dtype=np.float32)
    X_feat = scaler.transform(X_feat).astype(np.float32)
    X_ts = np.asarray(df_ts, dtype=np.float32)

    pred = model.predict([X_ts, X_feat])
    print(pred)
    y = pred.argmax(axis=1)
    return y