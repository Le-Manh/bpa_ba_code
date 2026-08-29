# Results first run

| Fold | Left out | sample of subj | Acc | MacroF1 | best val loss|
|:-------:|:--------:|--------|---------|-----------|--------------| 
Fold 00 | subj 1 | n=60 | acc=0.617 | macroF1=0.602 | best_val_loss=1.315
Fold 01 | subj 2 | n=80 | acc=0.362 | macroF1=0.360 | best_val_loss=2.224
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

# Results if trying to use a single input

| Fold | Left out | sample of subj | Acc | MacroF1 | best val loss|
|:-------:|:--------:|--------|---------|-----------|--------------| 
Fold 00 | subj 1 | n=60 | acc=0.233 | macroF1=0.198 | best_val_loss=1.596
Fold 01 | subj 2 | n=80 | acc=0.312 | macroF1=0.279 | best_val_loss=1.606
Fold 02 | subj 3 | n=190 | acc=0.321 | macroF1=0.275 | best_val_loss=1.552
Fold 03 | subj 4 | n=30 | acc=0.233 | macroF1=0.128 | best_val_loss=1.826
Fold 04 | subj 5 | n=30 | acc=0.367 | macroF1=0.314 | best_val_loss=1.649
Fold 05 | subj 6 | n=30 | acc=0.367 | macroF1=0.308 | best_val_loss=1.461
Fold 06 | subj 7 | n=30 | acc=0.300 | macroF1=0.211 | best_val_loss=1.587
Fold 07 | subj 8 | n=35 | acc=0.314 | macroF1=0.289 | best_val_loss=1.595
Fold 08 | subj 9 | n=30 | acc=0.300 | macroF1=0.221 | best_val_loss=1.582
Fold 09 | subj 10 | n=75 | acc=0.293 | macroF1=0.215 | best_val_loss=1.615
Fold 10 | subj 11 | n=50 | acc=0.280 | macroF1=0.181 | best_val_loss=1.623
Fold 11 | subj 12 | n=55 | acc=0.400 | macroF1=0.331 | best_val_loss=1.485
Fold 12 | subj 13 | n=50 | acc=0.260 | macroF1=0.182 | best_val_loss=1.606
Fold 13 | subj 14 | n=50 | acc=0.220 | macroF1=0.104 | best_val_loss=1.598
Fold 14 | subj 15 | n=50 | acc=0.240 | macroF1=0.157 | best_val_loss=1.630
Fold 15 | subj 16 | n=100 | acc=0.250 | macroF1=0.201 | best_val_loss=1.644
Fold 16 | subj 17 | n=50 | acc=0.200 | macroF1=0.069 | best_val_loss=1.630
Fold 17 | subj 18 | n=50 | acc=0.220 | macroF1=0.105 | best_val_loss=1.613
Fold 18 | subj 19 | n=50 | acc=0.300 | macroF1=0.243 | best_val_loss=1.613
Fold 19 | subj 20 | n=50 | acc=0.220 | macroF1=0.145 | best_val_loss=1.661
Fold 20 | subj 21 | n=50 | acc=0.620 | macroF1=0.613 | best_val_loss=1.271
Fold 21 | subj 22 | n=55 | acc=0.218 | macroF1=0.102 | best_val_loss=1.619

 ## LOSO summary 

|    |   left_out_subject |   n_val |   val_acc |   val_macro_f1 |   val_loss_best |   best_epoch |
|---:|-------------------:|--------:|----------:|---------------:|----------------:|-------------:|
|  0 |                  1 |      60 |  0.233333 |      0.197784  |         1.59623 |            5 |
|  1 |                  2 |      80 |  0.3125   |      0.278915  |         1.60645 |           20 |
|  2 |                  3 |     190 |  0.321053 |      0.274676  |         1.55242 |            5 |
|  3 |                  4 |      30 |  0.233333 |      0.127731  |         1.82643 |           14 |
|  4 |                  5 |      30 |  0.366667 |      0.313853  |         1.6487  |           18 |
|  5 |                  6 |      30 |  0.366667 |      0.30811   |         1.46123 |           24 |
|  6 |                  7 |      30 |  0.3      |      0.210753  |         1.5868  |            4 |
|  7 |                  8 |      35 |  0.314286 |      0.288889  |         1.59486 |            3 |
|  8 |                  9 |      30 |  0.3      |      0.220952  |         1.58245 |            6 |
|  9 |                 10 |      75 |  0.293333 |      0.215388  |         1.61478 |            5 |
| 10 |                 11 |      50 |  0.28     |      0.181462  |         1.62348 |           31 |
| 11 |                 12 |      55 |  0.4      |      0.331111  |         1.48549 |            3 |
| 12 |                 13 |      50 |  0.26     |      0.182395  |         1.6057  |            5 |
| 13 |                 14 |      50 |  0.22     |      0.10416   |         1.5985  |          103 |
| 14 |                 15 |      50 |  0.24     |      0.157477  |         1.62954 |            5 |
| 15 |                 16 |     100 |  0.25     |      0.200742  |         1.64425 |            6 |
| 16 |                 17 |      50 |  0.2      |      0.0689655 |         1.62975 |           17 |
| 17 |                 18 |      50 |  0.22     |      0.105329  |         1.61331 |           72 |
| 18 |                 19 |      50 |  0.3      |      0.243118  |         1.6129  |           53 |
| 19 |                 20 |      50 |  0.22     |      0.145436  |         1.66058 |           12 |
| 20 |                 21 |      50 |  0.62     |      0.612926  |         1.27107 |          119 |
| 21 |                 22 |      55 |  0.218182 |      0.102083  |         1.6188  |            3 |

