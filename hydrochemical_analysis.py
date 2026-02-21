#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
===============================================================================
SCALABLE HYDROCHEMICAL INTELLIGENCE PIPELINE
Groundwater Quality Analysis - Bhubaneswar, 2024
Three Seasons: Premonsoon, Monsoon, Postmonsoon

Features:
  - Modular, class-based architecture for scalability
  - Synthetic data generation for model robustness
  - Organized output: datasets/ and figures/task*/
  - Configurable parameters (seasons, standards, models)
  - Reproducible (random seeds, version tracking)
===============================================================================
"""

# ============================================================================
# IMPORTS
# ============================================================================
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.impute import KNNImputer
from sklearn.base import clone
import os, sys, io
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


# ============================================================================
# CONFIGURATION (Edit this section to scale to new datasets)
# ============================================================================
class Config:
    """Central configuration - edit here to adapt to any dataset."""

    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    DATA_FILE = BASE_DIR / 'water quality data_Three Seasons_2024.xlsx'
    DATASET_DIR = BASE_DIR / 'datasets'
    FIGURE_DIR = BASE_DIR / 'figures'

    SHEET_MAP = {
        'Data_Premonsoon 2024': 'Premonsoon',
        'Data_monsoon 2024': 'Monsoon',
        'Data_Postmonsoon 2024': 'Postmonsoon',
    }
    SEASON_ORDER = ['Premonsoon', 'Monsoon', 'Postmonsoon']
    SEASON_COLORS = {'Premonsoon': '#e74c3c', 'Monsoon': '#3498db', 'Postmonsoon': '#2ecc71'}

    CHEM_COLS = ['pH', 'EC', 'TDS', 'TH', 'Alkalinity', 'Ca', 'Mg', 'Na', 'K',
                 'Iron', 'HCO3', 'Cl', 'SO4', 'NO3', 'F', 'DO']
    META_COLS = ['Sl_No', 'Sites', 'Areas', 'Location_ID', 'Latitude', 'Longitude', 'Season']

    IS_STANDARDS = {
        'pH':         ((6.5, 8.5),  (6.5, 8.5)),
        'EC':         ((0, 750),    (0, 3000)),
        'TDS':        ((0, 500),    (0, 2000)),
        'TH':         ((0, 200),    (0, 600)),
        'Alkalinity': ((0, 200),    (0, 600)),
        'Ca':         ((0, 75),     (0, 200)),
        'Mg':         ((0, 30),     (0, 100)),
        'Na':         ((0, 200),    (0, 200)),
        'K':          ((0, 12),     (0, 12)),
        'Iron':       ((0, 0.3),    (0, 1.0)),
        'Cl':         ((0, 250),    (0, 1000)),
        'SO4':        ((0, 200),    (0, 400)),
        'NO3':        ((0, 45),     (0, 45)),
        'F':          ((0, 1.0),    (0, 1.5)),
        'DO':         ((5, 14),     (4, 14)),
    }

    SYNTHETIC_SAMPLES_PER_SEASON = 50
    RANDOM_SEED = 42
    ML_TARGETS = ['TDS', 'EC']
    CV_FOLDS = 5
    CBE_THRESHOLD = 10
    PLOT_DPI = 150
    SAVE_DPI = 300

    @classmethod
    def setup_dirs(cls):
        for d in [cls.DATASET_DIR,
                  cls.FIGURE_DIR / 'task1_cleaning',
                  cls.FIGURE_DIR / 'task2_validation',
                  cls.FIGURE_DIR / 'task3_seasonal',
                  cls.FIGURE_DIR / 'task4_safety',
                  cls.FIGURE_DIR / 'task5_source',
                  cls.FIGURE_DIR / 'task6_ml',
                  cls.FIGURE_DIR / 'task7_insights']:
            d.mkdir(parents=True, exist_ok=True)


plt.rcParams.update({
    'figure.figsize': (12, 8), 'figure.dpi': Config.PLOT_DPI,
    'font.size': 11, 'font.family': 'serif',
    'axes.labelsize': 12, 'axes.titlesize': 13,
    'xtick.labelsize': 10, 'ytick.labelsize': 10,
    'legend.fontsize': 10, 'figure.titlesize': 14,
    'savefig.dpi': Config.SAVE_DPI, 'savefig.bbox': 'tight'
})


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def save_fig(fig, task_folder, filename):
    path = Config.FIGURE_DIR / task_folder / filename
    fig.savefig(path, dpi=Config.SAVE_DPI, bbox_inches='tight')
    plt.close(fig)
    print(f"  [FIG] {path.relative_to(Config.BASE_DIR)}")

def save_dataset(df, filename):
    path = Config.DATASET_DIR / filename
    df.to_csv(path, index=False)
    print(f"  [CSV] {path.relative_to(Config.BASE_DIR)}")

def mg_to_meq(df):
    meq = pd.DataFrame(index=df.index)
    meq['Ca_meq']   = df['Ca']   / 20.04
    meq['Mg_meq']   = df['Mg']   / 12.15
    meq['Na_meq']   = df['Na']   / 22.99
    meq['K_meq']    = df['K']    / 39.10
    meq['HCO3_meq'] = df['HCO3'] / 61.02
    meq['Cl_meq']   = df['Cl']   / 35.45
    meq['SO4_meq']  = df['SO4']  / 48.03
    meq['NO3_meq']  = df['NO3']  / 62.00
    return meq

def classify_safety(value, param):
    if pd.isna(value) or param not in Config.IS_STANDARDS:
        return 'N/A'
    (low_d, high_d), (low_p, high_p) = Config.IS_STANDARDS[param]
    if low_d <= value <= high_d:
        return 'Safe'
    elif low_p <= value <= high_p:
        return 'Marginal'
    return 'Unsafe'


# ============================================================================
# TASK 1: DATA LOADING & CLEANING
# ============================================================================
def load_and_clean_sheet(filepath, sheet_name, season):
    df_raw = pd.read_excel(filepath, sheet_name=sheet_name, header=None)
    print(f"\n  Loading: {sheet_name}  (raw: {df_raw.shape})")

    headers = df_raw.iloc[1].tolist()
    df = df_raw.iloc[3:].copy().dropna(how='all')
    df.columns = range(len(headers))

    col_map = {}
    for i, h in enumerate(headers):
        if h is None or (isinstance(h, float) and pd.isna(h)):
            continue
        hc = str(h).strip().lower()
        if 'sl' in hc and 'no' in hc:                   col_map[i] = 'Sl_No'
        elif hc == 'sites':                               col_map[i] = 'Sites'
        elif hc == 'areas':                               col_map[i] = 'Areas'
        elif 'loction' in hc or 'location' in hc:        col_map[i] = 'Location_ID'
        elif hc == 'lat':                                 col_map[i] = 'Latitude'
        elif hc == 'long':                                col_map[i] = 'Longitude'
        elif hc == 'ph':                                  col_map[i] = 'pH'
        elif 'conductivity' in hc:                        col_map[i] = 'EC'
        elif hc in ('tds', 'tds  ') and 'TDS' not in col_map.values():
            col_map[i] = 'TDS'
        elif hc in ('th', 'hardness', 'hardness '):       col_map[i] = 'TH'
        elif hc in ('ta ', 'ta', 'alkalinity', 'alkalinity  '):
            col_map[i] = 'Alkalinity'
        elif hc.startswith('ca') and i < 20:              col_map[i] = 'Ca'
        elif hc.startswith('mg') and i < 20:              col_map[i] = 'Mg'
        elif hc.startswith('na') and 'nitrate' not in hc and i < 20:
            col_map[i] = 'Na'
        elif hc.startswith('k') and len(hc) <= 3:        col_map[i] = 'K'
        elif 'iron' in hc:                                col_map[i] = 'Iron'
        elif 'hco' in hc:                                 col_map[i] = 'HCO3'
        elif 'chloride' in hc:                            col_map[i] = 'Cl'
        elif 'sulphate' in hc:                            col_map[i] = 'SO4'
        elif 'nitrate' in hc:                             col_map[i] = 'NO3'
        elif 'fluoride' in hc:                            col_map[i] = 'F'
        elif hc in ('do', 'do  ', 'do '):                 col_map[i] = 'DO'

    df_clean = df[list(col_map.keys())].copy()
    df_clean.columns = [col_map[k] for k in col_map.keys()]
    if df_clean.columns.duplicated().any():
        df_clean = df_clean.loc[:, ~df_clean.columns.duplicated(keep='first')]
    if 'Sites' in df_clean.columns:
        df_clean['Sites'] = df_clean['Sites'].ffill()

    for col in Config.CHEM_COLS + ['Latitude', 'Longitude']:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

    df_clean['Season'] = season
    df_clean = df_clean.dropna(subset=['Location_ID']).reset_index(drop=True)
    print(f"    Cleaned: {df_clean.shape}  Locations: {df_clean['Location_ID'].tolist()}")
    return df_clean


def load_all_seasons():
    print("\n" + "=" * 70)
    print("TASK 1: DATA RECONSTRUCTION AND CLEANING")
    print("=" * 70)

    dfs = []
    for sheet, season in Config.SHEET_MAP.items():
        dfs.append(load_and_clean_sheet(Config.DATA_FILE, sheet, season))

    all_cols = set()
    for df in dfs:
        all_cols |= set(df.columns)
    for col in all_cols:
        for df in dfs:
            if col not in df.columns:
                df[col] = np.nan

    df_master = pd.concat(dfs, ignore_index=True)
    ordered = [c for c in Config.META_COLS + Config.CHEM_COLS if c in df_master.columns]
    df_master = df_master[ordered]

    print(f"\n  MASTER: {df_master.shape[0]} samples x {df_master.shape[1]} cols")
    print(f"  Seasons: {df_master['Season'].value_counts().to_dict()}")
    save_dataset(df_master, 'cleaned_original_2024.csv')
    return df_master


# ============================================================================
# SYNTHETIC DATA GENERATION
# ============================================================================
def generate_synthetic_data(df_original, n_per_season=None):
    if n_per_season is None:
        n_per_season = Config.SYNTHETIC_SAMPLES_PER_SEASON
    np.random.seed(Config.RANDOM_SEED)

    print("\n" + "=" * 70)
    print("SYNTHETIC DATA GENERATION")
    print("=" * 70)

    chem = Config.CHEM_COLS
    bounds = {
        'pH': (4.0, 9.5), 'EC': (50, 3000), 'TDS': (30, 2000),
        'TH': (2, 800), 'Alkalinity': (10, 600), 'Ca': (5, 200),
        'Mg': (1, 100), 'Na': (2, 300), 'K': (0.5, 50),
        'Iron': (0.01, 5.0), 'HCO3': (10, 500), 'Cl': (5, 500),
        'SO4': (1, 400), 'NO3': (0.5, 150), 'F': (0.01, 5.0),
        'DO': (2.0, 12.0)
    }

    locations = df_original['Location_ID'].unique()
    sites_map = df_original.drop_duplicates('Location_ID').set_index('Location_ID')[
        ['Sites', 'Areas', 'Latitude', 'Longitude']]

    synthetic_dfs = []
    for season in Config.SEASON_ORDER:
        print(f"\n  Generating {n_per_season} synthetic samples for {season}...")
        sdata = df_original[df_original['Season'] == season][chem].dropna()
        mean_vec = sdata.mean().values
        cov_mat = sdata.cov().values + np.eye(len(chem)) * 1e-4

        raw = np.random.multivariate_normal(mean_vec, cov_mat, size=n_per_season)
        df_syn = pd.DataFrame(raw, columns=chem)

        for col in chem:
            if col in bounds:
                df_syn[col] = df_syn[col].clip(bounds[col][0], bounds[col][1])
            df_syn[col] = df_syn[col].round(2 if col not in ('F', 'Iron') else 3)

        syn_ids, syn_sites, syn_areas, syn_lats, syn_longs = [], [], [], [], []
        for i in range(n_per_season):
            if i < len(locations):
                loc = locations[i % len(locations)]
                syn_ids.append(f"SYN-{loc}")
                row = sites_map.loc[loc]
                syn_sites.append(row['Sites'])
                syn_areas.append(str(row['Areas']) + ' (Syn)')
                syn_lats.append(row['Latitude'] + np.random.uniform(-0.01, 0.01))
                syn_longs.append(row['Longitude'] + np.random.uniform(-0.01, 0.01))
            else:
                syn_ids.append(f"SYN-X{i - len(locations) + 1}")
                syn_sites.append('Synthetic Zone')
                syn_areas.append(f'Synthetic Area {i - len(locations) + 1}')
                syn_lats.append(df_original['Latitude'].mean() + np.random.uniform(-0.05, 0.05))
                syn_longs.append(df_original['Longitude'].mean() + np.random.uniform(-0.05, 0.05))

        df_syn['Sl_No'] = range(1, n_per_season + 1)
        df_syn['Sites'] = syn_sites
        df_syn['Areas'] = syn_areas
        df_syn['Location_ID'] = syn_ids
        df_syn['Latitude'] = syn_lats
        df_syn['Longitude'] = syn_longs
        df_syn['Season'] = season
        df_syn['Data_Type'] = 'Synthetic'
        synthetic_dfs.append(df_syn)
        print(f"    TDS: [{df_syn['TDS'].min():.1f}, {df_syn['TDS'].max():.1f}]  "
              f"pH: [{df_syn['pH'].min():.2f}, {df_syn['pH'].max():.2f}]")

    df_synthetic = pd.concat(synthetic_dfs, ignore_index=True)
    df_orig_tagged = df_original.copy()
    df_orig_tagged['Data_Type'] = 'Original'

    # Align columns
    all_c = list(set(df_synthetic.columns) | set(df_orig_tagged.columns))
    for c in all_c:
        if c not in df_synthetic.columns:
            df_synthetic[c] = np.nan
        if c not in df_orig_tagged.columns:
            df_orig_tagged[c] = np.nan

    ordered = [c for c in Config.META_COLS + Config.CHEM_COLS + ['Data_Type'] if c in all_c]
    df_combined = pd.concat([df_orig_tagged[ordered], df_synthetic[ordered]], ignore_index=True)

    print(f"\n  Synthetic: {len(df_synthetic)} | Original: {len(df_orig_tagged)} | Combined: {len(df_combined)}")

    # Save all
    save_dataset(df_synthetic, 'synthetic_only.csv')
    save_dataset(df_combined, 'synthetic.csv')

    # Distribution comparison table
    print(f"\n  {'Param':<12} {'Orig Mean':>10} {'Syn Mean':>10} {'Diff%':>8}")
    print(f"  {'-'*42}")
    for col in chem:
        om = df_original[col].mean()
        sm = df_synthetic[col].mean()
        d = (sm - om) / om * 100 if om != 0 else 0
        print(f"  {col:<12} {om:>10.2f} {sm:>10.2f} {d:>+7.1f}%")

    # Distribution comparison plot
        units = {
        "pH": "", "EC": "µS/cm", "TDS": "mg/L",
        "Ca": "mg/L", "Mg": "mg/L", "Na": "mg/L",
        "K": "mg/L", "Cl": "mg/L", "SO4": "mg/L",
        "HCO3": "mg/L", "NO3": "mg/L"
    }

    plt.rcParams.update({
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 11,
        "legend.fontsize": 8
    })

    # ⬅ Increased width
    fig, axes = plt.subplots(4, 4, figsize=(20, 16))
    axes = axes.flatten()

    for i, col in enumerate(chem):
        ax = axes[i]
        combined = pd.concat([df_original[col], df_synthetic[col]]).dropna()
        bins = np.histogram_bin_edges(combined, bins=12)

        ax.hist(df_original[col].dropna(), bins=bins,
                alpha=0.6, label="Original",
                density=True, edgecolor="black")

        ax.hist(df_synthetic[col].dropna(), bins=bins,
                alpha=0.5, label="Synthetic",
                density=True, edgecolor="black")

        unit = units.get(col, "")
        ax.set_title(f"{col} ({unit})" if unit else col, fontweight="bold")
        ax.grid(alpha=0.25)

    for j in range(len(chem), len(axes)):
        axes[j].set_visible(False)

    # Proper margin adjustment (THIS IS IMPORTANT)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.08, top=0.92)

    # Shared labels (position adjusted inward)
    fig.text(0.04, 0.5, "Probability Density",
             va="center", rotation="vertical", fontsize=14)

    fig.text(0.5, 0.04, "Concentration / Parameter Value",
             ha="center", fontsize=14)

    fig.suptitle("Comparison of Original and Synthetic Groundwater Parameter Distributions",
                 fontsize=16, fontweight="bold")

    fig.savefig("fig_original_vs_synthetic_publication.png",
                dpi=600, bbox_inches="tight")

    plt.show()
    return df_synthetic, df_combined


# ============================================================================
# TASK 2: DATA VALIDATION
# ============================================================================
def validate_data(df, label="Dataset"):
    print(f"\n{'='*70}")
    print(f"TASK 2: DATA VALIDATION - {label}")
    print(f"{'='*70}")

    chem = Config.CHEM_COLS

    # Missing values
    missing = df[chem].isnull().sum()
    has_miss = missing.sum() > 0
    if has_miss:
        print("\n  Missing values:")
        print(missing[missing > 0].to_string())
    else:
        print("\n  No missing values.")

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(df[chem].isnull().T, cbar=True, yticklabels=True, cmap='YlOrRd', ax=ax)
    ax.set_title(f'Missing Values - {label}')
    plt.tight_layout()
    save_fig(fig, 'task2_validation', f'fig_missing_{label.lower().replace(" ","_")}.png')

    if has_miss:
        print("  KNN imputation...")
        imputer = KNNImputer(n_neighbors=3)
        df[chem] = pd.DataFrame(imputer.fit_transform(df[chem]), columns=chem, index=df.index)

    # Outliers
    print("\n  Outlier Detection:")
    for col in chem:
        data = df[col].dropna()
        Q1, Q3 = data.quantile(0.25), data.quantile(0.75)
        IQR = Q3 - Q1
        iqr_n = ((data < Q1 - 1.5*IQR) | (data > Q3 + 1.5*IQR)).sum()
        z_n = (np.abs(stats.zscore(data)) > 3).sum() if len(data) > 2 else 0
        if iqr_n > 0 or z_n > 0:
            print(f"    {col}: IQR={iqr_n}, Z={z_n}")

    # CBE
    meq = mg_to_meq(df)
    meq['TCC'] = meq[['Ca_meq', 'Mg_meq', 'Na_meq', 'K_meq']].sum(axis=1)
    meq['TCA'] = meq[['HCO3_meq', 'Cl_meq', 'SO4_meq', 'NO3_meq']].sum(axis=1)
    meq['CBE'] = ((meq['TCC'] - meq['TCA']) / (meq['TCC'] + meq['TCA'])) * 100
    df['CBE'] = meq['CBE'].values
    df['TCC_meq'] = meq['TCC'].values
    df['TCA_meq'] = meq['TCA'].values
    valid = df['CBE'].abs() <= Config.CBE_THRESHOLD
    df['CBE_Valid'] = valid
    nv = valid.sum()
    print(f"\n  CBE: {nv}/{len(df)} valid ({nv/len(df)*100:.1f}%)")
    print(f"  CBE range: [{df['CBE'].min():.1f}%, {df['CBE'].max():.1f}%]")

    # Descriptive stats
    desc = df[chem].describe().round(3)
    desc.loc['skewness'] = df[chem].skew().round(3)
    desc.loc['kurtosis'] = df[chem].kurtosis().round(3)
    desc.loc['CV%'] = ((df[chem].std() / df[chem].mean()) * 100).round(2)
    print("\n  Descriptive Statistics:")
    print(desc.to_string())
    return df


# ============================================================================
# TASK 3: EDA + SEASONAL ANALYSIS
# ============================================================================
def run_eda_and_seasonal(df):
    print(f"\n{'='*70}")
    print("TASK 3: EDA & SEASONAL DYNAMICS")
    print(f"{'='*70}")

    chem = Config.CHEM_COLS
    seasons = Config.SEASON_ORDER
    palette = Config.SEASON_COLORS

    # Distributions
    fig, axes = plt.subplots(4, 4, figsize=(18, 16))
    for i, col in enumerate(chem):
        ax = axes.flatten()[i]
        for s in seasons:
            ax.hist(df[df['Season'] == s][col].dropna(), bins=10, alpha=0.5, label=s, density=True)
        ax.set_title(col); ax.legend(fontsize=7)
    fig.suptitle('Distributions by Season', fontsize=14, y=1.01)
    plt.tight_layout()
    save_fig(fig, 'task3_seasonal', 'fig_distributions.png')

    # Correlation
    fig, ax = plt.subplots(figsize=(14, 12))
    corr = df[chem].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax)
    ax.set_title('Pearson Correlation')
    plt.tight_layout()
    save_fig(fig, 'task3_seasonal', 'fig_correlation_matrix.png')

    # Multicollinearity
    print("\n  Multicollinearity (|r|>0.7):")
    for i in range(len(chem)):
        for j in range(i+1, len(chem)):
            if abs(corr.iloc[i, j]) > 0.7:
                print(f"    {chem[i]} <-> {chem[j]}: {corr.iloc[i,j]:.3f}")

    # Seasonal stats
    means = df.groupby('Season')[chem].mean()
    print("\n  Seasonal Means:")
    print(means.loc[seasons].round(2).to_string())

    pct = pd.DataFrame()
    pct['Pre->Mon'] = ((means.loc['Monsoon'] - means.loc['Premonsoon']) / means.loc['Premonsoon'] * 100).round(2)
    pct['Mon->Post'] = ((means.loc['Postmonsoon'] - means.loc['Monsoon']) / means.loc['Monsoon'] * 100).round(2)
    print("\n  % Change:")
    print(pct.to_string())

    # Statistical tests
    print("\n  Statistical Tests:")
    for col in chem:
        groups = [df[df['Season'] == s][col].dropna().values for s in seasons]
        normality = all(stats.shapiro(g)[1] > 0.05 for g in groups if len(g) >= 3)
        if normality:
            stat, p = stats.f_oneway(*groups); test = 'ANOVA'
        else:
            stat, p = stats.kruskal(*groups); test = 'KW'
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
        if sig != 'ns':
            print(f"    {col}: {test} p={p:.4f} {sig}")

    # Boxplots
    fig, axes = plt.subplots(4, 4, figsize=(20, 18))
    for i, col in enumerate(chem):
        sns.boxplot(data=df, x='Season', y=col, order=seasons, palette=palette,
                    ax=axes.flatten()[i], width=0.6)
        axes.flatten()[i].set_title(col, fontweight='bold'); axes.flatten()[i].set_xlabel('')
    fig.suptitle('Seasonal Boxplots', fontsize=15, y=1.01)
    plt.tight_layout()
    save_fig(fig, 'task3_seasonal', 'fig_seasonal_boxplots.png')

    # Violins
    fig, axes = plt.subplots(4, 4, figsize=(20, 18))
    for i, col in enumerate(chem):
        sns.violinplot(data=df, x='Season', y=col, order=seasons, palette=palette,
                       ax=axes.flatten()[i], inner='quartile')
        axes.flatten()[i].set_title(col, fontweight='bold'); axes.flatten()[i].set_xlabel('')
    fig.suptitle('Seasonal Violin Plots', fontsize=15, y=1.01)
    plt.tight_layout()
    save_fig(fig, 'task3_seasonal', 'fig_seasonal_violins.png')

    # Heatmap
    fig, ax = plt.subplots(figsize=(16, 5))
    mn = means.copy()
    for c in chem:
        r = means[c].max() - means[c].min()
        mn[c] = (means[c] - means[c].min()) / r if r > 0 else 0
    sns.heatmap(mn.loc[seasons], annot=means.loc[seasons].round(2).values, fmt='',
                cmap='YlOrRd', ax=ax, linewidths=1)
    ax.set_title('Seasonal Mean Heatmap')
    plt.tight_layout()
    save_fig(fig, 'task3_seasonal', 'fig_seasonal_heatmap.png')

    # Trends
    fig, axes = plt.subplots(4, 4, figsize=(20, 16))
    for i, col in enumerate(chem):
        ax = axes.flatten()[i]
        for loc in df['Location_ID'].unique():
            ld = df[df['Location_ID'] == loc].set_index('Season')
            vals = [ld.loc[s, col] if s in ld.index else np.nan for s in seasons]
            ax.plot(seasons, vals, 'o-', alpha=0.15, markersize=2)
        ax.plot(seasons, [means.loc[s, col] for s in seasons], 's-', color='black',
                linewidth=2.5, markersize=8, zorder=5)
        ax.set_title(col, fontweight='bold'); ax.tick_params(axis='x', rotation=30)
    fig.suptitle('Seasonal Trends (Black=Mean)', fontsize=14, y=1.01)
    plt.tight_layout()
    save_fig(fig, 'task3_seasonal', 'fig_seasonal_trends.png')

    # Pairplot
    key = [p for p in ['pH', 'EC', 'TDS', 'Ca', 'Na', 'Cl', 'HCO3']
           if p in df.columns]

    g = sns.pairplot(
        df[key + ['Season']].dropna(),
        hue='Season',
        diag_kind='kde',
        plot_kws={'alpha': 0.5, 's': 35},
        palette='Set1',
        corner=True
    )

    # Improve spacing so title does not overlap
    g.fig.subplots_adjust(top=0.95)

    g.fig.suptitle(
        "Seasonal Variation of Groundwater Parameters",
        fontsize=16,
        fontweight="bold"
    )

    # Improve axis label font size
    for ax in g.axes.flatten():
        if ax is not None:
            ax.set_xlabel(ax.get_xlabel(), fontsize=10)
            ax.set_ylabel(ax.get_ylabel(), fontsize=10)

    g.fig.savefig(
        "fig_pairplot_publication.png",
        dpi=600,
        bbox_inches="tight"
    )

    plt.show()
    return means


# ============================================================================
# TASK 4: DRINKING WATER SAFETY
# ============================================================================
def assess_drinking_water(df):
    print(f"\n{'='*70}")
    print("TASK 4: DRINKING WATER RISK INTELLIGENCE")
    print(f"{'='*70}")

    results = []
    for _, row in df.iterrows():
        for p in Config.IS_STANDARDS:
            if p in df.columns:
                results.append({'Location_ID': row['Location_ID'], 'Season': row['Season'],
                                'Parameter': p, 'Value': row.get(p, np.nan),
                                'Status': classify_safety(row.get(p, np.nan), p)})
    comp_df = pd.DataFrame(results)

    summary = comp_df.groupby(['Parameter', 'Status']).size().unstack(fill_value=0)
    print("\n  Compliance Summary:")
    print((summary.div(summary.sum(axis=1), axis=0) * 100).round(1).to_string())

    non_safe = comp_df[comp_df['Status'].isin(['Unsafe', 'Marginal'])]
    if len(non_safe) > 0:
        print("\n  Exceedances by Season:")
        print(non_safe.groupby(['Season', 'Parameter']).size().unstack(fill_value=0).to_string())
        print("\n  Worst Locations:")
        worst = non_safe.groupby(['Location_ID', 'Season']).size().reset_index(name='Exc')
        print(worst.sort_values('Exc', ascending=False).head(15).to_string(index=False))

    # Heatmap
    fig, axes = plt.subplots(1, 3, figsize=(22, 8))
    for si, season in enumerate(Config.SEASON_ORDER):
        ax = axes[si]
        sd = df[df['Season'] == season].drop_duplicates('Location_ID').set_index('Location_ID').head(20)
        sn = pd.DataFrame(index=sd.index)
        for p in Config.IS_STANDARDS:
            if p in sd.columns:
                sn[p] = sd[p].apply(lambda v: {'Safe': 0, 'Marginal': 1, 'Unsafe': 2, 'N/A': np.nan}[classify_safety(v, p)])
        sns.heatmap(sn.astype(float), cmap=['#2ecc71', '#f39c12', '#e74c3c'], vmin=0, vmax=2,
                    ax=ax, linewidths=0.5)
        ax.set_title(season, fontweight='bold')
    fig.suptitle('Compliance Heatmap (IS 10500:2012)', fontsize=14)
    plt.tight_layout()
    save_fig(fig, 'task4_safety', 'fig_compliance_heatmap.png')
    return comp_df


# ============================================================================
# TASK 5: SOURCE ANALYSIS
# ============================================================================
def run_source_analysis(df):
    print(f"\n{'='*70}")
    print("TASK 5: SOURCE ANALYSIS")
    print(f"{'='*70}")

    chem = Config.CHEM_COLS
    seasons = Config.SEASON_ORDER
    pal = Config.SEASON_COLORS

    # PCA
    print("\n  --- PCA ---")
    pca_data = df[chem].dropna()
    scaler = StandardScaler()
    Xs = scaler.fit_transform(pca_data)
    pca = PCA()
    scores = pca.fit_transform(Xs)
    ve = pca.explained_variance_ratio_ * 100
    cv = np.cumsum(ve)
    for i in range(min(6, len(ve))):
        print(f"    PC{i+1}: {ve[i]:.2f}% (Cum: {cv[i]:.2f}%)")

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5))
    a1.bar(range(1, len(ve)+1), ve, color='steelblue')
    a1.plot(range(1, len(ve)+1), ve, 'ro-'); a1.set_xlabel('PC'); a1.set_ylabel('%'); a1.set_title('Scree')
    a2.plot(range(1, len(cv)+1), cv, 'bo-'); a2.axhline(80, color='r', ls='--')
    a2.set_xlabel('PCs'); a2.set_ylabel('Cum%'); a2.set_title('Cumulative')
    plt.tight_layout()
    save_fig(fig, 'task5_source', 'fig_pca_scree.png')

    npc = min(4, len(ve))
    loadings = pd.DataFrame(pca.components_[:npc].T, columns=[f'PC{i+1}' for i in range(npc)], index=chem)
    print("\n  PCA Loadings:")
    print(loadings.round(3).to_string())

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(loadings, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax)
    ax.set_title('PCA Loadings')
    plt.tight_layout()
    save_fig(fig, 'task5_source', 'fig_pca_loadings.png')

    fig, ax = plt.subplots(figsize=(10, 8))
    for s in seasons:
        mask = df['Season'].values == s
        idx = np.where(mask[:len(scores)])[0]
        if len(idx):
            ax.scatter(scores[idx, 0], scores[idx, 1], c=pal[s], label=s, s=50, alpha=0.6, edgecolors='k')
    for i, c in enumerate(chem):
        ax.annotate('', xy=(loadings.iloc[i, 0]*5, loadings.iloc[i, 1]*5), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='->', color='gray'))
        ax.text(loadings.iloc[i, 0]*5.5, loadings.iloc[i, 1]*5.5, c, fontsize=8, color='darkred')
    ax.set_xlabel(f'PC1 ({ve[0]:.1f}%)'); ax.set_ylabel(f'PC2 ({ve[1]:.1f}%)')
    ax.set_title('PCA Biplot'); ax.legend()
    plt.tight_layout()
    save_fig(fig, 'task5_source', 'fig_pca_biplot.png')

    # Clustering
    print("\n  --- Clustering ---")
    Z = linkage(Xs, method='ward')
    fig, ax = plt.subplots(figsize=(14, 6))
    lbl = df['Location_ID'].values[:len(Xs)] if len(Xs) <= 60 else ['' for _ in range(len(Xs))]
    dendrogram(Z, labels=lbl, leaf_rotation=90, leaf_font_size=6, ax=ax, color_threshold=0.7*max(Z[:, 2]))
    ax.set_title("Dendrogram (Ward's)"); ax.set_ylabel('Distance')
    plt.tight_layout()
    save_fig(fig, 'task5_source', 'fig_dendrogram.png')

    Kr = range(2, min(10, len(Xs)//2))
    inertias = [KMeans(n_clusters=k, random_state=42, n_init=10).fit(Xs).inertia_ for k in Kr]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(list(Kr), inertias, 'bo-'); ax.set_xlabel('k'); ax.set_ylabel('Inertia'); ax.set_title('Elbow')
    plt.tight_layout()
    save_fig(fig, 'task5_source', 'fig_elbow.png')

    km = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = km.fit_predict(Xs)
    dt = df.iloc[:len(Xs)].copy(); dt['Cluster'] = clusters
    print("\n  Cluster Means:")
    print(dt.groupby('Cluster')[chem].mean().round(2).to_string())

    fig, ax = plt.subplots(figsize=(10, 8))
    for c in range(3):
        idx = np.where(clusters == c)[0]
        ax.scatter(scores[idx, 0], scores[idx, 1], label=f'Cluster {c+1}', s=50, alpha=0.7, edgecolors='k')
    ax.set_xlabel(f'PC1 ({ve[0]:.1f}%)'); ax.set_ylabel(f'PC2 ({ve[1]:.1f}%)')
    ax.set_title('K-Means in PCA Space'); ax.legend()
    plt.tight_layout()
    save_fig(fig, 'task5_source', 'fig_kmeans_pca.png')

    # Ionic ratios
    print("\n  --- Ionic Ratios ---")
    meq = mg_to_meq(df)
    df['Na_Cl'] = meq['Na_meq'] / meq['Cl_meq']
    df['Ca_Mg'] = meq['Ca_meq'] / meq['Mg_meq']
    print(df.groupby('Season')[['Na_Cl', 'Ca_Mg']].mean().round(3).to_string())

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    for s in seasons:
        sm = mg_to_meq(df[df['Season'] == s])
        axes[0, 0].scatter(sm['Cl_meq'], sm['Na_meq'], c=pal[s], label=s, s=40, alpha=0.7)
        axes[0, 1].scatter(sm['Mg_meq'], sm['Ca_meq'], c=pal[s], label=s, s=40, alpha=0.7)
        axes[1, 0].scatter(sm['HCO3_meq']+sm['SO4_meq'], sm['Ca_meq']+sm['Mg_meq'], c=pal[s], label=s, s=40, alpha=0.7)
        axes[1, 1].scatter(sm['HCO3_meq'], sm['Ca_meq']+sm['Mg_meq'], c=pal[s], label=s, s=40, alpha=0.7)
    for ax in axes.flat:
        lm = [min(ax.get_xlim()[0], ax.get_ylim()[0]), max(ax.get_xlim()[1], ax.get_ylim()[1])]
        ax.plot(lm, lm, 'k--', alpha=0.4); ax.legend(fontsize=8)
    axes[0, 0].set_xlabel('Cl'); axes[0, 0].set_ylabel('Na'); axes[0, 0].set_title('Na vs Cl (meq/L)')
    axes[0, 1].set_xlabel('Mg'); axes[0, 1].set_ylabel('Ca'); axes[0, 1].set_title('Ca vs Mg')
    axes[1, 0].set_xlabel('HCO3+SO4'); axes[1, 0].set_ylabel('Ca+Mg'); axes[1, 0].set_title('Weathering Balance')
    axes[1, 1].set_xlabel('HCO3'); axes[1, 1].set_ylabel('Ca+Mg'); axes[1, 1].set_title('Carbonate Weathering')
    fig.suptitle('Ionic Ratio Plots', fontsize=14)
    plt.tight_layout()
    save_fig(fig, 'task5_source', 'fig_ionic_ratios.png')

    # Piper
    print("\n  --- Piper Diagram ---")
    mf = mg_to_meq(df)
    ct = mf[['Ca_meq', 'Mg_meq', 'Na_meq', 'K_meq']].sum(axis=1)
    at = mf[['HCO3_meq', 'Cl_meq', 'SO4_meq']].sum(axis=1)
    ca_p = mf['Ca_meq'] / ct * 100; mg_p = mf['Mg_meq'] / ct * 100
    nak_p = (mf['Na_meq'] + mf['K_meq']) / ct * 100
    hco3_p = mf['HCO3_meq'] / at * 100; cl_p = mf['Cl_meq'] / at * 100

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for s in seasons:
        m = df['Season'] == s
        axes[0].scatter(nak_p[m], ca_p[m], c=pal[s], label=s, s=40, alpha=0.7, edgecolors='k')
        axes[1].scatter(cl_p[m], hco3_p[m], c=pal[s], label=s, s=40, alpha=0.7, edgecolors='k')
        axes[2].scatter((nak_p[m]+cl_p[m])/2, (ca_p[m]+hco3_p[m])/2, c=pal[s], label=s, s=40, alpha=0.7, edgecolors='k')
    axes[0].set_xlabel('Na+K%'); axes[0].set_ylabel('Ca%'); axes[0].set_title('Cations')
    axes[1].set_xlabel('Cl%'); axes[1].set_ylabel('HCO3%'); axes[1].set_title('Anions')
    axes[2].set_xlabel('(Na+K+Cl)/2'); axes[2].set_ylabel('(Ca+HCO3)/2'); axes[2].set_title('Diamond')
    for ax in axes: ax.legend(); ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    fig.suptitle('Piper Diagram', fontsize=14)
    plt.tight_layout()
    save_fig(fig, 'task5_source', 'fig_piper_diagram.png')

    facies = []
    for i in range(len(df)):
        cat = 'Ca' if ca_p.iloc[i] > 50 else ('Mg' if mg_p.iloc[i] > 50 else 'Na-K')
        an = 'HCO3' if hco3_p.iloc[i] > 50 else ('Cl' if cl_p.iloc[i] > 50 else 'SO4')
        facies.append(f"{cat}-{an}")
    df['Facies'] = facies
    print("\n  Facies:")
    print(df.groupby(['Season', 'Facies']).size().unstack(fill_value=0).to_string())

    # Gibbs
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    for s in seasons:
        sd = df[df['Season'] == s]
        axes[0].scatter(sd['Na']/(sd['Na']+sd['Ca']), sd['TDS'], c=pal[s], label=s, s=40, alpha=0.7, edgecolors='k')
        axes[1].scatter(sd['Cl']/(sd['Cl']+sd['HCO3']), sd['TDS'], c=pal[s], label=s, s=40, alpha=0.7, edgecolors='k')
    for ax in axes:
        ax.set_ylabel('TDS (mg/L)'); ax.set_xlim(0, 1); ax.set_yscale('log'); ax.legend()
    axes[0].set_xlabel('Na/(Na+Ca)'); axes[0].set_title('Gibbs I - Cation')
    axes[1].set_xlabel('Cl/(Cl+HCO3)'); axes[1].set_title('Gibbs II - Anion')
    fig.suptitle('Gibbs Diagrams', fontsize=14)
    plt.tight_layout()
    save_fig(fig, 'task5_source', 'fig_gibbs_diagram.png')
    return df


# ============================================================================
# TASK 6: MACHINE LEARNING
# ============================================================================
def run_ml(df):
    print(f"\n{'='*70}")
    print("TASK 6: MACHINE LEARNING")
    print(f"{'='*70}")

    chem = Config.CHEM_COLS
    targets = Config.ML_TARGETS
    features = [c for c in chem if c not in targets]
    season_map = {s: i for i, s in enumerate(Config.SEASON_ORDER)}

    dml = df.copy()
    dml['Season_num'] = dml['Season'].map(season_map)
    feat_base = features + ['Season_num']

    models_dict = {
        'Random Forest': RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
        'SVR': SVR(kernel='rbf', C=100, epsilon=0.1),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.1, random_state=42),
        'Neural Network': MLPRegressor(hidden_layer_sizes=(64, 32, 16), max_iter=2000, random_state=42, early_stopping=True),
    }

    ml_results = {}
    kf = KFold(n_splits=Config.CV_FOLDS, shuffle=True, random_state=42)

    for target in targets:
        print(f"\n  TARGET: {target}")
        fc = [f for f in feat_base if f != target]
        dc = dml[fc + [target]].dropna()
        X, y = dc[fc].values, dc[target].values
        sX = StandardScaler(); Xn = sX.fit_transform(X)
        sY = StandardScaler(); yn = sY.fit_transform(y.reshape(-1, 1)).ravel()

        tres = {}
        for name, model in models_dict.items():
            scaled = name in ('SVR', 'Neural Network')
            Xu, yu = (Xn, yn) if scaled else (X, y)
            cv_r2 = cross_val_score(model, Xu, yu, cv=kf, scoring='r2')
            m = clone(model); m.fit(Xu, yu); yp = m.predict(Xu)
            if scaled:
                ypo = sY.inverse_transform(yp.reshape(-1, 1)).ravel()
                r2, rmse, mae = r2_score(y, ypo), np.sqrt(mean_squared_error(y, ypo)), mean_absolute_error(y, ypo)
            else:
                r2, rmse, mae = r2_score(y, yp), np.sqrt(mean_squared_error(y, yp)), mean_absolute_error(y, yp)
            tres[name] = {'CV_R2': cv_r2.mean(), 'CV_std': cv_r2.std(), 'R2': r2, 'RMSE': rmse, 'MAE': mae}
            fi_str = ''
            if hasattr(m, 'feature_importances_'):
                fi = sorted(zip(fc, m.feature_importances_), key=lambda x: -x[1])[:3]
                fi_str = f" Top: {', '.join(f'{n}={v:.3f}' for n,v in fi)}"
            print(f"    {name}: CV_R2={cv_r2.mean():.4f}+/-{cv_r2.std():.4f} R2={r2:.4f} RMSE={rmse:.1f}{fi_str}")

        ml_results[target] = tres
        best = max(tres.items(), key=lambda x: x[1]['CV_R2'])
        print(f"    * Best: {best[0]} (CV_R2={best[1]['CV_R2']:.4f})")

    # Feature importance
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    for ti, target in enumerate(targets):
        ax = axes[ti]
        fc = [f for f in feat_base if f != target]
        dc = dml[fc + [target]].dropna()
        rf = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
        rf.fit(dc[fc].values, dc[target].values)
        fi = pd.DataFrame({'F': fc, 'I': rf.feature_importances_}).sort_values('I')
        ax.barh(fi['F'], fi['I'], color='steelblue', edgecolor='navy')
        ax.set_title(f'RF Importance - {target}')
    plt.tight_layout()
    save_fig(fig, 'task6_ml', 'fig_feature_importance.png')

    # Actual vs Predicted
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    for ti, target in enumerate(targets):
        fc = [f for f in feat_base if f != target]
        dc = dml[fc + [target]].dropna()
        X, y = dc[fc].values, dc[target].values
        for mi, (mn, clr) in enumerate([('RF', 'steelblue'), ('GB', 'darkorange')]):
            ax = axes[ti, mi]
            m = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1) if mn == 'RF' else GradientBoostingRegressor(n_estimators=200, max_depth=4, random_state=42)
            m.fit(X, y); yp = m.predict(X)
            ax.scatter(y, yp, c=clr, s=40, alpha=0.6, edgecolors='k')
            lm = [min(y.min(), yp.min()), max(y.max(), yp.max())]
            ax.plot(lm, lm, 'r--', lw=2)
            ax.set_xlabel(f'Actual {target}'); ax.set_ylabel(f'Predicted')
            ax.set_title(f'{mn}: {target} (R2={r2_score(y, yp):.3f})')
    fig.suptitle('Actual vs Predicted', fontsize=14)
    plt.tight_layout()
    save_fig(fig, 'task6_ml', 'fig_actual_vs_predicted.png')
    return ml_results


# ============================================================================
# TASK 7: INSIGHTS
# ============================================================================
def generate_insights(df, ml_results):
    print(f"\n{'='*70}")
    print("TASK 7: SCIENTIFIC INSIGHTS")
    print(f"{'='*70}")

    chem = Config.CHEM_COLS

    print("\n  Salinity Drivers (corr with TDS):")
    print(df[chem].corrwith(df['TDS']).sort_values(ascending=False).round(3).to_string())

    print("\n  Seasonal Ranking:")
    season_exc = {}
    for s in Config.SEASON_ORDER:
        sd = df[df['Season'] == s]
        exc = sum(1 for _, r in sd.iterrows() for p in Config.IS_STANDARDS if p in sd.columns and classify_safety(r.get(p, np.nan), p) in ('Unsafe', 'Marginal'))
        season_exc[s] = exc
        print(f"    {s}: {exc} exceedances")
    worst = max(season_exc, key=season_exc.get)
    print(f"    * Worst: {worst}")

    print("\n  Location Ranking (TDS):")
    print(df.groupby('Location_ID')[['TDS', 'EC', 'pH']].mean().sort_values('TDS', ascending=False).round(2).head(10).to_string())

    meq = mg_to_meq(df)
    cat_m = meq[['Ca_meq', 'Mg_meq', 'Na_meq', 'K_meq']].mean()
    an_m = meq[['HCO3_meq', 'Cl_meq', 'SO4_meq', 'NO3_meq']].mean()
    dom_cat = cat_m.idxmax().replace('_meq', '')
    dom_an = an_m.idxmax().replace('_meq', '')
    print(f"\n  Dominant type: {dom_cat}-{dom_an}")
    print(f"  NO3: mean={df['NO3'].mean():.1f}, max={df['NO3'].max():.1f}")
    print(f"  Na-Cl excess: {(df['Na']/22.99 - df['Cl']/35.45).mean():.3f} meq/L")

    na_r = (df['Na'] / (df['Na'] + df['Ca'])).mean()
    bt = max(ml_results.get('TDS', {}).items(), key=lambda x: x[1]['CV_R2'], default=('N/A', {'CV_R2': 0}))
    be = max(ml_results.get('EC', {}).items(), key=lambda x: x[1]['CV_R2'], default=('N/A', {'CV_R2': 0}))

    # Radar
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))
    means = df.groupby('Season')[chem].mean()
    mn = means.copy()
    for c in chem:
        r = means[c].max() - means[c].min()
        mn[c] = (means[c] - means[c].min()) / r if r > 0 else 0
    angles = np.linspace(0, 2*np.pi, len(chem), endpoint=False).tolist() + [0]
    for s in Config.SEASON_ORDER:
        vals = mn.loc[s].tolist() + [mn.loc[s].tolist()[0]]
        ax.plot(angles, vals, 'o-', label=s, color=Config.SEASON_COLORS[s], linewidth=2)
        ax.fill(angles, vals, alpha=0.1, color=Config.SEASON_COLORS[s])
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(chem, fontsize=9)
    ax.set_title('Seasonal Radar', pad=20); ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    save_fig(fig, 'task7_insights', 'fig_seasonal_radar.png')

    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"  Samples: {len(df)}")
    print(f"  Facies: {dom_cat}-{dom_an}")
    print(f"  Worst Season: {worst}")
    print(f"  Mechanism: {'Rock weathering' if na_r < 0.5 else 'Evaporation/Mixed'}")
    print(f"  Best ML (TDS): {bt[0]} (CV R2={bt[1]['CV_R2']:.4f})")
    print(f"  Best ML (EC):  {be[0]} (CV R2={be[1]['CV_R2']:.4f})")
    return {'worst_season': worst, 'dominant_type': f'{dom_cat}-{dom_an}'}


# ============================================================================
# MAIN PIPELINE
# ============================================================================
def main():
    t0 = datetime.now()
    print("=" * 70)
    print("SCALABLE HYDROCHEMICAL INTELLIGENCE PIPELINE")
    print(f"Started: {t0.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    Config.setup_dirs()

    # Task 1
    df_original = load_all_seasons()

    # Synthetic generation
    df_synthetic, df_combined = generate_synthetic_data(df_original)

    # Task 2
    df_original = validate_data(df_original, "Original")
    df_combined = validate_data(df_combined, "Combined")
    save_dataset(df_original, 'validated_original.csv')
    save_dataset(df_combined, 'validated_combined.csv')

    # Task 3
    run_eda_and_seasonal(df_combined)

    # Task 4
    assess_drinking_water(df_combined)

    # Task 5
    df_combined = run_source_analysis(df_combined)

    # Task 6
    ml_results = run_ml(df_combined)

    # Task 7
    generate_insights(df_combined, ml_results)

    save_dataset(df_combined, 'final_analyzed.csv')

    elapsed = (datetime.now() - t0).total_seconds()
    print(f"\nPIPELINE COMPLETE in {elapsed:.1f}s")
    print(f"Datasets -> {Config.DATASET_DIR}")
    print(f"Figures  -> {Config.FIGURE_DIR}")


if __name__ == '__main__':
    main()
