#!/usr/bin/env python3
"""
make_ppt.py — Generate a professional academic PowerPoint presentation
for the Hydrochemical Intelligence Report on Bhubaneswar Groundwater 2024.

All values are extracted from actual pipeline outputs (output.log, CSVs, figures).
No placeholders — every number is real.

Author:  Auto-generated for Lakshya Nayyar & Vaibhav Bhaskar
Date:    2025
"""

from __future__ import annotations

import os
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ──────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent
FIG_DIR = BASE_DIR / "figures"
OUT_PPT = BASE_DIR / "Hydrochemical_Analysis_Presentation.pptx"

# Colour palette
CLR_TITLE_BG    = RGBColor(0x0D, 0x21, 0x37)   # dark navy
CLR_CONTENT_BG  = RGBColor(0xF5, 0xF7, 0xFA)   # off-white
CLR_ACCENT      = RGBColor(0x00, 0xB4, 0xD8)   # teal accent
CLR_WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
CLR_DARK        = RGBColor(0x1A, 0x1A, 0x2E)
CLR_GREY        = RGBColor(0x66, 0x66, 0x66)
CLR_RED         = RGBColor(0xE0, 0x3E, 0x3E)
CLR_GREEN       = RGBColor(0x2E, 0x8B, 0x57)

FONT_NAME = "Calibri"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

# ──────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────

def safe_pic(slide, img_path, left, top, width=None, height=None):
    """Add a picture to slide only if the file exists; skip silently otherwise."""
    p = Path(img_path)
    if not p.exists():
        print(f"  [WARN] Missing figure: {p}")
        return None
    kwargs = {"image_file": str(p), "left": left, "top": top}
    if width:
        kwargs["width"] = width
    if height:
        kwargs["height"] = height
    return slide.shapes.add_picture(**kwargs)


def add_teal_rule(slide, left, top, width=Inches(10)):
    """Draw a thin teal horizontal rule."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, Pt(3)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = CLR_ACCENT
    shape.line.fill.background()
    return shape


def add_footer(slide, text="Nayyar & Bhaskar | KIIT University | 2025"):
    """Place a subtle footer at the bottom-right."""
    txBox = slide.shapes.add_textbox(
        Inches(7.5), Inches(7.0), Inches(5.5), Inches(0.35)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(9)
    p.font.color.rgb = CLR_GREY
    p.font.name = FONT_NAME
    p.alignment = PP_ALIGN.RIGHT


def set_slide_bg(slide, color: RGBColor):
    """Set solid background colour for a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_textbox(slide, left, top, width, height, text,
                font_size=14, bold=False, color=CLR_DARK, alignment=PP_ALIGN.LEFT,
                font_name=FONT_NAME, line_spacing=1.15):
    """Add a text box with sane defaults."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    p.space_after = Pt(4)
    return txBox


def add_bullet_list(slide, left, top, width, height, items,
                    font_size=13, color=CLR_DARK, bullet_char="\u2022"):
    """Add a bulleted list text box."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = f"{bullet_char} {item}"
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = FONT_NAME
        p.space_after = Pt(3)
    return txBox


def add_title_bar(slide, title_text, subtitle_text=None):
    """Add a dark navy bar with title at top of content slide."""
    # Background bar
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_W, Inches(1.15)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = CLR_TITLE_BG
    bar.line.fill.background()

    # Title text
    add_textbox(slide, Inches(0.6), Inches(0.15), Inches(12), Inches(0.6),
                title_text, font_size=28, bold=True, color=CLR_WHITE)

    if subtitle_text:
        add_textbox(slide, Inches(0.6), Inches(0.7), Inches(12), Inches(0.35),
                    subtitle_text, font_size=14, color=CLR_ACCENT)

    # Teal accent line below title bar
    add_teal_rule(slide, Inches(0.6), Inches(1.12), Inches(12))


# ──────────────────────────────────────────────────────────────────────
# SLIDE BUILDERS
# ──────────────────────────────────────────────────────────────────────

