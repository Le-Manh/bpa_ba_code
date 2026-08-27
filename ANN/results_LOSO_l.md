# Results of Left Hand

| Fold | Left out | sample of subj | Acc | MacroF1 | best val loss|
|:-------:|:--------:|--------|---------|-----------|--------------| 
Fold 00 | subj 1 | n=30 | acc=0.633 | macroF1=0.622 | best_val_loss=1.452
Fold 01 | subj 2 | n=40 | acc=0.175 | macroF1=0.143 | best_val_loss=3.042
WARNING:tensorflow:5 out of the last 6 calls to <function TensorFlowTrainer.make_predict_function.<locals>.one_step_on_data_distributed at 0x7585f47968e0> triggered tf.function retracing. Tracing is expensive and the excessive number of tracings could be due to (1) creating @tf.function repeatedly in a loop, (2) passing tensors with different shapes, (3) passing Python objects instead of tensors. For (1), please define your @tf.function outside of the loop. For (2), @tf.function has reduce_retracing=True option that can avoid unnecessary retracing. For (3), please refer to https://www.tensorflow.org/guide/function#controlling_retracing and https://www.tensorflow.org/api_docs/python/tf/function for  more details.
Fold 02 | subj 3 | n=95 | acc=0.811 | macroF1=0.810 | best_val_loss=1.027
WARNING:tensorflow:6 out of the last 7 calls to <function TensorFlowTrainer.make_predict_function.<locals>.one_step_on_data_distributed at 0x7585d84ba700> triggered tf.function retracing. Tracing is expensive and the excessive number of tracings could be due to (1) creating @tf.function repeatedly in a loop, (2) passing tensors with different shapes, (3) passing Python objects instead of tensors. For (1), please define your @tf.function outside of the loop. For (2), @tf.function has reduce_retracing=True option that can avoid unnecessary retracing. For (3), please refer to https://www.tensorflow.org/guide/function#controlling_retracing and https://www.tensorflow.org/api_docs/python/tf/function for  more details.
Fold 03 | subj 4 | n=15 | acc=0.400 | macroF1=0.309 | best_val_loss=1.992
Fold 04 | subj 5 | n=15 | acc=0.467 | macroF1=0.386 | best_val_loss=1.916
Fold 05 | subj 6 | n=15 | acc=0.400 | macroF1=0.280 | best_val_loss=2.821
Fold 06 | subj 7 | n=15 | acc=0.600 | macroF1=0.467 | best_val_loss=1.238
Fold 07 | subj 8 | n=20 | acc=0.600 | macroF1=0.578 | best_val_loss=1.673
Fold 08 | subj 9 | n=15 | acc=0.533 | macroF1=0.468 | best_val_loss=1.912
Fold 09 | subj 10 | n=35 | acc=0.429 | macroF1=0.362 | best_val_loss=1.926
Fold 10 | subj 11 | n=25 | acc=0.280 | macroF1=0.227 | best_val_loss=2.565
Fold 11 | subj 12 | n=30 | acc=0.800 | macroF1=0.773 | best_val_loss=1.229
Fold 12 | subj 13 | n=25 | acc=0.480 | macroF1=0.441 | best_val_loss=2.015
Fold 13 | subj 14 | n=25 | acc=0.320 | macroF1=0.352 | best_val_loss=2.076
Fold 14 | subj 15 | n=25 | acc=0.320 | macroF1=0.331 | best_val_loss=2.172
Fold 15 | subj 16 | n=50 | acc=0.260 | macroF1=0.153 | best_val_loss=2.691
Fold 16 | subj 17 | n=25 | acc=0.240 | macroF1=0.182 | best_val_loss=3.075
Fold 17 | subj 18 | n=25 | acc=0.360 | macroF1=0.267 | best_val_loss=2.050
Fold 18 | subj 19 | n=25 | acc=0.520 | macroF1=0.506 | best_val_loss=1.654
Fold 19 | subj 20 | n=25 | acc=0.280 | macroF1=0.191 | best_val_loss=4.196
Fold 20 | subj 21 | n=25 | acc=0.640 | macroF1=0.594 | best_val_loss=1.469
Fold 21 | subj 22 | n=25 | acc=0.720 | macroF1=0.647 | best_val_loss=1.462

 ## LOSO summary 

