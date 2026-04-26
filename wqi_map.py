"""
WQI Spatial Map + Synthetic Location Naming
============================================
1. Generates fig_wqi_map.png  — geographic bubble map with properly-scaled WQI colorbar
2. Prints/saves a table of SYN-X locations reverse-geocoded to real BBS neighbourhoods
"""

import math, pandas as pd, numpy as np, matplotlib.pyplot as plt
import matplotlib.cm as cm, matplotlib.colors as mcolors
from matplotlib.patches import Patch
from pathlib import Path

BASE   = Path(__file__).parent
DATA   = BASE / "datasets"
FIGDIR = BASE / "figures" / "task4_safety"
FIGDIR.mkdir(parents=True, exist_ok=True)

# ── Known Bhubaneswar locality reference grid (lat, lon, name) ───────────────
# Sources: OSM / local knowledge; adequate for nearest-neighbour assignment
BBSR_LOCALITIES = [
    # original 15 sampling sites (used as anchors)
    (20.303531, 85.826217, "Acharya Vihar"),
    (20.278197, 85.840284, "Ram Mandir"),
    (20.337294, 85.810481, "Sailashree Vihar"),
    (20.323147, 85.823090, "OMFED Square"),
    (20.228015, 85.833273, "Old Town Bhubaneswar"),
    (20.305158, 85.857224, "Mancheswar Industrial Estate"),
    (20.347449, 85.814168, "Chandaka Industrial Area"),
    (20.329160, 85.826771, "OMFED Industries"),
    (20.298776, 85.866261, "Rasulgarh"),
    (20.363260, 85.753206, "Bharatpur / Anmol Industries"),
    (20.388678, 85.792107, "Bhuasuni"),
    (20.235861, 85.835820, "Lingaraj Railway Station"),
    (20.284301, 85.833995, "BMC Micro Composting Area"),
    (20.326795, 85.835968, "Gadakan Road"),
    (20.382316, 85.795063, "Daruthenga"),
    # supplementary Bhubaneswar localities
    (20.355000, 85.820000, "Patia"),
    (20.294000, 85.820000, "Jaydev Vihar"),
    (20.303000, 85.806000, "Nayapalli"),
    (20.272000, 85.789000, "Khandagiri"),
    (20.295000, 85.800000, "Baramunda"),
    (20.268000, 85.843000, "Sahid Nagar"),
    (20.287000, 85.852000, "Vani Vihar"),
    (20.340000, 85.793000, "Niladri Vihar"),
    (20.280000, 85.810000, "Pokhariput"),
    (20.270000, 85.852000, "Laxmisagar"),
    (20.355000, 85.864000, "KIIT University Campus"),
    (20.355000, 85.793000, "Infocity / IT Park"),
    (20.307000, 85.815000, "IRC Village"),
    (20.301000, 85.837000, "Satya Nagar"),
    (20.267000, 85.828000, "Bapuji Nagar"),
    (20.273000, 85.844000, "Master Canteen / Unit-1"),
    (20.276000, 85.828000, "Bhoinagar"),
    (20.361000, 85.844000, "Nalco Square / Pandara"),
    (20.281000, 85.802000, "Palasuni"),
    (20.319000, 85.788000, "Ghatikia"),
    (20.348000, 85.843000, "Forest Park / DY Patna"),
    (20.364000, 85.803000, "Tamando Industrial Area"),
    (20.272000, 85.866000, "Surya Nagar / Nakhara"),
    (20.292000, 85.863000, "Jayadev Vihar East"),
    (20.278000, 85.804000, "Aiginia"),
    (20.367000, 85.851000, "IMMT Area / Acharya Nagar"),
    (20.312000, 85.855000, "Bomikhal"),
    (20.289000, 85.795000, "Nayapalli Extension"),
    (20.344000, 85.862000, "Patia East / Damana"),
    (20.324000, 85.784000, "Kargil Square"),
    (20.291000, 85.783000, "Baramunda Bus Terminal"),
    (20.315000, 85.832000, "Janpath / Rajpath"),
    (20.335000, 85.851000, "Jatni Bypass"),
    (20.360000, 85.820000, "Chandrasekharpur"),
    (20.290000, 85.840000, "Ashok Nagar"),
    (20.306000, 85.848000, "Saheed Nagar Extension"),
    (20.299000, 85.823000, "Unit-IV"),
    (20.285000, 85.792000, "Nayapalli West"),
    (20.352000, 85.808000, "Niladri East"),
    (20.332000, 85.783000, "Kargil Nagar"),
    (20.276000, 85.814000, "Bhubaleswar Old City"),
    (20.363000, 85.867000, "Kalinga Nagar"),
    (20.285000, 85.865000, "Pahala"),
    (20.273000, 85.869000, "Maitri Vihar"),
    (20.268000, 85.869000, "Dumduma"),
    (20.351000, 85.823000, "Baramunda North"),
    (20.342000, 85.795000, "Khandagiri East"),
    (20.275000, 85.775000, "Baramunda West"),
    (20.317000, 85.791000, "Ghatikia South"),
    (20.296000, 85.775000, "Gajapati Nagar"),
    (20.308000, 85.780000, "Nayapalli North"),
]


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def nearest_locality(lat, lon):
    best, best_dist = "Unknown", float('inf')
    for lo_lat, lo_lon, lo_name in BBSR_LOCALITIES:
        d = haversine_km(lat, lon, lo_lat, lo_lon)
        if d < best_dist:
            best_dist, best = d, lo_name
    return best, round(best_dist, 3)


