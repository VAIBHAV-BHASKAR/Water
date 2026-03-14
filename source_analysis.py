#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
===============================================================================
ANTHROPOGENIC vs. GEOGENIC SOURCE IDENTIFICATION PIPELINE
Groundwater Quality Analysis — Bhubaneswar, 2024
Three Seasons: Premonsoon, Monsoon, Postmonsoon

Complete 14-step source fingerprinting analysis:
  Steps 1–2:  Data loading & meq/L conversion
  Step  3:    Diagnostic indices (ionic ratios, CAI, Gibbs coords, PIG, NBL)
  Steps 4–5:  Seasonal & area-wise statistical analysis
  Steps 6–8:  Piper diagram, Gibbs diagram, ionic-ratio scatter plots
  Steps 9–11: PCA, K-Means, hierarchical clustering
  Step  12:   Master attribution table
  Step  13:   CSV/figure export
  Step  14:   Markdown report
===============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from itertools import combinations
import os, sys, io, textwrap
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    import scikit_posthocs as sp
    HAS_POSTHOCS = True
except ImportError:
    HAS_POSTHOCS = False

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = BASE_DIR / 'datasets' / 'cleaned_hydrochemical_data_2024.csv'
FIG_DIR = BASE_DIR / 'figures' / 'task5_source'
CSV_DIR = BASE_DIR / 'datasets'

SEASON_ORDER = ['Premonsoon', 'Monsoon', 'Postmonsoon']
SEASON_COLORS = {'Premonsoon': '#e74c3c', 'Monsoon': '#3498db', 'Postmonsoon': '#2ecc71'}

# Area-type grouping (derived from Location_ID prefix)
AREA_TYPES = {'PD': 'Population Density', 'IA': 'Industrial Area', 'DY': 'Dumping Yard'}
AREA_COLORS = {'PD': '#2196F3', 'IA': '#F44336', 'DY': '#4CAF50'}  # Blue, Red, Green

# Marker styles for seasons
SEASON_MARKERS = {'Premonsoon': 'o', 'Monsoon': 's', 'Postmonsoon': '^'}
SEASON_FILL = {
    'Premonsoon': {'facecolors': None, 'edgecolors': None},   # solid
    'Monsoon': {'facecolors': 'white', 'edgecolors': None},   # half-filled (open face)
    'Postmonsoon': {'facecolors': 'none', 'edgecolors': None},  # open
}

SAVE_DPI = 300
CHEM_COLS = ['pH', 'EC', 'TDS', 'TH', 'Alkalinity', 'Ca', 'Mg', 'Na', 'K',
             'Iron', 'HCO3', 'Cl', 'SO4', 'NO3', 'F', 'DO']
MEQ_IONS = ['Ca', 'Mg', 'Na', 'K', 'HCO3', 'Cl', 'SO4', 'NO3', 'Iron', 'F']

# Equivalent weights for meq/L conversion
EQ_WEIGHTS = {
    'Ca': 20.04, 'Mg': 12.15, 'Na': 23.00, 'K': 39.10,
    'HCO3': 61.02, 'Cl': 35.45, 'SO4': 48.03, 'NO3': 62.00,
    'Iron': 27.93, 'F': 19.00,
}

# IS 10500:2012 Permissible limits (for PIG calculation)
IS10500_PERMISSIBLE = {
    'pH': 8.5, 'TDS': 2000, 'TH': 600, 'Alkalinity': 600,
    'Ca': 200, 'Mg': 100, 'Na': 200, 'K': 12,
    'Iron': 0.3, 'HCO3': 600, 'Cl': 1000, 'SO4': 400,
    'NO3': 45, 'F': 1.5, 'EC': 3000,
}