|    |   left_out_subject |   n_val |   val_acc |   val_macro_f1 |   val_loss_best |   best_epoch |
|---:|-------------------:|--------:|----------:|---------------:|----------------:|-------------:|
|  0 |                  1 |      30 |  0.633333 |       0.621523 |         1.45214 |           59 |
|  1 |                  2 |      40 |  0.175    |       0.143    |         3.04199 |            4 |
|  2 |                  3 |      95 |  0.810526 |       0.81025  |         1.02655 |           64 |
|  3 |                  4 |      15 |  0.4      |       0.309091 |         1.99151 |            2 |
|  4 |                  5 |      15 |  0.466667 |       0.385641 |         1.91556 |           23 |
|  5 |                  6 |      15 |  0.4      |       0.28     |         2.82051 |           34 |
|  6 |                  7 |      15 |  0.6      |       0.466667 |         1.23784 |           18 |
|  7 |                  8 |      20 |  0.6      |       0.577839 |         1.6726  |            7 |
|  8 |                  9 |      15 |  0.533333 |       0.467619 |         1.91242 |           34 |
|  9 |                 10 |      35 |  0.428571 |       0.361878 |         1.92629 |           15 |
| 10 |                 11 |      25 |  0.28     |       0.227279 |         2.56458 |            1 |
| 11 |                 12 |      30 |  0.8      |       0.772995 |         1.22861 |           11 |
| 12 |                 13 |      25 |  0.48     |       0.441457 |         2.01533 |           12 |
| 13 |                 14 |      25 |  0.32     |       0.352381 |         2.07571 |           11 |
| 14 |                 15 |      25 |  0.32     |       0.331429 |         2.17227 |           11 |
| 15 |                 16 |      50 |  0.26     |       0.15348  |         2.69052 |            1 |
| 16 |                 17 |      25 |  0.24     |       0.18226  |         3.07537 |            1 |
| 17 |                 18 |      25 |  0.36     |       0.266667 |         2.04981 |           37 |
| 18 |                 19 |      25 |  0.52     |       0.50641  |         1.65449 |           30 |
| 19 |                 20 |      25 |  0.28     |       0.190909 |         4.19649 |           36 |
| 20 |                 21 |      25 |  0.64     |       0.594118 |         1.46901 |            2 |
| 21 |                 22 |      25 |  0.72     |       0.647302 |         1.46165 |           63 |

Mean/Std across subjects: \
val_acc     : 0.46670141262246523 +/- 0.1836093320774723 \
val_macro_f1: 0.41319049918275924 +/- 0.1954305073113533

Overall (micro over all left-out samples): \
overall_acc     : 0.4912 \
overall_macro_f1: 0.4864300266688567

Confusion matrix: \
 [[71  6  9 12 27] \
 [17 67 24  5 12] \
 [14 16 64  6 25] \
 [25 14 12 34 40] \
 [21  7  9 17 71]]

# Results if trying to use a single input

| Fold | Left out | sample of subj | Acc | MacroF1 | best val loss|
|:-------:|:--------:|--------|---------|-----------|--------------| 
Fold 00 | subj 1 | n=30 | acc=0.233 | macroF1=0.157 | best_val_loss=1.600
Fold 01 | subj 2 | n=40 | acc=0.225 | macroF1=0.152 | best_val_loss=1.638
Fold 02 | subj 3 | n=95 | acc=0.316 | macroF1=0.292 | best_val_loss=1.558
Fold 03 | subj 4 | n=15 | acc=0.200 | macroF1=0.067 | best_val_loss=1.642
Fold 04 | subj 5 | n=15 | acc=0.200 | macroF1=0.067 | best_val_loss=1.957
Fold 05 | subj 6 | n=15 | acc=0.400 | macroF1=0.229 | best_val_loss=1.359
Fold 06 | subj 7 | n=15 | acc=0.400 | macroF1=0.292 | best_val_loss=1.563
Fold 07 | subj 8 | n=20 | acc=0.300 | macroF1=0.336 | best_val_loss=1.604
Fold 08 | subj 9 | n=15 | acc=0.333 | macroF1=0.233 | best_val_loss=1.611
Fold 09 | subj 10 | n=35 | acc=0.314 | macroF1=0.228 | best_val_loss=1.609
Fold 10 | subj 11 | n=25 | acc=0.200 | macroF1=0.067 | best_val_loss=1.637
Fold 11 | subj 12 | n=30 | acc=0.367 | macroF1=0.287 | best_val_loss=1.557
Fold 12 | subj 13 | n=25 | acc=0.440 | macroF1=0.365 | best_val_loss=1.508
Fold 13 | subj 14 | n=25 | acc=0.200 | macroF1=0.067 | best_val_loss=1.621
Fold 14 | subj 15 | n=25 | acc=0.120 | macroF1=0.069 | best_val_loss=1.626
Fold 15 | subj 16 | n=50 | acc=0.240 | macroF1=0.158 | best_val_loss=1.656
Fold 16 | subj 17 | n=25 | acc=0.200 | macroF1=0.067 | best_val_loss=1.641
Fold 17 | subj 18 | n=25 | acc=0.320 | macroF1=0.181 | best_val_loss=1.620
Fold 18 | subj 19 | n=25 | acc=0.280 | macroF1=0.175 | best_val_loss=1.588
Fold 19 | subj 20 | n=25 | acc=0.200 | macroF1=0.113 | best_val_loss=1.664
Fold 20 | subj 21 | n=25 | acc=0.480 | macroF1=0.416 | best_val_loss=1.611
Fold 21 | subj 22 | n=25 | acc=0.120 | macroF1=0.101 | best_val_loss=1.629

 ## LOSO summary 

