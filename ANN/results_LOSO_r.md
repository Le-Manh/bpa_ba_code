# Results of Right Hand

| Fold | Left out | sample of subj | Acc | MacroF1 | best val loss|
|:-------:|:--------:|--------|---------|-----------|--------------| 
Fold 00 | subj 1 | n=30 | acc=0.633 | macroF1=0.636 | best_val_loss=1.542
Fold 01 | subj 2 | n=40 | acc=0.600 | macroF1=0.581 | best_val_loss=1.779
Fold 02 | subj 3 | n=95 | acc=0.716 | macroF1=0.693 | best_val_loss=1.441
Fold 03 | subj 4 | n=15 | acc=0.533 | macroF1=0.541 | best_val_loss=1.684
Fold 04 | subj 5 | n=15 | acc=0.800 | macroF1=0.793 | best_val_loss=2.256
Fold 05 | subj 6 | n=15 | acc=0.533 | macroF1=0.497 | best_val_loss=2.302
Fold 06 | subj 7 | n=15 | acc=0.800 | macroF1=0.786 | best_val_loss=1.179
Fold 07 | subj 8 | n=15 | acc=0.533 | macroF1=0.533 | best_val_loss=1.587
Fold 08 | subj 9 | n=15 | acc=0.600 | macroF1=0.547 | best_val_loss=1.421
Fold 09 | subj 10 | n=40 | acc=0.475 | macroF1=0.482 | best_val_loss=1.899
Fold 10 | subj 11 | n=25 | acc=0.480 | macroF1=0.396 | best_val_loss=2.212
Fold 11 | subj 12 | n=25 | acc=0.800 | macroF1=0.733 | best_val_loss=1.115
Fold 12 | subj 13 | n=25 | acc=0.600 | macroF1=0.558 | best_val_loss=1.848
Fold 13 | subj 14 | n=25 | acc=0.600 | macroF1=0.607 | best_val_loss=1.580
Fold 14 | subj 15 | n=25 | acc=0.520 | macroF1=0.507 | best_val_loss=1.938
Fold 15 | subj 16 | n=50 | acc=0.380 | macroF1=0.311 | best_val_loss=2.603
Fold 16 | subj 17 | n=25 | acc=0.240 | macroF1=0.207 | best_val_loss=2.345
Fold 17 | subj 18 | n=25 | acc=0.320 | macroF1=0.213 | best_val_loss=2.345
Fold 18 | subj 19 | n=25 | acc=0.320 | macroF1=0.180 | best_val_loss=2.181
Fold 19 | subj 20 | n=25 | acc=0.520 | macroF1=0.448 | best_val_loss=1.810
Fold 20 | subj 21 | n=25 | acc=0.840 | macroF1=0.840 | best_val_loss=1.069
Fold 21 | subj 22 | n=30 | acc=0.700 | macroF1=0.699 | best_val_loss=1.604

 ## LOSO summary 

|    |   left_out_subject |   n_val |   val_acc |   val_macro_f1 |   val_loss_best |   best_epoch |
|---:|-------------------:|--------:|----------:|---------------:|----------------:|-------------:|
|  0 |                  1 |      30 |  0.633333 |       0.635758 |         1.54205 |           32 |
|  1 |                  2 |      40 |  0.6      |       0.581285 |         1.77946 |            6 |
|  2 |                  3 |      95 |  0.715789 |       0.693216 |         1.44074 |            7 |
|  3 |                  4 |      15 |  0.533333 |       0.540952 |         1.68375 |            3 |
|  4 |                  5 |      15 |  0.8      |       0.793333 |         2.25624 |            6 |
|  5 |                  6 |      15 |  0.533333 |       0.496508 |         2.30218 |           22 |
|  6 |                  7 |      15 |  0.8      |       0.785714 |         1.17922 |           64 |
|  7 |                  8 |      15 |  0.533333 |       0.533333 |         1.58697 |           18 |
|  8 |                  9 |      15 |  0.6      |       0.546667 |         1.42135 |            6 |
|  9 |                 10 |      40 |  0.475    |       0.481905 |         1.89852 |           10 |
| 10 |                 11 |      25 |  0.48     |       0.395804 |         2.21238 |           10 |
| 11 |                 12 |      25 |  0.8      |       0.733333 |         1.11536 |            2 |
| 12 |                 13 |      25 |  0.6      |       0.558333 |         1.84837 |           25 |
| 13 |                 14 |      25 |  0.6      |       0.606508 |         1.57951 |           18 |
| 14 |                 15 |      25 |  0.52     |       0.506667 |         1.93813 |            6 |
| 15 |                 16 |      50 |  0.38     |       0.31141  |         2.60291 |            1 |
| 16 |                 17 |      25 |  0.24     |       0.206664 |         2.34549 |           13 |
| 17 |                 18 |      25 |  0.32     |       0.213333 |         2.34504 |           14 |
| 18 |                 19 |      25 |  0.32     |       0.18     |         2.18079 |            7 |
| 19 |                 20 |      25 |  0.52     |       0.448312 |         1.80981 |            3 |
| 20 |                 21 |      25 |  0.84     |       0.839899 |         1.0688  |           32 |
| 21 |                 22 |      30 |  0.7      |       0.698834 |         1.60408 |           16 |

Mean/Std across subjects: \
val_acc     : 0.5701874003189792 +/- 0.16525928292725103 \
val_macro_f1: 0.5358077257276648 +/- 0.1891288757610023

Overall (micro over all left-out samples): \
overall_acc     : 0.5728 \
overall_macro_f1: 0.5722665400622979

Confusion matrix: \
 [[80  9  8 15 13] \
 [14 75 15 13  8] \
 [ 1 25 72  9 18] \
 [ 9 15 12 52 37] \
 [ 7  5 17 17 79]]