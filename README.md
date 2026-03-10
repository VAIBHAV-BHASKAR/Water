# Scalable Hydrochemical Intelligence Pipeline

**Groundwater Quality Analysis — Bhubaneswar, Odisha, India (2024)**

> A comprehensive, end-to-end Python pipeline for analysing groundwater quality across three seasons (Premonsoon, Monsoon, Postmonsoon) using 16 hydrochemical parameters measured at 15 sampling locations. The pipeline covers data cleaning, synthetic augmentation with noise injection, statistical analysis, regulatory compliance assessment (IS 10500:2012), source apportionment, machine learning forecasting, and automated report generation.

**Authors:**  Lakshya Nayyar (23053133) · Vaibhav Bhaskar (23053173)  
**Faculty Advisor:**  Dr. Ajit Kumar Pasayat  
**Institution:**  School of Civil Engineering, KIIT Deemed to be University, Bhubaneswar  
**Academic Year:**  2024–25

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Quick Start](#quick-start)
3. [Project Structure — Complete File Listing](#project-structure--complete-file-listing)
   - [Root-Level Files](#root-level-files)
   - [datasets/ — Generated CSV Outputs](#datasets--generated-csv-outputs)
   - [figures/ — Generated Visualisations](#figures--generated-visualisations)
4. [Pipeline Methodology — Detailed Walkthrough](#pipeline-methodology--detailed-walkthrough)
   - [Task 1: Data Reconstruction & Cleaning](#task-1-data-reconstruction--cleaning)
   - [Synthetic Data Generation (with Noise Injection)](#synthetic-data-generation-with-noise-injection)
   - [Task 2: Data Validation](#task-2-data-validation)
   - [WQI Computation](#wqi-computation)
   - [Task 3: EDA & Seasonal Dynamics](#task-3-eda--seasonal-dynamics)
   - [Task 4: Drinking Water Risk Intelligence (IS 10500:2012)](#task-4-drinking-water-risk-intelligence-is-105002012)
   - [Task 5: Source Analysis](#task-5-source-analysis)
   - [Task 6: ML-Based Forecasting](#task-6-ml-based-forecasting)
   - [Task 7: Scientific Insights](#task-7-scientific-insights)
5. [Configuration & Scalability](#configuration--scalability)
6. [Dependencies](#dependencies)
7. [References](#references)

---

## Project Overview

This project implements a **7-task scalable analysis framework** that processes raw groundwater quality data from an Excel workbook and produces:

- **Cleaned and validated datasets** with outlier detection and ionic balance checks
- **150 synthetic samples** generated via multivariate Gaussian sampling with 5-layer noise injection to prevent overfitting
- **IS 10500:2012 compliance assessment** — 3-tier classification (Safe / Caution / Unsafe) for every sample against Bureau of Indian Standards limits
- **Water Quality Index (WQI)** computed using the Brown et al. (1970) weighted arithmetic method
- **Source apportionment** — PCA, K-Means clustering, Piper diagrams, Gibbs mechanism, ionic ratios
- **Machine learning models** — 5 algorithms (Random Forest, Gradient Boosting, SVR, Neural Network, XGBoost) trained on 3 targets (TDS, EC, WQI) with SHAP explainability, residual analysis, and uncertainty quantification (GA, NSE, RSR, MAPE)
- **Professional outputs** — a Jupyter notebook report and a 15-slide PowerPoint presentation, both auto-generated from pipeline results

The entire pipeline runs in under 3 minutes and is controlled by a single `Config` class, making it straightforward to adapt to any new study area or dataset.

---

## Quick Start

```bash
# 1. Activate the virtual environment
.venv\Scripts\Activate.ps1          # Windows PowerShell
# source .venv/bin/activate         # Linux / macOS

# 2. Run the full analysis pipeline (generates all datasets + figures)
python hydrochemical_analysis.py

# 3. Generate the Jupyter notebook report
python make_notebook.py

# 4. Generate the PowerPoint presentation
python make_ppt.py
```

**Prerequisites:** Python 3.13+ with packages listed in [Dependencies](#dependencies). The raw data file `water quality data_Three Seasons_2024.xlsx` must be present in the project root.

---

## Project Structure — Complete File Listing

### Root-Level Files

| File | Description |
|------|-------------|
| `hydrochemical_analysis.py` | **Core pipeline script (~1,740 lines).** Contains all 7 analysis tasks, synthetic data generation, WQI computation, ML modelling, and figure/dataset export. This is the main script that drives the entire analysis. Running it executes all tasks sequentially and populates the `datasets/` and `figures/` directories. |
| `make_notebook.py` | **Jupyter notebook generator.** Reads the pipeline code and programmatically creates `Hydrochemical_Analysis_Report.ipynb` — a 49-cell notebook that documents the full analysis with code, markdown explanations, and embedded figures. |
| `make_ppt.py` | **PowerPoint generator (~910 lines).** Uses `python-pptx` to build a 15-slide widescreen (13.33 × 7.5 in) academic presentation. All metrics are hardcoded from the latest pipeline run. Slides cover: title, outline, introduction, dataset, methodology, seasonal dynamics (2 slides), IS 10500 compliance + WQI, source analysis, PCA & clustering, ML comparison (2 slides), conclusions, acknowledgement, and references. |
| `main.py` | **Project entry point stub.** Minimal placeholder (`print("Hello from water!")`) created by the `uv` package manager during project initialisation. Not used in the analysis pipeline. |
| `water quality data_Three Seasons_2024.xlsx` | **Raw input data.** Excel workbook with 3 sheets (`Data_Premonsoon 2024`, `Data_monsoon 2024`, `Data_Postmonsoon 2024`). Each sheet contains 15 groundwater sampling locations (PD-1..5, IA-1..5, DY-1..5) with 16 chemical parameters, GPS coordinates, site names, and area identifiers. |
| `Hydrochemical_Analysis_Report.ipynb` | **Generated Jupyter notebook** — the output of `make_notebook.py`. Contains 49 cells documenting the entire analysis pipeline with code and narrative. |
| `Hydrochemical_Analysis_Presentation.pptx` | **Generated PowerPoint presentation** — the output of `make_ppt.py`. 15 slides with embedded figures, tables, and key findings. |
| `fig_original_vs_synthetic_publication.png` | **Publication-quality comparison figure** — 4×4 grid of overlaid histograms showing the probability density distributions of all 16 parameters for original vs. noisy synthetic data. Saved at 600 DPI. |
| `output.log` | **Pipeline execution log.** Complete console output from the most recent run of `hydrochemical_analysis.py`, including all printed statistics, metric tables, file paths, and the final summary. Useful for auditing results without re-running. |
| `logbook.txt` | **Development logbook.** Records the chronological history of changes, features added, and bugs fixed throughout the project's development. |
| `paper1.pdf` | **Reference paper.** Sekar, S., et al. (2025). "Machine learning-based prediction of seasonal groundwater quality for Melur, Tamil Nadu." *Results in Engineering*, 28. Used as methodological reference for ML pipeline design. |
| `is.10500.2012.pdf` | **IS 10500:2012 standard document.** The official Bureau of Indian Standards specification for drinking water quality (Second Revision, 2012). Used to define all acceptable and permissible limits. |
| `pyproject.toml` | **Python project metadata.** Defines project name (`water`), version (`0.1.0`), and Python version requirement (≥3.13). Created by the `uv` package manager. |
| `.python-version` | **Python version pin.** Specifies the exact Python interpreter version for the project (used by `uv` and `pyenv`). |
| `.gitignore` | **Git ignore rules.** Excludes virtual environment, `__pycache__`, and other generated files from version control. |

### datasets/ — Generated CSV Outputs

All files in this directory are **generated by `hydrochemical_analysis.py`**. They are recreated on every pipeline run.

| File | Rows | Description |
|------|------|-------------|
| `cleaned_original_2024.csv` | 45 | **Task 1 output.** The 45 original groundwater samples (15 locations × 3 seasons) after cleaning: duplicate header rows removed, column names standardised, computed columns dropped, `NaN`-only rows removed, numeric types enforced. Contains 7 metadata columns + 16 chemical parameter columns. |
| `synthetic_clean.csv` | 150 | **Clean synthetic data (no noise).** 150 samples (50 per season) generated from the exact multivariate Gaussian distribution (mean vector + covariance matrix) of the original data per season. This represents the "overfitting" version — patterns mirror the original almost perfectly. Saved for comparison purposes. |
| `synthetic_noisy.csv` | 150 | **Noisy synthetic data.** Same 150 samples but generated with 5-layer noise injection: (1) covariance inflation (+40% diagonal), (2) mean jitter (±6% of std), (3) independent Gaussian noise (8% of std), (4) outlier perturbation (5% of samples × 2.5σ), (5) physical bounds clipping. This is the version used in the actual analysis to prevent overfitting. |
| `synthetic_only.csv` | 150 | **Backward-compatible alias** — identical to `synthetic_noisy.csv`. Kept for scripts that reference this filename. |
| `synthetic.csv` | 195 | **Combined dataset.** 45 original + 150 noisy synthetic = 195 total samples. This is the primary input to all downstream tasks (validation, EDA, compliance, ML, etc.). Each row has a `Data_Type` column (`Original` or `Synthetic`). |
| `validated_original.csv` | 45 | **Task 2 output (original only).** The 45 original samples after validation: missing value audit, outlier detection (IQR + Z-score), descriptive statistics, and Charge Balance Error (CBE) computation. No rows are removed — validation is diagnostic. |
| `validated_combined.csv` | 195 | **Task 2 output (combined).** The full 195-sample dataset after the same validation pipeline. CBE validity drops from 93.3% (original) to 64.6% (combined) — expected because noise introduces realistic ionic imbalance. |
| `wqi_results.csv` | 195 | **WQI output.** Each sample's computed Water Quality Index value and category (`Excellent`, `Good`, `Poor`, `Very Poor`, `Unsuitable`). Columns: `Location_ID`, `Season`, `WQI`, `WQI_Category`. |
| `is10500_compliance_report.csv` | varies | **Task 4 output.** Parameter-level compliance matrix: for each of the 16 parameters, the count and percentage of samples classified as Safe, Marginal (Caution), or Unsafe under IS 10500:2012. Includes exceedance factors. |
| `is10500_sample_safety.csv` | 195 | **Task 4 output.** Sample-level safety verdict: each of the 195 samples is classified as `SAFE` (all parameters within acceptable), `CAUTION` (within permissible but exceeds acceptable), or `UNSAFE` (at least one parameter exceeds permissible limit). |
| `final_analyzed.csv` | 195 | **Final enriched dataset.** The complete 195-sample dataset with all original columns plus computed fields: `WQI`, `WQI_Category`, PCA cluster assignments, and any intermediate columns added during source analysis. This is the "one file that has everything." |
| `cleaned_hydrochemical_data_2024.csv` | 45 | **Legacy export.** An earlier version of the cleaned original data, kept for backward compatibility. Identical in content to `cleaned_original_2024.csv`. |

### figures/ — Generated Visualisations

All figures are generated by `hydrochemical_analysis.py` at 300 DPI (configurable via `Config.SAVE_DPI`).

#### `figures/task1_cleaning/`

| Figure | Description |
|--------|-------------|
| `fig_original_vs_synthetic.png` | Side-by-side comparison of original and synthetic sample distributions (quick overview version). |

#### `figures/task2_validation/`

| Figure | Description |
|--------|-------------|
| `fig_missing_original.png` | Missing value heatmap for the 45 original samples. Shows a matrix where each cell indicates whether a value is present or absent. |
| `fig_missing_combined.png` | Missing value heatmap for the 195 combined samples. |
| `fig_missing_values_heatmap.png` | Alternative missing-value visualisation (legacy format). |

#### `figures/task3_seasonal/`

| Figure | Description |
|--------|-------------|
| `fig_seasonal_boxplots.png` | Box plots of all 16 parameters grouped by season. Shows median, IQR, whiskers, and outliers for Premonsoon, Monsoon, and Postmonsoon side by side. |
| `fig_seasonal_violins.png` | Violin plots showing the full probability density shape of each parameter's distribution per season — more informative than box plots for multimodal data. |
| `fig_seasonal_heatmap.png` | Heatmap of mean parameter values per season, with colour intensity proportional to concentration. Reveals seasonal enrichment/depletion patterns at a glance. |
| `fig_seasonal_trends.png` | Line plots showing how each parameter's mean changes across the three seasons (Pre → Mon → Post). Error bars indicate standard deviation. |
| `fig_correlation_matrix.png` | Pearson correlation matrix (16×16) for all chemical parameters. Colour-coded from −1 (blue) to +1 (red). Key finding: EC↔TDS r = 0.859 after noise injection. |
| `fig_distributions.png` | Histograms with KDE overlays showing the frequency distribution of each parameter across all 195 samples. |
| `fig_pairplot.png` | Pairwise scatter plot matrix for selected parameters, coloured by season. |
| `fig_pairplot_publication.png` | Publication-quality version of the pairplot at higher resolution. |

#### `figures/task4_safety/`

| Figure | Description |
|--------|-------------|
| `fig_is10500_compliance_heatmap.png` | Heatmap showing compliance status (Safe/Caution/Unsafe) for each parameter × season combination. Dark red = high non-compliance. |
| `fig_is10500_compliance_bars.png` | Stacked bar chart showing the count of Safe, Caution, and Unsafe samples per parameter. |
| `fig_is10500_exceedance_factor.png` | Bar chart of exceedance factors — how many times each parameter's mean exceeds its IS 10500 acceptable limit. Values > 1.0 indicate non-compliance on average. |
| `fig_wqi_analysis.png` | Three-panel WQI figure: (1) histogram by season, (2) box plot by season, (3) pie chart of WQI categories (Excellent / Good / Poor / etc.). |

#### `figures/task5_source/`

| Figure | Description |
|--------|-------------|
| `fig_pca_scree.png` | Scree plot showing explained variance (%) per principal component + cumulative variance curve. Used to determine the optimal number of PCs to retain (6 PCs = 73.3% variance). |
| `fig_pca_loadings.png` | Heatmap of PCA loading coefficients — shows which original parameters contribute most to each principal component. |
| `fig_pca_biplot.png` | Biplot overlaying sample scores (dots, coloured by season) with parameter loading vectors (arrows) on the PC1–PC2 plane. Reveals relationships between samples and variables. |
| `fig_kmeans_pca.png` | K-Means cluster assignments (k = 3) plotted on the PC1–PC2 plane. Each cluster represents a distinct hydrochemical facies. |
| `fig_dendrogram.png` | Hierarchical clustering dendrogram (Ward's method) showing sample groupings. Confirms the 3-cluster structure found by K-Means. |
| `fig_elbow.png` | Elbow plot of within-cluster sum of squares (WCSS) vs. number of clusters (k = 1..10). The "elbow" at k = 3 justifies the chosen cluster count. |
| `fig_piper_diagram.png` | Piper trilinear diagram — the classic hydrochemistry plot showing cation (Ca–Mg–Na+K) and anion (HCO₃–SO₄–Cl) ternary diagrams with a central diamond. Used to classify water type / hydrochemical facies (e.g., Ca-Cl, Na-HCO₃). |
| `fig_gibbs_diagram.png` | Gibbs diagram — plots TDS vs. Na/(Na+Ca) and TDS vs. Cl/(Cl+HCO₃) to identify the dominant mechanism controlling water chemistry: (1) precipitation dominance, (2) rock-water interaction, or (3) evaporation-crystallisation. |
| `fig_ionic_ratios.png` | Bar plots of key ionic ratios (Na/Cl, Ca/Mg) per season. Na/Cl > 1 suggests silicate weathering or anthropogenic Na input; Ca/Mg > 2 indicates calcite dissolution dominance. |

#### `figures/task6_ml/`

| Figure | Description |
|--------|-------------|
| `fig_feature_importance.png` | Random Forest feature importance bar charts — shows the top features (by Gini importance) for each of the 3 targets (TDS, EC, WQI). |
| `fig_actual_vs_predicted_tds.png` | Actual vs. predicted scatter plot for TDS — shows all 5 models' predictions against the 1:1 line. Points closer to the line indicate better predictions. |
| `fig_actual_vs_predicted_ec.png` | Same as above, for EC. |
| `fig_actual_vs_predicted_wqi.png` | Same as above, for WQI. |
| `fig_actual_vs_predicted.png` | Combined actual-vs-predicted overview (legacy format). |
| `fig_shap_tds.png` | SHAP bar plot for TDS — shows mean absolute SHAP values per feature, quantifying each feature's average contribution to TDS predictions. |
| `fig_shap_ec.png` | SHAP bar plot for EC. |
| `fig_shap_wqi.png` | SHAP bar plot for WQI. |
| `fig_shap_summary_tds.png` | SHAP beeswarm/summary plot for TDS — each dot is a sample, positioned by its SHAP value, coloured by feature value (red = high, blue = low). Reveals non-linear feature effects. |
| `fig_shap_summary_ec.png` | SHAP beeswarm plot for EC. |
| `fig_shap_summary_wqi.png` | SHAP beeswarm plot for WQI. |
| `fig_residuals_tds.png` | Residual analysis plot for TDS — shows the distribution of prediction errors (Actual − Predicted) for the best model. A symmetric, zero-centred distribution indicates unbiased predictions. |
| `fig_residuals_ec.png` | Residual analysis plot for EC. |
| `fig_residuals_wqi.png` | Residual analysis plot for WQI. |

#### `figures/task7_insights/`

| Figure | Description |
|--------|-------------|
| `fig_seasonal_radar.png` | Radar (spider) chart showing normalised mean concentrations of all 16 parameters per season. Each axis represents one parameter, scaled 0–1. Reveals the "shape" of each season's chemical signature. |

---

## Pipeline Methodology — Detailed Walkthrough

The pipeline is implemented in `hydrochemical_analysis.py` and orchestrated by the `main()` function, which executes 7 tasks sequentially. Below is a detailed explanation of every step.

### Task 1: Data Reconstruction & Cleaning

**Function:** `load_all_seasons()` → calls `load_and_clean_sheet()` per season  
**Purpose:** Transform raw Excel data into a clean, analysis-ready DataFrame.

**What it does:**

1. **Reads each Excel sheet** (`Data_Premonsoon 2024`, `Data_monsoon 2024`, `Data_Postmonsoon 2024`) using `openpyxl`.
2. **Identifies column headers** from row 2 of each sheet (the raw data has an irregular header layout with merged cells). A fuzzy string-matching approach maps raw header text (e.g., `"conductivity"`, `"sulphate"`, `"loction id"`) to standardised column names (`EC`, `SO4`, `Location_ID`).
3. **Removes noise rows** — duplicate header rows, blank rows, and `NaN`-only rows that appear in the raw data due to Excel formatting.
4. **Forward-fills the `Sites` column** (which is sometimes merged across rows in the original Excel).
5. **Coerces all chemical parameter columns to numeric** (`pd.to_numeric(..., errors='coerce')`), converting any remaining text values to `NaN`.
6. **Adds a `Season` column** based on which sheet the data came from.
7. **Concatenates** all 3 seasonal DataFrames into a single master DataFrame (45 rows × 23 columns).
8. **Exports** to `datasets/cleaned_original_2024.csv`.

**Output:** 45 samples (15 locations × 3 seasons) × 16 chemical parameters + 7 metadata columns.

---

### Synthetic Data Generation (with Noise Injection)

**Function:** `generate_synthetic_data(df_original, n_per_season=50)`  
**Purpose:** Augment the small original dataset (n = 45) with 150 realistic synthetic samples to improve ML model robustness and statistical power, while injecting controlled noise to prevent overfitting.

**Why noise injection is needed:**  
Without noise, synthetic data generated from the exact mean vector and covariance matrix of the original data replicates the original patterns too perfectly. ML models trained on such data achieve artificially high R² scores (>0.93) that do not reflect true predictive ability — this is overfitting. The noise injection introduces realistic variability that forces models to learn genuine patterns rather than memorising exact relationships.

**How it works (5-layer noise injection):**

For each of the 3 seasons independently:

1. **Compute statistics** — Calculate the mean vector (μ) and covariance matrix (Σ) of the 15 original samples for that season across all 16 chemical parameters.

2. **Layer 1 — Covariance Inflation (COV\_INFLATION = 1.40):**  
   The diagonal of the covariance matrix is multiplied by 1.40, inflating the variance of each parameter by 40%. This widens the overall spread of the generated samples beyond the tight original distribution. Off-diagonal (correlation) elements are preserved.

3. **Layer 2 — Mean Jitter (MEAN\_JITTER\_FRAC = 0.06):**  
   Each element of the mean vector is randomly perturbed by up to ±6% of the parameter's standard deviation. This shifts the centre of the synthetic distribution slightly away from the original, preventing the synthetic mean from being an exact copy.

4. **Layer 3 — Multivariate Gaussian Sampling:**  
   50 samples are drawn from the multivariate normal distribution N(μ\_jittered, Σ\_inflated). This is the core generation step — the multivariate approach preserves inter-parameter correlations (e.g., EC ↔ TDS) while the inflated covariance adds spread.

5. **Layer 4 — Independent Gaussian Noise (INDEP\_NOISE\_FRAC = 0.08):**  
   Each generated value receives an additional independent Gaussian perturbation with standard deviation equal to 8% of the parameter's original standard deviation. This breaks perfect correlations between parameters, adding uncorrelated noise that simulates real-world measurement variability.

6. **Layer 5 — Outlier Perturbation (OUTLIER\_FRAC = 0.05, OUTLIER\_SCALE = 2.5):**  
   5% of synthetic samples (at least 1) are selected randomly. For each, 2–4 random parameters are perturbed by ±(0.3 to 1.0) × 2.5 × σ. This creates realistic outlier-like data points that exist in any real dataset but are absent when sampling from a smooth Gaussian.

7. **Physical Bounds Clipping:**  
   All values are clipped to physically meaningful ranges (e.g., pH: 4.0–9.5; TDS: 30–2000 mg/L; Iron: 0.01–5.0 mg/L) and rounded to appropriate decimal places.

**Both versions are saved:**
- `synthetic_clean.csv` — generated without any noise (Layers 2–5 skipped), for comparison
- `synthetic_noisy.csv` — generated with all 5 noise layers, used in the actual analysis
- `synthetic.csv` — 45 original + 150 noisy synthetic = 195 combined samples

**Verification:** A parameter-by-parameter comparison table is printed showing the mean difference (%) between original and synthetic data — typical deviations are 1–8%, confirming the noise is realistic but non-trivial.

---

### Task 2: Data Validation

**Function:** `validate_data(df, label)`  
**Purpose:** Audit data quality without removing any rows.

**Steps:**

1. **Missing value analysis** — Counts `NaN` values per column and generates a heatmap visualisation. (In the current dataset, there are zero missing values.)

2. **Outlier detection** — Two independent methods:
   - **IQR method:** Values below Q1 − 1.5×IQR or above Q3 + 1.5×IQR are flagged.
   - **Z-score method:** Values with |Z| > 3 are flagged.
   - Both counts are printed per parameter. Outliers are flagged but not removed — they may represent genuine extreme conditions.

3. **Charge Balance Error (CBE)** — The fundamental quality check for water chemistry data. Computes:

$$\text{CBE} = \frac{\sum \text{cations (meq/L)} - \sum \text{anions (meq/L)}}{\sum \text{cations (meq/L)} + \sum \text{anions (meq/L)}} \times 100\%$$

   Cations: Ca²⁺, Mg²⁺, Na⁺, K⁺ (converted from mg/L to meq/L using equivalent weights).  
   Anions: HCO₃⁻, Cl⁻, SO₄²⁻, NO₃⁻.  
   Acceptable range: ±10%. In the original data, 93.3% of samples pass; in the combined noisy data, 64.6% pass (expected — noise breaks exact ionic balance).

4. **Descriptive statistics** — Prints count, mean, std, min, Q1, median, Q3, max, skewness, kurtosis, and CV% for all 16 parameters.

**Run twice:** Once for original data (45 samples), once for combined data (195 samples). Both validated datasets are saved.

---

### WQI Computation

**Function:** `compute_wqi(df)`  
**Purpose:** Compute a single-number Water Quality Index for each sample using the weighted arithmetic method of Brown et al. (1970).

**Formula:**

$$\text{WQI} = \sum_{i=1}^{n} W_i \times q_i$$

where:
- $q_i = (C_i / S_i) \times 100$ — the quality rating for parameter $i$ ($C_i$ = measured concentration, $S_i$ = IS 10500 standard value)
- $W_i = w_i / \sum w_i$ — the relative weight of parameter $i$
- $w_i$ = assigned weight (1–5) based on health significance:
  - Weight 5 (highest health impact): TDS, NO₃, F
  - Weight 4: pH, EC, Iron, SO₄, DO
  - Weight 3: Na, Cl
  - Weight 2: TH, Alkalinity, Ca, Mg, K
  - Weight 1: HCO₃

**Classification:**

| WQI Range | Category |
|-----------|----------|
| < 50 | Excellent |
| 50–100 | Good |
| 100–200 | Poor |
| 200–300 | Very Poor |
| > 300 | Unsuitable |

**Output:** Adds `WQI` and `WQI_Category` columns to the DataFrame. Saves `wqi_results.csv`. Generates a 3-panel figure (`fig_wqi_analysis.png`).

---

### Task 3: EDA & Seasonal Dynamics

**Function:** `run_eda_and_seasonal(df)`  
**Purpose:** Explore seasonal variation patterns through statistical tests and visualisations.

**Steps:**

1. **Seasonal summary statistics** — Mean, std, min, max for each parameter per season.
2. **Statistical tests for seasonal differences:**
   - **ANOVA** (if data is normally distributed per Shapiro-Wilk) or **Kruskal-Wallis** (non-parametric alternative). Tests the null hypothesis that all 3 seasons have the same mean/median.
   - Parameters with p < 0.05 are "significant" — their distributions differ meaningfully across seasons.
   - Effect size computed as η² (eta-squared) = SS_between / SS_total.
3. **Percentage change** — Calculates the % change in mean concentration between consecutive seasons (Pre→Mon, Mon→Post).
4. **Correlation matrix** — Pearson r for all 16×16 parameter pairs. Identifies multicollinear pairs (|r| > 0.7).
5. **Visualisations generated:** box plots, violin plots, seasonal heatmap, trend lines, correlation matrix, distribution histograms, pair plots.

---

### Task 4: Drinking Water Risk Intelligence (IS 10500:2012)

**Function:** `assess_drinking_water(df)`  
**Purpose:** Assess every sample against the Indian national drinking water standard.

**How the 3-tier classification works:**

For each of the 16 parameters and each of the 195 samples, the measured value is compared against two thresholds from IS 10500:2012:

| Classification | Condition |
|----------------|-----------|
| **Compliant – Safe** | Value ≤ Acceptable Limit |
| **Permissible – Needs Caution** | Acceptable < Value ≤ Permissible Limit |
| **Non-Compliant – Unsafe** | Value > Permissible Limit |

For range-based parameters (pH, DO), both upper and lower bounds are checked.

**Standards used:**
- **IS 10500:2012 (BIS)** — pH, TDS, TH, Alkalinity, Ca, Mg, Iron, Cl, SO₄, NO₃, F (official Indian standard)
- **WHO (2011) / GoI supplementary** — EC, Na, K, DO, HCO₃ (not in IS 10500 but referenced in WHO/FSSAI/CPCB frameworks)

**Sample-level safety verdict:**
- **SAFE** — all 16 parameters within acceptable limits
- **CAUTION** — at least one parameter in the permissible zone, none unsafe
- **UNSAFE** — at least one parameter exceeds permissible limit

**Exceedance factor** — For each parameter: (Mean measured value) / (Acceptable limit). Values > 1.0 indicate the average sample fails the standard.

**Outputs:** `is10500_compliance_report.csv`, `is10500_sample_safety.csv`, compliance heatmap, bar chart, exceedance factor chart. Also prints specific remediation recommendations for each non-compliant parameter (cause, action).

---

### Task 5: Source Analysis

**Function:** `run_source_analysis(df)`  
**Purpose:** Identify the geogenic (natural) and anthropogenic (human) sources controlling groundwater chemistry.

**Techniques used:**

1. **Principal Component Analysis (PCA):**
   - Standardises all 16 parameters (z-score normalisation).
   - Computes eigenvalues and eigenvectors of the correlation matrix.
   - Identifies the dominant "factors" driving water chemistry variation.
   - Interpretation: PC1 (mineralization), PC2 (carbonate weathering), PC3 (anthropogenic inputs), PC4 (redox/iron).
   - Scree plot, loading heatmap, and biplot are generated.

2. **K-Means Clustering:**
   - Groups samples into k = 3 clusters (determined by elbow method — plotting WCSS vs. k and finding the inflection point).
   - Each cluster represents a distinct hydrochemical facies with characteristic chemistry.
   - Cluster means for all 16 parameters are printed and plotted on the PC1–PC2 space.

3. **Hierarchical Clustering:**
   - Ward's method dendrogram — an alternative clustering that does not require specifying k in advance. Confirms the 3-cluster structure.

4. **Piper Diagram:**
   - The standard hydrochemical classification plot. Converts cations (Ca, Mg, Na+K) and anions (HCO₃+CO₃, SO₄, Cl) to milliequivalent percentages.
   - Plots on two ternary diagrams (cation and anion triangles) with a central diamond that classifies the water type (e.g., Ca-Cl, Na-HCO₃, Ca-SO₄).
   - Each sample is a point, coloured by season. The dominant facies in this study is **Ca-Cl**.

5. **Gibbs Diagram:**
   - Two scatter plots: TDS vs. Na/(Na+Ca) and TDS vs. Cl/(Cl+HCO₃).
   - Samples falling in different zones indicate different controlling mechanisms:
     - Bottom-left: Precipitation dominance
     - Middle: Rock-water interaction (weathering)
     - Top-right: Evaporation-crystallisation
   - This study: samples cluster in the **rock-water interaction** zone.

6. **Ionic Ratios:**
   - **Na/Cl**: ≈ 1 suggests halite dissolution; > 1 suggests silicate weathering; < 1 suggests reverse ion exchange or anthropogenic Cl.
   - **Ca/Mg**: > 2 indicates calcite dissolution; ≈ 1 suggests dolomite; < 1 indicates silicate weathering.
   - Computed per season and plotted as bar charts.

**Output:** Adds cluster labels to the DataFrame; generates 9 figures in `figures/task5_source/`.

---

### Task 6: ML-Based Forecasting

**Function:** `run_ml(df)`  
**Purpose:** Train, evaluate, and explain 5 machine learning models for predicting TDS, EC, and WQI from the other hydrochemical parameters.

**Pipeline for each target (TDS, EC, WQI):**

1. **Feature selection:** All 16 chemical parameters minus the target variable (and minus related variables that would cause data leakage — e.g., when predicting TDS, EC is excluded because they are physically the same measurement). A `Season_num` ordinal feature is added (Premonsoon=0, Monsoon=1, Postmonsoon=2).

2. **Train-test split:** 80% train / 20% test, stratified by season, random seed = 42 for reproducibility.

3. **Standardisation:** `StandardScaler` — fit on training data, applied to both train and test. Essential for SVR and Neural Network which are sensitive to feature scales.

4. **5 models trained:**

| Model | Algorithm | Key Hyperparameters |
|-------|-----------|---------------------|
| **Random Forest** | Bagging ensemble of decision trees | n_estimators=200, max_depth=10 |
| **Gradient Boosting** | Sequential boosting of weak learners | n_estimators=200, learning_rate=0.1, max_depth=4 |
| **SVR** | Support Vector Regression with RBF kernel | C=100, epsilon=0.1 |
| **Neural Network** | MLP Regressor (multi-layer perceptron) | hidden_layers=(128, 64, 32), max_iter=1000, early_stopping |
| **XGBoost** | Extreme Gradient Boosting | n_estimators=200, learning_rate=0.1, max_depth=4 |

5. **Evaluation metrics:**
   - **Train R²** — how well the model fits the training data
   - **Test R²** — how well the model generalises to unseen data
   - **CV R²** — 5-fold cross-validation R² (most reliable metric for model comparison, averaged over 5 random train/test splits)
   - **RMSE** — Root Mean Square Error (in original units)
   - **MAE** — Mean Absolute Error (in original units)

6. **Uncertainty quantification (per Sekar et al., 2025):**
   - **GA (Generalization Ability):** $\text{GA} = 1 - |1 - R^2_{\text{test}} / R^2_{\text{train}}|$ — measures how well training performance transfers to test. GA > 0.9 = Excellent, 0.7–0.9 = Good, < 0.7 = Weak.
   - **NSE (Nash-Sutcliffe Efficiency):** $\text{NSE} = 1 - \frac{\sum(O_i - P_i)^2}{\sum(O_i - \bar{O})^2}$ — NSE = 1 is perfect; > 0.75 = Very Good.
   - **RSR (RMSE-observations Standard deviation Ratio):** $\text{RSR} = \text{RMSE} / \text{Std}(O)$ — RSR < 0.50 = Very Good.
   - **MAPE (Mean Absolute Percentage Error):** Average |error| as % of actual value.

7. **SHAP (SHapley Additive exPlanations):**
   - Uses the Lundberg & Lee (2017) framework to compute the marginal contribution of each feature to each prediction.
   - Generates bar plots (mean |SHAP|) and beeswarm plots (individual sample SHAP values coloured by feature magnitude).
   - Provides model-agnostic interpretability.

8. **Residual analysis:**
   - Plots the distribution of residuals (Actual − Predicted) for the best model per target.
   - A zero-centred, symmetric distribution indicates unbiased predictions.

9. **Feature importance (Random Forest & XGBoost):**
   - Gini impurity-based importance from ensemble tree models.
   - Top features printed and plotted.

**Output:** 14 figures in `figures/task6_ml/`, printed performance summary table, and a `ml_results` dictionary passed to Task 7.

---

### Task 7: Scientific Insights

**Function:** `generate_insights(df, ml_results)`  
**Purpose:** Synthesise findings from all previous tasks into actionable scientific conclusions.

**Analyses performed:**

1. **Salinity drivers** — Pearson correlation of each parameter with TDS, sorted by magnitude. Identifies which parameters most strongly influence groundwater salinity.

2. **Seasonal exceedance ranking** — Counts total parameter exceedances (Safe/Marginal/Unsafe) per season. Identifies the worst season for water quality.

3. **Location ranking** — Mean TDS, EC, and pH per sampling location, ranked by TDS. Identifies the most contaminated sites.

4. **Dominant hydrochemical type** — Determined from milliequivalent concentrations of cations and anions.

5. **Anthropogenic indicators:**
   - Na–Cl excess (meq/L): negative values suggest anthropogenic Cl input.
   - NO₃ statistics: high values (>45 mg/L) indicate agricultural or sewage contamination.

6. **Gibbs mechanism classification** — Na/(Na+Ca) ratio: < 0.5 = rock weathering; > 0.5 = evaporation/mixed.

7. **Seasonal radar chart** — Normalised (0–1) radar plot of all 16 parameters per season.

8. **Final summary** printed to console with all key numbers.

---

## Configuration & Scalability

The entire pipeline is controlled by the `Config` class at the top of `hydrochemical_analysis.py`. To adapt the pipeline to a different study area or dataset:

| Setting | Current Value | What to Change |
|---------|---------------|----------------|
| `DATA_FILE` | `water quality data_Three Seasons_2024.xlsx` | Path to your Excel file |
| `SHEET_MAP` | 3 sheets → 3 season names | Map your sheet names to season labels |
| `SEASON_ORDER` | `['Premonsoon', 'Monsoon', 'Postmonsoon']` | Your seasons in chronological order |
| `CHEM_COLS` | 16 parameters | Your chemical parameter column names |
| `IS_10500` | BIS limits per parameter | Update limits for your regulatory framework |
| `SYNTHETIC_SAMPLES_PER_SEASON` | 50 | Number of synthetic samples per season |
| `ML_TARGETS` | `['TDS', 'EC', 'WQI']` | Which parameters to predict with ML |
| `CV_FOLDS` | 5 | Number of cross-validation folds |
| `RANDOM_SEED` | 42 | For reproducibility |
| `PLOT_DPI` / `SAVE_DPI` | 150 / 300 | Figure resolution |

The column-header matching in `load_and_clean_sheet()` uses fuzzy string matching, so minor spelling variations in your Excel headers will be handled automatically.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `pandas` | Data manipulation and CSV I/O |
| `numpy` | Numerical computation, random sampling |
| `matplotlib` | All plotting (Agg backend for headless operation) |
| `seaborn` | Statistical visualisation (box plots, heatmaps, violin plots) |
| `scipy` | Statistical tests (ANOVA, Kruskal-Wallis, Shapiro-Wilk), hierarchical clustering |
| `scikit-learn` | ML models (RF, GB, SVR, MLP), preprocessing (StandardScaler), PCA, K-Means, cross-validation |
| `xgboost` | XGBoost regressor |
| `shap` | SHAP explainability (Lundberg & Lee, 2017) |
| `openpyxl` | Reading Excel (.xlsx) files |
| `python-pptx` | PowerPoint generation |

Install all dependencies:
```bash
pip install pandas numpy matplotlib seaborn scipy scikit-learn xgboost shap openpyxl python-pptx
```

---

## References

1. Bureau of Indian Standards (BIS). **IS 10500:2012** — Drinking Water Specification (Second Revision). New Delhi: BIS, 2012.
2. World Health Organization (WHO). **Guidelines for Drinking-water Quality**, 4th Edition. Geneva: WHO, 2011.
3. Brown, R.M., McClelland, N., Deininger, R.A. & Tozer, R.G. (1970). **A Water Quality Index — Do We Dare?** *Water & Sewage Works*, 117(10).
4. Sekar, S., et al. (2025). **Machine learning-based prediction of seasonal groundwater quality for Melur, Tamil Nadu.** *Results in Engineering*, 28.
5. Piper, A.M. (1944). **A Graphic Procedure in the Geochemical Interpretation of Water Analyses.** *Trans. AGU*, 25(6), 914–928.
6. Gibbs, R.J. (1970). **Mechanisms Controlling World Water Chemistry.** *Science*, 170(3962), 1088–1090.
7. Lundberg, S.M. & Lee, S.-I. (2017). **A Unified Approach to Interpreting Model Predictions.** *NeurIPS 2017*.
8. Central Pollution Control Board (CPCB). **Drinking Water Quality Standards** — Class A Criteria. Government of India.

---

*Generated as part of the Hydrochemical Intelligence Pipeline — School of Civil Engineering, KIIT University, 2024–25.*
