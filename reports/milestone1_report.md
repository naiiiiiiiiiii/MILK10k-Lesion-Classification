# MILK10k Lesion Classification — Milestone 1 Report

## Label strategy

The main objective is the classification of `diagnosis_1` (Benign / Malignant / Indeterminate).
**Indeterminate is maintained as a separate group** and is not removed or merged: removing does not account for the presence of lesions that can be ambiguous in nature at the time of interpretation, merging with the Malignant group brings about the workload that is not necessary, while merging with the Benign class may lead to loss of the malignant lesions.
In order not to lose out on the classification class, the fact that it is rare (123/5,240 lesions, 2.3% globally) is dealt with through class-weighting.

The creation of an 11-class target will ensure that all classes remain separate rather than combining the rarest classes (DF, INF, VASC, BEN_OTH, MAL_OTH, all below 75 lesions). Class combination is not optimal for four of these five classes since they are **Benign**, and **MAL_OTH** is malignant. However, because malignant and benign tumors would get mixed in one bucket in case of combination, it would violate clinical protocol to maintain a clear mapping during the process of diagnosis. It needs to be stated that even though rarity is maintained by assigning class weights, `MAL_OTH` (N=9 lesions) will not be statistically reliable.

## Split design and verification

The process of splitting occurs at the **lesion** level, which is the smallest clinical unit because both representations of a lesion (dermoscopic and clinical) carry the same diagnosis. `StratifiedGroupKFold` takes into account both the `lesion_id` while grouping instances and ensures that the instances split correspond to their class labels across the 11 classes with `seed=0`, `val_size=0.15`, and `test_size=0.15`.

Verification results (full dataset, 5,240 lesions / 10,480 images):
- **Zero lesion_id overlap** between every pair of splits.
- **Zero lesions** with ≠2 images within their assigned split.
- **Max class-proportion deviation from global: 0.09 percentage points**
  across all 11 classes (e.g. BCC: 48.16% train vs. 48.13% global).
- `diagnosis_1` proportions are near-identical across splits (Malignant
  69.35/69.43/69.29%, Benign 28.27/28.30/28.44%, Indeterminate
  2.38/2.27/2.27% for train/val/test).
- Split sizes: train = 3,742 lesions (7,484 images), val = test = 749
  lesions (1,498 images each).

## Imbalance ratio on TRAIN

- **11-class**: BCC (3,604 images) vs. MAL_OTH (14 images) — a
  **257.4:1** ratio.
- **diagnosis_1**: Malignant (5,190) vs. Indeterminate (178) — a
  **29.2:1** ratio. The loader's computed loss weights reflect this:
  Benign=1.18, Indeterminate=14.02, Malignant=0.48.

Both ratios are severe enough that unweighted training would likely
collapse rare-class recall toward zero, motivating the dual
imbalance-handling strategy below.

## Quality issues found and handling

- **Full-dataset image integrity scan** (10,480 files): all rows were referred to an available file, while `Image.verify()` detected zero unreadable files. The loader throws `FileNotFoundError` by default if it fails to find a missing file rather than ignoring it completely.
- **The risk of shortcutting — `image_manipulation`**: when compared with `diagnosis_1`, "altered" images demonstrate a 12.8% Indeterminate score vs. 2.0% for "instrument only" (6× difference), which indicates the practice of acquisition, not biology. **Excluded from model inputs.**
- **Columns with label leakage excluded**: `diagnosis_2/3/4` (directly dictate `diagnosis_1`), `diagnosis_confirm_type` (72% Malignant for those confirmed by histopathology vs. 2% for those determined clinically — a proxy for the label itself), `melanocytic` (more or less deterministic function of the class).
- **Missing data**: `age_approx` (0.4% missing) filled with the median from train-only; `anatom_site_general` (37.3%) and `melanocytic` (77.2%) considered as "unknown" category rather than removed, as missingness alone was informative (NV lesions occurred 11pp more on the rows with missing site).

## Preprocessing choices

- **Resolution: 224×224.** A full scan of all 10,480 images confirmed 100% are larger than both 224px and 256px in both dimensions (every image is uniformly 600×450) — both choices only downsample, so 224 was selected for ImageNet-backbone compatibility and lower compute cost.
- **Normalization**: standard ImageNet mean/std (`[0.485,0.456,0.406]`/`[0.229,0.224,0.225]`).
- **Augmentations (train only)**: horizontal flip (p=0.5), vertical flip (p=0.5), rotation (±30°) — justified by the lack of any canonical lesion orientation. Brightness jitter is capped at 0.03, deliberately **below** the real measured Benign/Malignant brightness gap (V≈0.056, from a dedicated quantitative audit). **Hue jitter is excluded entirely**: even the mildest tested setting (0.02) produced a larger shift (~4.3°) than the real class hue gap (~2.4°), so any hue augmentation risks erasing a genuine, already-weak clinical signal.
- **Imbalance handling**: both inverse-frequency class-weighted loss weights and a `WeightedRandomSampler` are implemented together; the sampler was verified to produce near-balanced batches (20-batch histogram: Benign 224, Indeterminate 226, Malignant 190) despite the raw 29:1 train imbalance. Batch sanity checks confirmed correct shape `(32,3,224,224)`, dtype `float32`, and min/max values matching the theoretical normalization bounds exactly (-2.118/2.640).

## What could still go wrong

In spite of this pipeline, there are still various risks. First, **residual leakage**: even in the absence of any leakage at the lesion level, if two nearly identical images are taken of the same lesion, a model that is powerful enough could learn to extract the features associated with different acquisition processes instead of those relevant for diagnosis, therefore requiring the aggregation of the predictions at the lesion level rather than at the image level. Second, **biopsy-enrichment bias**: MILK10k does not constitute a random selection of lesions; it contains a significant number of lesions that doctors suspected were harmful, which leads to a composed data set with 69% malignant and only 28% benign cases that depending on the data set can be the opposite of reality. While any performance number generated by this model could not be construed as a true diagnostic measure in the real-world applications of sensitivity/specificity and calibrating to realistic priors, there are some serious issues with those **unreliable rare-class metrics** present in the classes where our targets would be `MAL_OTH` (only total of 9 lesions being present), and across the board, the outputs would be very noisy and uncertain whenever we looked at the performances of several models that were not weighted properly.