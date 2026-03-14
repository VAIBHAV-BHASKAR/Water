# Source Identification Report
## Anthropogenic vs. Geogenic Source Analysis
### Groundwater Quality — Bhubaneswar, Odisha, India (2024)

**Generated:** 2026-03-14 23:44:36

---

## 1. Study Overview

| Parameter | Value |
|-----------|-------|
| Samples | 45 |
| Locations | 15 (PD-1..5, IA-1..5, DY-1..5) |
| Seasons | 3 (Premonsoon, Monsoon, Postmonsoon) |
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
- **Mixed**: 35 samples (77.8%)
- **Geogenic**: 10 samples (22.2%)

    ### 3.2 Controlling Mechanism (Gibbs)
    - Dominant: **Rock-Water Interaction**
    - This indicates that groundwater chemistry is primarily controlled by mineral dissolution and rock-water interaction.

    ### 3.3 Ion Exchange
    - Dominant process: **Reverse ion exchange**
    - Reverse ion exchange suggests Ca release into solution (mixed process).

    ### 3.4 Pollution Index (PIG)
    - Mean PIG: **3.3783**
    - Dominant category: **Very High**

    ### 3.5 Seasonal Patterns
    - Parameters with significant seasonal variation (Kruskal-Wallis p<0.05):
      **Na_Cl_meq**, **CAI_1**, **Cl**, **TDS**, **EC**, **F**, **Na**, **Ca**, **Mg**, **HCO3**

    ### 3.6 Area-wise Differences
    | Area Type | Geogenic | Mixed |
|-----------|-------|-------|
| DY | 4 | 11 |
| IA | 2 | 13 |
| PD | 4 | 11 |

    ## 4. Diagnostic Ratio Interpretation Guide

    | Ratio | Interpretation |
    |-------|---------------|
    | Na_Cl_meq | >1: silicate weathering / ion exchange; ≈1: halite dissolution; <1: reverse ion exchange |
| Ca_Mg_meq | >1: calcite dissolution; <1: dolomite dissolution; >>2: silicate weathering |
| HCO3_Cl_meq | >1: rock-water interaction dominates; <1: saline/evaporation influence |
| Ca_SO4_meq | ≈1: gypsum dissolution; >1: carbonate/silicate Ca source |
| Mg_Ca_meq | >1: dolomite/ferromagnesian minerals; <1: calcite dominance |
| CaMg_HCO3SO4_meq | ≈1: weathering dominant; >1: reverse ion exchange; <1: ion exchange |
| Na_K_meq | High: albite/Na-feldspar; Low: K-feldspar or agricultural K |
| NO3_Cl_meq | High: agricultural/sewage input; Low: natural or dilution |
| SO4_Cl_meq | High: oxidation of sulfides/industrial; Low: marine/evaporite |
| HCO3_sum_anion | >0.5: weathering-controlled; <0.5: anthropogenic anion inputs |

    ## 5. NBL Exceedance Summary
    - **Iron** (NBL upper: 0.3 mg/L): 19/45 samples exceed (42.2%)
- **F** (NBL upper: 1.0 mg/L): 0/45 samples exceed (0.0%)
- **NO3** (NBL upper: 10.0 mg/L): 40/45 samples exceed (88.9%)
- **Cl** (NBL upper: 50.0 mg/L): 28/45 samples exceed (62.2%)
- **SO4** (NBL upper: 30.0 mg/L): 5/45 samples exceed (11.1%)
- **Na** (NBL upper: 30.0 mg/L): 21/45 samples exceed (46.7%)

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
    