|    |   left_out_subject |   n_val |   val_acc |   val_macro_f1 |   val_loss_best |   best_epoch |
|---:|-------------------:|--------:|----------:|---------------:|----------------:|-------------:|
|  0 |                  1 |      30 |  0.233333 |      0.157143  |         1.59991 |           12 |
|  1 |                  2 |      40 |  0.225    |      0.152381  |         1.63808 |           33 |
|  2 |                  3 |      95 |  0.315789 |      0.292288  |         1.558   |           10 |
|  3 |                  4 |      15 |  0.2      |      0.0666667 |         1.64172 |           41 |
|  4 |                  5 |      15 |  0.2      |      0.0666667 |         1.95696 |           48 |
|  5 |                  6 |      15 |  0.4      |      0.229091  |         1.35936 |           27 |
|  6 |                  7 |      15 |  0.4      |      0.292308  |         1.56328 |            7 |
|  7 |                  8 |      20 |  0.3      |      0.335531  |         1.60389 |            5 |
|  8 |                  9 |      15 |  0.333333 |      0.2329    |         1.61136 |           18 |
|  9 |                 10 |      35 |  0.314286 |      0.227807  |         1.60891 |           14 |
| 10 |                 11 |      25 |  0.2      |      0.0666667 |         1.63698 |           23 |
| 11 |                 12 |      30 |  0.366667 |      0.286667  |         1.55652 |            7 |
| 12 |                 13 |      25 |  0.44     |      0.364825  |         1.50821 |          123 |
| 13 |                 14 |      25 |  0.2      |      0.0666667 |         1.62143 |           70 |
| 14 |                 15 |      25 |  0.12     |      0.0688645 |         1.62567 |            7 |
| 15 |                 16 |      50 |  0.24     |      0.157621  |         1.65564 |           14 |
| 16 |                 17 |      25 |  0.2      |      0.0666667 |         1.64076 |           19 |
| 17 |                 18 |      25 |  0.32     |      0.180952  |         1.61991 |           60 |
| 18 |                 19 |      25 |  0.28     |      0.175     |         1.5883  |            4 |
| 19 |                 20 |      25 |  0.2      |      0.113158  |         1.6639  |           26 |
| 20 |                 21 |      25 |  0.48     |      0.416434  |         1.61086 |           10 |
| 21 |                 22 |      25 |  0.12     |      0.101053  |         1.62858 |            5 |

Mean/Std across subjects: \
val_acc     : 0.27674584187742085 +/- 0.0988943062476056 \
val_macro_f1: 0.18715257106624195 +/- 0.1082995385741029

Overall (micro over all left-out samples): \
overall_acc     : 0.2768 \
overall_macro_f1: 0.27365301007683385

Confusion matrix: \
 [[38 24 16 26 21] \
 [17 48 21 13 26] \
 [14 24 36 24 27] \
 [21 23 33 17 31] \
 [25 18 32 16 34]]