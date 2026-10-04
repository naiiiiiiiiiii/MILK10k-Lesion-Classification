# Data Quality Report — MILK10k

Generated: 2026-10-04

## 1. Missing-value handling decisions

| Column | Missing (n) | Missing (%) | Decision |
|---|---|---|---|
| age_approx | 40 | 0.4% | impute (median, train-only) |
| anatom_site_general | 3912 | 37.3% | 'unknown' category |
| anatom_site_special | 10274 | 98.0% | drop column (too sparse to use) |
| diagnosis_3 | 158 | 1.5% | leave NaN (not used as model input; label-hierarchy field only) |
| diagnosis_4 | 8958 | 85.5% | leave NaN (not used as model input; label-hierarchy field only) |
| melanocytic | 8088 | 77.2% | 'unknown' category |

## 2. Label-consistency checks

- Exactly 2 images per lesion: **0 violations** out of 5240 lesions (PASS)
- One dermoscopic + one clinical image per lesion: **0 violations** out of 5240 lesions (PASS)

## 3. Suspicious shortcut checks

### image_manipulation vs diagnosis_1 (row %)

| image_manipulation | Benign | Indeterminate | Malignant |
|---|---|---|---|
| altered | 39.7 | 12.8 | 47.5 |
| instrument only | 27.9 | 2.0 | 70.1 |

**Conclusion:** `image_manipulation` is strongly associated with `diagnosis_1` -- 'altered' images show a 12.8% Indeterminate rate vs. 2.0% for 'instrument only' (6x difference), plus a notably different Benign/Malignant split. This reflects acquisition/documentation practice, not lesion biology, and is a clear shortcut risk: `image_manipulation` must NOT be used as a model input.

### image_type vs diagnosis_1 (row %)

| image_type | Benign | Indeterminate | Malignant |
|---|---|---|---|
| clinical: close-up | 28.3 | 2.3 | 69.4 |
| dermoscopic | 28.3 | 2.3 | 69.4 |

**Conclusion:** No difference between dermoscopic and clinical rows -- expected, since every lesion contributes exactly one image of each type, so the diagnosis_1 distribution is identical by construction. Not a shortcut risk.

## 4. Columns excluded from model inputs (label leakage)

| Column | Reason excluded |
|---|---|
| diagnosis_2 | intermediate label in the diagnosis hierarchy -- directly determines diagnosis_1 |
| diagnosis_3 | finer label in the hierarchy -- directly determines diagnosis_1/2 |
| diagnosis_4 | finest label in the hierarchy -- directly determines diagnosis_1/2/3 |
| diagnosis_confirm_type | proxy for the label itself (histopathology-confirmed lesions are 72% Malignant vs. 2% for clinical-assessment-only, see B2/A1.2 Q5) |
| image_manipulation | correlated with diagnosis_1 for acquisition/documentation reasons, not biology (see shortcut check above) |
| melanocytic | near-deterministic function of the 11-class label (e.g. melanocytic lesions are NV/MEL by definition) |
| lesion_id / isic_id | identifiers, not features |
