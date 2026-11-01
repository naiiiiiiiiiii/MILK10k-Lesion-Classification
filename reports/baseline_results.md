# Baseline results (auto-generated)

Target: `diagnosis_1` | classes: [np.str_('Benign'), np.str_('Indeterminate'), np.str_('Malignant')] | lesions: 5240 | features: 44 (sets: ['color_stats', 'histogram', 'texture', 'base_33', 'extended_44'])
Split (grouped by lesion_id, stratified): train 3742, val 749, test 749

## Lesions per split
| class | train | val | test |
|---|---|---|---|
| Malignant | 2595 | 519 | 520 |
| Benign | 1059 | 212 | 212 |
| Indeterminate | 88 | 18 | 17 |

## Validation (top 10 by macro-F1)
| feature_set | model | val_accuracy | val_macro_f1 | recall_Benign | recall_Indeterminate | recall_Malignant |
|---|---|---|---|---|---|---|
| extended_44 | RandomForest (balanced) | 0.776 | 0.560 | 0.575 | 0.167 | 0.879 |
| base_33 | RandomForest (balanced) | 0.762 | 0.542 | 0.547 | 0.167 | 0.871 |
| histogram | RandomForest (balanced) | 0.764 | 0.529 | 0.542 | 0.111 | 0.877 |
| extended_44 | SVM-RBF (balanced) | 0.649 | 0.497 | 0.604 | 0.556 | 0.671 |
| color_stats | RandomForest (balanced) | 0.696 | 0.486 | 0.524 | 0.167 | 0.784 |
| extended_44 | kNN k=5 | 0.724 | 0.486 | 0.368 | 0.111 | 0.890 |
| base_33 | SVM-RBF (balanced) | 0.614 | 0.472 | 0.590 | 0.500 | 0.628 |
| extended_44 | LogReg (balanced) | 0.559 | 0.451 | 0.580 | 0.722 | 0.545 |
| color_stats | kNN k=5 | 0.702 | 0.448 | 0.410 | 0.056 | 0.844 |
| base_33 | LogReg (balanced) | 0.550 | 0.442 | 0.618 | 0.556 | 0.522 |

Majority-class floor (val macro-F1): 0.273

## Selected configuration
features = `extended_44`, model = `RandomForest (balanced)`, validation macro-F1 = 0.560

## Test (evaluated once)
accuracy = 0.7543 | macro-F1 = 0.5034
recall per class = {Benign: 0.552, Indeterminate: 0.059, Malignant: 0.860}

```
               precision    recall  f1-score   support

       Benign       0.62      0.55      0.58       212
Indeterminate       0.25      0.06      0.10        17
    Malignant       0.80      0.86      0.83       520

     accuracy                           0.75       749
    macro avg       0.56      0.49      0.50       749
 weighted avg       0.74      0.75      0.74       749

```

Confusion matrix (rows = truth):
|  | pred Benign | pred Indeterminate | pred Malignant |
|---|---|---|---|
| true Benign | 117 | 1 | 94 |
| true Indeterminate | 0 | 1 | 16 |
| true Malignant | 71 | 2 | 447 |

Figures: figures/baseline_confusion_matrix_test.png, figures/baseline_validation_heatmap.png
