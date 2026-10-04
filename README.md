# MILK10k Lesion Classification — Milestone 1

## 1. What this project is

**Task.** Predict `diagnosis_1` — a 3-class skin lesion diagnosis (`Benign` /
`Malignant` / `Indeterminate`) — from a dermoscopic image of a skin lesion,
optionally combined with its matching clinical close-up image and simple
patient metadata (age, sex, anatomical site). As a stretch goal, the same
pipeline also supports predicting the finer-grained 11-class diagnosis
scheme (`AKIEC`, `BCC`, `BEN_OTH`, `BKL`, `DF`, `INF`, `MAL_OTH`, `MEL`,
`NV`, `SCCKA`, `VASC`), from which `diagnosis_1` can mostly — but not
always — be derived (see Key Decisions below).

**Dataset.** [MILK10k](https://challenge.isic-archive.com/) — provided by
the MILK study team, licensed `CC-BY-NC`. 5,240 lesions, each with exactly
two images (one dermoscopic, one clinical close-up), for 10,480 images
total. Metadata includes age, sex, anatomical site, diagnosis hierarchy
(`diagnosis_1` → `diagnosis_2` → `diagnosis_3`), and acquisition details
(image type, manipulation flag, confirmation type).

**Goal of Milestone 1.** Turn the exploratory Session 2 code (metadata
analysis, preprocessing, data loader, visualizer) into a **leak-free,
reproducible pipeline**: a lesion-level train/val/test split that never
puts both images of a lesion on different sides of a split, a documented
label strategy, train-only-fitted preprocessing statistics, a
`Dataset`/`DataLoader` that returns one item per lesion, and automated
tests that catch regressions in all of the above.

---

## 2. How to set it up and run it

**Python version:** 3.11 (matches the project venv; see `pyvenv.cfg`).

**Install dependencies:**
```bash
python3.11 -m venv venv
source venv/bin/activate          # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Get the data.** Download MILK10k (`metadata.csv`, `images/`,
`supplements/training_gt.csv`, `licenses/`, `attribution.txt`) and place
it anywhere on disk. Point the code at it with a **single environment
variable** — nothing in this repo hard-codes a path:
```bash
export MILK10K_DIR=/path/to/milk10k   # folder containing metadata.csv, images/, supplements/
```
If `MILK10K_DIR` is not set, the code falls back to `./data/milk10k`
relative to the repo root (see `src/config.py`).

**Reproduce the splits, figures and tests:**
```bash
# 1. Build the leak-free lesion-level train/val/test split (writes outputs/splits/)
python -m src.data.splits --seed 0 --val-size 0.15 --test-size 0.15

# 2. Regenerate exploratory figures (writes outputs/figures/)
python -m src.eda --out outputs/figures

# 3. Run the automated tests (split integrity, dataset correctness, etc.)
pytest src/tests/ -v
```

All three commands are idempotent and deterministic given the same seed —
re-running them reproduces identical output.

---

## 3. Repository structure

```
MILK10k-Lesion-Classification/
├── README.md                  # this file
├── SUBMISSION.md               # Part B: links to every deliverable file
├── requirements.txt            # pinned dependencies
├── .gitignore                  # excludes data/, venv/, outputs/, __pycache__/
├── data/
│   └── milk10k/                 # NOT committed (raw data; see Data Handling Rules)
├── notebooks/                  # exploration and homework notebooks only
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── session_02.ipynb
│   ├── session_02_questions.ipynb
│   └── session_03_hw.ipynb
├── src/                         # all reusable logic — imported by notebooks, never copy-pasted
│   ├── __init__.py
│   ├── config.py                 # single source of truth: paths, seed, image size
│   ├── eda.py                    # metadata analysis, class-balance plots
│   ├── loader.py                 # image loading, "available images only" filtering
│   ├── preprocessing.py          # single + batch preprocessing functions
│   ├── utils.py                  # shared helpers
│   ├── visualization.py          # image-grid visualizer
│   ├── data/
│   │   ├── splits.py              # split_lesions(): leak-free StratifiedGroupKFold split
│   │   └── dataset.py             # LesionDataset, aggregate_predictions
│   └── tests/
│       └── test_pipeline.py       # property tests: split integrity, dataset correctness
├── outputs/                     # NOT committed — all generated files
│   ├── splits/                    # split_seed{N}_{date}.json
│   └── figures/                   # regenerated plots
└── reports/
    └── milestone1_report.md     # label strategy, split design, imbalance handling, with figures
```

**Why organised this way:** `src/` holds every piece of logic that is
reused more than once (loading, preprocessing, splitting, the dataset
class) so that notebooks never contain copy-pasted function definitions —
a notebook only *calls* `src` functions and shows results. `notebooks/`
is strictly for exploration, homework answers, and figures meant to be
read once; nothing in `notebooks/` is imported anywhere else. `outputs/`
separates **generated** artifacts (splits, figures) from **source**
artifacts (code), which keeps the repo diffable and makes it obvious what
to regenerate versus what to edit by hand. `reports/` holds the narrative
write-up for the milestone, separate from code and from raw exploration,
so a reader can get the story without digging through notebooks.

---

## 4. Data handling rules

- **Raw images are never committed.** `data/milk10k/` is listed in
  `.gitignore` in full; only this README documents where to obtain the
  data and how to point the code at it (see Section 2).
- **Generated files** (splits, figures, cached preprocessed arrays) are
  written under `outputs/`, which is also gitignored — anyone can
  regenerate them from the commands in Section 2.
- **Split reproducibility:** the canonical lesion-level split was created
  with **seed = 0** on **[FILL IN: the date you generate your final
  split]**, using `split_lesions(lesions, val_size=0.15, test_size=0.15,
  seed=0)`. Re-running `src/data/splits.py` with the same seed reproduces
  it exactly (verified by the property test in
  `src/tests/test_pipeline.py`, see A3.2).
- **Single point of configuration:** `src/config.py` holds `MILK10K_DIR`
  (resolved from the environment variable, falling back to
  `./data/milk10k`), `SEED = 0`, and `IMAGE_SIZE = 224`. No other file in
  the repo hard-codes a path, a seed, or an image size.

---

## 5. Key decisions and results so far

- **Label strategy:** `diagnosis_1` (3-class: Benign / Malignant /
  Indeterminate) is the primary prediction target. It can be derived
  deterministically from the 11-class scheme for 10 of 11 classes, but
  **AKIEC is ambiguous** — 180 of its lesions are `Malignant` and 123 are
  `Indeterminate` (verified in `notebooks/session_03_hw.ipynb`, A1.1c).
  The pipeline therefore keeps both label columns available and treats
  AKIEC's 3-class label as a known source of irreducible noise rather
  than silently resolving it.
- **Split design:** splitting is done at the **lesion** level (the
  atomic unit — see A3.1/A3.6), using `StratifiedGroupKFold` so that
  no lesion's two images are ever split across train/val/test, while
  class proportions stay balanced within ~0.1 percentage points of
  target (verified in A3.3, which compares this against plain
  `GroupKFold` and plain `StratifiedKFold`).
- **Preprocessing:** images resized to 224×224, converted to tensors;
  any imputation/normalization statistics are fit on the train split
  only, inside a single `Pipeline`/transform object, never leaking
  val/test statistics into training (see A3.1).
- **Imbalance handling:** `diagnosis_1` is heavily imbalanced
  (~69% Malignant / ~28% Benign / ~2% Indeterminate at the image level);
  the rarest 11-class categories (e.g. `MAL_OTH`, n=9) have so few
  lesions that per-class metrics for them are inherently noisy even
  with stratified splitting (A3.2). Handling strategy (sampler/loss
  weighting) and the full rationale are detailed in
  `reports/milestone1_report.md`.

For full detail, figures, and the quantitative audits behind each
decision above, see `reports/milestone1_report.md`.