# ── Load data ─────────────────────────────────────────────────────────────────
df_wqi  = pd.read_csv(DATA / "wqi_results.csv")
df_comb = pd.read_csv(DATA / "validated_combined.csv")

# Attach coordinates to WQI table
coord_map = (df_comb.drop_duplicates(subset=["Location_ID", "Season"])
                     .set_index(["Location_ID", "Season"])[["Latitude", "Longitude"]])
df_wqi = df_wqi.join(coord_map, on=["Location_ID", "Season"])

# ── PART 1 — WQI Spatial Map ──────────────────────────────────────────────────
WQI_MIN, WQI_MAX = 30, 80   # rescaled range (actual data: 30.81 – 77.04)
seasons   = ["Premonsoon", "Monsoon", "Postmonsoon"]
markers   = {"Premonsoon": "o", "Monsoon": "s", "Postmonsoon": "^"}
cmap      = plt.get_cmap("RdYlGn_r")     # red = high WQI (worse), green = low
norm      = mcolors.Normalize(vmin=WQI_MIN, vmax=WQI_MAX)

# Category boundaries for threshold lines on colorbar
cat_thresholds = [50, 100, 200, 300]   # Excellent | Good | Poor | VPoor | Unsuitable

fig, axes = plt.subplots(1, 3, figsize=(20, 7),
                          gridspec_kw={"wspace": 0.04})
fig.patch.set_facecolor("#F0F4FA")

