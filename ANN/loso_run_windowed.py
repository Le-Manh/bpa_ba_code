from loso_windowed_blockfeat import run_window_grid_loso, suggested_grids
from ANN.LOSO_Run_2_input import tsfel_feature, build_model, build_model_feat
import pandas as pd
from auswertung_features.build_features import split_into_label_blocks, load_session

grid1, grid_feat_time_test, grid2_ensemble, grid2_compute = suggested_grids()


meta = pd.read_csv("../auswertung_features/meta.csv")
meta_tr: dict[int, pd.DataFrame] = {}
meta_te: dict[int, pd.DataFrame] = {}

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


df_folds_all, df_summary = run_window_grid_loso(
    meta_blocks, dict_blocks,
    tsfel_feature_fn=tsfel_feature,
    build_model_fn=build_model_feat,
    grid=grid2_compute,
    epochs=200,
    batch_size=32,
    patience=10,
    verbose=0
)

print(df_summary.to_markdown(index=False))
best = df_summary.iloc[0]
print("Best config:", int(best["T"]), int(best["stride"]))