# Natural Background Level (NBL) ranges — Indian hard-rock aquifers
# Based on published literature for peninsular gneissic complex
NBL_RANGES = {
    'Iron': (0.0, 0.3), 'F': (0.0, 1.0), 'NO3': (0.0, 10.0),
    'Cl': (0.0, 50.0), 'SO4': (0.0, 30.0), 'Na': (0.0, 30.0),
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def save_fig(fig, filename):
    path = FIG_DIR / filename
    fig.savefig(path, dpi=SAVE_DPI, bbox_inches='tight')
    plt.close(fig)
    print(f"  [FIG] {path.relative_to(BASE_DIR)}")

def save_csv(df, filename):
    path = CSV_DIR / filename
    df.to_csv(path, index=False)
    print(f"  [CSV] {path.relative_to(BASE_DIR)}")

def get_area_type(loc_id):
    """Extract area type prefix from Location_ID (e.g. 'PD-1' -> 'PD')."""
    return loc_id.split('-')[0]


# ============================================================================
# STEP 1: DATA LOADING
# ============================================================================
def load_data():
    print(f"\n{'='*70}")
    print("STEP 1: DATA LOADING")
    print(f"{'='*70}")

    df = pd.read_csv(DATA_FILE)
    df['Area_Type'] = df['Location_ID'].apply(get_area_type)
    df['Area_Label'] = df['Area_Type'].map(AREA_TYPES)

    print(f"  Loaded {len(df)} samples from {DATA_FILE.name}")
    print(f"  Locations: {sorted(df['Location_ID'].unique())}")
    print(f"  Seasons: {list(df['Season'].unique())}")
    print(f"  Area types: {dict(df.groupby('Area_Type').size())}")
    return df


# ============================================================================
# STEP 2: meq/L CONVERSION
# ============================================================================
def convert_to_meq(df):
    print(f"\n{'='*70}")
    print("STEP 2: meq/L CONVERSION")
    print(f"{'='*70}")

    meq = pd.DataFrame(index=df.index)
    for ion, ew in EQ_WEIGHTS.items():
        if ion in df.columns:
            col_name = f'{ion}_meq'
            meq[col_name] = df[ion] / ew
            print(f"  {ion:>6} / {ew:>6.2f} -> {col_name}")

    # Add meq columns to main df
    for c in meq.columns:
        df[c] = meq[c]

    # Cation/Anion totals
    df['TCC_meq_src'] = df[['Ca_meq', 'Mg_meq', 'Na_meq', 'K_meq']].sum(axis=1)
    df['TCA_meq_src'] = df[['HCO3_meq', 'Cl_meq', 'SO4_meq', 'NO3_meq']].sum(axis=1)

    save_csv(meq.assign(Location_ID=df['Location_ID'], Season=df['Season']),
             'source_meq_conversion.csv')
    print(f"  meq/L conversion table saved ({len(meq)} rows, {len(meq.columns)} ions)")
    return df


# ============================================================================
# STEP 3: DIAGNOSTIC INDICES
# ============================================================================
def compute_diagnostic_indices(df):
    print(f"\n{'='*70}")
    print("STEP 3: DIAGNOSTIC INDICES")
    print(f"{'='*70}")

    # --- 3a: Ionic Ratios ---
    print("\n  --- 3a: Ionic Ratios ---")
    df['Na_Cl_meq'] = df['Na_meq'] / df['Cl_meq']
    df['Ca_Mg_meq'] = df['Ca_meq'] / df['Mg_meq']
    df['HCO3_Cl_meq'] = df['HCO3_meq'] / df['Cl_meq']
    df['Ca_SO4_meq'] = df['Ca_meq'] / df['SO4_meq']
    df['Mg_Ca_meq'] = df['Mg_meq'] / df['Ca_meq']
    df['CaMg_HCO3SO4_meq'] = (df['Ca_meq'] + df['Mg_meq']) / (df['HCO3_meq'] + df['SO4_meq'])
    df['Na_K_meq'] = df['Na_meq'] / df['K_meq']
    df['NO3_Cl_meq'] = df['NO3_meq'] / df['Cl_meq']
    df['SO4_Cl_meq'] = df['SO4_meq'] / df['Cl_meq']
    df['HCO3_sum_anion'] = df['HCO3_meq'] / df['TCA_meq_src']

    ratio_cols = ['Na_Cl_meq', 'Ca_Mg_meq', 'HCO3_Cl_meq', 'Ca_SO4_meq',
                  'Mg_Ca_meq', 'CaMg_HCO3SO4_meq', 'Na_K_meq', 'NO3_Cl_meq',
                  'SO4_Cl_meq', 'HCO3_sum_anion']
    diagnostic_labels = {
        'Na_Cl_meq': 'Na/Cl',
        'Ca_Mg_meq': 'Ca/Mg',
        'HCO3_Cl_meq': 'HCO₃/Cl',
        'Ca_SO4_meq': 'Ca/SO₄',
        'Mg_Ca_meq': 'Mg/Ca',
        'CaMg_HCO3SO4_meq': '(Ca+Mg)/(HCO₃+SO₄)',
        'Na_K_meq': 'Na/K',
        'NO3_Cl_meq': 'NO₃/Cl',
        'SO4_Cl_meq': 'SO₄/Cl',
        'HCO3_sum_anion': 'HCO₃/ΣAnion',
    }

    ratio_interpretations = {
        'Na_Cl_meq': '>1: silicate weathering / ion exchange; ≈1: halite dissolution; <1: reverse ion exchange',
        'Ca_Mg_meq': '>1: calcite dissolution; <1: dolomite dissolution; >>2: silicate weathering',
        'HCO3_Cl_meq': '>1: rock-water interaction dominates; <1: saline/evaporation influence',
        'Ca_SO4_meq': '≈1: gypsum dissolution; >1: carbonate/silicate Ca source',
        'Mg_Ca_meq': '>1: dolomite/ferromagnesian minerals; <1: calcite dominance',
        'CaMg_HCO3SO4_meq': '≈1: weathering dominant; >1: reverse ion exchange; <1: ion exchange',
        'Na_K_meq': 'High: albite/Na-feldspar; Low: K-feldspar or agricultural K',
        'NO3_Cl_meq': 'High: agricultural/sewage input; Low: natural or dilution',
        'SO4_Cl_meq': 'High: oxidation of sulfides/industrial; Low: marine/evaporite',
        'HCO3_sum_anion': '>0.5: weathering-controlled; <0.5: anthropogenic anion inputs',
    }

    ratios_summary = df.groupby('Season')[ratio_cols].agg(['mean', 'std']).round(4)
    print(ratios_summary.to_string())

    # --- 3b: Chloro-Alkaline Indices (CAI) ---
    print("\n  --- 3b: Chloro-Alkaline Indices ---")
    # CAI-1 = [Cl − (Na + K)] / Cl  (all in meq/L)
    # CAI-2 = [Cl − (Na + K)] / (SO4 + HCO3 + NO3)  (all in meq/L)
    df['CAI_1'] = (df['Cl_meq'] - (df['Na_meq'] + df['K_meq'])) / df['Cl_meq']
    df['CAI_2'] = (df['Cl_meq'] - (df['Na_meq'] + df['K_meq'])) / (df['SO4_meq'] + df['HCO3_meq'] + df['NO3_meq'])

    # Positive CAI → reverse ion exchange (Ca in solution exchanged for Na in clay)
    # Negative CAI → direct/normal ion exchange (Na released, Ca adsorbed)
    cai_summary = df.groupby('Season')[['CAI_1', 'CAI_2']].agg(['mean', 'std']).round(4)
    print(cai_summary.to_string())
    df['IonExchange'] = np.where((df['CAI_1'] < 0) & (df['CAI_2'] < 0),
                                  'Direct ion exchange',
                                  np.where((df['CAI_1'] > 0) & (df['CAI_2'] > 0),
                                           'Reverse ion exchange', 'Mixed'))
    print(f"\n  Ion exchange classification:\n{df['IonExchange'].value_counts().to_string()}")

    # --- 3c: Gibbs Coordinates ---
    print("\n  --- 3c: Gibbs Coordinates ---")
    df['Gibbs_Cation'] = df['Na'] / (df['Na'] + df['Ca'])  # mg/L ratio
    df['Gibbs_Anion'] = df['Cl'] / (df['Cl'] + df['HCO3'])  # mg/L ratio
    print(f"  Gibbs Cation range: {df['Gibbs_Cation'].min():.3f} - {df['Gibbs_Cation'].max():.3f}")
    print(f"  Gibbs Anion  range: {df['Gibbs_Anion'].min():.3f} - {df['Gibbs_Anion'].max():.3f}")

    # --- 3d: Pollution Index of Groundwater (PIG) ---
    print("\n  --- 3d: Pollution Index of Groundwater (PIG) ---")
    # PIG = Σ (Ow × Sc)  where Ow = 1/Sp  (Sp = IS10500 permissible limit)
    # Sc = C/Sp (C = measured concentration)
    # Classification: <1 insignificant, 1-1.5 low, 1.5-2 moderate, 2-2.5 high, >2.5 very high
    pig_params = [p for p in IS10500_PERMISSIBLE if p in df.columns and p != 'pH']
    pig_values = np.zeros(len(df))
    for p in pig_params:
        sp = IS10500_PERMISSIBLE[p]
        ow = 1.0 / sp
        sc = df[p] / sp
        pig_values += ow * sc

    df['PIG'] = pig_values
    pig_cats = pd.cut(df['PIG'],
                      bins=[-np.inf, 1.0, 1.5, 2.0, 2.5, np.inf],
                      labels=['Insignificant', 'Low', 'Moderate', 'High', 'Very High'])
    df['PIG_Category'] = pig_cats
    print(f"  PIG range: {df['PIG'].min():.4f} - {df['PIG'].max():.4f}")
    print(f"  PIG classification:\n{df['PIG_Category'].value_counts().to_string()}")

    # --- 3e: Natural Background Level (NBL) Exceedance ---
    print("\n  --- 3e: NBL Exceedance ---")
    nbl_flags = {}
    for param, (lo, hi) in NBL_RANGES.items():
        if param in df.columns:
            flag_col = f'{param}_NBL_exceed'
            df[flag_col] = df[param] > hi
            n_exceed = df[flag_col].sum()
            pct = n_exceed / len(df) * 100
            nbl_flags[param] = {'n_exceed': n_exceed, 'pct': f'{pct:.1f}%', 'NBL_upper': hi}
            print(f"  {param:>6}: {n_exceed:>3}/{len(df)} samples exceed NBL ({hi} mg/L) [{pct:.1f}%]")
    df['NBL_total_exceed'] = sum(df[f'{p}_NBL_exceed'].astype(int) for p in NBL_RANGES if p in df.columns)

    # --- 3f: Scatter-plot pairs (to be plotted in Step 8) ---
    scatter_pairs = [
        ('Na_meq', 'Cl_meq'), ('Ca_meq', 'SO4_meq'),
        ('Ca_meq', 'HCO3_meq'), ('Mg_meq', 'HCO3_meq'),
        ('Na_meq', 'HCO3_meq'), ('Ca_meq', 'Mg_meq'),
        ('Na_meq', 'SO4_meq'), ('TCC_meq_src', 'TCA_meq_src'),
        ('Cl_meq', 'NO3_meq'),
    ]

    # Save all diagnostic indices
    idx_cols = (['Location_ID', 'Season', 'Area_Type'] + ratio_cols +
                ['CAI_1', 'CAI_2', 'IonExchange', 'Gibbs_Cation', 'Gibbs_Anion',
                 'PIG', 'PIG_Category', 'NBL_total_exceed'])
    save_csv(df[idx_cols], 'source_diagnostic_indices.csv')

    return df, ratio_cols, diagnostic_labels, ratio_interpretations, scatter_pairs


# ============================================================================
# STEP 4: SEASONAL PATTERN ANALYSIS
# ============================================================================
def seasonal_analysis(df):
    print(f"\n{'='*70}")
    print("STEP 4: SEASONAL PATTERN ANALYSIS")
    print(f"{'='*70}")

    test_params = ['Na_Cl_meq', 'CAI_1', 'NO3', 'Cl', 'SO4', 'TDS', 'EC',
                   'PIG', 'Iron', 'F', 'Na', 'Ca', 'Mg', 'HCO3']

    season_results = []
    for param in test_params:
        if param not in df.columns:
            continue
        groups = [df[df['Season'] == s][param].dropna() for s in SEASON_ORDER]
        if any(len(g) < 3 for g in groups):
            continue

        # Kruskal-Wallis test
        h_stat, p_val = stats.kruskal(*groups)
        sig = 'Yes' if p_val < 0.05 else 'No'

        # Dilution ratio: Premonsoon_mean / Monsoon_mean
        pre_mean = groups[0].mean()
        mon_mean = groups[1].mean()
        dilution = pre_mean / mon_mean if mon_mean != 0 else np.nan

        result = {
            'Parameter': param,
            'Premonsoon_mean': round(pre_mean, 4),
            'Monsoon_mean': round(mon_mean, 4),
            'Postmonsoon_mean': round(groups[2].mean(), 4),
            'Dilution_Ratio': round(dilution, 4),
            'KW_H': round(h_stat, 4),
            'KW_p': round(p_val, 6),
            'Significant_0.05': sig,
        }

        # Dunn's post-hoc if significant
        if p_val < 0.05 and HAS_POSTHOCS:
            data_for_dunn = pd.DataFrame({
                'value': pd.concat(groups, ignore_index=True),
                'season': sum([[s]*len(g) for s, g in zip(SEASON_ORDER, groups)], [])
            })
            dunn_p = sp.posthoc_dunn(data_for_dunn, val_col='value', group_col='season', p_adjust='bonferroni')
            # Extract pairwise comparisons
            pairs = [('Premonsoon', 'Monsoon'), ('Premonsoon', 'Postmonsoon'), ('Monsoon', 'Postmonsoon')]
            for s1, s2 in pairs:
                result[f'Dunn_{s1[:3]}_{s2[:3]}'] = round(dunn_p.loc[s1, s2], 6)

        season_results.append(result)

    season_df = pd.DataFrame(season_results)
    save_csv(season_df, 'source_seasonal_stats.csv')

    print(f"\n  Kruskal-Wallis results:")
    for _, r in season_df.iterrows():
        flag = '*' if r['Significant_0.05'] == 'Yes' else ' '
        print(f"    {flag} {r['Parameter']:<20} H={r['KW_H']:>8.3f}  p={r['KW_p']:.6f}  "
              f"Dilution={r['Dilution_Ratio']:.3f}")

    return season_df


# ============================================================================
# STEP 5: AREA-WISE ANALYSIS
# ============================================================================
def area_analysis(df):
    print(f"\n{'='*70}")
    print("STEP 5: AREA-WISE ANALYSIS (PD vs IA vs DY)")
    print(f"{'='*70}")

    test_params = ['NO3', 'Cl', 'SO4', 'Iron', 'F', 'TDS', 'EC', 'Na',
                   'PIG', 'CAI_1', 'Na_Cl_meq', 'NBL_total_exceed']

    area_results = []
    area_types = ['PD', 'IA', 'DY']

    for param in test_params:
        if param not in df.columns:
            continue
        groups = [df[df['Area_Type'] == a][param].dropna() for a in area_types]
        if any(len(g) < 3 for g in groups):
            continue

        h_stat, p_val = stats.kruskal(*groups)
        sig = 'Yes' if p_val < 0.05 else 'No'

        result = {
            'Parameter': param,
            'PD_mean': round(groups[0].mean(), 4),
            'IA_mean': round(groups[1].mean(), 4),
            'DY_mean': round(groups[2].mean(), 4),
            'KW_H': round(h_stat, 4),
            'KW_p': round(p_val, 6),
            'Significant_0.05': sig,
        }

        # Mann-Whitney pairwise comparisons
        for (i, a1), (j, a2) in combinations(enumerate(area_types), 2):
            u_stat, mw_p = stats.mannwhitneyu(groups[i], groups[j], alternative='two-sided')
            result[f'MW_{a1}_{a2}_p'] = round(mw_p, 6)

        area_results.append(result)

    area_df = pd.DataFrame(area_results)
    save_csv(area_df, 'source_area_stats.csv')

    print(f"\n  Area-wise statistical results:")
    for _, r in area_df.iterrows():
        flag = '*' if r['Significant_0.05'] == 'Yes' else ' '
        print(f"    {flag} {r['Parameter']:<20} PD={r['PD_mean']:>8.3f}  IA={r['IA_mean']:>8.3f}  "
              f"DY={r['DY_mean']:>8.3f}  KW_p={r['KW_p']:.6f}")

    return area_df


# ============================================================================
# STEP 6: PIPER DIAGRAM (Manual ternary implementation)
# ============================================================================
def _ternary_to_cart(a, b, c):
    """Convert ternary coordinates (a, b, c summing to 100) to Cartesian (x, y)."""
    total = a + b + c
    a, b, c = a / total * 100, b / total * 100, c / total * 100
    x = 0.5 * (2 * b + c) / 100.0
    y = (np.sqrt(3) / 2.0) * c / 100.0
    return x, y


def plot_piper(df):
    print(f"\n{'='*70}")
    print("STEP 6: PIPER DIAGRAM")
    print(f"{'='*70}")

    # Calculate %meq for cations and anions
    cat_total = df[['Ca_meq', 'Mg_meq', 'Na_meq', 'K_meq']].sum(axis=1)
    an_total = df[['HCO3_meq', 'Cl_meq', 'SO4_meq']].sum(axis=1)

    # Cation ternary: Ca%, Mg%, (Na+K)%
    ca_pct = df['Ca_meq'] / cat_total * 100
    mg_pct = df['Mg_meq'] / cat_total * 100
    nak_pct = (df['Na_meq'] + df['K_meq']) / cat_total * 100

    # Anion ternary: HCO3%, SO4%, Cl%
    hco3_pct = df['HCO3_meq'] / an_total * 100
    so4_pct = df['SO4_meq'] / an_total * 100
    cl_pct = df['Cl_meq'] / an_total * 100

    fig, axes = plt.subplots(1, 3, figsize=(18, 7))

    # --- Ternary helper ---
    def draw_ternary(ax, title, labels):
        """Draw ternary triangle frame on a matplotlib axes."""
        import matplotlib.patches as mpatches
        # Triangle vertices
        verts = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2]])
        triangle = plt.Polygon(verts, fill=False, edgecolor='black', linewidth=1.2)
        ax.add_patch(triangle)
        # Grid lines
        for i in range(1, 10):
            f = i / 10.0
            # Lines parallel to each side
            p1 = verts[0] + f * (verts[2] - verts[0])
            p2 = verts[1] + f * (verts[2] - verts[1])
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'gray', lw=0.3, alpha=0.5)
            p1 = verts[0] + f * (verts[1] - verts[0])
            p2 = verts[2] + f * (verts[1] - verts[2])
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'gray', lw=0.3, alpha=0.5)
            p1 = verts[1] + f * (verts[2] - verts[1])
            p2 = verts[0] + f * (verts[2] - verts[0])
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'gray', lw=0.3, alpha=0.5)

        # Labels at vertices
        offset = 0.06
        ax.text(0 - offset, -offset, labels[0], ha='center', fontsize=10, fontweight='bold')
        ax.text(1 + offset, -offset, labels[1], ha='center', fontsize=10, fontweight='bold')
        ax.text(0.5, np.sqrt(3)/2 + offset, labels[2], ha='center', fontsize=10, fontweight='bold')
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        ax.set_xlim(-0.15, 1.15)
        ax.set_ylim(-0.15, 1.05)
        ax.set_aspect('equal')
        ax.axis('off')

    # --- Cation ternary ---
    draw_ternary(axes[0], 'Cation Triangle', ['Ca²⁺', 'Na⁺+K⁺', 'Mg²⁺'])
    for _, row in df.iterrows():
        at = row['Area_Type']
        s = row['Season']
        i = df.index.get_loc(_) if _ in df.index else 0
        # Ternary coords: (Ca, Na+K, Mg) — first=left, second=right, third=top
        x, y = _ternary_to_cart(ca_pct.iloc[i], nak_pct.iloc[i], mg_pct.iloc[i])
        c = AREA_COLORS[at]
        m = SEASON_MARKERS[s]
        fc = c if s == 'Premonsoon' else ('white' if s == 'Monsoon' else 'none')
        axes[0].scatter(x, y, c=fc, edgecolors=c, marker=m, s=50, linewidths=1.2, zorder=5)

    # --- Anion ternary ---
    draw_ternary(axes[1], 'Anion Triangle', ['HCO₃⁻', 'Cl⁻', 'SO₄²⁻'])
    for idx_pos in range(len(df)):
        row = df.iloc[idx_pos]
        at = row['Area_Type']
        s = row['Season']
        x, y = _ternary_to_cart(hco3_pct.iloc[idx_pos], cl_pct.iloc[idx_pos], so4_pct.iloc[idx_pos])
        c = AREA_COLORS[at]
        m = SEASON_MARKERS[s]
        fc = c if s == 'Premonsoon' else ('white' if s == 'Monsoon' else 'none')
        axes[1].scatter(x, y, c=fc, edgecolors=c, marker=m, s=50, linewidths=1.2, zorder=5)

    # --- Diamond (simplified as combined scatter) ---
    draw_ternary(axes[2], 'Diamond (Simplified)', ['Ca²⁺+HCO₃⁻', 'Na⁺+Cl⁻', 'Mg²⁺+SO₄²⁻'])
    for idx_pos in range(len(df)):
        row = df.iloc[idx_pos]
        at = row['Area_Type']
        s = row['Season']
        d1 = ca_pct.iloc[idx_pos] + hco3_pct.iloc[idx_pos]
        d2 = nak_pct.iloc[idx_pos] + cl_pct.iloc[idx_pos]
        d3 = mg_pct.iloc[idx_pos] + so4_pct.iloc[idx_pos]
        x, y = _ternary_to_cart(d1, d2, d3)
        c = AREA_COLORS[at]
        m = SEASON_MARKERS[s]
        fc = c if s == 'Premonsoon' else ('white' if s == 'Monsoon' else 'none')
        axes[2].scatter(x, y, c=fc, edgecolors=c, marker=m, s=50, linewidths=1.2, zorder=5)

    # Legend
    legend_elements = []
    for at, label in AREA_TYPES.items():
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                               markerfacecolor=AREA_COLORS[at], markersize=8, label=label))
    for s in SEASON_ORDER:
        m = SEASON_MARKERS[s]
        fc = 'gray' if s == 'Premonsoon' else ('white' if s == 'Monsoon' else 'none')
        legend_elements.append(plt.Line2D([0], [0], marker=m, color='w',
                               markerfacecolor=fc, markeredgecolor='gray', markersize=8, label=s))
    fig.legend(handles=legend_elements, loc='lower center', ncol=6, fontsize=9,
               bbox_to_anchor=(0.5, -0.02))

    fig.suptitle('Piper Diagram — Hydrochemical Facies Classification', fontsize=14, fontweight='bold')
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    save_fig(fig, 'fig_piper_ternary.png')

    # Classify hydrochemical facies
    facies = []
    for i in range(len(df)):
        cat_dom = 'Ca' if ca_pct.iloc[i] > 50 else ('Mg' if mg_pct.iloc[i] > 50 else 'Na-K')
        an_dom = 'HCO₃' if hco3_pct.iloc[i] > 50 else ('Cl' if cl_pct.iloc[i] > 50 else 'SO₄')
        facies.append(f"{cat_dom}-{an_dom}")
    df['Facies_Source'] = facies
    print(f"\n  Facies distribution:")
    print(df.groupby(['Season', 'Facies_Source']).size().unstack(fill_value=0).to_string())
    return df