Mean/Std across subjects: \
val_acc     : 0.2940615226081733 +/- 0.09108973616457669 \
val_macro_f1: 0.22146620347850973 +/- 0.11549885637446855

Overall (micro over all left-out samples): \
overall_acc     : 0.2936 \
overall_macro_f1: 0.29044051184730446

Confusion matrix: \
 [[105  39  25  44  37] \
 [ 42  76  45  39  48] \
 [ 47  48  78  35  42] \
 [ 45  37  52  43  73] \
 [ 43  41  64  37  65]]

# run a little window with the feature table as global
This is the same as on the right hand
|   T |   stride |   f1_mean |   f1_std |   acc_mean |   acc_std |   n_blocks_mean |   n_windows_mean |   best_epoch_mean |
|----:|---------:|----------:|---------:|-----------:|----------:|----------------:|-----------------:|------------------:|
| 500 |      250 |  0.838562 | 0.189894 |   0.848353 |  0.17799  |         56.8182 |          198.364 |           62.1818 |
| 250 |      250 |  0.835324 | 0.197207 |   0.847426 |  0.176799 |         56.8182 |          255.136 |           58.5909 |
| 500 |      500 |  0.804774 | 0.228507 |   0.817204 |  0.212927 |         56.8182 |          140.409 |           65.4091 |
Best config: 500 250
and somehow it is even better