for ax, season in zip(axes, seasons):
    sd      = df_wqi[df_wqi["Season"] == season].dropna(subset=["Latitude", "Longitude", "WQI"])
    orig    = sd[~sd["Location_ID"].str.startswith("SYN")]
    syn_x   = sd[sd["Location_ID"].str.startswith("SYN-X")]
    syn_pd  = sd[sd["Location_ID"].str.startswith("SYN-") & ~sd["Location_ID"].str.startswith("SYN-X")]

    ax.set_facecolor("#E8F2FC")
    for spine in ax.spines.values():
        spine.set_edgecolor("#7C9CBF"); spine.set_linewidth(0.8)

    # Background grid
    ax.grid(True, color="#C0D0E8", linewidth=0.5, zorder=0)

    # Zone background shading by longitude band
    ax.axvspan(85.74, 85.80, color="#FFF8E7", alpha=0.45, zorder=1, label="_W zone")
    ax.axvspan(85.80, 85.83, color="#F0FFF0", alpha=0.45, zorder=1, label="_C zone")
    ax.axvspan(85.83, 85.88, color="#FFF0F0", alpha=0.45, zorder=1, label="_E zone")

    # Synthetic-zone bubbles (faint, background layer)
    if len(syn_x) > 0:
        sc_sx = ax.scatter(syn_x["Longitude"], syn_x["Latitude"],
                           c=syn_x["WQI"], cmap=cmap, norm=norm,
                           s=55, marker="D", alpha=0.50, linewidths=0.4,
                           edgecolors="grey", zorder=3)

    # SYN-PD/IA/DY bubbles
    if len(syn_pd) > 0:
        sc_sp = ax.scatter(syn_pd["Longitude"], syn_pd["Latitude"],
                           c=syn_pd["WQI"], cmap=cmap, norm=norm,
                           s=70, marker="P", alpha=0.60, linewidths=0.4,
                           edgecolors="navy", zorder=4)

    # Original site bubbles (prominent)
    sc_orig = ax.scatter(orig["Longitude"], orig["Latitude"],
                         c=orig["WQI"], cmap=cmap, norm=norm,
                         s=180, marker="o", alpha=0.92, linewidths=0.8,
                         edgecolors="white", zorder=5)

    # Label original sites
    for _, row in orig.iterrows():
        ax.annotate(row["Location_ID"],
                    xy=(row["Longitude"], row["Latitude"]),
                    xytext=(3, 4), textcoords="offset points",
                    fontsize=6.5, color="#1A2A3A", fontweight="bold",
                    zorder=6)

    # WQI value labels for original
    for _, row in orig.iterrows():
        ax.annotate(f"{row['WQI']:.1f}",
                    xy=(row["Longitude"], row["Latitude"]),
                    xytext=(3, -9), textcoords="offset points",
                    fontsize=5.8, color="#333333",
                    zorder=6)

    # Stats box
    mn, mx, mu = sd["WQI"].min(), sd["WQI"].max(), sd["WQI"].mean()
    stats_txt = f"n={len(sd)}\nMin={mn:.1f}\nMean={mu:.1f}\nMax={mx:.1f}"
    ax.text(0.02, 0.98, stats_txt, transform=ax.transAxes,
            fontsize=7.5, va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#4A90D9", alpha=0.85))

    ax.set_title(season, fontsize=13, fontweight="bold", color="#0D2137", pad=5)
    ax.set_xlabel("Longitude (°E)", fontsize=9)
    ax.set_xlim(85.740, 85.880)
    ax.set_ylim(20.215, 20.405)
    ax.tick_params(labelsize=7.5)

axes[0].set_ylabel("Latitude (°N)", fontsize=9)
axes[1].set_ylabel("")
axes[2].set_ylabel("")

# Shared colorbar
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar_ax = fig.add_axes([0.92, 0.14, 0.018, 0.70])
cbar    = fig.colorbar(sm, cax=cbar_ax)
cbar.set_label("WQI Value", fontsize=10, fontweight="bold")
cbar.set_ticks([30, 40, 50, 60, 70, 80])
cbar.ax.axhline(50, color="black", linewidth=1.5, linestyle="--")   # Excellent | Good
cbar.ax.text(1.05, 50, "Good↑", transform=cbar.ax.get_yaxis_transform(),
             va="center", fontsize=7.5, color="#1565C0")
cbar.ax.text(1.05, 35, "Excellent", transform=cbar.ax.get_yaxis_transform(),
             va="center", fontsize=7.5, color="#2E7D32")

# Legend
legend_handles = [
    Patch(fc=cmap(norm(38)), ec="white",      label="WQI < 50  — Excellent"),
    Patch(fc=cmap(norm(62)), ec="white",      label="WQI 50-77 — Good"),
    plt.scatter([], [], s=180, marker="o", fc="grey", ec="white", label="Original sites"),
    plt.scatter([], [], s=70,  marker="P", fc="grey", ec="navy",  label="Synthetic (SYN-PD/IA/DY)"),
    plt.scatter([], [], s=55,  marker="D", fc="grey", ec="grey",  label="Synthetic (SYN-X extra)"),
]
axes[0].legend(handles=legend_handles, loc="lower left", fontsize=7,
               framealpha=0.9, edgecolor="#4A90D9", title="Legend", title_fontsize=8)

fig.suptitle(
    "Water Quality Index (WQI) — Spatial Distribution Map\n"
    "Bhubaneswar, Odisha  |  WQI Scale: 30–80  |  All Sites: Excellent–Good  |  Brown et al. (1970)",
    fontsize=13, fontweight="bold", color="#0D2137", y=1.01
)
plt.tight_layout(rect=[0, 0, 0.91, 1])
out_map = FIGDIR / "fig_wqi_map.png"
fig.savefig(str(out_map), dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"✓ WQI spatial map saved → {out_map}")


# ── PART 1b — fig_wqi_analysis.png: 3 spatial maps (report quality, all 195) ─
import re as _re

CMAP_WQI = plt.get_cmap("RdYlGn_r")
NORM_WQI = mcolors.Normalize(vmin=30, vmax=100)   # full WQI scale 0–100
SEASONS  = ["Premonsoon", "Monsoon", "Postmonsoon"]

SEAS_TITLE = {
    "Premonsoon":  "Season 1 — Premonsoon  (Pre-wet)",
    "Monsoon":     "Season 2 — Monsoon  (Wet)",
    "Postmonsoon": "Season 3 — Postmonsoon  (Post-wet)",
}
SEAS_STATS_CLR = {"Premonsoon": "#C0392B", "Monsoon": "#2980B9", "Postmonsoon": "#27AE60"}

fig_maps, axes_maps = plt.subplots(
    1, 3, figsize=(24, 8.5),
    gridspec_kw={"wspace": 0.06}
)
fig_maps.patch.set_facecolor("white")

for ax, season in zip(axes_maps, SEASONS):
    sd     = df_wqi[df_wqi["Season"] == season].dropna(subset=["Latitude","Longitude","WQI"])
    orig   = sd[~sd["Location_ID"].str.startswith("SYN")]
    syn_pd = sd[sd["Location_ID"].str.startswith("SYN-") &
                ~sd["Location_ID"].str.startswith("SYN-X")]
    syn_x  = sd[sd["Location_ID"].str.startswith("SYN-X")]

    ax.set_facecolor("#EEF4FB")
    ax.grid(True, color="#C8D8EB", linewidth=0.55, zorder=0)
    for sp in ax.spines.values():
        sp.set_edgecolor("#7090B0"); sp.set_linewidth(0.9)

    # Shaded zone bands
    ax.axvspan(85.740, 85.800, color="#FFF9EC", alpha=0.5, zorder=1)
    ax.axvspan(85.800, 85.835, color="#F0FFF4", alpha=0.5, zorder=1)
    ax.axvspan(85.835, 85.885, color="#FFF0F0", alpha=0.5, zorder=1)

    # Layer 1 – SYN-X (background, small diamonds)
    if len(syn_x):
        ax.scatter(syn_x["Longitude"], syn_x["Latitude"],
                   c=syn_x["WQI"], cmap=CMAP_WQI, norm=NORM_WQI,
                   s=38, marker="D", alpha=0.45, linewidths=0.3,
                   edgecolors="#888888", zorder=3, label="SYN-X (extra)")

    # Layer 2 – SYN-PD/IA/DY (mid, plus markers)
    if len(syn_pd):
        ax.scatter(syn_pd["Longitude"], syn_pd["Latitude"],
                   c=syn_pd["WQI"], cmap=CMAP_WQI, norm=NORM_WQI,
                   s=65, marker="P", alpha=0.62, linewidths=0.5,
                   edgecolors="#334455", zorder=4, label="SYN-PD/IA/DY")

    # Layer 3 – Original 15 (prominent circles)
    sc = ax.scatter(orig["Longitude"], orig["Latitude"],
                    c=orig["WQI"], cmap=CMAP_WQI, norm=NORM_WQI,
                    s=200, marker="o", alpha=0.95, linewidths=1.0,
                    edgecolors="white", zorder=5, label="Original sites")

    # ID + value labels on originals
    for _, row in orig.iterrows():
        ax.annotate(
            row["Location_ID"],
            xy=(row["Longitude"], row["Latitude"]),
            xytext=(4, 5), textcoords="offset points",
            fontsize=6.8, fontweight="bold", color="#0D1F2D", zorder=6
        )
        ax.annotate(
            f"{row['WQI']:.1f}",
            xy=(row["Longitude"], row["Latitude"]),
            xytext=(4, -10), textcoords="offset points",
            fontsize=6.0, color="#333333", zorder=6
        )

    # Stats box
    mn, mx, mu, sd_val = (sd["WQI"].min(), sd["WQI"].max(),
                          sd["WQI"].mean(), sd["WQI"].std())
    exc = (sd["WQI_Category"] == "Excellent").sum()
    good = (sd["WQI_Category"] == "Good").sum()
    txt = (f"n = {len(sd)}\nMin = {mn:.1f}\nMean = {mu:.1f}\n"
           f"Max = {mx:.1f}\nSD = {sd_val:.1f}\n"
           f"Excellent: {exc} ({exc*100//len(sd)}%)\n"
           f"Good:      {good} ({good*100//len(sd)}%)")
    ax.text(0.015, 0.99, txt, transform=ax.transAxes,
            fontsize=7.2, va="top", ha="left", linespacing=1.45,
            fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.35", fc="white",
                      ec=SEAS_STATS_CLR[season], lw=1.2, alpha=0.92))

    # Season header band
    ax.set_title(SEAS_TITLE[season], fontsize=11.5, fontweight="bold",
                 color="#0D1F2D", pad=7,
                 bbox=dict(fc=SEAS_STATS_CLR[season], ec="none",
                           boxstyle="round,pad=0.25", alpha=0.15))

    ax.set_xlabel("Longitude  (°E)", fontsize=9)
    ax.set_xlim(85.738, 85.882)
    ax.set_ylim(20.210, 20.408)
    ax.tick_params(labelsize=7.8)
    ax.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{v:.3f}°E"))
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{v:.3f}°N"))

