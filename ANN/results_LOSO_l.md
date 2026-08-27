# Results of Left Hand

| Fold | Left out | sample of subj | Acc | MacroF1 | best val loss|
|:-------:|:--------:|--------|---------|-----------|--------------| 
Fold 00 | subj 1 | n=30 | acc=0.433 | macroF1=0.361 | best_val_loss=1.665
Fold 01 | subj 2 | n=40 | acc=0.275 | macroF1=0.210 | best_val_loss=2.276
Fold 02 | subj 3 | n=95 | acc=0.663 | macroF1=0.633 | best_val_loss=1.639
Fold 03 | subj 4 | n=15 | acc=0.600 | macroF1=0.541 | best_val_loss=1.811
Fold 04 | subj 5 | n=15 | acc=0.267 | macroF1=0.171 | best_val_loss=2.059
Fold 05 | subj 6 | n=15 | acc=0.467 | macroF1=0.364 | best_val_loss=1.786
Fold 06 | subj 7 | n=15 | acc=0.533 | macroF1=0.540 | best_val_loss=1.695
Fold 07 | subj 8 | n=20 | acc=0.550 | macroF1=0.483 | best_val_loss=1.772
Fold 08 | subj 9 | n=15 | acc=0.467 | macroF1=0.398 | best_val_loss=1.652
Fold 09 | subj 10 | n=35 | acc=0.486 | macroF1=0.450 | best_val_loss=1.714
Fold 10 | subj 11 | n=25 | acc=0.280 | macroF1=0.248 | best_val_loss=2.437
Fold 11 | subj 12 | n=30 | acc=0.867 | macroF1=0.858 | best_val_loss=1.291
Fold 12 | subj 13 | n=25 | acc=0.480 | macroF1=0.415 | best_val_loss=2.095
Fold 13 | subj 14 | n=25 | acc=0.520 | macroF1=0.503 | best_val_loss=1.601
Fold 14 | subj 15 | n=25 | acc=0.360 | macroF1=0.360 | best_val_loss=1.906
Fold 15 | subj 16 | n=50 | acc=0.240 | macroF1=0.136 | best_val_loss=2.009
Fold 16 | subj 17 | n=25 | acc=0.200 | macroF1=0.067 | best_val_loss=2.490
Fold 17 | subj 18 | n=25 | acc=0.360 | macroF1=0.335 | best_val_loss=1.640
Fold 18 | subj 19 | n=25 | acc=0.400 | macroF1=0.362 | best_val_loss=1.799
Fold 19 | subj 20 | n=25 | acc=0.360 | macroF1=0.297 | best_val_loss=2.050
Fold 20 | subj 21 | n=25 | acc=0.680 | macroF1=0.614 | best_val_loss=1.530
Fold 21 | subj 22 | n=25 | acc=0.520 | macroF1=0.496 | best_val_loss=1.459

 ## LOSO summary 
Note: 200 was the end epoch. It did not train after that. 

|    |   left_out_subject |   n_val |   val_acc |   val_macro_f1 |   val_loss_best |   best_epoch |
|---:|-------------------:|--------:|----------:|---------------:|----------------:|-------------:|
|  0 |                  1 |      30 |  0.433333 |      0.361425  |         1.66488 |           49 |
|  1 |                  2 |      40 |  0.275    |      0.209697  |         2.27585 |           17 |
|  2 |                  3 |      95 |  0.663158 |      0.632506  |         1.6395  |          176 |
|  3 |                  4 |      15 |  0.6      |      0.540952  |         1.81139 |            6 |
|  4 |                  5 |      15 |  0.266667 |      0.170588  |         2.05874 |           23 |
|  5 |                  6 |      15 |  0.466667 |      0.363736  |         1.78631 |           66 |
|  6 |                  7 |      15 |  0.533333 |      0.54      |         1.69453 |            5 |
|  7 |                  8 |      20 |  0.55     |      0.483175  |         1.77236 |           37 |
|  8 |                  9 |      15 |  0.466667 |      0.397619  |         1.65161 |           63 |
|  9 |                 10 |      35 |  0.485714 |      0.449676  |         1.7143  |           60 |
| 10 |                 11 |      25 |  0.28     |      0.247619  |         2.43742 |            1 |
| 11 |                 12 |      30 |  0.866667 |      0.857862  |         1.29123 |            3 |
| 12 |                 13 |      25 |  0.48     |      0.41533   |         2.09459 |           10 |
| 13 |                 14 |      25 |  0.52     |      0.503333  |         1.60117 |          200 |
| 14 |                 15 |      25 |  0.36     |      0.360476  |         1.90579 |           31 |
| 15 |                 16 |      50 |  0.24     |      0.135632  |         2.00922 |           34 |
| 16 |                 17 |      25 |  0.2      |      0.0666667 |         2.48989 |           16 |
| 17 |                 18 |      25 |  0.36     |      0.335123  |         1.64048 |           65 |
| 18 |                 19 |      25 |  0.4      |      0.361616  |         1.79874 |          113 |
| 19 |                 20 |      25 |  0.36     |      0.296667  |         2.04976 |           40 |
| 20 |                 21 |      25 |  0.68     |      0.613751  |         1.52952 |          132 |
| 21 |                 22 |      25 |  0.52     |      0.496154  |         1.45859 |           78 |

Mean/Std across subjects: \
val_acc     : 0.4548729778992937 +/- 0.16186625699034757
val_macro_f1: 0.4018002184512003 +/- 0.18154418954362447

Overall (micro over all left-out samples): \
overall_acc     : 0.4672 \
overall_macro_f1: 0.45124148574922673

Confusion matrix: \
 [[73 15 15  8 14] \
 [16 77 19  7  6] \
 [18 30 61  3 13] \
 [25 19 25 22 34] \
 [25  9 22 10 59]]
