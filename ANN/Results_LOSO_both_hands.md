# Results first run

| Fold | Left out | sample of subj | Acc | MacroF1 | best val loss|
|:-------:|:--------:|--------|---------|-----------|--------------| 
Fold 00 | subj 1 | n=60 | acc=0.617 | macroF1=0.602 | best_val_loss=1.315
Fold 01 | subj 2 | n=80 | acc=0.362 | macroF1=0.360 | best_val_loss=2.224
WARNING:tensorflow:5 out of the last 6 calls to <function TensorFlowTrainer.make_predict_function.<locals>.one_step_on_data_distributed at 0x75f5b65ba8e0> triggered tf.function retracing. Tracing is expensive and the excessive number of tracings could be due to (1) creating @tf.function repeatedly in a loop, (2) passing tensors with different shapes, (3) passing Python objects instead of tensors. For (1), please define your @tf.function outside of the loop. For (2), @tf.function has reduce_retracing=True option that can avoid unnecessary retracing. For (3), please refer to https://www.tensorflow.org/guide/function#controlling_retracing and https://www.tensorflow.org/api_docs/python/tf/function for  more details.
WARNING:tensorflow:6 out of the last 11 calls to <function TensorFlowTrainer.make_predict_function.<locals>.one_step_on_data_distributed at 0x75f5b65ba8e0> triggered tf.function retracing. Tracing is expensive and the excessive number of tracings could be due to (1) creating @tf.function repeatedly in a loop, (2) passing tensors with different shapes, (3) passing Python objects instead of tensors. For (1), please define your @tf.function outside of the loop. For (2), @tf.function has reduce_retracing=True option that can avoid unnecessary retracing. For (3), please refer to https://www.tensorflow.org/guide/function#controlling_retracing and https://www.tensorflow.org/api_docs/python/tf/function for  more details.
Fold 02 | subj 3 | n=190 | acc=0.716 | macroF1=0.700 | best_val_loss=1.302
Fold 03 | subj 4 | n=30 | acc=0.500 | macroF1=0.476 | best_val_loss=1.787
Fold 04 | subj 5 | n=30 | acc=0.567 | macroF1=0.583 | best_val_loss=1.932
Fold 05 | subj 6 | n=30 | acc=0.467 | macroF1=0.381 | best_val_loss=2.472
Fold 06 | subj 7 | n=30 | acc=0.667 | macroF1=0.631 | best_val_loss=1.130
Fold 07 | subj 8 | n=35 | acc=0.657 | macroF1=0.639 | best_val_loss=1.232
Fold 08 | subj 9 | n=30 | acc=0.567 | macroF1=0.540 | best_val_loss=1.709
Fold 09 | subj 10 | n=75 | acc=0.427 | macroF1=0.453 | best_val_loss=1.762
Fold 10 | subj 11 | n=50 | acc=0.340 | macroF1=0.327 | best_val_loss=2.013
Fold 11 | subj 12 | n=55 | acc=0.836 | macroF1=0.826 | best_val_loss=0.875
Fold 12 | subj 13 | n=50 | acc=0.420 | macroF1=0.407 | best_val_loss=1.947
Fold 13 | subj 14 | n=50 | acc=0.460 | macroF1=0.470 | best_val_loss=1.594
Fold 14 | subj 15 | n=50 | acc=0.440 | macroF1=0.417 | best_val_loss=2.061
Fold 15 | subj 16 | n=100 | acc=0.340 | macroF1=0.255 | best_val_loss=2.591
Fold 16 | subj 17 | n=50 | acc=0.260 | macroF1=0.235 | best_val_loss=2.333
Fold 17 | subj 18 | n=50 | acc=0.320 | macroF1=0.220 | best_val_loss=2.088
Fold 18 | subj 19 | n=50 | acc=0.360 | macroF1=0.289 | best_val_loss=2.099
Fold 19 | subj 20 | n=50 | acc=0.380 | macroF1=0.365 | best_val_loss=2.156
Fold 20 | subj 21 | n=50 | acc=0.720 | macroF1=0.709 | best_val_loss=1.459
Fold 21 | subj 22 | n=55 | acc=0.545 | macroF1=0.499 | best_val_loss=1.763

 ## LOSO summary 

|    |   left_out_subject |   n_val |   val_acc |   val_macro_f1 |   val_loss_best |   best_epoch |
|---:|-------------------:|--------:|----------:|---------------:|----------------:|-------------:|
|  0 |                  1 |      60 |  0.616667 |       0.602296 |        1.31456  |           33 |
|  1 |                  2 |      80 |  0.3625   |       0.359513 |        2.22401  |           20 |
|  2 |                  3 |     190 |  0.715789 |       0.699962 |        1.30233  |           56 |
|  3 |                  4 |      30 |  0.5      |       0.475556 |        1.78691  |            2 |
|  4 |                  5 |      30 |  0.566667 |       0.583175 |        1.93164  |            7 |
|  5 |                  6 |      30 |  0.466667 |       0.380952 |        2.47225  |           16 |
|  6 |                  7 |      30 |  0.666667 |       0.630953 |        1.12997  |           34 |
|  7 |                  8 |      35 |  0.657143 |       0.639309 |        1.23238  |           59 |
|  8 |                  9 |      30 |  0.566667 |       0.54     |        1.70893  |           13 |
|  9 |                 10 |      75 |  0.426667 |       0.453071 |        1.76154  |           46 |
| 10 |                 11 |      50 |  0.34     |       0.326778 |        2.01261  |           29 |
| 11 |                 12 |      55 |  0.836364 |       0.825842 |        0.875264 |           43 |
| 12 |                 13 |      50 |  0.42     |       0.407368 |        1.94724  |            8 |
| 13 |                 14 |      50 |  0.46     |       0.470297 |        1.59415  |           67 |
| 14 |                 15 |      50 |  0.44     |       0.417253 |        2.06064  |           23 |
| 15 |                 16 |     100 |  0.34     |       0.255453 |        2.5909   |            9 |
| 16 |                 17 |      50 |  0.26     |       0.234921 |        2.33299  |           18 |
| 17 |                 18 |      50 |  0.32     |       0.219697 |        2.08756  |           38 |
| 18 |                 19 |      50 |  0.36     |       0.288671 |        2.09939  |            6 |
| 19 |                 20 |      50 |  0.38     |       0.364864 |        2.15635  |           25 |
| 20 |                 21 |      50 |  0.72     |       0.709041 |        1.45891  |           31 |
| 21 |                 22 |      55 |  0.545455 |       0.498653 |        1.763    |           18 |

Mean/Std across subjects: \
val_acc     : 0.4985113869384205 +/- 0.15388458127320268 \
val_macro_f1: 0.47198297708341513 +/- 0.16657803849609465

Overall (micro over all left-out samples): \
overall_acc     : 0.508 \
overall_macro_f1: 0.5054310998485924

Confusion matrix: \
 [[142  28  24  24  32] \
 [ 20 133  50  29  18] \
 [  6  44 152  14  34] \
 [ 23  43  32  78  74] \
 [ 20  23  33  44 130]]