axes_maps[0].set_ylabel("Latitude  (°N)", fontsize=9)
axes_maps[1].set_ylabel("")
axes_maps[2].set_ylabel("")

# Shared colorbar
sm_r = cm.ScalarMappable(cmap=CMAP_WQI, norm=NORM_WQI)
sm_r.set_array([])
cbar_ax_r = fig_maps.add_axes([0.925, 0.13, 0.016, 0.72])
cbar_r     = fig_maps.colorbar(sm_r, cax=cbar_ax_r)
cbar_r.set_label("WQI  Value", fontsize=10, fontweight="bold", labelpad=6)
cbar_r.set_ticks([30, 40, 50, 60, 70, 80, 90, 100])
# Category boundary
cbar_r.ax.axhline(50, color="#0D5B1E", linewidth=2.0, linestyle="--")
cbar_r.ax.text(1.08, 50, "Excellent / Good\nboundary (50)",
               transform=cbar_r.ax.get_yaxis_transform(),
               va="center", fontsize=7, color="#0D5B1E")
cbar_r.ax.text(1.08, 38, "EXCELLENT\n(WQI < 50)",
               transform=cbar_r.ax.get_yaxis_transform(),
               va="center", fontsize=7, color="#1A7A40", fontweight="bold")
cbar_r.ax.text(1.08, 70, "GOOD\n(WQI 50–100)",
               transform=cbar_r.ax.get_yaxis_transform(),
               va="center", fontsize=7, color="#7B4F00", fontweight="bold")

# Legend
leg_handles = [
    plt.scatter([], [], s=200, marker="o", fc="#3EAF66", ec="white",
                label="Original 15 sites"),
    plt.scatter([], [], s=65,  marker="P", fc="#3EAF66", ec="#334455",
                label="Synthetic — SYN-PD/IA/DY (15 sites)"),
    plt.scatter([], [], s=38,  marker="D", fc="#3EAF66", ec="#888888",
                label="Synthetic — SYN-X extra (35 sites)"),
    Patch(fc="#fff9ec", ec="#999", label="West zone (Khandagiri–Baramunda)"),
    Patch(fc="#f0fff4", ec="#999", label="Central zone (OMFED–IRC Village)"),
    Patch(fc="#fff0f0", ec="#999", label="East zone (Rasulgarh–Bomikhal)"),
]
axes_maps[0].legend(handles=leg_handles, loc="lower left", fontsize=7.2,
                    framealpha=0.92, edgecolor="#6090B0",
                    title="Map Legend", title_fontsize=8)

fig_maps.suptitle(
    "Water Quality Index (WQI) — Seasonal Spatial Distribution\n"
    "Bhubaneswar, Odisha (2024)  ·  195 Samples (45 Original + 150 Synthetic)"
    "  ·  IS 10500:2012  ·  Brown et al. (1970)",
    fontsize=13, fontweight="bold", color="#0D1F2D", y=1.01
)
fig_maps.tight_layout(rect=[0, 0, 0.92, 1])
out_analysis = FIGDIR / "fig_wqi_analysis.png"
fig_maps.savefig(str(out_analysis), dpi=200, bbox_inches="tight",
                 facecolor="white")
plt.close()
print(f"✓ WQI 3-map analysis figure → {out_analysis}")


# ── PART 1c — Bar chart: Original 15 sites → fig_wqi_bar_original.png ─────────
orig_wqi = df_wqi[~df_wqi["Location_ID"].str.startswith("SYN")].copy()