# ============================================================================
# STEP 7: GIBBS DIAGRAM
# ============================================================================
def plot_gibbs(df):
    print(f"\n{'='*70}")
    print("STEP 7: GIBBS DIAGRAM")
    print(f"{'='*70}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    titles = ['Gibbs I — Cation Ratio', 'Gibbs II — Anion Ratio']
    x_labels = ['Na⁺ / (Na⁺ + Ca²⁺)', 'Cl⁻ / (Cl⁻ + HCO₃⁻)']
    x_cols = ['Gibbs_Cation', 'Gibbs_Anion']

    for ax_idx, (ax, title, xlabel, xcol) in enumerate(zip(axes, titles, x_labels, x_cols)):
        # Draw Gibbs zones (approximate boundaries)
        # Evaporation dominance: upper-right
        ax.annotate('Evaporation\nDominance', xy=(0.8, 5000), fontsize=9,
                     fontstyle='italic', ha='center', color='brown', alpha=0.7)
        # Rock dominance: middle
        ax.annotate('Rock–Water\nInteraction', xy=(0.5, 300), fontsize=9,
                     fontstyle='italic', ha='center', color='darkgreen', alpha=0.7)
        # Precipitation dominance: lower-left
        ax.annotate('Precipitation\nDominance', xy=(0.2, 20), fontsize=9,
                     fontstyle='italic', ha='center', color='blue', alpha=0.7)

        # Draw approximate zone boundaries
        # Rock-water zone box
        ax.fill_between([0.15, 0.85], 50, 5000, alpha=0.05, color='green')
        ax.axhline(50, color='gray', ls=':', alpha=0.3)
        ax.axhline(5000, color='gray', ls=':', alpha=0.3)

        for _, row in df.iterrows():
            at = row['Area_Type']
            s = row['Season']
            c = AREA_COLORS[at]
            m = SEASON_MARKERS[s]
            fc = c if s == 'Premonsoon' else ('white' if s == 'Monsoon' else 'none')
            ax.scatter(row[xcol], row['TDS'], c=fc, edgecolors=c, marker=m,
                       s=60, linewidths=1.2, zorder=5)

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('TDS (mg/L)', fontsize=12)
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.set_xlim(0, 1)
        ax.set_yscale('log')
        ax.set_ylim(10, 10000)

    # Legend
    legend_elements = []
    for at, label in AREA_TYPES.items():
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                               markerfacecolor=AREA_COLORS[at], markersize=8, label=label))
    for s in SEASON_ORDER:
        m = SEASON_MARKERS[s]
        fc = 'gray' if s == 'Premonsoon' else ('white' if s == 'Monsoon' else 'none')
        legend_elements.append(plt.Line2D([0], [0], marker=m, color='w',
                               markerfacecolor=fc, markeredgecolor='gray', markersize=8, label=s))
    axes[1].legend(handles=legend_elements, loc='upper right', fontsize=8)

    fig.suptitle('Gibbs Diagrams — Controlling Mechanisms of Groundwater Chemistry',
                 fontsize=14, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    save_fig(fig, 'fig_gibbs_diagram.png')

    # Classify Gibbs mechanism
    mechanisms = []
    for _, row in df.iterrows():
        gc = row['Gibbs_Cation']
        ga = row['Gibbs_Anion']
        tds = row['TDS']
        if tds > 2000 and (gc > 0.7 or ga > 0.7):
            mechanisms.append('Evaporation Dominance')
        elif tds < 50:
            mechanisms.append('Precipitation Dominance')
        else:
            mechanisms.append('Rock-Water Interaction')
    df['Gibbs_Mechanism'] = mechanisms
    print(f"\n  Gibbs mechanism classification:")
    print(df['Gibbs_Mechanism'].value_counts().to_string())
    return df


# ============================================================================
# STEP 8: IONIC RATIO SCATTER PLOTS (9-panel)
# ============================================================================
def plot_ionic_ratios(df, scatter_pairs):
    print(f"\n{'='*70}")
    print("STEP 8: IONIC RATIO SCATTER PLOTS (9-panel)")
    print(f"{'='*70}")

    label_map = {
        'Na_meq': 'Na⁺ (meq/L)', 'Cl_meq': 'Cl⁻ (meq/L)',
        'Ca_meq': 'Ca²⁺ (meq/L)', 'Mg_meq': 'Mg²⁺ (meq/L)',
        'SO4_meq': 'SO₄²⁻ (meq/L)', 'HCO3_meq': 'HCO₃⁻ (meq/L)',
        'NO3_meq': 'NO₃⁻ (meq/L)', 'K_meq': 'K⁺ (meq/L)',
        'TCC_meq_src': 'Σ Cations (meq/L)', 'TCA_meq_src': 'Σ Anions (meq/L)',
    }

    title_map = {
        ('Na_meq', 'Cl_meq'): 'Na⁺ vs Cl⁻ — Halite / Silicate',
        ('Ca_meq', 'SO4_meq'): 'Ca²⁺ vs SO₄²⁻ — Gypsum',
        ('Ca_meq', 'HCO3_meq'): 'Ca²⁺ vs HCO₃⁻ — Calcite',
        ('Mg_meq', 'HCO3_meq'): 'Mg²⁺ vs HCO₃⁻ — Dolomite',
        ('Na_meq', 'HCO3_meq'): 'Na⁺ vs HCO₃⁻ — Silicate weather.',
        ('Ca_meq', 'Mg_meq'): 'Ca²⁺ vs Mg²⁺ — Carbonate/Silicate',
        ('Na_meq', 'SO4_meq'): 'Na⁺ vs SO₄²⁻ — Mirabilite',
        ('TCC_meq_src', 'TCA_meq_src'): 'Σ Cations vs Σ Anions',
        ('Cl_meq', 'NO3_meq'): 'Cl⁻ vs NO₃⁻ — Anthropogenic',
    }

    fig, axes = plt.subplots(3, 3, figsize=(16, 14))

    for idx, ((xc, yc), ax) in enumerate(zip(scatter_pairs, axes.flat)):
        for _, row in df.iterrows():
            at = row['Area_Type']
            s = row['Season']
            c = AREA_COLORS[at]
            m = SEASON_MARKERS[s]
            fc = c if s == 'Premonsoon' else ('white' if s == 'Monsoon' else 'none')
            ax.scatter(row[xc], row[yc], c=fc, edgecolors=c, marker=m,
                       s=40, linewidths=1.0, zorder=5)

        # 1:1 line
        lims = [min(ax.get_xlim()[0], ax.get_ylim()[0]),
                max(ax.get_xlim()[1], ax.get_ylim()[1])]
        ax.plot(lims, lims, 'k--', alpha=0.4, lw=1, label='1:1 line')

        ax.set_xlabel(label_map.get(xc, xc), fontsize=9)
        ax.set_ylabel(label_map.get(yc, yc), fontsize=9)
        title = title_map.get((xc, yc), f'{yc} vs {xc}')
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.tick_params(labelsize=8)

    # Legend
    legend_elements = []
    for at, label in AREA_TYPES.items():
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                               markerfacecolor=AREA_COLORS[at], markersize=7, label=label))
    for s in SEASON_ORDER:
        m = SEASON_MARKERS[s]
        fc = 'gray' if s == 'Premonsoon' else ('white' if s == 'Monsoon' else 'none')
        legend_elements.append(plt.Line2D([0], [0], marker=m, color='w',
                               markerfacecolor=fc, markeredgecolor='gray', markersize=7, label=s))
    fig.legend(handles=legend_elements, loc='lower center', ncol=6, fontsize=9,
               bbox_to_anchor=(0.5, -0.01))

    fig.suptitle('Ionic Ratio Scatter Plots (meq/L) — Source Identification',
                 fontsize=14, fontweight='bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    save_fig(fig, 'fig_ionic_scatter_9panel.png')


# ============================================================================
# STEP 9: PCA ANALYSIS
# ============================================================================
def run_pca(df):
    print(f"\n{'='*70}")
    print("STEP 9: PCA ANALYSIS")
    print(f"{'='*70}")

    pca_vars = ['pH', 'EC', 'TDS', 'TH', 'Ca', 'Mg', 'Na', 'K', 'Iron',
                'HCO3', 'Cl', 'SO4', 'NO3', 'F']
    pca_data = df[pca_vars].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(pca_data)

    pca = PCA()
    scores = pca.fit_transform(X_scaled)
    ve = pca.explained_variance_ratio_ * 100
    cv = np.cumsum(ve)
    eigenvalues = pca.explained_variance_

    print(f"\n  PCA Results (n={len(pca_data)} samples, {len(pca_vars)} variables):")
    print(f"  {'PC':>4} {'Eigenvalue':>12} {'% Variance':>12} {'Cumul. %':>10}")
    print(f"  {'-'*40}")
    for i in range(min(8, len(ve))):
        print(f"  PC{i+1:>2} {eigenvalues[i]:>12.4f} {ve[i]:>12.2f} {cv[i]:>10.2f}")

    # Number of PCs with eigenvalue > 1 (Kaiser criterion)
    n_kaiser = np.sum(eigenvalues > 1)
    print(f"\n  Kaiser criterion (eigenvalue > 1): {n_kaiser} PCs retained")

    npc = max(n_kaiser, 2)  # At least 2 for biplot
    loadings = pd.DataFrame(
        pca.components_[:npc].T,
        columns=[f'PC{i+1}' for i in range(npc)],
        index=pca_vars
    )

    # === Figure 1: Scree Plot ===
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5))
    bars = a1.bar(range(1, len(ve)+1), ve, color='steelblue', edgecolor='navy', alpha=0.8)
    a1.plot(range(1, len(ve)+1), ve, 'ro-', ms=5)
    a1.axhline(100/len(pca_vars), color='gray', ls=':', alpha=0.5, label=f'Average ({100/len(pca_vars):.1f}%)')
    a1.set_xlabel('Principal Component', fontsize=12)
    a1.set_ylabel('Explained Variance (%)', fontsize=12)
    a1.set_title('Scree Plot', fontsize=13, fontweight='bold')
    a1.legend(fontsize=9)

    a2.plot(range(1, len(cv)+1), cv, 'bo-', ms=5)
    a2.axhline(80, color='r', ls='--', alpha=0.6, label='80% threshold')
    a2.fill_between(range(1, len(cv)+1), cv, alpha=0.1, color='blue')
    a2.set_xlabel('Number of Components', fontsize=12)
    a2.set_ylabel('Cumulative Variance (%)', fontsize=12)
    a2.set_title('Cumulative Explained Variance', fontsize=13, fontweight='bold')
    a2.legend(fontsize=9)
    plt.tight_layout()
    save_fig(fig, 'fig_pca_scree.png')

    # === Figure 2: Biplot ===
    fig, ax = plt.subplots(figsize=(12, 10))
    # Plot scores colored by area type
    for at in ['PD', 'IA', 'DY']:
        mask = df['Area_Type'].values[:len(scores)] == at
        idx = np.where(mask)[0]
        if len(idx):
            ax.scatter(scores[idx, 0], scores[idx, 1],
                       c=AREA_COLORS[at], label=AREA_TYPES[at],
                       s=60, alpha=0.7, edgecolors='k', linewidths=0.5, zorder=5)

    # Loading vectors
    scale_factor = 4.0
    for i, var in enumerate(pca_vars):
        lx, ly = loadings.iloc[i, 0] * scale_factor, loadings.iloc[i, 1] * scale_factor
        ax.annotate('', xy=(lx, ly), xytext=(0, 0),
                     arrowprops=dict(arrowstyle='->', color='darkred', lw=1.5))
        ax.text(lx * 1.12, ly * 1.12, var, fontsize=9, color='darkred',
                ha='center', va='center', fontweight='bold')

    ax.axhline(0, color='gray', ls=':', alpha=0.3)
    ax.axvline(0, color='gray', ls=':', alpha=0.3)
    ax.set_xlabel(f'PC1 ({ve[0]:.1f}%)', fontsize=12)
    ax.set_ylabel(f'PC2 ({ve[1]:.1f}%)', fontsize=12)
    ax.set_title('PCA Biplot — Variable Loadings & Sample Scores', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    plt.tight_layout()
    save_fig(fig, 'fig_pca_biplot.png')

    # === Figure 3: Loading Heatmap ===
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(loadings, annot=True, fmt='.3f', cmap='RdBu_r', center=0,
                linewidths=0.5, ax=ax, vmin=-1, vmax=1,
                cbar_kws={'label': 'Loading Coefficient'})
    ax.set_title(f'PCA Loading Matrix (Top {npc} PCs, Kaiser Criterion)',
                 fontsize=13, fontweight='bold')
    ax.set_ylabel('Variable', fontsize=12)
    ax.set_xlabel('Principal Component', fontsize=12)
    plt.tight_layout()
    save_fig(fig, 'fig_pca_loadings_heatmap.png')

    # Save loadings
    loadings_out = loadings.copy()
    loadings_out['Variable'] = loadings_out.index
    loadings_out = loadings_out[['Variable'] + [c for c in loadings_out.columns if c != 'Variable']]
    save_csv(loadings_out, 'source_pca_loadings.csv')

    return scores, pca, ve, pca_vars, X_scaled


# ============================================================================
# STEP 10: K-MEANS CLUSTERING
# ============================================================================
def run_kmeans(df, scores, ve, X_scaled):
    print(f"\n{'='*70}")
    print("STEP 10: K-MEANS CLUSTERING")
    print(f"{'='*70}")

    # Elbow method
    K_range = range(2, min(10, len(X_scaled) // 2))
    inertias = []
    silhouettes = []
    from sklearn.metrics import silhouette_score
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertias.append(km.inertia_)
        if k >= 2:
            silhouettes.append(silhouette_score(X_scaled, labels))

    # Elbow plot
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5))
    a1.plot(list(K_range), inertias, 'bo-', ms=6)
    a1.set_xlabel('Number of Clusters (k)', fontsize=12)
    a1.set_ylabel('Inertia (WCSS)', fontsize=12)
    a1.set_title('Elbow Method', fontsize=13, fontweight='bold')

    a2.plot(list(K_range), silhouettes, 'go-', ms=6)
    a2.set_xlabel('Number of Clusters (k)', fontsize=12)
    a2.set_ylabel('Silhouette Score', fontsize=12)
    a2.set_title('Silhouette Analysis', fontsize=13, fontweight='bold')
    plt.tight_layout()
    save_fig(fig, 'fig_kmeans_elbow.png')

    # Optimal k (use 3 since we have 3 area types)
    optimal_k = 3
    print(f"\n  Using k={optimal_k} clusters")
    km = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    clusters = km.fit_predict(X_scaled)
    df_clustered = df.iloc[:len(clusters)].copy()
    df_clustered['KMeans_Cluster'] = clusters + 1  # 1-indexed

    # Cluster in PCA space
    fig, ax = plt.subplots(figsize=(10, 8))
    cluster_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    for c in range(optimal_k):
        idx = np.where(clusters == c)[0]
        ax.scatter(scores[idx, 0], scores[idx, 1],
                   c=cluster_colors[c], label=f'Cluster {c+1}',
                   s=60, alpha=0.7, edgecolors='k', linewidths=0.5)
    # Centroids in PCA space
    centroids_pca = km.cluster_centers_ @ PCA(n_components=2).fit(X_scaled).components_.T
    # Actually compute properly
    pca_2 = PCA(n_components=2).fit(X_scaled)
    centroids_pca = pca_2.transform(km.cluster_centers_)
    for c in range(optimal_k):
        ax.scatter(centroids_pca[c, 0], centroids_pca[c, 1],
                   c=cluster_colors[c], marker='X', s=200, edgecolors='black', linewidths=2, zorder=10)

    ax.set_xlabel(f'PC1 ({ve[0]:.1f}%)', fontsize=12)
    ax.set_ylabel(f'PC2 ({ve[1]:.1f}%)', fontsize=12)
    ax.set_title(f'K-Means Clusters (k={optimal_k}) in PCA Space', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    plt.tight_layout()
    save_fig(fig, 'fig_kmeans_pca.png')

    # Cluster means
    pca_vars_avail = [c for c in CHEM_COLS if c in df_clustered.columns]
    cluster_means = df_clustered.groupby('KMeans_Cluster')[pca_vars_avail].mean().round(2)
    print(f"\n  Cluster means:")
    print(cluster_means.to_string())

    # Cross-tab: cluster vs area type
    ct = pd.crosstab(df_clustered['KMeans_Cluster'], df_clustered['Area_Type'])
    print(f"\n  Cluster × Area Type:")
    print(ct.to_string())

    save_csv(df_clustered[['Location_ID', 'Season', 'Area_Type', 'KMeans_Cluster']],
             'source_kmeans_clusters.csv')

    return df_clustered, clusters


# ============================================================================
# STEP 11: HIERARCHICAL CLUSTERING
# ============================================================================
def run_hierarchical(df, X_scaled):
    print(f"\n{'='*70}")
    print("STEP 11: HIERARCHICAL CLUSTERING (Ward's Method)")
    print(f"{'='*70}")

    Z = linkage(X_scaled, method='ward')

    fig, ax = plt.subplots(figsize=(16, 7))
    labels = [f"{row['Location_ID']}_{row['Season'][:3]}" for _, row in df.iloc[:len(X_scaled)].iterrows()]

    # Color threshold for 3 clusters
    max_d = 0.7 * max(Z[:, 2])

    dn = dendrogram(Z, labels=labels, leaf_rotation=90, leaf_font_size=7,
                     ax=ax, color_threshold=max_d, above_threshold_color='gray')

    ax.axhline(max_d, color='red', ls='--', alpha=0.6, label=f'Cut threshold ({max_d:.1f})')
    ax.set_xlabel('Sample (Location_Season)', fontsize=12)
    ax.set_ylabel('Euclidean Distance (Ward)', fontsize=12)
    ax.set_title("Hierarchical Clustering Dendrogram (Ward's Method)", fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    plt.tight_layout()
    save_fig(fig, 'fig_dendrogram.png')

    # Extract cluster assignments at the same threshold
    hc_labels = fcluster(Z, t=max_d, criterion='distance')
    df_hc = df.iloc[:len(hc_labels)].copy()
    df_hc['HC_Cluster'] = hc_labels

    ct = pd.crosstab(df_hc['HC_Cluster'], df_hc['Area_Type'])
    print(f"\n  HC Cluster × Area Type:")
    print(ct.to_string())

    return df_hc


# ============================================================================
# STEP 12: MASTER ATTRIBUTION TABLE
# ============================================================================
def build_attribution_table(df):
    print(f"\n{'='*70}")
    print("STEP 12: MASTER ATTRIBUTION TABLE")
    print(f"{'='*70}")

    rows = []
    for _, row in df.iterrows():
        attr = {
            'Location_ID': row['Location_ID'],
            'Season': row['Season'],
            'Area_Type': row['Area_Type'],
        }

        # Evidence accumulation
        evidence_geo = []   # Geogenic evidence
        evidence_anth = []  # Anthropogenic evidence
        evidence_mixed = [] # Mixed evidence

        # 1. Na/Cl ratio
        na_cl = row.get('Na_Cl_meq', np.nan)
        if not np.isnan(na_cl):
            if na_cl > 1.2:
                evidence_geo.append('Na/Cl>1.2 (silicate weathering)')
            elif 0.8 <= na_cl <= 1.2:
                evidence_mixed.append('Na/Cl≈1 (halite possible)')
            else:
                evidence_anth.append('Na/Cl<0.8 (reverse ion exchange / anthropogenic Cl)')

        # 2. Ca/Mg ratio
        ca_mg = row.get('Ca_Mg_meq', np.nan)
        if not np.isnan(ca_mg):
            if ca_mg > 2:
                evidence_geo.append('Ca/Mg>2 (silicate weathering)')
            elif 1 <= ca_mg <= 2:
                evidence_geo.append('Ca/Mg 1-2 (calcite/dolomite)')
            else:
                evidence_mixed.append('Ca/Mg<1 (dolomite/Mg-rich)')

        # 3. Ion exchange (CAI)
        cai1 = row.get('CAI_1', np.nan)
        cai2 = row.get('CAI_2', np.nan)
        if not (np.isnan(cai1) or np.isnan(cai2)):
            if cai1 < 0 and cai2 < 0:
                evidence_geo.append('CAI<0 (direct ion exchange)')
            elif cai1 > 0 and cai2 > 0:
                evidence_mixed.append('CAI>0 (reverse ion exchange)')

        # 4. (Ca+Mg)/(HCO3+SO4)
        cm_hs = row.get('CaMg_HCO3SO4_meq', np.nan)
        if not np.isnan(cm_hs):
            if 0.8 <= cm_hs <= 1.2:
                evidence_geo.append('(Ca+Mg)/(HCO₃+SO₄)≈1 (weathering)')
            elif cm_hs > 1.2:
                evidence_mixed.append('(Ca+Mg)/(HCO₃+SO₄)>1 (reverse ion exch.)')
            else:
                evidence_geo.append('(Ca+Mg)/(HCO₃+SO₄)<1 (ion exchange)')

        # 5. NO3 exceedance
        no3 = row.get('NO3', np.nan)
        if not np.isnan(no3):
            if no3 > 10:  # NBL threshold
                evidence_anth.append(f'NO₃={no3:.1f} (>NBL 10 mg/L)')
            else:
                evidence_geo.append(f'NO₃={no3:.1f} (within NBL)')

        # 6. Cl exceedance
        cl_val = row.get('Cl', np.nan)
        if not np.isnan(cl_val):
            if cl_val > 50:  # NBL threshold
                evidence_anth.append(f'Cl={cl_val:.1f} (>NBL 50 mg/L)')

        # 7. Iron exceedance
        fe = row.get('Iron', np.nan)
        if not np.isnan(fe):
            if fe > 0.3:
                evidence_geo.append(f'Fe={fe:.2f} (>0.3, laterite/weathering)')

        # 8. Gibbs mechanism
        gibbs = row.get('Gibbs_Mechanism', '')
        if gibbs == 'Rock-Water Interaction':
            evidence_geo.append('Gibbs: Rock-water interaction')
        elif gibbs == 'Evaporation Dominance':
            evidence_mixed.append('Gibbs: Evaporation dominance')

        # 9. HCO3 dominance
        hco3_frac = row.get('HCO3_sum_anion', np.nan)
        if not np.isnan(hco3_frac):
            if hco3_frac > 0.5:
                evidence_geo.append('HCO₃ dominant anion (weathering)')

        # 10. PIG
        pig = row.get('PIG', np.nan)
        if not np.isnan(pig):
            if pig > 1.5:
                evidence_anth.append(f'PIG={pig:.3f} (moderate-high pollution)')

        # Compile
        n_geo = len(evidence_geo)
        n_anth = len(evidence_anth)
        n_mixed = len(evidence_mixed)
        total = n_geo + n_anth + n_mixed

        if total == 0:
            dominant = 'Insufficient Data'
            confidence = 'Low'
        else:
            geo_pct = n_geo / total * 100
            anth_pct = n_anth / total * 100
            if geo_pct >= 60:
                dominant = 'Geogenic'
                confidence = 'High' if geo_pct >= 75 else 'Moderate'
            elif anth_pct >= 60:
                dominant = 'Anthropogenic'
                confidence = 'High' if anth_pct >= 75 else 'Moderate'
            else:
                dominant = 'Mixed'
                confidence = 'Moderate'

        attr['Geogenic_Evidence'] = '; '.join(evidence_geo)
        attr['Anthropogenic_Evidence'] = '; '.join(evidence_anth)
        attr['Mixed_Evidence'] = '; '.join(evidence_mixed)
        attr['N_Geogenic'] = n_geo
        attr['N_Anthropogenic'] = n_anth
        attr['N_Mixed'] = n_mixed
        attr['Dominant_Source'] = dominant
        attr['Confidence'] = confidence

        rows.append(attr)

    attr_df = pd.DataFrame(rows)
    save_csv(attr_df, 'source_master_attribution.csv')

    # Summary
    print(f"\n  Attribution summary:")
    print(attr_df['Dominant_Source'].value_counts().to_string())
    print(f"\n  By Area Type:")
    print(pd.crosstab(attr_df['Area_Type'], attr_df['Dominant_Source']).to_string())
    print(f"\n  By Season:")
    print(pd.crosstab(attr_df['Season'], attr_df['Dominant_Source']).to_string())

    return attr_df


# ============================================================================
# STEP 14: MARKDOWN REPORT
# ============================================================================
def write_report(df, season_df, area_df, attr_df, ratio_interpretations):
    print(f"\n{'='*70}")
    print("STEP 14: MARKDOWN REPORT")
    print(f"{'='*70}")

    report_path = BASE_DIR / 'SOURCE_ANALYSIS_REPORT.md'

    # Collect statistics
    n_samples = len(df)
    n_locations = df['Location_ID'].nunique()
    n_seasons = df['Season'].nunique()

    # Attribution summary
    source_counts = attr_df['Dominant_Source'].value_counts()
    area_source = pd.crosstab(attr_df['Area_Type'], attr_df['Dominant_Source'])

    # Significant seasonal parameters
    sig_seasonal = season_df[season_df['Significant_0.05'] == 'Yes']['Parameter'].tolist() if len(season_df) > 0 else []

    # Gibbs dominant mechanism
    gibbs_dom = df['Gibbs_Mechanism'].value_counts().idxmax() if 'Gibbs_Mechanism' in df.columns else 'N/A'

    # Ion exchange dominant type
    ie_dom = df['IonExchange'].value_counts().idxmax() if 'IonExchange' in df.columns else 'N/A'

    # PIG stats
    pig_mean = df['PIG'].mean() if 'PIG' in df.columns else 0
    pig_dom = df['PIG_Category'].value_counts().idxmax() if 'PIG_Category' in df.columns else 'N/A'

    report = textwrap.dedent(f"""\
    # Source Identification Report
    ## Anthropogenic vs. Geogenic Source Analysis
    ### Groundwater Quality — Bhubaneswar, Odisha, India (2024)

    **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    ---

    ## 1. Study Overview

    | Parameter | Value |
    |-----------|-------|
    | Samples | {n_samples} |
    | Locations | {n_locations} (PD-1..5, IA-1..5, DY-1..5) |
    | Seasons | {n_seasons} (Premonsoon, Monsoon, Postmonsoon) |
    | Area Types | Population Density (PD), Industrial Area (IA), Dumping Yard (DY) |
    | Data Source | `cleaned_hydrochemical_data_2024.csv` |

    ## 2. Methodology

    This analysis employs a multi-evidence convergence approach combining:

    1. **Ionic Ratio Analysis** — 10 diagnostic ratios in meq/L space
    2. **Chloro-Alkaline Indices (CAI-1, CAI-2)** — Ion exchange processes
    3. **Gibbs Diagrams** — Controlling mechanisms (rock/precipitation/evaporation)
    4. **Pollution Index of Groundwater (PIG)** — IS 10500:2012 permissible limits
    5. **Natural Background Level (NBL) Exceedance** — Indian hard-rock aquifer benchmarks
    6. **Piper Diagram** — Hydrochemical facies classification
    7. **PCA** — Multivariate factor identification (Kaiser criterion)
    8. **K-Means & Hierarchical Clustering** — Unsupervised grouping

    ## 3. Key Findings

    ### 3.1 Dominant Source Attribution
    """)

    for src, cnt in source_counts.items():
        pct = cnt / len(attr_df) * 100
        report += f"- **{src}**: {cnt} samples ({pct:.1f}%)\n"

    report += f"""
    ### 3.2 Controlling Mechanism (Gibbs)
    - Dominant: **{gibbs_dom}**
    - This indicates that groundwater chemistry is primarily controlled by {'mineral dissolution and rock-water interaction' if gibbs_dom == 'Rock-Water Interaction' else gibbs_dom.lower()}.

    ### 3.3 Ion Exchange
    - Dominant process: **{ie_dom}**
    - {'Direct ion exchange suggests Na release from clay minerals with concurrent Ca/Mg adsorption (geogenic process).' if 'Direct' in ie_dom else 'Reverse ion exchange suggests Ca release into solution (mixed process).'}

    ### 3.4 Pollution Index (PIG)
    - Mean PIG: **{pig_mean:.4f}**
    - Dominant category: **{pig_dom}**

    ### 3.5 Seasonal Patterns
    - Parameters with significant seasonal variation (Kruskal-Wallis p<0.05):
    """
    if sig_seasonal:
        report += '  ' + ', '.join(f'**{p}**' for p in sig_seasonal) + '\n'
    else:
        report += '  None (no significant seasonal variation detected)\n'

    report += """
    ### 3.6 Area-wise Differences
    """
    # Manual markdown table (avoids tabulate dependency)
    report += '| Area Type | ' + ' | '.join(area_source.columns) + ' |\n'
    report += '|-----------|' + '|'.join(['-------'] * len(area_source.columns)) + '|\n'
    for idx_row, row_data in area_source.iterrows():
        report += f'| {idx_row} | ' + ' | '.join(str(v) for v in row_data) + ' |\n'

    report += """
    ## 4. Diagnostic Ratio Interpretation Guide

    | Ratio | Interpretation |
    |-------|---------------|
    """
    for ratio, interp in ratio_interpretations.items():
        report += f"| {ratio} | {interp} |\n"

    report += """
    ## 5. NBL Exceedance Summary
    """
    for param, (lo, hi) in NBL_RANGES.items():
        if param in df.columns:
            exceed = (df[param] > hi).sum()
            pct = exceed / len(df) * 100
            report += f"- **{param}** (NBL upper: {hi} mg/L): {exceed}/{len(df)} samples exceed ({pct:.1f}%)\n"

    report += """
    ## 6. Output Files

    ### CSV Files
    | File | Description |
    |------|-------------|
    | `source_meq_conversion.csv` | meq/L conversion table |
    | `source_diagnostic_indices.csv` | All ionic ratios, CAI, Gibbs coords, PIG, NBL |
    | `source_seasonal_stats.csv` | Kruskal-Wallis + Dunn's post-hoc results |
    | `source_area_stats.csv` | Area-wise statistics + Mann-Whitney pairwise |
    | `source_pca_loadings.csv` | PCA loading matrix |
    | `source_kmeans_clusters.csv` | K-Means cluster assignments |
    | `source_master_attribution.csv` | Per-sample source attribution with evidence |

    ### Figures (in `figures/task5_source/`)
    | File | Description |
    |------|-------------|
    | `fig_piper_ternary.png` | Piper diagram (ternary cation/anion/diamond) |
    | `fig_gibbs_diagram.png` | Gibbs diagrams (cation & anion ratios vs TDS) |
    | `fig_ionic_scatter_9panel.png` | 9-panel ionic ratio scatter plots |
    | `fig_pca_scree.png` | Scree plot + cumulative variance |
    | `fig_pca_biplot.png` | PCA biplot with loadings and area-coded scores |
    | `fig_pca_loadings_heatmap.png` | PCA loading coefficient heatmap |
    | `fig_kmeans_elbow.png` | Elbow method + silhouette analysis |
    | `fig_kmeans_pca.png` | K-Means clusters projected in PCA space |
    | `fig_dendrogram.png` | Hierarchical clustering dendrogram (Ward's) |

    ## 7. References

    1. Gibbs, R.J. (1970). Mechanisms controlling world water chemistry. *Science*, 170(3962), 1088-1090.
    2. Piper, A.M. (1944). A graphic procedure in the geochemical interpretation of water analyses. *Trans. AGU*, 25(6), 914-928.
    3. Schoeller, H. (1965). Qualitative evaluation of groundwater resources. *UNESCO Methods and Techniques of Groundwater Investigation*.
    4. Bureau of Indian Standards (2012). IS 10500:2012 — Drinking Water Specification (2nd Rev.). New Delhi.
    5. Subramani, T. et al. (2010). Evaluation of the groundwater quality and its suitability for drinking and irrigation. *Environ. Monit. Assess.*, 171, 289-308.
    6. Gaillardet, J. et al. (1999). Global silicate weathering and CO2 consumption rates. *Chem. Geol.*, 159, 3-30.

    ---
    *Report generated by Source Analysis Pipeline v1.0*
    """

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  [REPORT] {report_path.relative_to(BASE_DIR)}")


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("="*70)
    print("ANTHROPOGENIC vs. GEOGENIC SOURCE IDENTIFICATION PIPELINE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Ensure output directories exist
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    CSV_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Load data
    df = load_data()

    # Step 2: meq/L conversion
    df = convert_to_meq(df)

    # Step 3: Diagnostic indices
    df, ratio_cols, diag_labels, ratio_interps, scatter_pairs = compute_diagnostic_indices(df)

    # Step 4: Seasonal analysis
    season_df = seasonal_analysis(df)

    # Step 5: Area-wise analysis
    area_df = area_analysis(df)

    # Step 6: Piper diagram
    df = plot_piper(df)

    # Step 7: Gibbs diagram
    df = plot_gibbs(df)

    # Step 8: Ionic ratio scatter plots
    plot_ionic_ratios(df, scatter_pairs)

    # Step 9: PCA
    scores, pca_model, ve, pca_vars, X_scaled = run_pca(df)

    # Step 10: K-Means
    df, clusters = run_kmeans(df, scores, ve, X_scaled)

    # Step 11: Hierarchical clustering
    df = run_hierarchical(df, X_scaled)

    # Step 12: Master attribution table
    attr_df = build_attribution_table(df)

    # Step 13 (outputs already saved in each step)
    print(f"\n{'='*70}")
    print("STEP 13: ALL OUTPUTS SAVED")
    print(f"{'='*70}")

    # Step 14: Markdown report
    write_report(df, season_df, area_df, attr_df, ratio_interps)

    print(f"\n{'='*70}")
    print(f"PIPELINE COMPLETE — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
