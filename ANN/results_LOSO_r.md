# Results of Right Hand. 2 Input

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


# Results if trying to use a single input

| Fold | Left out | sample of subj | Acc | MacroF1 | best val loss|
|:-------:|:--------:|--------|---------|-----------|--------------| 
Fold 00 | subj 1 | n=30 | acc=0.500 | macroF1=0.484 | best_val_loss=1.295
Fold 01 | subj 2 | n=40 | acc=0.550 | macroF1=0.541 | best_val_loss=1.333
Fold 02 | subj 3 | n=95 | acc=0.368 | macroF1=0.306 | best_val_loss=1.456
Fold 03 | subj 4 | n=15 | acc=0.267 | macroF1=0.175 | best_val_loss=1.847
Fold 04 | subj 5 | n=15 | acc=0.467 | macroF1=0.350 | best_val_loss=1.233
Fold 05 | subj 6 | n=15 | acc=0.467 | macroF1=0.378 | best_val_loss=1.357
Fold 06 | subj 7 | n=15 | acc=0.200 | macroF1=0.067 | best_val_loss=1.600
Fold 07 | subj 8 | n=15 | acc=0.400 | macroF1=0.306 | best_val_loss=1.551
Fold 08 | subj 9 | n=15 | acc=0.333 | macroF1=0.193 | best_val_loss=1.475
Fold 09 | subj 10 | n=40 | acc=0.300 | macroF1=0.228 | best_val_loss=1.605
Fold 10 | subj 11 | n=25 | acc=0.240 | macroF1=0.120 | best_val_loss=1.600
Fold 11 | subj 12 | n=25 | acc=0.520 | macroF1=0.441 | best_val_loss=1.405
Fold 12 | subj 13 | n=25 | acc=0.400 | macroF1=0.292 | best_val_loss=1.548
Fold 13 | subj 14 | n=25 | acc=0.200 | macroF1=0.067 | best_val_loss=1.587
Fold 14 | subj 15 | n=25 | acc=0.280 | macroF1=0.158 | best_val_loss=1.622
Fold 15 | subj 16 | n=50 | acc=0.260 | macroF1=0.195 | best_val_loss=1.615
Fold 16 | subj 17 | n=25 | acc=0.240 | macroF1=0.173 | best_val_loss=1.622
Fold 17 | subj 18 | n=25 | acc=0.120 | macroF1=0.044 | best_val_loss=1.627
Fold 18 | subj 19 | n=25 | acc=0.200 | macroF1=0.069 | best_val_loss=1.582
Fold 19 | subj 20 | n=25 | acc=0.200 | macroF1=0.080 | best_val_loss=1.598
Fold 20 | subj 21 | n=25 | acc=0.760 | macroF1=0.696 | best_val_loss=1.122
Fold 21 | subj 22 | n=30 | acc=0.300 | macroF1=0.243 | best_val_loss=1.605

 ## LOSO summary 

|    |   left_out_subject |   n_val |   val_acc |   val_macro_f1 |   val_loss_best |   best_epoch |
|---:|-------------------:|--------:|----------:|---------------:|----------------:|-------------:|
|  0 |                  1 |      30 |  0.5      |      0.483805  |         1.29519 |          108 |
|  1 |                  2 |      40 |  0.55     |      0.540952  |         1.33316 |           86 |
|  2 |                  3 |      95 |  0.368421 |      0.305834  |         1.45586 |            7 |
|  3 |                  4 |      15 |  0.266667 |      0.175     |         1.84741 |           32 |
|  4 |                  5 |      15 |  0.466667 |      0.35      |         1.23275 |           70 |
|  5 |                  6 |      15 |  0.466667 |      0.377778  |         1.35714 |          200 |
|  6 |                  7 |      15 |  0.2      |      0.0666667 |         1.60038 |            6 |
|  7 |                  8 |      15 |  0.4      |      0.305641  |         1.55142 |            6 |
|  8 |                  9 |      15 |  0.333333 |      0.192727  |         1.47497 |            7 |
|  9 |                 10 |      40 |  0.3      |      0.227954  |         1.60525 |           10 |
| 10 |                 11 |      25 |  0.24     |      0.119697  |         1.6004  |           53 |
| 11 |                 12 |      25 |  0.52     |      0.440909  |         1.40463 |            8 |
| 12 |                 13 |      25 |  0.4      |      0.292308  |         1.54773 |            8 |
| 13 |                 14 |      25 |  0.2      |      0.0666667 |         1.58657 |          124 |
| 14 |                 15 |      25 |  0.28     |      0.157576  |         1.62219 |            6 |
| 15 |                 16 |      50 |  0.26     |      0.195172  |         1.61523 |           12 |
| 16 |                 17 |      25 |  0.24     |      0.172778  |         1.62175 |           25 |
| 17 |                 18 |      25 |  0.12     |      0.0444444 |         1.62728 |           11 |
| 18 |                 19 |      25 |  0.2      |      0.0689655 |         1.58202 |           83 |
| 19 |                 20 |      25 |  0.2      |      0.08      |         1.59755 |            5 |
| 20 |                 21 |      25 |  0.76     |      0.696104  |         1.12222 |          127 |
| 21 |                 22 |      30 |  0.3      |      0.242857  |         1.60477 |            9 |

Mean/Std across subjects: \
val_acc     : 0.344170653907496 +/- 0.15175735512973829 \
val_macro_f1: 0.2547197894440054 +/- 0.17233615119121598 \

Overall (micro over all left-out samples): \
overall_acc     : 0.3472 \
overall_macro_f1: 0.3380510351384518

Confusion matrix: \
 [[70 20  8 13 14] \
 [26 49 20 15 15] \
 [26 24 39 11 25] \
 [32 14 25 24 30] \
 [24 19 25 22 35]]

# run a little window with the feature table as global

|   T |   stride |   f1_mean |   f1_std |   acc_mean |   acc_std |   n_blocks_mean |   n_windows_mean |   best_epoch_mean |
|----:|---------:|----------:|---------:|-----------:|----------:|----------------:|-----------------:|------------------:|
| 250 |      250 |  0.720554 | 0.255133 |   0.74797  |  0.228605 |         28.4091 |         125.818  |           27.7273 |
| 750 |      750 |  0.663897 | 0.242099 |   0.697998 |  0.217147 |         28.4091 |          53.6818 |           27.2273 |
| 500 |      500 |  0.661909 | 0.298949 |   0.694474 |  0.269708 |         28.4091 |          69.3636 |           30.7727 |
Best config: 250 250

## Tested if it's the amount of windows

|   T |   stride |   f1_mean |   f1_std |   acc_mean |   acc_std |   n_blocks_mean |   n_windows_mean |   best_epoch_mean |
|----:|---------:|----------:|---------:|-----------:|----------:|----------------:|-----------------:|------------------:|
| 500 |      250 |  0.716288 | 0.234328 |   0.747891 |  0.203851 |         28.4091 |          97.4091 |           32      |
| 750 |      375 |  0.704429 | 0.265259 |   0.731954 |  0.232904 |         28.4091 |          61.0455 |           29.9545 |

The amount of windows is important. Going with T=500 and stride=250