# Fixed location order matching the 3 zone groups
LOC_ORDER  = ["PD-1","PD-2","PD-3","PD-4","PD-5",
              "IA-1","IA-2","IA-3","IA-4","IA-5",
              "DY-1","DY-2","DY-3","DY-4","DY-5"]
AREA_NAMES = {
    "PD-1": "Acharya\nVihar",    "PD-2": "Ram\nMandir",
    "PD-3": "Sailashree\nVihar", "PD-4": "OMFED\nSquare",
    "PD-5": "Old Town\nBBS",     "IA-1": "Mancheswar\nInd.",
    "IA-2": "Chandaka\nInd.",    "IA-3": "OMFED\nInd.",
    "IA-4": "Rasulgarh",         "IA-5": "Anmol\nInd.",
    "DY-1": "Bhuasuni",          "DY-2": "Lingaraj\nRly.",
    "DY-3": "BMC Micro\nComp.",  "DY-4": "Gadakan\nRoad",
    "DY-5": "Daruthenga",
}

SEASON_BAR_CFG = {
    "Premonsoon":  {"color": "#E07070", "hatch": "",   "label": "Premonsoon"},
    "Monsoon":     {"color": "#4A90D9", "hatch": "",   "label": "Monsoon"},
    "Postmonsoon": {"color": "#2ECC71", "hatch": "",   "label": "Postmonsoon"},
}

n_loc   = len(LOC_ORDER)
n_seas  = 3
bar_w   = 0.24
x_pos   = np.arange(n_loc)
offsets = [-bar_w, 0, bar_w]

fig2, axes2 = plt.subplots(
    2, 2, figsize=(22, 11),
    gridspec_kw={"height_ratios": [2.2, 1], "hspace": 0.45, "wspace": 0.25}
)
fig2.patch.set_facecolor("#F4F7FC")

# ── Panel A: main grouped bar chart ──────────────────────────────────────────
ax_bar = axes2[0, :]  # span both columns
ax_bar = fig2.add_subplot(2, 1, 1)
ax_bar.set_facecolor("#F9FBFF")

# Category band shading (background)
ax_bar.axhspan(0,  50,  color="#E8F8EE", alpha=0.55, zorder=0)   # Excellent (green)
ax_bar.axhspan(50, 100, color="#FFF8E7", alpha=0.55, zorder=0)   # Good      (amber)

# Category boundary lines
ax_bar.axhline(50,  color="#2ECC71", linewidth=1.6, linestyle="--", zorder=2,
               label="_exc_boundary")
ax_bar.axhline(100, color="#E07070", linewidth=1.6, linestyle="--", zorder=2,
               label="_good_boundary")

# Zone separator vertical lines (between PD/IA/DY)
for x_sep in [4.5, 9.5]:
    ax_bar.axvline(x_sep, color="#AABBCC", linewidth=1.2, linestyle=":", zorder=2)

# Zone labels
for xt, zlbl, zclr in [
    (2.0,  "Population Density (PD)",  "#1A6B3C"),
    (7.0,  "Industrial Areas (IA)",    "#1A3B6B"),
    (12.0, "Dumping Yards (DY)",       "#6B1A1A"),
]:
    ax_bar.text(xt, 101.5, zlbl, ha="center", va="bottom", fontsize=10,
                fontweight="bold", color=zclr)

for i, (season, cfg) in enumerate(SEASON_BAR_CFG.items()):
    wqi_vals = []
    for loc in LOC_ORDER:
        row = orig_wqi[(orig_wqi["Location_ID"] == loc) & (orig_wqi["Season"] == season)]
        wqi_vals.append(row["WQI"].values[0] if len(row) else np.nan)

    bars = ax_bar.bar(
        x_pos + offsets[i], wqi_vals,
        width=bar_w, label=cfg["label"],
        color=cfg["color"], edgecolor="white",
        linewidth=0.7, zorder=3, alpha=0.90
    )

    # Value labels on top of each bar
    for bar, val in zip(bars, wqi_vals):
        if not np.isnan(val):
            ax_bar.text(
                bar.get_x() + bar.get_width() / 2,
                val + 0.8,
                f"{val:.1f}",
                ha="center", va="bottom",
                fontsize=6.8, color="#333333", rotation=90,
                fontweight="bold"
            )

# Category band annotations (right side)
ax_bar.text(n_loc - 0.1, 25,  "Excellent\n(WQI < 50)",  ha="right", va="center",
            fontsize=9.5, color="#1A7A40", fontweight="bold",
            bbox=dict(fc="#E8F8EE", ec="#2ECC71", boxstyle="round,pad=0.3", alpha=0.85))
ax_bar.text(n_loc - 0.1, 73,  "Good\n(WQI 50–100)", ha="right", va="center",
            fontsize=9.5, color="#7B4F00", fontweight="bold",
            bbox=dict(fc="#FFF8E7", ec="#F39C12", boxstyle="round,pad=0.3", alpha=0.85))

