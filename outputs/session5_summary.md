# Session 5 - baseline summary

- Target: diagnosis_1 (Benign, Indeterminate, Malignant)
- Selected on validation: features = extended_44, model = RandomForest (balanced), val macro-F1 = 0.560
- class_weight: balanced
- Test accuracy: 0.7543 | Test macro-F1: 0.5034
- Test recall: Benign: 0.552, Indeterminate: 0.059, Malignant: 0.860
- Majority-class baseline: accuracy 0.694, macro-F1 0.273
- Course reference (random forest): val 0.534, test 0.495