## Tested without time_data
Put the Time_data to zeros to see which Branch is dominating:
=== Running LOSO for T=500, stride=250 (opt: macroF1_block) ===
[Fold 00] est windows: train=4096 (avg 3.44/block), val=268 (avg 4.47/block)
E0000 00:00:1788031942.527296 1037714 cuda_platform.cc:52] failed call to cuInit: INTERNAL: CUDA error: Failed call to cuInit: UNKNOWN ERROR (303)
Fold 00 | subj 1 | blocks=60 windows=268 | acc_block=1.000 | macroF1_block=1.000
[Fold 01] est windows: train=4044 (avg 3.46/block), val=320 (avg 4.00/block)
Fold 01 | subj 2 | blocks=80 windows=320 | acc_block=1.000 | macroF1_block=1.000
[Fold 02] est windows: train=3814 (avg 3.60/block), val=550 (avg 2.89/block)
Fold 02 | subj 3 | blocks=190 windows=550 | acc_block=0.695 | macroF1_block=0.699
[Fold 03] est windows: train=4241 (avg 3.48/block), val=123 (avg 4.10/block)
Fold 03 | subj 4 | blocks=30 windows=123 | acc_block=0.500 | macroF1_block=0.500
[Fold 04] est windows: train=4270 (avg 3.50/block), val=94 (avg 3.13/block)
Fold 04 | subj 5 | blocks=30 windows=94 | acc_block=1.000 | macroF1_block=1.000
[Fold 05] est windows: train=4247 (avg 3.48/block), val=117 (avg 3.90/block)
Fold 05 | subj 6 | blocks=30 windows=117 | acc_block=0.833 | macroF1_block=0.798
[Fold 06] est windows: train=4266 (avg 3.50/block), val=98 (avg 3.27/block)
Fold 06 | subj 7 | blocks=30 windows=98 | acc_block=1.000 | macroF1_block=1.000
[Fold 07] est windows: train=4268 (avg 3.51/block), val=96 (avg 2.74/block)
Fold 07 | subj 8 | blocks=35 windows=96 | acc_block=0.857 | macroF1_block=0.836
[Fold 08] est windows: train=4272 (avg 3.50/block), val=92 (avg 3.07/block)
Fold 08 | subj 9 | blocks=30 windows=92 | acc_block=1.000 | macroF1_block=1.000
[Fold 09] est windows: train=4127 (avg 3.51/block), val=237 (avg 3.16/block)
Fold 09 | subj 10 | blocks=75 windows=237 | acc_block=1.000 | macroF1_block=1.000
[Fold 10] est windows: train=4214 (avg 3.51/block), val=150 (avg 3.00/block)
Fold 10 | subj 11 | blocks=50 windows=150 | acc_block=0.900 | macroF1_block=0.893
[Fold 11] est windows: train=4227 (avg 3.54/block), val=137 (avg 2.49/block)
Fold 11 | subj 12 | blocks=55 windows=137 | acc_block=0.709 | macroF1_block=0.653
[Fold 12] est windows: train=4203 (avg 3.50/block), val=161 (avg 3.22/block)
Fold 12 | subj 13 | blocks=50 windows=161 | acc_block=0.700 | macroF1_block=0.713
[Fold 13] est windows: train=4239 (avg 3.53/block), val=125 (avg 2.50/block)
Fold 13 | subj 14 | blocks=50 windows=125 | acc_block=0.600 | macroF1_block=0.467
[Fold 14] est windows: train=4199 (avg 3.50/block), val=165 (avg 3.30/block)
Fold 14 | subj 15 | blocks=50 windows=165 | acc_block=0.500 | macroF1_block=0.500
[Fold 15] est windows: train=3983 (avg 3.46/block), val=381 (avg 3.81/block)
Fold 15 | subj 16 | blocks=100 windows=381 | acc_block=0.650 | macroF1_block=0.629
[Fold 16] est windows: train=4216 (avg 3.51/block), val=148 (avg 2.96/block)
Fold 16 | subj 17 | blocks=50 windows=148 | acc_block=1.000 | macroF1_block=1.000
[Fold 17] est windows: train=4070 (avg 3.39/block), val=294 (avg 5.88/block)
Fold 17 | subj 18 | blocks=50 windows=294 | acc_block=1.000 | macroF1_block=1.000
[Fold 18] est windows: train=4165 (avg 3.47/block), val=199 (avg 3.98/block)
Fold 18 | subj 19 | blocks=50 windows=199 | acc_block=0.900 | macroF1_block=0.893
[Fold 19] est windows: train=4139 (avg 3.45/block), val=225 (avg 4.50/block)
Fold 19 | subj 20 | blocks=50 windows=225 | acc_block=1.000 | macroF1_block=1.000
[Fold 20] est windows: train=4129 (avg 3.44/block), val=235 (avg 4.70/block)
Fold 20 | subj 21 | blocks=50 windows=235 | acc_block=1.000 | macroF1_block=1.000
[Fold 21] est windows: train=4215 (avg 3.53/block), val=149 (avg 2.71/block)
Fold 21 | subj 22 | blocks=55 windows=149 | acc_block=0.818 | macroF1_block=0.808
|   T |   stride |   f1_mean |   f1_std |   acc_mean |   acc_std |   n_blocks_mean |   n_windows_mean |   best_epoch_mean |
|----:|---------:|----------:|---------:|-----------:|----------:|----------------:|-----------------:|------------------:|
| 500 |      250 |  0.835921 | 0.189008 |   0.848295 |  0.175287 |         56.8182 |          198.364 |           62.1818 |
Best config: 500 250

It does like the whole work

## Tested with stable tsfel
|   T |   stride |   f1_mean |   f1_std |   acc_mean |   acc_std |   n_blocks_mean |   n_windows_mean |   best_epoch_mean |
|----:|---------:|----------:|---------:|-----------:|----------:|----------------:|-----------------:|------------------:|
| 250 |      250 |  0.837456 | 0.19557  |   0.847761 |  0.176858 |         56.8182 |          255.136 |           54.8636 |
| 500 |      500 |  0.833033 | 0.184895 |   0.842057 |  0.168651 |         56.8182 |          140.409 |           60.4091 |
| 500 |      250 |  0.81988  | 0.20632  |   0.837009 |  0.183461 |         56.8182 |          198.364 |           52.0909 |
Best config: 250 250

This time TSFEL has been build with an window of 2000 Samples every time so the Arduino builds TSFEL more consistent