ax_bar.set_xticks(x_pos)
ax_bar.set_xticklabels(
    [f"{loc}\n{AREA_NAMES[loc]}" for loc in LOC_ORDER],
    fontsize=8.2
)
ax_bar.set_yticks(range(0, 101, 10))
ax_bar.set_ylim(0, 108)
ax_bar.set_xlim(-0.6, n_loc - 0.4)
ax_bar.set_ylabel("WQI Value", fontsize=11, fontweight="bold")
ax_bar.set_title(
    "Water Quality Index (WQI) per Sampling Location and Season\n"
    "WQI = Σ(Wᵢ × qᵢ),  qᵢ = (Cᵢ / Sᵢ) × 100  |  IS 10500:2012 Standards  |  Brown et al. (1970)",
    fontsize=12, fontweight="bold", color="#0D2137", pad=8
)
ax_bar.legend(fontsize=10, loc="upper left", framealpha=0.9,
              edgecolor="#4A90D9", title="Season", title_fontsize=10)
ax_bar.grid(axis="y", color="#CCDDEE", linewidth=0.6, zorder=1)
for spine in ax_bar.spines.values():
    spine.set_edgecolor("#9AABBF")

# ── Panel B: Boxplot by season (bottom-left) ─────────────────────────────────
import matplotlib.patches as mpatches
ax_box = axes2[1, 0]
ax_box.set_facecolor("#F9FBFF")

box_data  = [orig_wqi[orig_wqi["Season"] == s]["WQI"].dropna().values
             for s in ["Premonsoon", "Monsoon", "Postmonsoon"]]
box_colors = ["#E07070", "#4A90D9", "#2ECC71"]
bp = ax_box.boxplot(box_data, patch_artist=True, widths=0.45,
                    medianprops=dict(color="white", linewidth=2.5),
                    whiskerprops=dict(linewidth=1.4),
                    capprops=dict(linewidth=1.4),
                    flierprops=dict(marker="o", ms=5, alpha=0.6))
for patch, clr in zip(bp["boxes"], box_colors):
    patch.set_facecolor(clr); patch.set_alpha(0.85)

ax_box.axhspan(0,  50,  color="#E8F8EE", alpha=0.45, zorder=0)
ax_box.axhspan(50, 100, color="#FFF8E7", alpha=0.45, zorder=0)
ax_box.axhline(50, color="#2ECC71", linewidth=1.3, linestyle="--")
ax_box.set_xticks([1, 2, 3])
ax_box.set_xticklabels(["Premonsoon", "Monsoon", "Postmonsoon"], fontsize=10)
ax_box.set_ylabel("WQI Value", fontsize=10)
ax_box.set_ylim(0, 100)
ax_box.set_title("WQI Distribution by Season\n(Original 15 Sites)", fontsize=11,
                 fontweight="bold", color="#0D2137")
ax_box.grid(axis="y", color="#CCDDEE", linewidth=0.6)
for s, clr, xp in zip(["Premonsoon", "Monsoon", "Postmonsoon"], box_colors, [1, 2, 3]):
    sd    = orig_wqi[orig_wqi["Season"] == s]["WQI"].dropna()
    mu    = sd.mean()
    ax_box.text(xp, mu + 1.5, f"μ={mu:.1f}", ha="center", va="bottom",
                fontsize=8.5, fontweight="bold", color="white",
                bbox=dict(fc=clr, ec="none", boxstyle="round,pad=0.2", alpha=0.85))

# ── Panel C: Pie chart (bottom-right) ────────────────────────────────────────
ax_pie = axes2[1, 1]
cat_counts = orig_wqi["WQI_Category"].value_counts()
cat_colors_map = {"Excellent": "#2ECC71", "Good": "#4A90D9"}
cats = [c for c in ["Excellent", "Good", "Poor", "Very Poor", "Unsuitable"]
        if c in cat_counts.index]
wedge_colors = [cat_colors_map.get(c, "#AAAAAA") for c in cats]
wedges, texts, autotexts = ax_pie.pie(
    [cat_counts[c] for c in cats],
    labels=cats, autopct="%1.1f%%",
    colors=wedge_colors, startangle=90,
    wedgeprops=dict(edgecolor="white", linewidth=2),
    textprops=dict(fontsize=11)
)
for at in autotexts:
    at.set_fontsize(11); at.set_fontweight("bold")
ax_pie.set_title("WQI Category Distribution\n(All 195 samples: Original + Synthetic)",
                 fontsize=11, fontweight="bold", color="#0D2137")

# Overall suptitle
fig2.suptitle(
    "Hydrochemical Water Quality Index (WQI) Analysis — Bhubaneswar, Odisha (2024)",
    fontsize=14, fontweight="bold", color="#0D2137", y=1.005
)

# Fix layout — remove the duplicate ax from gridspec
fig2.delaxes(axes2[0, 0])
fig2.delaxes(axes2[0, 1])

out_bar = FIGDIR / "fig_wqi_bar_original.png"
fig2.savefig(str(out_bar), dpi=200, bbox_inches="tight", facecolor=fig2.get_facecolor())
plt.close()
print(f"✓ WQI original-15 bar chart → {out_bar}")


# ── PART 1d — Bar chart: 150 Synthetic sites → fig_wqi_bar_synthetic.png ──────
syn_wqi = df_wqi[df_wqi["Location_ID"].str.startswith("SYN")].copy()

# --- Natural-sort helper ---
def _nsort(ids):
    def _key(s):
        parts = _re.split(r'(\d+)', s)
        return [int(p) if p.isdigit() else p for p in parts]
    return sorted(ids, key=_key)

SYN_PD_ORDER = _nsort([i for i in syn_wqi["Location_ID"].unique()
                        if not i.startswith("SYN-X")])
SYN_X_ORDER  = _nsort([i for i in syn_wqi["Location_ID"].unique()
                        if i.startswith("SYN-X")])

