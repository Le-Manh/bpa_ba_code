# Results first run

| Fold | Left out | sample of subj | Acc | MacroF1 | best val loss|
|:-------:|:--------:|--------|---------|-----------|--------------| 
Fold 00 |  subj 1  | n=60 | acc=0.467 | macroF1=0.399 | best_val_loss=1.425
Fold 01 |  subj 2  | n=80 | acc=0.475 | macroF1=0.475 | best_val_loss=1.959
Fold 02 |  subj 3  | n=190 | acc=0.616 | macroF1=0.565 | best_val_loss=1.382
Fold 03 |  subj 4  | n=30 | acc=0.300 | macroF1=0.291 | best_val_loss=1.656
Fold 04 |  subj 5  | n=30 | acc=0.600 | macroF1=0.627 | best_val_loss=1.422
Fold 05 |  subj 6  | n=30 | acc=0.433 | macroF1=0.443 | best_val_loss=1.713
Fold 06 |  subj 7  | n=30 | acc=0.533 | macroF1=0.512 | best_val_loss=1.419
Fold 07 |  subj 8  | n=35 | acc=0.457 | macroF1=0.429 | best_val_loss=1.444
Fold 08 |  subj 9  | n=30 | acc=0.400 | macroF1=0.353 | best_val_loss=1.399
Fold 09 | subj 10  | n=75 | acc=0.453 | macroF1=0.437 | best_val_loss=1.635
Fold 10 | subj 11  | n=50 | acc=0.340 | macroF1=0.270 | best_val_loss=1.769
Fold 11 | subj 12  | n=55 | acc=0.764 | macroF1=0.745 | best_val_loss=1.294
Fold 12 | subj 13  | n=50 | acc=0.460 | macroF1=0.449 | best_val_loss=1.787
Fold 13 | subj 14  | n=50 | acc=0.360 | macroF1=0.303 | best_val_loss=1.599
Fold 14 | subj 15  | n=50 | acc=0.340 | macroF1=0.300 | best_val_loss=1.664
Fold 15 | subj 16  | n=100 | acc=0.270 | macroF1=0.200 | best_val_loss=1.914
Fold 16 | subj 17  | n=50 | acc=0.200 | macroF1=0.092 | best_val_loss=1.933
Fold 17 | subj 18  | n=50 | acc=0.260 | macroF1=0.237 | best_val_loss=1.813
Fold 18 | subj 19  | n=50 | acc=0.300 | macroF1=0.167 | best_val_loss=2.035
Fold 19 | subj 20  | n=50 | acc=0.400 | macroF1=0.325 | best_val_loss=1.866
Fold 20 | subj 21  | n=50 | acc=0.660 | macroF1=0.588 | best_val_loss=1.432
Fold 21 | subj 22  | n=55 | acc=0.473 | macroF1=0.438 | best_val_loss=1.445

## LOSO summary
|    |   left_out_subject |   n_val |   val_acc |   val_macro_f1 |   val_loss_best |   best_epoch |
|---:|-------------------:|--------:|----------:|---------------:|----------------:|-------------:|
|  0 |                  1 |      60 |  0.466667 |      0.398503  |         1.42518 |          111 |
|  1 |                  2 |      80 |  0.475    |      0.475203  |         1.95934 |           18 |
|  2 |                  3 |     190 |  0.615789 |      0.565175  |         1.38171 |           56 |
|  3 |                  4 |      30 |  0.3      |      0.291467  |         1.65625 |           45 |
|  4 |                  5 |      30 |  0.6      |      0.626998  |         1.42227 |           70 |
|  5 |                  6 |      30 |  0.433333 |      0.442883  |         1.71301 |           51 |
|  6 |                  7 |      30 |  0.533333 |      0.511818  |         1.41876 |           74 |
|  7 |                  8 |      35 |  0.457143 |      0.428791  |         1.4436  |           66 |
|  8 |                  9 |      30 |  0.4      |      0.35254   |         1.39949 |           58 |
|  9 |                 10 |      75 |  0.453333 |      0.437115  |         1.63505 |           70 |
| 10 |                 11 |      50 |  0.34     |      0.269699  |         1.76863 |           67 |
| 11 |                 12 |      55 |  0.763636 |      0.745299  |         1.29438 |            2 |
| 12 |                 13 |      50 |  0.46     |      0.44868   |         1.78699 |           45 |
| 13 |                 14 |      50 |  0.36     |      0.30289   |         1.59891 |           91 |
| 14 |                 15 |      50 |  0.34     |      0.300006  |         1.66364 |           72 |
| 15 |                 16 |     100 |  0.27     |      0.200177  |         1.91391 |           27 |
| 16 |                 17 |      50 |  0.2      |      0.0921212 |         1.93282 |           43 |
| 17 |                 18 |      50 |  0.26     |      0.237296  |         1.81268 |           45 |
| 18 |                 19 |      50 |  0.3      |      0.166667  |         2.03485 |           45 |
| 19 |                 20 |      50 |  0.4      |      0.325333  |         1.86646 |           37 |
| 20 |                 21 |      50 |  0.66     |      0.588412  |         1.43185 |           79 |
| 21 |                 22 |      55 |  0.472727 |      0.438279  |         1.44505 |           98 |

Mean/Std across subjects: \
val_acc     : 0.43458921062988054 +/- 0.13961387998711697 \
val_macro_f1: 0.3929706022111395 +/- 0.15888690862992208

Overall (micro over all left-out samples): \
overall_acc     : 0.4496 \
overall_macro_f1: 0.43790100889751554

Confusion matrix: \
 [[132  49  23  22  24] \
 [ 35 157  33  15  10] \
 [ 11  82 122  16  19] \
 [ 37  57  46  51  59] \
 [ 34  41  56  19 100]] 