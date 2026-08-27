# Results of Right Hand

| Fold | Left out | sample of subj | Acc | MacroF1 | best val loss|
|:-------:|:--------:|--------|---------|-----------|--------------| 
Fold 00 | subj 1 | n=30 | acc=0.567 | macroF1=0.483 | best_val_loss=1.427
Fold 01 | subj 2 | n=40 | acc=0.700 | macroF1=0.709 | best_val_loss=1.642
Fold 02 | subj 3 | n=95 | acc=0.695 | macroF1=0.645 | best_val_loss=1.435
Fold 03 | subj 4 | n=15 | acc=0.533 | macroF1=0.546 | best_val_loss=1.613
Fold 04 | subj 5 | n=15 | acc=0.800 | macroF1=0.721 | best_val_loss=1.558
Fold 05 | subj 6 | n=15 | acc=0.400 | macroF1=0.373 | best_val_loss=1.743
Fold 06 | subj 7 | n=15 | acc=0.467 | macroF1=0.429 | best_val_loss=1.887
Fold 07 | subj 8 | n=15 | acc=0.333 | macroF1=0.280 | best_val_loss=1.883
Fold 08 | subj 9 | n=15 | acc=0.467 | macroF1=0.393 | best_val_loss=1.437
Fold 09 | subj 10 | n=40 | acc=0.550 | macroF1=0.517 | best_val_loss=1.739
Fold 10 | subj 11 | n=25 | acc=0.440 | macroF1=0.331 | best_val_loss=1.969
Fold 11 | subj 12 | n=25 | acc=0.760 | macroF1=0.735 | best_val_loss=1.148
Fold 12 | subj 13 | n=25 | acc=0.520 | macroF1=0.506 | best_val_loss=1.578
Fold 13 | subj 14 | n=25 | acc=0.480 | macroF1=0.363 | best_val_loss=1.703
Fold 14 | subj 15 | n=25 | acc=0.400 | macroF1=0.337 | best_val_loss=1.652
Fold 15 | subj 16 | n=50 | acc=0.360 | macroF1=0.274 | best_val_loss=1.898
Fold 16 | subj 17 | n=25 | acc=0.280 | macroF1=0.228 | best_val_loss=1.835
Fold 17 | subj 18 | n=25 | acc=0.320 | macroF1=0.298 | best_val_loss=1.869
Fold 18 | subj 19 | n=25 | acc=0.360 | macroF1=0.236 | best_val_loss=1.987
Fold 19 | subj 20 | n=25 | acc=0.520 | macroF1=0.401 | best_val_loss=1.754
Fold 20 | subj 21 | n=25 | acc=0.640 | macroF1=0.551 | best_val_loss=1.394
Fold 21 | subj 22 | n=30 | acc=0.433 | macroF1=0.346 | best_val_loss=1.561

 ## LOSO summary 

|    |   left_out_subject |   n_val |   val_acc |   val_macro_f1 |   val_loss_best |   best_epoch |
|---:|-------------------:|--------:|----------:|---------------:|----------------:|-------------:|
|  0 |                  1 |      30 |  0.566667 |       0.482995 |         1.42667 |           48 |
|  1 |                  2 |      40 |  0.7      |       0.708796 |         1.64228 |           22 |
|  2 |                  3 |      95 |  0.694737 |       0.645437 |         1.43489 |           72 |
|  3 |                  4 |      15 |  0.533333 |       0.545714 |         1.61281 |           56 |
|  4 |                  5 |      15 |  0.8      |       0.721429 |         1.558   |           68 |
|  5 |                  6 |      15 |  0.4      |       0.373333 |         1.74284 |           27 |
|  6 |                  7 |      15 |  0.466667 |       0.428889 |         1.88726 |            1 |
|  7 |                  8 |      15 |  0.333333 |       0.28     |         1.88317 |           53 |
|  8 |                  9 |      15 |  0.466667 |       0.393333 |         1.43739 |           60 |
|  9 |                 10 |      40 |  0.55     |       0.517142 |         1.73916 |           83 |
| 10 |                 11 |      25 |  0.44     |       0.330714 |         1.96914 |           11 |
| 11 |                 12 |      25 |  0.76     |       0.734921 |         1.14831 |            2 |
| 12 |                 13 |      25 |  0.52     |       0.50641  |         1.57832 |           41 |
| 13 |                 14 |      25 |  0.48     |       0.36337  |         1.70321 |           36 |
| 14 |                 15 |      25 |  0.4      |       0.337179 |         1.65191 |           94 |
| 15 |                 16 |      50 |  0.36     |       0.273939 |         1.89791 |           49 |
| 16 |                 17 |      25 |  0.28     |       0.228205 |         1.83487 |           82 |
| 17 |                 18 |      25 |  0.32     |       0.298377 |         1.86902 |           36 |
| 18 |                 19 |      25 |  0.36     |       0.236232 |         1.9868  |           43 |
| 19 |                 20 |      25 |  0.52     |       0.40098  |         1.75426 |           62 |
| 20 |                 21 |      25 |  0.64     |       0.55098  |         1.39429 |           56 |
| 21 |                 22 |      30 |  0.433333 |       0.346032 |         1.56077 |          110 |

Mean/Std across subjects:\
val_acc     : 0.5011244019138755 +/- 0.14514272508064077 \
val_macro_f1: 0.4411094117525762 +/- 0.1575720327395439

Overall (micro over all left-out samples): \
overall_acc     : 0.5232 \
overall_macro_f1: 0.5178772620577234

Confusion matrix: \
 [[84  7 11 12 11] \
 [10 74 23 16  2] \
 [ 4 31 76  9  5] \
 [19 13 30 38 25] \
 [13  5 35 17 55]]