# Area labels for SYN-PD/IA/DY (strip 'SYN-' prefix then look up)
AREA_NAMES_SYN = {f"SYN-{k}": f"SYN-{k}\n({v.replace(chr(10),' ')})"
                  for k, v in AREA_NAMES.items()}

BAR_W_S = 0.24
OFFSETS_S = [-BAR_W_S, 0, BAR_W_S]
SEASON_CLR = {"Premonsoon": "#E07070", "Monsoon": "#4A90D9", "Postmonsoon": "#2ECC71"}

fig_syn = plt.figure(figsize=(26, 14))
fig_syn.patch.set_facecolor("#F4F7FC")

# ─ Panel A: SYN-PD/IA/DY ────────────────────────────────────────────────────
ax_a = fig_syn.add_subplot(2, 1, 1)
ax_a.set_facecolor("#F9FBFF")
ax_a.axhspan(0,  50,  color="#E8F8EE", alpha=0.55, zorder=0)
ax_a.axhspan(50, 100, color="#FFF8E7", alpha=0.55, zorder=0)
ax_a.axhline(50,  color="#2ECC71", lw=1.8, ls="--", zorder=2)
ax_a.axhline(100, color="#E07070", lw=1.8, ls="--", zorder=2)

# Zone separators for SYN matching original PD/IA/DY groups
for xv in [4.5, 9.5]:
    ax_a.axvline(xv, color="#AABBCC", lw=1.2, ls=":", zorder=2)
for xt, zlbl, zclr in [(2.0, "SYN — Population Density (PD)", "#1A6B3C"),
                        (7.0, "SYN — Industrial Areas (IA)",   "#1A3B6B"),
                        (12.0,"SYN — Dumping Yards (DY)",      "#6B1A1A")]:
    ax_a.text(xt, 102.5, zlbl, ha="center", va="bottom",
              fontsize=9.5, fontweight="bold", color=zclr)

xpos_a = np.arange(len(SYN_PD_ORDER))
for i, (season, clr) in enumerate(SEASON_CLR.items()):
    vals = []
    for loc in SYN_PD_ORDER:
        row = syn_wqi[(syn_wqi["Location_ID"] == loc) &
                      (syn_wqi["Season"] == season)]
        vals.append(row["WQI"].values[0] if len(row) else np.nan)
    bars = ax_a.bar(xpos_a + OFFSETS_S[i], vals, width=BAR_W_S,
                    label=season, color=clr, edgecolor="white",
                    linewidth=0.7, zorder=3, alpha=0.90)
    for bar, val in zip(bars, vals):
        if not np.isnan(val):
            ax_a.text(bar.get_x() + bar.get_width()/2, val + 0.8,
                      f"{val:.1f}", ha="center", va="bottom",
                      fontsize=7.0, color="#333", rotation=90, fontweight="bold")

ax_a.set_xticks(xpos_a)
ax_a.set_xticklabels(
    [f"{loc}\n({AREA_NAMES.get(loc.replace('SYN-',''), loc)})"
     .replace('\n(','  ').replace(')','') for loc in SYN_PD_ORDER],
    fontsize=8.0
)
ax_a.set_yticks(range(0, 101, 10))
ax_a.set_ylim(0, 109)
ax_a.set_xlim(-0.55, len(SYN_PD_ORDER) - 0.45)
ax_a.set_ylabel("WQI Value", fontsize=11, fontweight="bold")
ax_a.set_title(
    "Synthetic Locations — SYN-PD / SYN-IA / SYN-DY  (15 locations × 3 seasons = 45 samples)\n"
    "Mirroring original 15 sites with CMGP ±6% mean jitter + 8% noise",
    fontsize=11, fontweight="bold", color="#0D2137", pad=6
)
ax_a.legend(fontsize=10, loc="upper right", framealpha=0.9, title="Season")
ax_a.grid(axis="y", color="#CCDDEE", lw=0.6, zorder=1)

# Category annotations
ax_a.text(len(SYN_PD_ORDER)-0.1, 25, "Excellent (WQI < 50)",
          ha="right", va="center", fontsize=9, color="#1A7A40", fontweight="bold",
          bbox=dict(fc="#E8F8EE", ec="#2ECC71", boxstyle="round,pad=0.3", alpha=0.85))
ax_a.text(len(SYN_PD_ORDER)-0.1, 73, "Good (WQI 50–100)",
          ha="right", va="center", fontsize=9, color="#7B4F00", fontweight="bold",
          bbox=dict(fc="#FFF8E7", ec="#F39C12", boxstyle="round,pad=0.3", alpha=0.85))

# ─ Panel B: SYN-X1 to SYN-X35 ───────────────────────────────────────────────
ax_b = fig_syn.add_subplot(2, 1, 2)
ax_b.set_facecolor("#F9FBFF")
ax_b.axhspan(0,  50,  color="#E8F8EE", alpha=0.55, zorder=0)
ax_b.axhspan(50, 100, color="#FFF8E7", alpha=0.55, zorder=0)
ax_b.axhline(50,  color="#2ECC71", lw=1.8, ls="--", zorder=2)
ax_b.axhline(100, color="#E07070", lw=1.8, ls="--", zorder=2)

xpos_b = np.arange(len(SYN_X_ORDER))
BAR_W_X = 0.26
OFFSETS_X = [-BAR_W_X, 0, BAR_W_X]

