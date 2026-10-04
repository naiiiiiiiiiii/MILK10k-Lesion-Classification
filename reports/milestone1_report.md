# MILK10k Lesion Classification — Milestone 1 Report

## Label strategy

The primary target is `diagnosis_1` (Benign / Malignant / Indeterminate).
**Indeterminate is kept as a 3rd class** rather than merged or dropped:
dropping ignores that ambiguous lesions still occur at inference, merging
into Malignant inflates unnecessary workups, and merging into Benign risks
missing real malignancies. Its rarity (123/5,240 lesions, 2.3% globally)
is handled through class weighting, not by removing the class.

For the 11-class stretch target, all 11 classes are kept separate rather
than merging the rarest ones (DF, INF, VASC, BEN_OTH, MAL_OTH; all <75
lesions). Merging was rejected because four of these five are **Benign**
while **MAL_OTH is Malignant** — a merged "OTHER" bucket would mix
malignant and benign lesions under one label, which is clinically
incoherent and would corrupt the otherwise-clean 11-class→`diagnosis_1`
mapping (only `AKIEC` is genuinely ambiguous there: 180 Malignant vs. 123
Indeterminate lesions). Rarity is instead handled via class weighting,
with the caveat that `MAL_OTH` (n=9 lesions total) will have statistically
unreliable per-class metrics regardless of strategy.

## Split design and verification

Splitting is done at the **lesion** level — the atomic clinical unit,
since both of a lesion's two images (dermoscopic + clinical) share one
diagnosis. `StratifiedGroupKFold` groups by `lesion_id` and stratifies on
the 11-class label, with `seed=0`, `val_size=0.15`, `test_size=0.15`.

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

- **Full-dataset image integrity scan** (10,480 files): all rows
  resolved to an existing file, and `Image.verify()` found zero
  unreadable files. The loader raises `FileNotFoundError` by default on
  a missing file rather than silently skipping it.
- **Shortcut risk — `image_manipulation`**: cross-tabbed against
  `diagnosis_1`, "altered" images show a 12.8% Indeterminate rate vs.
  2.0% for "instrument only" (6× difference), reflecting acquisition
  practice, not biology. **Excluded from model inputs.**
- **Label-leakage columns excluded**: `diagnosis_2/3/4` (directly
  determine `diagnosis_1`), `diagnosis_confirm_type` (72% Malignant for
  histopathology-confirmed vs. 2% for clinical-assessment-only — a proxy
  for the label itself), `melanocytic` (near-deterministic function of
  class).
- **Missing values**: `age_approx` (0.4% missing) imputed with the
  train-only median; `anatom_site_general` (37.3%) and `melanocytic`
  (77.2%) encoded as an explicit "unknown" category rather than dropped,
  since missingness itself was found to be informative (NV lesions are
  11pp more common among site-missing rows).

## Preprocessing choices

- **Resolution: 224×224.** A full scan of all 10,480 images confirmed
  100% are larger than both 224px and 256px in both dimensions (every
  image is uniformly 600×450) — both choices only downsample, so 224 was
  selected for ImageNet-backbone compatibility and lower compute cost.
- **Normalization**: standard ImageNet mean/std
  (`[0.485,0.456,0.406]`/`[0.229,0.224,0.225]`).
- **Augmentations (train only)**: horizontal flip (p=0.5), vertical flip
  (p=0.5), rotation (±30°) — justified by the lack of any canonical
  lesion orientation. Brightness jitter is capped at 0.03, deliberately
  **below** the real measured Benign/Malignant brightness gap (V≈0.056,
  from a dedicated quantitative audit). **Hue jitter is excluded
  entirely**: even the mildest tested setting (0.02) produced a larger
  shift (~4.3°) than the real class hue gap (~2.4°), so any hue
  augmentation risks erasing a genuine, already-weak clinical signal.
- **Imbalance handling**: both inverse-frequency class-weighted loss
  weights and a `WeightedRandomSampler` are implemented together; the
  sampler was verified to produce near-balanced batches (20-batch
  histogram: Benign 224, Indeterminate 226, Malignant 190) despite the
  raw 29:1 train imbalance. Batch sanity checks confirmed correct shape
  `(32,3,224,224)`, dtype `float32`, and min/max values matching the
  theoretical normalization bounds exactly (-2.118/2.640).

## What could still go wrong

Several risks remain despite this pipeline. First, **residual leakage**:
even with a leak-free lesion-level split, two visually near-duplicate
images of the same lesion could still let a sufficiently expressive model
implicitly learn acquisition-specific cues rather than diagnostic
features, and evaluation must always aggregate predictions to the lesion
level, never per-image. Second, **biopsy-enrichment bias**: MILK10k is
not a random sample of lesions — it is skewed toward lesions a clinician
already suspected, producing a 69% Malignant / 28% Benign split that
inverts real-world prevalence. Any accuracy figure from this model should
not be read as real-world diagnostic performance; sensitivity/specificity
or explicit recalibration to a realistic prior are more appropriate.
Third, **unreliable rare-class metrics**: classes like `MAL_OTH` (9
lesions total) will have inherently noisy, low-confidence per-class
metrics regardless of split or weighting strategy — a clinician should
treat this model's performance on rare categories as unproven. Finally,
demographic and acquisition-device representativeness have not been
audited in this milestone and remain an open risk for generalization
beyond this dataset's specific population and equipment.