def slide_01_title(prs):
    """SLIDE 1: Title Slide"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout
    set_slide_bg(slide, CLR_TITLE_BG)

    # Main title
    add_textbox(slide, Inches(1), Inches(1.2), Inches(11), Inches(1.2),
                "Hydrochemical Intelligence Report",
                font_size=40, bold=True, color=CLR_WHITE,
                alignment=PP_ALIGN.CENTER)

    # Subtitle
    add_textbox(slide, Inches(1), Inches(2.3), Inches(11), Inches(0.8),
                "Multi-Seasonal Groundwater Quality Assessment\nBhubaneswar, Odisha — 2024",
                font_size=22, color=CLR_ACCENT, alignment=PP_ALIGN.CENTER)

    # Teal rule
    add_teal_rule(slide, Inches(3.5), Inches(3.2), Inches(6))

    # Authors
    add_textbox(slide, Inches(1), Inches(3.6), Inches(11), Inches(0.7),
                "Lakshya Nayyar (23053133)  |  Vaibhav Bhaskar (23053173)",
                font_size=18, color=CLR_WHITE, alignment=PP_ALIGN.CENTER)

    # Affiliation
    add_textbox(slide, Inches(1), Inches(4.3), Inches(11), Inches(0.5),
                "School of Civil Engineering, KIIT Deemed to be University, Bhubaneswar",
                font_size=14, color=CLR_GREY, alignment=PP_ALIGN.CENTER)

    # Guide
    add_textbox(slide, Inches(1), Inches(5.0), Inches(11), Inches(0.5),
                "Under the guidance of Dr. Ajit Kumar Pasayat",
                font_size=15, color=CLR_WHITE, alignment=PP_ALIGN.CENTER)

    # Date
    add_textbox(slide, Inches(1), Inches(5.7), Inches(11), Inches(0.4),
                "Academic Year 2024–25",
                font_size=13, color=CLR_GREY, alignment=PP_ALIGN.CENTER)

    add_footer(slide, "KIIT University | 2025")


def slide_02_outline(prs):
    """SLIDE 2: Presentation Outline"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_CONTENT_BG)
    add_title_bar(slide, "Presentation Outline")

    outline_items = [
        "1.  Introduction & Study Area",
        "2.  Dataset Description & Synthetic Augmentation",
        "3.  Methodology Pipeline",
        "4.  Seasonal Hydrochemical Dynamics",
        "5.  IS 10500:2012 Compliance & Water Quality Index",
        "6.  Anthropogenic & Geogenic Source Analysis",
        "7.  Parameter Grouping — PCA & Clustering",
        "8.  ML-Based Forecasting (RF, GB, NN, SVR, XGBoost)",
        "9.  SHAP Explainability & Residual Analysis",
        "10. Conclusions & Policy Recommendations",
    ]

    txBox = slide.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(10), Inches(5.5))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(outline_items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(18)
        p.font.color.rgb = CLR_DARK
        p.font.name = FONT_NAME
        p.space_after = Pt(10)
        p.space_before = Pt(4)

    add_footer(slide)


def slide_03_introduction(prs):
    """SLIDE 3: Introduction & Study Area"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_CONTENT_BG)
    add_title_bar(slide, "Introduction & Study Area",
                  "Bhubaneswar, Odisha — 15 Groundwater Monitoring Locations")

    # Motivation text
    add_textbox(slide, Inches(0.6), Inches(1.4), Inches(6.5), Inches(1.0),
                "Bhubaneswar relies heavily on groundwater for drinking and domestic use. "
                "Rapid urbanisation, industrial activity, and waste dumping degrade aquifer quality. "
                "This study investigates hydrochemical signatures across 15 sampling sites "
                "spanning 3 land-use categories over 3 seasons of 2024.",
                font_size=13, color=CLR_DARK)

    # Site table header
    add_textbox(slide, Inches(0.6), Inches(2.5), Inches(4), Inches(0.35),
                "Population Density Areas (PD)", font_size=14, bold=True, color=CLR_ACCENT)
    pd_sites = [
        "PD-1: Acharya Vihar",
        "PD-2: Ram Mandir",
        "PD-3: Sailashree Vihar",
        "PD-4: OMFED Square",
        "PD-5: Old Town",
    ]
    add_bullet_list(slide, Inches(0.8), Inches(2.85), Inches(3.8), Inches(1.5),
                    pd_sites, font_size=11)

    add_textbox(slide, Inches(4.8), Inches(2.5), Inches(4), Inches(0.35),
                "Industrial Areas (IA)", font_size=14, bold=True, color=CLR_ACCENT)
    ia_sites = [
        "IA-1: Mancheswar Industrial Estate",
        "IA-2: Chandaka Industrial Area",
        "IA-3: OMFED Industries",
        "IA-4: Rasulgarh",
        "IA-5: Anmol Industries",
    ]
    add_bullet_list(slide, Inches(5.0), Inches(2.85), Inches(3.8), Inches(1.5),
                    ia_sites, font_size=11)

    add_textbox(slide, Inches(9.0), Inches(2.5), Inches(4), Inches(0.35),
                "Dumping Yards (DY)", font_size=14, bold=True, color=CLR_ACCENT)
    dy_sites = [
        "DY-1: Bhuasuni Temple Area",
        "DY-2: Lingaraj Railway Station",
        "DY-3: BMC Micro Compost",
        "DY-4: Gadakan Road",
        "DY-5: Daruthenga",
    ]
    add_bullet_list(slide, Inches(9.2), Inches(2.85), Inches(3.8), Inches(1.5),
                    dy_sites, font_size=11)

    # Key numbers
    add_textbox(slide, Inches(0.6), Inches(4.6), Inches(12), Inches(0.4),
                "16 hydrochemical parameters  |  3 seasons (Premonsoon, Monsoon, Postmonsoon)  |  45 original samples",
                font_size=13, bold=True, color=CLR_DARK, alignment=PP_ALIGN.CENTER)

    # Parameters list
    add_textbox(slide, Inches(0.6), Inches(5.1), Inches(12), Inches(0.7),
                "Parameters: pH, EC, TDS, TH, Alkalinity, Ca, Mg, Na, K, Iron, "
                "HCO\u2083, Cl, SO\u2084, NO\u2083, F, DO",
                font_size=12, color=CLR_GREY, alignment=PP_ALIGN.CENTER)

    # Image — original vs synthetic publication figure if exists
    safe_pic(slide, FIG_DIR / "task1_cleaning" / "fig_original_vs_synthetic.png",
             Inches(0.6), Inches(5.6), width=Inches(5), height=Inches(1.6))

    add_footer(slide)


def slide_04_dataset(prs):
    """SLIDE 4: Dataset Description & Synthetic Augmentation"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_CONTENT_BG)
    add_title_bar(slide, "Dataset Description & Synthetic Augmentation",
                  "From 45 Original Samples to 195 Combined Samples")

    # Left column — Original data
    add_textbox(slide, Inches(0.6), Inches(1.5), Inches(5.8), Inches(0.4),
                "Original Dataset", font_size=18, bold=True, color=CLR_ACCENT)
    orig_items = [
        "Source: water quality data_Three Seasons_2024.xlsx",
        "3 Excel sheets: Premonsoon, Monsoon, Postmonsoon 2024",
        "15 locations × 3 seasons = 45 samples × 16 parameters",
        "Cleaning: removed duplicate headers, computed columns, NaN rows",
        "Charge Balance Error: 93.3% valid (42/45 within ±10%)",
        "Mean CBE = 0.76%, Median = 2.54%, Range = [−10.36%, 10.74%]",
        "No missing values in chemical parameters",
    ]
    add_bullet_list(slide, Inches(0.8), Inches(1.95), Inches(5.6), Inches(2.5),
                    orig_items, font_size=12)

    # Right column — Synthetic data
    add_textbox(slide, Inches(7.0), Inches(1.5), Inches(5.8), Inches(0.4),
                "Synthetic Augmentation", font_size=18, bold=True, color=CLR_ACCENT)
    syn_items = [
        "Method: Multivariate Gaussian sampling per season + noise injection",
        "Covariance inflation (40%), mean jitter (\u00b16%), independent Gaussian noise (8%)",
        "Outlier perturbation: 5% of samples at 2.5\u00d7 std for realistic spread",
        "Physical bounds clipping enforces realistic ranges",
        "150 synthetic samples (50 per season); Combined: 195 samples",
        "CBE on combined: 64.6% valid (noise introduces realistic ionic imbalance)",
        "Purpose: improve ML robustness & reduce overfitting of original patterns",
    ]
    add_bullet_list(slide, Inches(7.2), Inches(1.95), Inches(5.6), Inches(2.5),
                    syn_items, font_size=12)

    # Figure — publication-quality side-by-side
    safe_pic(slide, BASE_DIR / "fig_original_vs_synthetic_publication.png",
             Inches(1.5), Inches(4.5), width=Inches(10), height=Inches(2.7))

    add_footer(slide)


def slide_05_methodology(prs):
    """SLIDE 5: Methodology Pipeline"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_CONTENT_BG)
    add_title_bar(slide, "Methodology Pipeline",
                  "7-Task Scalable Analysis Framework")

    pipeline_steps = [
        ("Task 1", "Data Reconstruction & Cleaning",
         "Load 3 seasonal Excel sheets, clean headers, align columns, export CSV"),
        ("Task 2", "Data Validation",
         "Missing-value analysis, IQR + Z-score outlier detection, ionic balance (CBE ±10%)"),
        ("Task 3", "EDA & Seasonal Dynamics",
         "Descriptive statistics, box/violin plots, ANOVA/KW tests, seasonal % change"),
        ("Task 4", "Drinking Water Risk Intelligence",
         "IS 10500:2012 3-tier compliance, exceedance factors, WQI (Brown et al., 1970)"),
        ("Task 5", "Source Analysis",
         "PCA, K-Means clustering, Piper diagram, Gibbs diagram, ionic ratios"),
        ("Task 6", "ML Forecasting",
         "5 models (RF, GB, NN, SVR, XGBoost), SHAP, residuals, GA/NSE/RSR/MAPE"),
        ("Task 7", "Scientific Insights",
         "Salinity drivers, seasonal ranking, spatial clustering, risk assessment"),
    ]

    y = Inches(1.5)
    for step_id, step_title, step_desc in pipeline_steps:
        # Step ID box
        box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), y, Inches(1.0), Inches(0.6)
        )
        box.fill.solid()
        box.fill.fore_color.rgb = CLR_ACCENT
        box.line.fill.background()
        tf = box.text_frame
        tf.word_wrap = True
        tf.paragraphs[0].text = step_id
        tf.paragraphs[0].font.size = Pt(12)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = CLR_WHITE
        tf.paragraphs[0].font.name = FONT_NAME
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

        # Title
        add_textbox(slide, Inches(1.8), y, Inches(3.5), Inches(0.35),
                    step_title, font_size=14, bold=True, color=CLR_DARK)
        # Description
        add_textbox(slide, Inches(5.5), y + Inches(0.05), Inches(7.2), Inches(0.5),
                    step_desc, font_size=11, color=CLR_GREY)

        y += Inches(0.75)

    # Frameworks box
    add_textbox(slide, Inches(0.6), y + Inches(0.3), Inches(12), Inches(0.5),
                "Standards:  IS 10500:2012 (BIS)  |  WHO Guidelines (4th Ed., 2011)  |  "
                "GoI FSSAI / CPCB Class A Criteria",
                font_size=12, bold=True, color=CLR_DARK, alignment=PP_ALIGN.CENTER)

    add_footer(slide)


def slide_06a_seasonal(prs):
    """SLIDE 6a: Seasonal Variation — Statistical Overview"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_CONTENT_BG)
    add_title_bar(slide, "Seasonal Hydrochemical Dynamics — Statistics",
                  "ANOVA/Kruskal-Wallis Tests & Seasonal Trends")

    # Key findings
    findings = [
        "15 of 16 parameters show statistically significant seasonal variation (p < 0.05)",
        "Only pH is non-significant — all others (including Mg, Iron, SO\u2084, NO\u2083) now significant",
        "Monsoon EC mean = 609 \u00b5S/cm vs Premonsoon 407 \u00b5S/cm (+49.7%)",
        "Total Hardness surges 530% from Premonsoon (23.4) to Monsoon (147.6 mg/L)",
        "Alkalinity drops 47.9% from Premonsoon (112.8) to Postmonsoon (58.8 mg/L)",
        "Na surges +80.3% Pre\u2192Mon; K surges +103.1% Pre\u2192Mon — anthropogenic mobilisation",
    ]
    add_bullet_list(slide, Inches(0.6), Inches(1.4), Inches(6), Inches(3.0),
                    findings, font_size=12)

    # Figures
    safe_pic(slide, FIG_DIR / "task3_seasonal" / "fig_seasonal_boxplots.png",
             Inches(6.8), Inches(1.3), width=Inches(6), height=Inches(2.8))

    safe_pic(slide, FIG_DIR / "task3_seasonal" / "fig_seasonal_heatmap.png",
             Inches(0.6), Inches(4.5), width=Inches(5.8), height=Inches(2.7))

    safe_pic(slide, FIG_DIR / "task3_seasonal" / "fig_seasonal_trends.png",
             Inches(6.8), Inches(4.5), width=Inches(6), height=Inches(2.7))

    add_footer(slide)


def slide_06b_seasonal(prs):
    """SLIDE 6b: Seasonal Variation — Distributions & Correlations"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_CONTENT_BG)
    add_title_bar(slide, "Seasonal Variation — Distributions & Correlations",
                  "Violin Plots, Radar, and Correlation Structure")

    # Interpretation text
    interp = [
        "Dilution Effect: Monsoon rainwater infiltration lowers TDS, EC concentrations in some zones",
        "Concentration Effect: Premonsoon (dry) shows higher concentrations due to evapotranspiration",
        "Mineral Dissolution: Enhanced recharge during monsoon promotes rock-water interaction",
        "Post-Monsoon Recovery: Transitional phase — residual recharge effects gradually diminish",
        "Multicollinearity: EC\u2194TDS (r=0.859) — only pair above |r|>0.7 after noise injection",
    ]
    add_bullet_list(slide, Inches(0.6), Inches(1.4), Inches(5.5), Inches(2.0),
                    interp, font_size=11)

    # Figures
    safe_pic(slide, FIG_DIR / "task3_seasonal" / "fig_seasonal_violins.png",
             Inches(6.5), Inches(1.3), width=Inches(6.3), height=Inches(2.8))

    safe_pic(slide, FIG_DIR / "task3_seasonal" / "fig_correlation_matrix.png",
             Inches(0.6), Inches(3.6), width=Inches(5.8), height=Inches(3.5))

    safe_pic(slide, FIG_DIR / "task7_insights" / "fig_seasonal_radar.png",
             Inches(6.8), Inches(4.3), width=Inches(5.8), height=Inches(2.8))

    add_footer(slide)


def slide_07_compliance_wqi(prs):
    """SLIDE 7: IS 10500:2012 Compliance & Water Quality Index"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_CONTENT_BG)
    add_title_bar(slide, "IS 10500:2012 Compliance & Water Quality Index",
                  "3-Tier BIS Assessment + WQI (Brown et al., 1970)")

    # Left column — Safety summary
    add_textbox(slide, Inches(0.6), Inches(1.4), Inches(5.5), Inches(0.35),
                "Overall Sample Safety (n = 195)", font_size=15, bold=True, color=CLR_ACCENT)
    safety_items = [
        "UNSAFE: 183 samples (93.8%) — at least one parameter exceeds permissible limit",
        "CAUTION: 3 samples (1.5%) — within permissible but exceeds acceptable limit",
        "SAFE: 9 samples (4.6%) — all parameters within acceptable limits",
        "Primary drivers: pH (76.4% unsafe), Iron (51.8%), NO\u2083 (23.6%), K (22.6%)",
        "DO: 12.3% unsafe, 39.5% caution — organic contamination in monsoon",
        "Worst season: Monsoon (221 exceedances across all parameters)",
        "Worst locations: SYN-X12, SYN-X11 (5 exceedances each in single season)",
    ]
    add_bullet_list(slide, Inches(0.8), Inches(1.85), Inches(5.3), Inches(2.5),
                    safety_items, font_size=11)

    # Right column — WQI summary
    add_textbox(slide, Inches(6.5), Inches(1.4), Inches(6.3), Inches(0.35),
                "Water Quality Index (WQI)", font_size=15, bold=True, color=CLR_ACCENT)
    wqi_items = [
        "Method: Weighted arithmetic (Brown et al., 1970) — 16 parameters",
        "Mean WQI = 52.49   |   Range = [30.64, 77.02]",
        "Excellent (WQI < 50): 82 samples (42.1%)",
        "Good (50 \u2264 WQI < 100): 113 samples (57.9%)",
        "No samples in Poor, Very Poor, or Unsuitable categories",
        "Premonsoon WQI lower (better) than Monsoon / Postmonsoon",
        "IS 10500 Reference: BIS (2012), Supplementary: WHO (2011, 4th Ed.)",
    ]
    add_bullet_list(slide, Inches(6.7), Inches(1.85), Inches(6.1), Inches(2.5),
                    wqi_items, font_size=11)

    # Figures
    safe_pic(slide, FIG_DIR / "task4_safety" / "fig_is10500_compliance_heatmap.png",
             Inches(0.4), Inches(4.4), width=Inches(4.2), height=Inches(2.8))

    safe_pic(slide, FIG_DIR / "task4_safety" / "fig_is10500_exceedance_factor.png",
             Inches(4.7), Inches(4.4), width=Inches(4.0), height=Inches(2.8))

    safe_pic(slide, FIG_DIR / "task4_safety" / "fig_wqi_analysis.png",
             Inches(8.9), Inches(4.4), width=Inches(4.0), height=Inches(2.8))

    add_footer(slide)


def slide_08_source(prs):
    """SLIDE 8: Anthropogenic & Geogenic Source Analysis"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_CONTENT_BG)
    add_title_bar(slide, "Anthropogenic & Geogenic Source Analysis",
                  "Piper Diagram, Gibbs Mechanism, Ionic Ratios")

    # Findings
    src_items = [
        "Dominant hydrochemical facies: Ca-Cl type",
        "Gibbs mechanism: Rock-water interaction (weathering dominant)",
        "Mean Na/(Na+Ca) = 0.444 — below 0.5 confirms rock weathering",
        "Mean Cl/(Cl+HCO\u2083) = 0.433 — supports weathering over evaporation",
        "Na/Cl mean = 0.89 — Cl excess suggests anthropogenic input or evaporite dissolution",
        "Ca/Mg mean = 3.28 — Ca/Mg > 2 indicates calcite dissolution dominant",
        "NO\u2083: mean = 29.0 mg/L, max = 95.2 mg/L — agricultural/sewage contamination likely",
        "Na-Cl excess = \u22120.476 meq/L — possible anthropogenic Cl input",
        "K enrichment (22.6% non-compliant) — probable fertilizer (potash) origin",
    ]
    add_bullet_list(slide, Inches(0.6), Inches(1.4), Inches(5.5), Inches(3.2),
                    src_items, font_size=11)

    # Figures — Piper and Gibbs
    safe_pic(slide, FIG_DIR / "task5_source" / "fig_piper_diagram.png",
             Inches(6.5), Inches(1.3), width=Inches(3.2), height=Inches(2.8))

    safe_pic(slide, FIG_DIR / "task5_source" / "fig_gibbs_diagram.png",
             Inches(9.8), Inches(1.3), width=Inches(3.2), height=Inches(2.8))

    safe_pic(slide, FIG_DIR / "task5_source" / "fig_ionic_ratios.png",
             Inches(0.6), Inches(4.5), width=Inches(5.5), height=Inches(2.7))

    safe_pic(slide, FIG_DIR / "task3_seasonal" / "fig_distributions.png",
             Inches(6.5), Inches(4.3), width=Inches(6.3), height=Inches(2.8))

    add_footer(slide)


def slide_09_pca_clustering(prs):
    """SLIDE 9: Parameter Grouping — PCA & Clustering"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_CONTENT_BG)
    add_title_bar(slide, "Parameter Grouping — PCA & Clustering",
                  "Principal Component Analysis & K-Means Classification")

    # PCA findings
    pca_items = [
        "PCA on 16 standardised parameters (correlation matrix)",
        "PC1 = 28.7% variance — overall mineralization (EC, TDS, Ca, Na dominant)",
        "PC2 = 12.2% — carbonate vs non-carbonate weathering (HCO\u2083, Na, Alkalinity)",
        "PC3 = 12.0% — anthropogenic inputs (Mg, HCO\u2083, Iron)",
        "PC4 = 7.9% — redox conditions (Iron = 0.488 loading)",
        "6 PCs explain 73.3% cumulative variance",
    ]
    add_bullet_list(slide, Inches(0.6), Inches(1.4), Inches(6), Inches(2.2),
                    pca_items, font_size=12)

    # Clustering findings
    clust_items = [
        "K-Means with k = 3 (elbow method optimised)",
        "Cluster 0: High-mineralization (TDS \u2248 403, EC \u2248 620)",
        "Cluster 1: Low-mineralization (TDS \u2248 251, EC \u2248 390)",
        "Cluster 2: Moderate, hardness-enriched (TDS \u2248 356, EC \u2248 559)",
        "Hierarchical dendrogram confirms 3-cluster structure",
    ]
    add_bullet_list(slide, Inches(6.8), Inches(1.4), Inches(6), Inches(2.0),
                    clust_items, font_size=12)

    # Figures
    safe_pic(slide, FIG_DIR / "task5_source" / "fig_pca_scree.png",
             Inches(0.4), Inches(3.8), width=Inches(3.2), height=Inches(2.5))

    safe_pic(slide, FIG_DIR / "task5_source" / "fig_pca_biplot.png",
             Inches(3.8), Inches(3.8), width=Inches(3.0), height=Inches(2.5))

    safe_pic(slide, FIG_DIR / "task5_source" / "fig_kmeans_pca.png",
             Inches(7.0), Inches(3.8), width=Inches(3.0), height=Inches(2.5))

    safe_pic(slide, FIG_DIR / "task5_source" / "fig_dendrogram.png",
             Inches(10.2), Inches(3.8), width=Inches(2.8), height=Inches(2.5))

    # PCA loadings inline
    safe_pic(slide, FIG_DIR / "task5_source" / "fig_pca_loadings.png",
             Inches(0.4), Inches(6.4), width=Inches(4.5), height=Inches(0.9))

    safe_pic(slide, FIG_DIR / "task5_source" / "fig_elbow.png",
             Inches(5.5), Inches(6.4), width=Inches(3.5), height=Inches(0.9))

    add_footer(slide)


def slide_10a_ml(prs):
    """SLIDE 10a: ML Forecasting — Model Comparison"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_CONTENT_BG)
    add_title_bar(slide, "ML-Based Forecasting — Model Comparison",
                  "5 Models × 3 Targets (TDS, EC, WQI) with 80:20 Train-Test Split")

    # Table data — Model performance summary
    add_textbox(slide, Inches(0.6), Inches(1.4), Inches(12), Inches(0.35),
                "Best Models: SVR (TDS), Random Forest (EC), Neural Network (WQI)",
                font_size=15, bold=True, color=CLR_ACCENT)

    # TDS results
    add_textbox(slide, Inches(0.6), Inches(1.9), Inches(4), Inches(0.3),
                "TARGET: TDS", font_size=14, bold=True, color=CLR_DARK)
    tds_items = [
        "SVR: CV R\u00b2 = 0.732, Test R\u00b2 = 0.767, RMSE = 41.2, MAE = 33.0",
        "Random Forest: CV R\u00b2 = 0.690, Test R\u00b2 = 0.761, RMSE = 41.8",
        "XGBoost: CV R\u00b2 = 0.631, Test R\u00b2 = 0.752, RMSE = 42.5",
        "Gradient Boosting: CV R\u00b2 = 0.620, Test R\u00b2 = 0.698, RMSE = 46.9",
        "Neural Network: CV R\u00b2 = 0.594, Test R\u00b2 = 0.661, RMSE = 49.7",
    ]
    add_bullet_list(slide, Inches(0.8), Inches(2.25), Inches(4), Inches(1.8),
                    tds_items, font_size=10)

    # EC results
    add_textbox(slide, Inches(4.8), Inches(1.9), Inches(4), Inches(0.3),
                "TARGET: EC", font_size=14, bold=True, color=CLR_DARK)
    ec_items = [
        "Random Forest: CV R\u00b2 = 0.722, Test R\u00b2 = 0.771, RMSE = 58.7, MAE = 44.7",
        "Gradient Boosting: CV R\u00b2 = 0.681, Test R\u00b2 = 0.785, RMSE = 56.9",
        "SVR: CV R\u00b2 = 0.677, Test R\u00b2 = 0.699, RMSE = 67.3",
        "XGBoost: CV R\u00b2 = 0.666, Test R\u00b2 = 0.751, RMSE = 61.2",
        "Neural Network: CV R\u00b2 = 0.647, Test R\u00b2 = 0.710, RMSE = 66.0",
    ]
    add_bullet_list(slide, Inches(5.0), Inches(2.25), Inches(4), Inches(1.8),
                    ec_items, font_size=10)

    # WQI results
    add_textbox(slide, Inches(9.0), Inches(1.9), Inches(4), Inches(0.3),
                "TARGET: WQI", font_size=14, bold=True, color=CLR_DARK)
    wqi_items = [
        "Neural Network: CV R\u00b2 = 0.903, Test R\u00b2 = 0.954, RMSE = 2.1, MAE = 1.6",
        "SVR: CV R\u00b2 = 0.883, Test R\u00b2 = 0.951, RMSE = 2.1",
        "XGBoost: CV R\u00b2 = 0.830, Test R\u00b2 = 0.886, RMSE = 3.3",
        "Gradient Boosting: CV R\u00b2 = 0.830, Test R\u00b2 = 0.881, RMSE = 3.3",
        "Random Forest: CV R\u00b2 = 0.800, Test R\u00b2 = 0.863, RMSE = 3.6",
    ]
    add_bullet_list(slide, Inches(9.2), Inches(2.25), Inches(3.8), Inches(1.8),
                    wqi_items, font_size=10)

    # Figures
    safe_pic(slide, FIG_DIR / "task6_ml" / "fig_actual_vs_predicted_tds.png",
             Inches(0.3), Inches(4.3), width=Inches(4.2), height=Inches(2.9))

    safe_pic(slide, FIG_DIR / "task6_ml" / "fig_actual_vs_predicted_ec.png",
             Inches(4.6), Inches(4.3), width=Inches(4.2), height=Inches(2.9))

    safe_pic(slide, FIG_DIR / "task6_ml" / "fig_actual_vs_predicted_wqi.png",
             Inches(9.0), Inches(4.3), width=Inches(4.0), height=Inches(2.9))

    add_footer(slide)


def slide_10b_shap_residuals(prs):
    """SLIDE 10b: SHAP Explainability & Residual Analysis + Uncertainty"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_CONTENT_BG)
    add_title_bar(slide, "SHAP Explainability, Residuals & Uncertainty Metrics",
                  "Feature Importance, Generalization Ability, NSE, RSR, MAPE")

    # Uncertainty metrics header
    add_textbox(slide, Inches(0.6), Inches(1.4), Inches(6), Inches(0.35),
                "Generalization & Uncertainty — Best Model Per Target",
                font_size=14, bold=True, color=CLR_ACCENT)
    uncert_items = [
        "TDS (SVR):  GA = 0.774, MAPE = 10.9%, NSE = 0.767, RSR = 0.483",
        "EC  (RF):   GA = 0.798, MAPE = 10.4%, NSE = 0.771, RSR = 0.479",
        "WQI (NN):   GA = 0.964, MAPE = 3.2%, NSE = 0.953, RSR = 0.216",
        "WQI: Excellent GA (>0.9); TDS/EC: Good GA (0.7\u20130.9) — noise reduces overfitting",
    ]
    add_bullet_list(slide, Inches(0.8), Inches(1.8), Inches(5.5), Inches(1.6),
                    uncert_items, font_size=11)

    # Feature importance
    add_textbox(slide, Inches(6.8), Inches(1.4), Inches(6), Inches(0.35),
                "Top Features (Random Forest / XGBoost)",
                font_size=14, bold=True, color=CLR_ACCENT)
    feat_items = [
        "TDS: Na (0.330), Ca (0.291), K (0.086), Season (0.086)",
        "EC:  Na (0.395), Ca (0.238), K (0.116), SO\u2084 (0.041)",
        "WQI: EC (0.400), TDS (0.209), NO\u2083 (0.132), K (0.071)",
        "SHAP confirms Na, Ca, EC as primary drivers of water quality",
    ]
    add_bullet_list(slide, Inches(7.0), Inches(1.8), Inches(6), Inches(1.6),
                    feat_items, font_size=11)

    # Figures — SHAP and Residuals
    safe_pic(slide, FIG_DIR / "task6_ml" / "fig_shap_summary_tds.png",
             Inches(0.3), Inches(3.5), width=Inches(4.2), height=Inches(1.8))

    safe_pic(slide, FIG_DIR / "task6_ml" / "fig_shap_summary_ec.png",
             Inches(4.6), Inches(3.5), width=Inches(4.2), height=Inches(1.8))

    safe_pic(slide, FIG_DIR / "task6_ml" / "fig_shap_summary_wqi.png",
             Inches(9.0), Inches(3.5), width=Inches(4.0), height=Inches(1.8))

    safe_pic(slide, FIG_DIR / "task6_ml" / "fig_residuals_tds.png",
             Inches(0.3), Inches(5.4), width=Inches(4.2), height=Inches(1.8))

    safe_pic(slide, FIG_DIR / "task6_ml" / "fig_residuals_ec.png",
             Inches(4.6), Inches(5.4), width=Inches(4.2), height=Inches(1.8))

    safe_pic(slide, FIG_DIR / "task6_ml" / "fig_residuals_wqi.png",
             Inches(9.0), Inches(5.4), width=Inches(4.0), height=Inches(1.8))

    add_footer(slide)


def slide_11_conclusion(prs):
    """SLIDE 11: Conclusions"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_CONTENT_BG)
    add_title_bar(slide, "Conclusions & Policy Recommendations")

    # Key conclusions
    add_textbox(slide, Inches(0.6), Inches(1.4), Inches(6), Inches(0.35),
                "Key Findings", font_size=16, bold=True, color=CLR_ACCENT)
    conclusions = [
        "93.8% of all samples classified as UNSAFE under IS 10500:2012",
        "pH (76.4% unsafe), Iron (51.8%), NO\u2083 (23.6%), K (22.6%) are primary risk drivers",
        "Dominant facies: Ca-Cl — rock-water interaction (weathering) controls chemistry",
        "Monsoon is the worst season (221 exceedances) due to surface runoff mobilisation",
        "WQI range [30.6, 77.0] — no samples in 'Poor' or 'Unsuitable' categories",
        "Best models: SVR (TDS, CV R\u00b2=0.73), RF (EC, 0.72), NN (WQI, 0.90)",
        "SHAP confirms Na, Ca, EC as dominant drivers; NO\u2083, K signal anthropogenic loading",
        "Noisy synthetic augmentation (150 samples) reduces overfitting & improves generalisability",
    ]
    add_bullet_list(slide, Inches(0.8), Inches(1.85), Inches(5.8), Inches(3.0),
                    conclusions, font_size=12)

    # Policy recommendations
    add_textbox(slide, Inches(7.0), Inches(1.4), Inches(6), Inches(0.35),
                "Policy Recommendations", font_size=16, bold=True, color=CLR_ACCENT)
    policies = [
        "Establish continuous groundwater quality monitoring at IA-3, DY-4, IA-1",
        "pH correction: alkaline dosing (lime/soda ash) at extraction points",
        "Regulate fertilizer (potash) use near K-enriched zones (22.6% non-compliant)",
        "Implement rainwater harvesting to enhance natural aquifer recharge",
        "Manage organic waste near DY sites to reduce acidification risk",
        "Periodic ionic balance (CBE) validation ensures data quality assurance",
        "Deploy target-specific best models: SVR (TDS), RF (EC), NN (WQI) for forecasting",
        "Climate-adaptive monitoring — monsoon variability may shift recharge patterns",
    ]
    add_bullet_list(slide, Inches(7.2), Inches(1.85), Inches(5.6), Inches(3.0),
                    policies, font_size=12)

    # Health implications box
    add_textbox(slide, Inches(0.6), Inches(5.2), Inches(12), Inches(0.35),
                "Health Implications", font_size=14, bold=True, color=CLR_RED)
    health_items = [
        "pH < 6.5: Corrosive water — metal leaching from pipes (Cu, Pb risk)",
        "NO\u2083 > 45 mg/L: Methemoglobinemia (blue baby syndrome) risk at some locations",
        "Iron (51.8% unsafe): Exceeds 0.3 mg/L — taste issues, bacterial growth promotion",
        "Low DO (12.3% unsafe, 39.5% caution): Organic contamination in monsoon samples",
    ]
    add_bullet_list(slide, Inches(0.8), Inches(5.6), Inches(12), Inches(1.5),
                    health_items, font_size=11, color=CLR_DARK)

    add_footer(slide)


def slide_12_acknowledgement(prs):
    """SLIDE 12: Acknowledgement"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_TITLE_BG)

    add_textbox(slide, Inches(1), Inches(1.5), Inches(11), Inches(0.8),
                "Acknowledgement",
                font_size=36, bold=True, color=CLR_WHITE, alignment=PP_ALIGN.CENTER)

    add_teal_rule(slide, Inches(4), Inches(2.4), Inches(5))

    ack_text = (
        "We express our sincere gratitude to Dr. Ajit Kumar Pasayat\n"
        "for his invaluable guidance and mentorship throughout this project.\n\n"
        "We also thank the School of Civil Engineering,\n"
        "KIIT Deemed to be University, Bhubaneswar,\n"
        "for providing the laboratory facilities and groundwater sampling infrastructure.\n\n"
        "This study was conducted as part of the coursework\n"
        "for the Academic Year 2024–25."
    )
    add_textbox(slide, Inches(1.5), Inches(2.9), Inches(10), Inches(2.5),
                ack_text, font_size=18, color=CLR_WHITE, alignment=PP_ALIGN.CENTER)

    add_textbox(slide, Inches(1), Inches(5.6), Inches(11), Inches(0.5),
                "Lakshya Nayyar (23053133)  |  Vaibhav Bhaskar (23053173)",
                font_size=16, color=CLR_ACCENT, alignment=PP_ALIGN.CENTER)

    add_textbox(slide, Inches(1), Inches(6.2), Inches(11), Inches(0.4),
                "School of Civil Engineering, KIIT University, Bhubaneswar",
                font_size=13, color=CLR_GREY, alignment=PP_ALIGN.CENTER)

    add_footer(slide, "Thank You")


def slide_13_references(prs):
    """SLIDE 13 (Bonus): References"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, CLR_CONTENT_BG)
    add_title_bar(slide, "References")

    refs = [
        "1. Bureau of Indian Standards (BIS). IS 10500:2012 — Drinking Water Specification (Second Revision). New Delhi: BIS, 2012.",
        "2. World Health Organization (WHO). Guidelines for Drinking-water Quality, 4th Edition. Geneva: WHO, 2011.",
        "3. Brown, R.M., McClelland, N., Deininger, R.A. & Tozer, R.G. (1970). A Water Quality Index — Do We Dare? Water & Sewage Works, 117(10).",
        "4. Sekar, S., et al. (2025). Machine learning-based prediction of seasonal groundwater quality for Melur, Tamil Nadu. Results in Engineering, 28.",
        "5. Piper, A.M. (1944). A Graphic Procedure in the Geochemical Interpretation of Water Analyses. Trans. AGU, 25(6), 914–928.",
        "6. Gibbs, R.J. (1970). Mechanisms Controlling World Water Chemistry. Science, 170(3962), 1088–1090.",
        "7. Lundberg, S.M. & Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions. NeurIPS 2017.",
        "8. Central Pollution Control Board (CPCB). Drinking Water Quality Standards — Class A Criteria. Government of India.",
        "9. FSSAI / Government of India. Food Safety and Standards (Drinking Water) Regulations.",
    ]

    txBox = slide.shapes.add_textbox(Inches(0.6), Inches(1.5), Inches(12), Inches(5.5))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, ref in enumerate(refs):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = ref
        p.font.size = Pt(12)
        p.font.color.rgb = CLR_DARK
        p.font.name = FONT_NAME
        p.space_after = Pt(8)

    add_footer(slide)


# ──────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  GENERATING POWERPOINT PRESENTATION")
    print("=" * 70)

    prs = Presentation()

    # Set widescreen slide size (13.333 × 7.5 inches)
    prs.slide_width = Emu(12192000)   # 13.333 inches
    prs.slide_height = Emu(6858000)   # 7.5 inches

    # Build all slides
    builders = [
        ("Slide 1:  Title", slide_01_title),
        ("Slide 2:  Outline", slide_02_outline),
        ("Slide 3:  Introduction & Study Area", slide_03_introduction),
        ("Slide 4:  Dataset & Synthetic Augmentation", slide_04_dataset),
        ("Slide 5:  Methodology Pipeline", slide_05_methodology),
        ("Slide 6a: Seasonal Dynamics — Statistics", slide_06a_seasonal),
        ("Slide 6b: Seasonal Variation — Distributions", slide_06b_seasonal),
        ("Slide 7:  IS 10500 Compliance & WQI", slide_07_compliance_wqi),
        ("Slide 8:  Source Analysis", slide_08_source),
        ("Slide 9:  PCA & Clustering", slide_09_pca_clustering),
        ("Slide 10a: ML Model Comparison", slide_10a_ml),
        ("Slide 10b: SHAP & Residuals", slide_10b_shap_residuals),
        ("Slide 11:  Conclusions", slide_11_conclusion),
        ("Slide 12:  Acknowledgement", slide_12_acknowledgement),
        ("Slide 13:  References", slide_13_references),
    ]

    for label, builder in builders:
        print(f"  Building {label} ...")
        builder(prs)

    prs.save(str(OUT_PPT))
    print(f"\n  Saved to: {OUT_PPT}")
    print(f"  Total slides: {len(prs.slides)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