for i, (season, clr) in enumerate(SEASON_CLR.items()):
    vals = []
    for loc in SYN_X_ORDER:
        row = syn_wqi[(syn_wqi["Location_ID"] == loc) &
                      (syn_wqi["Season"] == season)]
        vals.append(row["WQI"].values[0] if len(row) else np.nan)
    bars = ax_b.bar(xpos_b + OFFSETS_X[i], vals, width=BAR_W_X,
                    label=season, color=clr, edgecolor="white",
                    linewidth=0.5, zorder=3, alpha=0.90)
    for bar, val in zip(bars, vals):
        if not np.isnan(val):
            ax_b.text(bar.get_x() + bar.get_width()/2, val + 0.5,
                      f"{val:.0f}", ha="center", va="bottom",
                      fontsize=5.5, color="#333", rotation=90)

# Look up nearest locality for each SYN-X for x-tick label
synx_name_map = {}
if (DATA / "syn_x_location_names.csv").exists():
    _nl = pd.read_csv(DATA / "syn_x_location_names.csv")
    synx_name_map = dict(zip(_nl["Location_ID"], _nl["Nearest_Locality"]))

ax_b.set_xticks(xpos_b)
ax_b.set_xticklabels(
    [f"{loc}\n{synx_name_map.get(loc, '')}" for loc in SYN_X_ORDER],
    fontsize=7.2, rotation=0
)
ax_b.set_yticks(range(0, 101, 10))
ax_b.set_ylim(0, 109)
ax_b.set_xlim(-0.6, len(SYN_X_ORDER) - 0.4)
ax_b.set_ylabel("WQI Value", fontsize=11, fontweight="bold")
ax_b.set_title(
    "Synthetic Extra Locations — SYN-X1 to SYN-X35  (35 locations × 3 seasons = 105 samples)\n"
    "Randomly placed within ±0.05° of study area centroid via CMGP; "
    "nearest Bhubaneswar locality shown on X-axis",
    fontsize=11, fontweight="bold", color="#0D2137", pad=6
)
ax_b.legend(fontsize=10, loc="upper right", framealpha=0.9, title="Season")
ax_b.grid(axis="y", color="#CCDDEE", lw=0.6, zorder=1)
ax_b.text(len(SYN_X_ORDER)-0.1, 25, "Excellent (WQI < 50)",
          ha="right", va="center", fontsize=9, color="#1A7A40", fontweight="bold",
          bbox=dict(fc="#E8F8EE", ec="#2ECC71", boxstyle="round,pad=0.3", alpha=0.85))
ax_b.text(len(SYN_X_ORDER)-0.1, 73, "Good (WQI 50–100)",
          ha="right", va="center", fontsize=9, color="#7B4F00", fontweight="bold",
          bbox=dict(fc="#FFF8E7", ec="#F39C12", boxstyle="round,pad=0.3", alpha=0.85))

fig_syn.suptitle(
    "Water Quality Index (WQI) — All 150 Synthetic Samples\n"
    "Bhubaneswar, Odisha (2024)  ·  CMGP Augmentation  ·  IS 10500:2012  ·  Brown et al. (1970)",
    fontsize=13, fontweight="bold", color="#0D2137", y=1.01
)
fig_syn.tight_layout(h_pad=3.5)
out_syn = FIGDIR / "fig_wqi_bar_synthetic.png"
fig_syn.savefig(str(out_syn), dpi=200, bbox_inches="tight",
                facecolor=fig_syn.get_facecolor())
plt.close()
print(f"✓ WQI synthetic bar chart    → {out_syn}")


# ── PART 2 — Name SYN-X locations ─────────────────────────────────────────────
synx_df = (df_comb[df_comb["Location_ID"].str.startswith("SYN-X")]
           [["Location_ID", "Latitude", "Longitude", "Season"]]
           .copy())

# Use one canonical coordinate per SYN-X (mean across seasons)
synx_mean = (synx_df.groupby("Location_ID")[["Latitude", "Longitude"]]
                    .mean().reset_index())

synx_mean["Nearest_Locality"]      = synx_mean.apply(
    lambda r: nearest_locality(r["Latitude"], r["Longitude"])[0], axis=1)
synx_mean["Distance_km"]           = synx_mean.apply(
    lambda r: nearest_locality(r["Latitude"], r["Longitude"])[1], axis=1)

# Natural sort
import re
synx_mean["_sort"] = synx_mean["Location_ID"].apply(
    lambda x: int(re.search(r"\d+", x).group()))
synx_mean = synx_mean.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)
synx_mean.index += 1  # 1-based

out_csv = DATA / "syn_x_location_names.csv"
synx_mean.to_csv(str(out_csv), index=False)

print(f"\n✓ SYN-X location names saved → {out_csv}")
print(f"\n{'─'*75}")
print(f"  {'ID':<10} {'Mean Lat':>10} {'Mean Lon':>10}  {'Nearest Locality':<40} {'km':>6}")
print(f"{'─'*75}")
for _, row in synx_mean.iterrows():
    print(f"  {row['Location_ID']:<10} {row['Latitude']:>10.5f} {row['Longitude']:>10.5f}  "
          f"{row['Nearest_Locality']:<40} {row['Distance_km']:>6.3f}")
print(f"{'─'*75}")
print(f"\nNote: 'Distance_km' = Haversine distance to nearest named locality.")
print( "      SYN-X coordinates are jittered ±0.05° per season — mean used above.")
