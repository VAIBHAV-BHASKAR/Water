"use strict";
/**
 * make_report.js
 * Generates Project_Report_Lakshya_Nayyar_Vaibhav_Bhaskar.docx
 * KIIT School of Computer Engineering format
 * Node.js + docx v9.x
 */

const fs   = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, PageBreak, ImageRun, BorderStyle,
  WidthType, TableLayoutType, Header, Footer, TextDirection,
  PageNumber, NumberFormat, SectionType, VerticalAlign,
  convertInchesToTwip, LineRuleType, UnderlineType, ShadingType,
  LevelFormat, TabStopType, TabStopPosition, Tab,
} = require("docx");

// ── Constants ──────────────────────────────────────────────────────────────
const ROOT  = __dirname;
const OUT   = path.join(ROOT, "Project_Report_Lakshya_Nayyar_Vaibhav_Bhaskar.docx");

// KIIT A4 page geometry (DXA = twentieths of a point)
const PAGE_W  = 11906;
const PAGE_H  = 16838;
const MAR_T   = 1440;  // 1 inch
const MAR_B   = 1440;
const MAR_L   = 1800;  // 1.25 inch
const MAR_R   = 1440;
const CONTENT_W = PAGE_W - MAR_L - MAR_R; // 8666 DXA ≈ 6.02 in

// Typography
const FONT    = "Times New Roman";
const SZ_BODY = 24;   // 12pt (half-points)
const SZ_H1   = 28;   // 14pt
const SZ_H2   = 24;   // 12pt
const SZ_COVER_TITLE = 36; // 18pt
const SZ_COVER_BODY  = 28; // 14pt
const COLOR_HEADER_ROW = "D9D9D9";
const COLOR_ALT_ROW    = "F2F2F2";

// ── Helpers ────────────────────────────────────────────────────────────────
function safeImage(relPath, widthPx, heightPx) {
  const fullPath = path.join(ROOT, relPath);
  if (!fs.existsSync(fullPath)) {
    console.warn("  [MISSING] " + fullPath);
    return new Paragraph({
      children: [new TextRun({ text: "[Figure not found: " + relPath + "]", italics: true, size: SZ_BODY, font: FONT })],
      alignment: AlignmentType.CENTER,
    });
  }
  const data = fs.readFileSync(fullPath);
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [
      new ImageRun({
        data,
        transformation: { width: widthPx, height: heightPx },
        type: "png",
      }),
    ],
    spacing: { after: 80 },
  });
}

function figCaption(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [new TextRun({ text, italics: true, size: SZ_BODY - 2, font: FONT })],
  });
}

function body(text, opts = {}) {
  return new Paragraph({
    alignment: opts.center ? AlignmentType.CENTER : AlignmentType.JUSTIFIED,
    spacing: { line: 360, lineRule: LineRuleType.AUTO, after: opts.after ?? 160 },
    indent: opts.indent ? { firstLine: 360 } : undefined,
    children: [new TextRun({
      text,
      size: SZ_BODY,
      font: FONT,
      bold: opts.bold ?? false,
      italics: opts.italic ?? false,
    })],
  });
}

function bullet(text, level = 0) {
  return new Paragraph({
    bullet: { level },
    spacing: { line: 360, lineRule: LineRuleType.AUTO, after: 80 },
    children: [new TextRun({ text, size: SZ_BODY, font: FONT })],
  });
}

function chapterHeading(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 240 },
    children: [new TextRun({ text, bold: true, size: SZ_H1, font: FONT, allCaps: true })],
  });
}

function sectionHeading(text) {
  return new Paragraph({
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, bold: true, size: SZ_H2, font: FONT })],
  });
}

function subHeading(text) {
  return new Paragraph({
    spacing: { before: 160, after: 80 },
    children: [new TextRun({ text, bold: true, italics: true, size: SZ_BODY, font: FONT })],
  });
}

function emptyLine(n = 1) {
  const paras = [];
  for (let i = 0; i < n; i++) {
    paras.push(new Paragraph({ spacing: { after: 0, line: 360 }, children: [] }));
  }
  return paras;
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function centeredBold(text, size = SZ_BODY) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 160 },
    children: [new TextRun({ text, bold: true, size, font: FONT })],
  });
}

function centeredText(text, size = SZ_BODY, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: opts.after ?? 160 },
    children: [new TextRun({ text, size, font: FONT, bold: opts.bold, italics: opts.italic })],
  });
}

// Simple single-row table cell helper
function cell(text, opts = {}) {
  return new TableCell({
    shading: opts.shade ? { fill: opts.shade, type: ShadingType.SOLID } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    width: opts.width ? { size: opts.width, type: WidthType.DXA } : undefined,
    children: [new Paragraph({
      alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
      spacing: { after: 60, before: 60 },
      children: [new TextRun({ text: String(text), size: SZ_BODY - 2, font: FONT, bold: opts.bold ?? false })],
    })],
  });
}

function makeTable(headers, rows, colWidths) {
  const totalCols = headers.length;
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) =>
      cell(h, { shade: COLOR_HEADER_ROW, bold: true, center: true, width: colWidths ? colWidths[i] : undefined })
    ),
  });
  const dataRows = rows.map((row, ri) =>
    new TableRow({
      children: row.map((d, i) =>
        cell(d, { shade: ri % 2 === 1 ? COLOR_ALT_ROW : "FFFFFF", center: i > 0, width: colWidths ? colWidths[i] : undefined })
      ),
    })
  );
  // Compute columnWidths for tblGrid (critical for WPS/Word rendering)
  const gridWidths = colWidths
    ? colWidths
    : Array(totalCols).fill(Math.floor(CONTENT_W / totalCols));
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    layout: TableLayoutType.FIXED,
    columnWidths: gridWidths,
    rows: [headerRow, ...dataRows],
  });
}

// ── Running header/footer builders ─────────────────────────────────────────
function makeHeader(title) {
  return new Header({
    children: [
      new Paragraph({
        alignment: AlignmentType.LEFT,
        border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "000000", space: 6 } },
        children: [new TextRun({ text: title, italics: true, size: SZ_BODY - 2, font: FONT, color: "444444" })],
      }),
    ],
  });
}

function makeFooter(pageNumFmt) {
  return new Footer({
    children: [
      new Paragraph({
        border: { top: { style: BorderStyle.SINGLE, size: 6, color: "000000", space: 6 } },
        children: [
          new TextRun({ text: "School of Computer Engineering, KIIT, Bhubaneswar", size: SZ_BODY - 2, font: FONT }),
          new TextRun({ children: [new Tab()], size: SZ_BODY - 2, font: FONT }),
          new TextRun({
            children: [PageNumber.CURRENT],
            size: SZ_BODY - 2,
            font: FONT,
          }),
        ],
        tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }],
      }),
    ],
  });
}

// ── Section geometry helper ────────────────────────────────────────────────
function sectionProps(opts = {}) {
  return {
    properties: {
      type: opts.type ?? SectionType.NEXT_PAGE,
      page: {
        size: { width: PAGE_W, height: PAGE_H },
        margin: { top: MAR_T, bottom: MAR_B, left: MAR_L, right: MAR_R, header: 720, footer: 720 },
        pageNumbers: opts.pageNumbers ?? undefined,
      },
    },
    headers: opts.header ? { default: opts.header } : undefined,
    footers: opts.footer ? { default: opts.footer } : undefined,
  };
}

// ══════════════════════════════════════════════════════════════════════════
//  SECTION 1 — COVER PAGES (no page numbers)
// ══════════════════════════════════════════════════════════════════════════
function buildCoverSection() {
  // ── Cover Page 1: Outer Cover ──────────────────────────────────────────
  const cover1 = [
    ...emptyLine(2),
    centeredText("KIIT UNIVERSITY", SZ_COVER_TITLE, { bold: true }),
    centeredText("(Deemed to be University u/s 3 of UGC Act, 1956)", SZ_BODY, { italic: true, after: 80 }),
    centeredText("School of Computer Engineering", SZ_COVER_BODY, { bold: true }),
    ...emptyLine(2),
    centeredText("Mini Project Report", SZ_BODY, { italic: true }),
    ...emptyLine(1),
    centeredText(
      "HYDROCHEMICAL ANALYSIS AND MACHINE LEARNING-BASED PREDICTION OF GROUNDWATER QUALITY IN BHUBANESWAR, ODISHA",
      SZ_COVER_TITLE, { bold: true, after: 240 }
    ),
    ...emptyLine(2),
    centeredText("Submitted by", SZ_BODY, { italic: true }),
    ...emptyLine(1),
    centeredBold("Vaibhav Bhaskar", SZ_COVER_BODY),
    centeredText("Roll No.: 23053173", SZ_BODY),
    ...emptyLine(1),
    centeredBold("Lakshya Nayyar", SZ_COVER_BODY),
    centeredText("Roll No.: 23053133", SZ_BODY),
    ...emptyLine(2),
    centeredText("Under the guidance of", SZ_BODY, { italic: true }),
    ...emptyLine(1),
    centeredBold("Dr. Ajit Kumar Pasayat", SZ_COVER_BODY),
    centeredText("Associate Professor, School of Computer Engineering", SZ_BODY),
    centeredText("KIIT University, Bhubaneswar, Odisha – 751024", SZ_BODY),
    ...emptyLine(2),
    centeredText("Academic Year 2024–25", SZ_BODY, { bold: true }),
    pageBreak(),
  ];

  // ── Cover Page 2: Inner Title Page ────────────────────────────────────
  const cover2 = [
    ...emptyLine(2),
    centeredBold("KIIT UNIVERSITY", SZ_COVER_TITLE),
    centeredText("School of Computer Engineering", SZ_COVER_BODY, { bold: true }),
    centeredText("Bhubaneswar, Odisha – 751024", SZ_BODY, { after: 80 }),
    centeredText("(Deemed to be University u/s 3 of UGC Act, 1956)", SZ_BODY, { italic: true }),
    ...emptyLine(2),
    centeredText("MINI PROJECT REPORT", SZ_COVER_BODY, { bold: true }),
    ...emptyLine(1),
    centeredText(
      "ON",
      SZ_BODY, { italic: true }
    ),
    ...emptyLine(1),
    centeredBold(
      "HYDROCHEMICAL ANALYSIS AND MACHINE LEARNING-BASED PREDICTION OF GROUNDWATER QUALITY IN BHUBANESWAR, ODISHA",
      SZ_COVER_TITLE
    ),
    ...emptyLine(3),
    makeTable(
      ["Student Name", "Roll Number", "School"],
      [
        ["Vaibhav Bhaskar", "23053173", "School of Computer Engineering"],
        ["Lakshya Nayyar",  "23053133", "School of Computer Engineering"],
      ],
      [3200, 2000, 3466]
    ),
    ...emptyLine(2),
    centeredText("Supervisor", SZ_BODY, { italic: true }),
    centeredBold("Dr. Ajit Kumar Pasayat", SZ_COVER_BODY),
    centeredText("Associate Professor", SZ_BODY),
    centeredText("School of Computer Engineering, KIIT University", SZ_BODY),
    ...emptyLine(1),
    centeredText("Session: 2024–25", SZ_BODY, { bold: true }),
  ];

  return {
    children: [...cover1, ...cover2],
    ...sectionProps({ type: SectionType.NEXT_PAGE }),
  };
}

// ══════════════════════════════════════════════════════════════════════════
//  SECTION 2 — CERTIFICATE
// ══════════════════════════════════════════════════════════════════════════
function buildCertificateSection() {

  const children = [
    chapterHeading("CERTIFICATE"),
    ...emptyLine(1),
    body(
      'This is to certify that the mini project entitled \u201cHydrochemical Analysis and Machine Learning-Based Prediction of Groundwater Quality in Bhubaneswar, Odisha\u201d has been carried out by ' +
      'Vaibhav Bhaskar (Roll No. 23053173) and Lakshya Nayyar (Roll No. 23053133) under my supervision, in partial fulfilment of the requirements for the award of the degree of Bachelor of Technology ' +
      'in Computer Science and Engineering from KIIT University, Bhubaneswar.',
      { indent: true }
    ),
    ...emptyLine(1),
    body(
      "To the best of my knowledge, the work presented in this report is original and has not been submitted elsewhere for any other degree or diploma.",
      { indent: true }
    ),
    ...emptyLine(4),
    new Paragraph({
      children: [
        new TextRun({ text: "Dr. Ajit Kumar Pasayat", bold: true, size: SZ_BODY, font: FONT }),
      ],
    }),
    body("Associate Professor"),
    body("School of Computer Engineering"),
    body("KIIT University, Bhubaneswar – 751024"),
    ...emptyLine(1),
    body("Date: _______________"),
    ...emptyLine(2),
    body("Place: Bhubaneswar, Odisha"),
  ];

  return {
    children,
    ...sectionProps({ type: SectionType.NEXT_PAGE }),
  };
}

// ══════════════════════════════════════════════════════════════════════════
//  SECTION 3 — PRELIMS (Roman numerals: i, ii, iii, …)
//     Acknowledgements | Abstract | TOC | List of Figures | Abbreviations
// ══════════════════════════════════════════════════════════════════════════
function buildPrelimsSection() {
  const hdr = makeHeader("Groundwater Quality Analysis — Bhubaneswar 2024");
  const ftr = makeFooter(NumberFormat.LOWER_ROMAN);

  // ── Acknowledgements ──────────────────────────────────────────────────
  const ack = [
    chapterHeading("ACKNOWLEDGEMENTS"),
    body(
      "We would like to express our sincere and profound gratitude to Dr. Ajit Kumar Pasayat, Associate Professor, School of Computer Engineering, KIIT University, for his invaluable guidance, " +
      "unwavering support, and constructive feedback throughout the course of this mini-project. His constant encouragement and insightful suggestions have been instrumental in shaping this work.",
      { indent: true }
    ),
    body(
      "We extend our heartfelt thanks to the faculty and staff of the School of Computer Engineering, KIIT University, for providing the necessary infrastructure and resources. " +
      "We are grateful to the Bhubaneswar Municipal Corporation (BMC) and local stakeholders for facilitating access to groundwater sampling sites across Bhubaneswar city.",
      { indent: true }
    ),
    body(
      "We sincerely thank our family and friends for their moral support and motivation throughout this journey. Any shortcomings that remain in this report are entirely our own.",
      { indent: true }
    ),
    ...emptyLine(4),
    new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: "Vaibhav Bhaskar (23053173)", size: SZ_BODY, font: FONT })],
    }),
    new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: "Lakshya Nayyar (23053133)", size: SZ_BODY, font: FONT })],
    }),
    pageBreak(),
  ];

  // ── Abstract ──────────────────────────────────────────────────────────
  const abs = [
    chapterHeading("ABSTRACT"),
    body(
      "Access to safe groundwater is a critical public health priority in rapidly urbanising regions of India. The present study investigates the hydrochemical status and machine learning-based prediction of groundwater quality in Bhubaneswar, Odisha, utilising samples collected from 15 monitoring sites spanning three land-use categories — Population Density (PD), Industrial Area (IA), and Dumping Yard (DY) zones — across three hydrological seasons: Premonsoon (April–May 2024), Monsoon (July–August 2024), and Postmonsoon (October–November 2024).",
      { indent: true }
    ),
    body(
      "A total of 45 original hydrochemical observations (15 sites × 3 seasons) were collected, covering 16 physicochemical parameters: pH, Electrical Conductivity (EC), Total Dissolved Solids (TDS), Total Hardness (TH), Alkalinity, Calcium (Ca), Magnesium (Mg), Sodium (Na), Potassium (K), Iron, Bicarbonate (HCO₃), Chloride (Cl), Sulphate (SO₄), Nitrate (NO₃), Fluoride (F), and Dissolved Oxygen (DO). To overcome the small-sample constraint limiting robust statistical and machine learning analysis, the original dataset was augmented to 195 samples (45 original + 150 synthetic) using a novel Controlled Multivariate Gaussian Perturbation (CMGP) framework incorporating 5-layer noise injection. Statistical validation confirmed the augmented dataset is statistically consistent with the original (PASS; average KS overlap 67.0%, Cohen's d 0.077, correlation preservation 92.6%).",
      { indent: true }
    ),
    body(
      "Seasonal analysis revealed pronounced hydrochemical variability (all 16 parameters statistically significant, p < 0.05), with monsoon recharge causing dramatic ionic enrichment — particularly Total Hardness (+497%), Sodium (+101%), and Potassium (+122%). IS 10500:2012 compliance assessment identified pH as the most critical concern (75.4% non-compliant), followed by Iron (45.1% non-compliant). At the sample level, 91.1% of the original samples were classified as UNSAFE for drinking. The Water Quality Index (WQI, Brown et al. 1970) ranged from 30.81 to 77.04 (mean 51.82 ± 8.92), with all 195 samples falling in the Excellent or Good categories, indicating the aquifer system is not severely degraded despite individual parameter exceedances.",
      { indent: true }
    ),
    body(
      "Hydrogeochemical source apportionment using Principal Component Analysis (6 PCs, 73.15% cumulative variance), Piper trilinear diagrams, Gibbs plots, ionic ratio analysis, and K-Means clustering (K = 3, elbow method) revealed that rock-water interaction is the dominant process across all seasons. PC1 (29.29% variance) represents a mineralization axis driven by EC, TDS, and Ca, while PC4 (8.23%) captures redox/laterite dissolution through Iron loading. Piper diagrams show Ca-Cl as the dominant monsoon facies and Na-K-SO₄ in premonsoon, reflecting silicate weathering and dry-season evaporative concentration.",
      { indent: true }
    ),
    body(
      "Machine learning models (Random Forest, Gradient Boosting, Support Vector Regression, Neural Network, XGBoost) were trained to predict TDS, EC, and WQI. Random Forest achieved the best performance for TDS (Test R² = 0.7637, RMSE = 49.3 mg/L) and EC (Test R² = 0.7570, RMSE = 67.6 µS/cm), while a Neural Network (128-64-32 architecture) best predicted WQI (CV R² = 0.9447, Test R² = 0.9364, RMSE = 2.1). SHAP analysis identified Ca and Na as the top drivers of TDS and EC prediction, and EC as the dominant WQI predictor.",
      { indent: true }
    ),
    body(
      "The findings indicate that while the groundwater system is broadly within tolerable limits for most constituents, immediate interventions are warranted to address pH acidity and iron contamination, particularly in industrial and dumping yard zones during the monsoon season. The CMGP augmentation methodology and ML pipeline developed in this study provide a replicable framework for hydrochemical analysis in data-scarce environments.",
      { indent: true }
    ),
    new Paragraph({
      spacing: { before: 160, after: 80 },
      children: [new TextRun({ text: "Keywords: ", bold: true, size: SZ_BODY, font: FONT }), new TextRun({ text: "groundwater quality, hydrochemical analysis, IS 10500:2012, Water Quality Index, machine learning, SHAP, Bhubaneswar, data augmentation, CMGP, PCA, K-Means, random forest, neural network", italics: true, size: SZ_BODY, font: FONT })],
    }),
    pageBreak(),
  ];

  // ── Table of Contents ─────────────────────────────────────────────────
  const toc = [
    chapterHeading("TABLE OF CONTENTS"),
    makeTable(
      ["Section", "Title", "Page"],
      [
        ["", "Certificate", "ii"],
        ["", "Acknowledgements", "iii"],
        ["", "Abstract", "iv"],
        ["", "Table of Contents", "v"],
        ["", "List of Figures", "vi"],
        ["", "List of Tables", "vii"],
        ["", "List of Abbreviations", "viii"],
        ["Chapter 1", "Introduction", "1"],
        ["1.1", "Background and Motivation", "1"],
        ["1.2", "Study Area", "2"],
        ["1.3", "Objectives", "3"],
        ["1.4", "Scope and Significance", "3"],
        ["Chapter 2", "Literature Review", "5"],
        ["2.1", "Hydrochemical Studies in Urban India", "5"],
        ["2.2", "IS 10500:2012 and WQI Methods", "6"],
        ["2.3", "Machine Learning in Water Quality", "6"],
        ["2.4", "Data Augmentation in Environmental Sciences", "7"],
        ["Chapter 3", "Materials and Methods", "8"],
        ["3.1", "Sampling Design", "8"],
        ["3.2", "Analytical Methods", "9"],
        ["3.3", "Data Augmentation (CMGP)", "9"],
        ["3.4", "Water Quality Index", "10"],
        ["3.5", "IS 10500:2012 Compliance", "11"],
        ["3.6", "Source Apportionment", "11"],
        ["3.7", "Machine Learning Pipeline", "12"],
        ["Chapter 4", "Results and Discussion", "13"],
        ["4.1", "Data Validation", "13"],
        ["4.2", "Seasonal Hydrochemistry", "14"],
        ["4.3", "IS 10500 Compliance and WQI", "16"],
        ["4.4", "Source Apportionment", "18"],
        ["4.5", "Machine Learning Results", "22"],
        ["Chapter 5", "Integrated Discussion", "26"],
        ["Chapter 6", "Conclusions and Recommendations", "28"],
        ["", "References", "30"],
        ["", "Individual Contribution", "34"],
        ["", "Plagiarism Declaration", "35"],
      ],
      [1600, 5266, 1800]
    ),
    pageBreak(),
  ];

  // ── List of Figures ───────────────────────────────────────────────────
  const lof = [
    chapterHeading("LIST OF FIGURES"),
    makeTable(
      ["Figure No.", "Caption", "Page"],
      [
        ["1.1",  "Map of 15 groundwater sampling sites across Bhubaneswar", "2"],
        ["2.1",  "Original vs. Synthetic sample distributions (16 parameters)", "13"],
        ["2.2",  "Missing value heatmaps — original and combined datasets", "13"],
        ["2.3",  "Synthetic data statistical defense summary", "14"],
        ["2.4",  "Correlation preservation scatter plots (original vs. augmented)", "14"],
        ["3.1",  "Seasonal hydrochemical distributions — violin plots (16 params)", "15"],
        ["3.2",  "Seasonal trend lines for key parameters", "15"],
        ["3.3",  "Seasonal boxplots — EC, TDS, TH, Na, K", "15"],
        ["3.4",  "Seasonal heatmap — mean concentrations", "15"],
        ["3.5",  "Pairplot — hydrochemical parameter inter-relationships (publication)", "16"],
        ["3.6",  "Correlation matrix — 16 parameters (combined dataset)", "16"],
        ["4.1",  "IS 10500:2012 compliance bar chart — all 16 parameters", "17"],
        ["4.2",  "IS 10500:2012 compliance heatmap (sample × parameter)", "17"],
        ["4.3",  "Exceedance factor heat map", "17"],
        ["4.4",  "WQI analysis — distribution, boxplot, and pie chart", "18"],
        ["5.1",  "Hierarchical clustering dendrogram (Ward's method)", "19"],
        ["5.2",  "Elbow method — optimal K for K-Means clustering", "19"],
        ["5.3",  "K-Means (K=3) clusters in PCA score space", "19"],
        ["5.4",  "PCA scree plot and cumulative variance", "20"],
        ["5.5",  "PCA loadings heatmap (PC1–PC4)", "20"],
        ["5.6",  "PCA biplot — variable loadings & sample scores", "20"],
        ["5.7",  "Piper trilinear diagram — seasonal hydrochemical facies", "21"],
        ["5.8",  "Gibbs diagram — mechanism of mineralization", "21"],
        ["5.9",  "Ionic ratio plots (Na/Cl, Ca/Mg, Ca+Mg vs. HCO₃+SO₄)", "21"],
        ["6.1",  "Actual vs. Predicted — TDS (Random Forest)", "22"],
        ["6.2",  "Actual vs. Predicted — EC (Random Forest)", "23"],
        ["6.3",  "Actual vs. Predicted — WQI (Neural Network)", "23"],
        ["6.4",  "Residuals plot — TDS", "24"],
        ["6.5",  "Residuals plot — EC", "24"],
        ["6.6",  "Residuals plot — WQI", "24"],
        ["6.7",  "SHAP summary plot — TDS (Random Forest)", "25"],
        ["6.8",  "SHAP summary plot — EC (Random Forest)", "25"],
        ["6.9",  "SHAP summary plot — WQI (Neural Network)", "25"],
        ["7.1",  "Seasonal radar chart — parameter-level deviations", "26"],
      ],
      [1400, 5466, 1800]
    ),
    pageBreak(),
  ];

  // ── List of Tables ────────────────────────────────────────────────────
  const lot = [
    chapterHeading("LIST OF TABLES"),
    makeTable(
      ["Table No.", "Caption", "Page"],
      [
        ["1.1", "Description of 15 groundwater sampling sites", "2"],
        ["3.1", "IS 10500:2012 permissible limits for 16 parameters", "11"],
        ["3.2", "WQI weights and parameter groups (Brown et al., 1970)", "10"],
        ["4.1", "Descriptive statistics of original 45 samples (mean ± sd)", "13"],
        ["4.2", "CMGP augmentation validation metrics", "14"],
        ["4.3", "Seasonal mean concentrations — 16 parameters", "15"],
        ["4.4", "Statistical significance of seasonal variation (ANOVA/KW)", "16"],
        ["4.5", "IS 10500:2012 compliance summary (% of 195 samples)", "17"],
        ["4.6", "WQI classification by season", "18"],
        ["4.7", "PCA — variance explained by component", "20"],
        ["4.8", "K-Means cluster means (K=3)", "20"],
        ["4.9", "Machine learning model performance metrics", "23"],
        ["4.10","SHAP top-3 feature importances per target", "25"],
      ],
      [1400, 5466, 1800]
    ),
    pageBreak(),
  ];

  // ── List of Abbreviations ─────────────────────────────────────────────
  const abbrev = [
    chapterHeading("LIST OF ABBREVIATIONS"),
    makeTable(
      ["Abbreviation", "Full Form"],
      [
        ["ANOVA",    "Analysis of Variance"],
        ["BMC",      "Bhubaneswar Municipal Corporation"],
        ["Ca",       "Calcium"],
        ["CAI",      "Chloro-Alkaline Index"],
        ["CBE",      "Charge Balance Error"],
        ["Cl",       "Chloride"],
        ["CMGP",     "Controlled Multivariate Gaussian Perturbation"],
        ["CV",       "Cross-Validation"],
        ["DO",       "Dissolved Oxygen"],
        ["DY",       "Dumping Yard (Zone)"],
        ["EC",       "Electrical Conductivity"],
        ["F",        "Fluoride"],
        ["GB",       "Gradient Boosting"],
        ["HCO₃",    "Bicarbonate"],
        ["IA",       "Industrial Area (Zone)"],
        ["IS",       "Indian Standard"],
        ["K",        "Potassium"],
        ["K-W",      "Kruskal-Wallis Test"],
        ["MAE",      "Mean Absolute Error"],
        ["MAPE",     "Mean Absolute Percentage Error"],
        ["Mg",       "Magnesium"],
        ["ML",       "Machine Learning"],
        ["MVN",      "Multivariate Normal Distribution"],
        ["Na",       "Sodium"],
        ["NN",       "Neural Network (MLP Regressor)"],
        ["NO₃",     "Nitrate"],
        ["NSE",      "Nash-Sutcliffe Efficiency"],
        ["PC",       "Principal Component"],
        ["PCA",      "Principal Component Analysis"],
        ["PD",       "Population Density (Zone)"],
        ["PD-1…DY-5","Site notation: Zone-SiteID"],
        ["RF",       "Random Forest"],
        ["RMSE",     "Root Mean Square Error"],
        ["RSR",      "RMSE-Observation Standard Deviation Ratio"],
        ["SHAP",     "SHapley Additive exPlanations"],
        ["SO₄",     "Sulphate"],
        ["SVR",      "Support Vector Regression"],
        ["TDS",      "Total Dissolved Solids"],
        ["TH",       "Total Hardness"],
        ["WQI",      "Water Quality Index"],
        ["XGB",      "Extreme Gradient Boosting (XGBoost)"],
      ],
      [2200, 6466]
    ),
  ];

  return {
    children: [...ack, ...abs, ...toc, ...lof, ...lot, ...abbrev],
    ...sectionProps({
      type: SectionType.NEXT_PAGE,
      header: hdr,
      footer: ftr,
      pageNumbers: { start: 1, formatType: NumberFormat.LOWER_ROMAN },
    }),
  };
}

// ══════════════════════════════════════════════════════════════════════════
//  SECTION 4 — CHAPTERS (Arabic page numbers starting at 1)
// ══════════════════════════════════════════════════════════════════════════
function buildChaptersSection() {
  const hdr = makeHeader("Groundwater Quality Analysis — Bhubaneswar 2024");
  const ftr = makeFooter(NumberFormat.DECIMAL);
  const children = [];

  // ════════════════════════════════════════════
  //  CHAPTER 1 — INTRODUCTION
  // ════════════════════════════════════════════
  children.push(chapterHeading("CHAPTER 1: INTRODUCTION"));

  children.push(sectionHeading("1.1  Background and Motivation"));
  children.push(body(
    "Groundwater constitutes approximately 30% of global freshwater resources and serves as the primary source of potable water for more than 60% of India's rural population and a significant fraction of urban demand. The rapid urbanisation of secondary Indian cities, including Bhubaneswar — the capital of Odisha and a fast-growing Smart City — has placed acute pressure on shallow aquifer systems through increased abstraction, land-use change, industrial effluent infiltration, and improper solid-waste disposal.",
    { indent: true }
  ));
  children.push(body(
    "Bhubaneswar presents a hydrogeologically complex setting characterised by lateritic over-burden, weathered Archaean basement, and alluvial fills in low-lying areas. The orographic rainfall pattern of Odisha (annual precipitation ~1500 mm, ~80% during June–September monsoon) drives pronounced seasonal recharge–discharge cycles that modulate groundwater chemistry. Prior studies focusing on Odisha groundwaters have documented iron enrichment from laterite dissolution, pH depression from carbonic acid generated during monsoon infiltration, and nitrate contamination linked to agricultural and anthropogenic nitrogen loads.",
    { indent: true }
  ));
  children.push(body(
    "Despite the public health relevance of groundwater quality in Bhubaneswar, systematic multi-seasonal hydrochemical datasets coupled with advanced statistical and machine learning (ML) analysis remain scarce. The present mini-project addresses this gap by combining classical hydrogeochemical methods (IS 10500:2012 compliance, WQI, Piper/Gibbs classification, PCA, K-Means) with modern ML models and explainability tools (SHAP), while employing a novel data augmentation strategy to overcome the limited original sample size.",
    { indent: true }
  ));

  children.push(sectionHeading("1.2  Study Area"));
  children.push(body(
    "The study area encompasses the Bhubaneswar Municipal Corporation (BMC) boundary (approximately 18°47'N–20°32'N, 84°47'E–86°02'E) covering an area of ~517 km². Fifteen groundwater monitoring sites were selected across three representative land-use categories:",
    { indent: true }
  ));
  children.push(makeTable(
    ["Site ID", "Location Name", "Zone Type", "Latitude Range", "Rationale"],
    [
      ["PD-1", "Acharya Vihar",            "Population Density", "20.26°N", "Dense residential; domestic wells"],
      ["PD-2", "Ram Mandir",               "Population Density", "20.28°N", "Old town, high density"],
      ["PD-3", "Sailashree Vihar",         "Population Density", "20.27°N", "Planned residential colony"],
      ["PD-4", "OMFED Square",             "Population Density", "20.29°N", "Commercial/residential mix"],
      ["PD-5", "Old Town Bhubaneswar",     "Population Density", "20.24°N", "Heritage zone, shallow dug-wells"],
      ["IA-1", "Mancheswar Industrial",    "Industrial Area",    "20.26°N", "Heavy industry, effluents"],
      ["IA-2", "Chandaka Industrial Area", "Industrial Area",    "20.23°N", "CSIR campus, light industry"],
      ["IA-3", "OMFED Industries",         "Industrial Area",    "20.29°N", "Dairy processing units"],
      ["IA-4", "Rasulgarh",               "Industrial Area",    "20.28°N", "Mixed industrial estate"],
      ["IA-5", "Anmol Industries",         "Industrial Area",    "20.26°N", "Chemical manufacturing"],
      ["DY-1", "Bhuasuni Temple Area",     "Dumping Yard",      "20.24°N", "BMC landfill proximity"],
      ["DY-2", "Lingaraj Railway Station", "Dumping Yard",      "20.24°N", "Railway-side dumping"],
      ["DY-3", "BMC Micro Compost",        "Dumping Yard",      "20.30°N", "Composting facility"],
      ["DY-4", "Gadakan Road",             "Dumping Yard",      "20.25°N", "Semi-urban waste site"],
      ["DY-5", "Daruthenga",              "Dumping Yard",      "20.22°N", "Peripheral dump zone"],
    ],
    [900, 2200, 1500, 1200, 2866]
  ));
  children.push(body("Table 1.1: Description of 15 groundwater sampling sites in Bhubaneswar.", { center: true, italic: true }));

  children.push(sectionHeading("1.3  Objectives"));
  children.push(body("The specific objectives of this study are:", { indent: true }));
  children.push(bullet("To characterise the seasonal hydrochemistry (Premonsoon, Monsoon, Postmonsoon 2024) of groundwater at 15 sites across three land-use zones in Bhubaneswar.", 0));
  children.push(bullet("To develop and validate a Controlled Multivariate Gaussian Perturbation (CMGP) data augmentation framework for hydrochemical datasets.", 0));
  children.push(bullet("To assess potability of groundwater against IS 10500:2012 permissible limits and compute the Water Quality Index (WQI) using Brown et al. (1970) formulation.", 0));
  children.push(bullet("To identify the hydro-geochemical processes governing groundwater chemistry using PCA, Piper/Gibbs classification, ionic ratios, and K-Means clustering.", 0));
  children.push(bullet("To build and benchmark five machine learning models for predicting TDS, EC, and WQI, and interpret predictions using SHAP feature importance.", 0));

  children.push(sectionHeading("1.4  Scope and Significance"));
  children.push(body(
    "This study contributes to the growing literature on data-driven groundwater management in Indian Smart Cities. The CMGP methodology is novel in the context of small hydrochemical datasets and provides a replicable template for researchers working in data-scarce environments. The ML pipeline with SHAP explainability bridges the gap between black-box models and actionable hydrogeochemical insights. The findings directly inform groundwater governance, BMC water supply planning, and the need for targeted remediation.",
    { indent: true }
  ));

  children.push(pageBreak());

  // ════════════════════════════════════════════
  //  CHAPTER 2 — LITERATURE REVIEW
  // ════════════════════════════════════════════
  children.push(chapterHeading("CHAPTER 2: LITERATURE REVIEW"));

  children.push(sectionHeading("2.1  Hydrochemical Studies in Urban India"));
  children.push(body(
    "The hydrochemistry of shallow urban aquifers in India has been studied extensively in cities including Chennai (Thilagavathi et al., 2012), Hyderabad (Nagaraju et al., 2014), and Lucknow (Shukla and Saxena, 2018). These studies consistently document pH depression to < 6.5 in monsoon recharge zones underlain by lateritic or granitic soils, elevated iron from reductive dissolution of iron oxyhydroxides, hardness increase from calcite dissolution, and seasonally driven ionic enrichment due to evapotranspiration during the dry season. Studies in Odisha are fewer; notable contributions include Prusty et al. (2020) who characterised groundwater in Cuttack using Piper diagrams, reporting a dominant Ca-Mg-HCO₃ facies in pre-monsoon and Ca-Na-Cl in post-monsoon.",
    { indent: true }
  ));

  children.push(sectionHeading("2.2  IS 10500:2012 and WQI Methods"));
  children.push(body(
    "IS 10500:2012 (BIS, 2012) is the Indian standard specification for drinking water quality, prescribing acceptable/permissible limits for 26 parameters. The standard is based on WHO Guidelines (2011) with adaptation for Indian conditions. Non-compliance with pH (6.5–8.5 acceptable range), Iron < 0.3 mg/L, and TDS < 500 mg/L are frequently violated in urban shallow groundwaters (CGWB, 2022). The Water Quality Index (Brown et al., 1970) aggregates multi-parameter information into a single potability score using weighted normalised sub-indices (qᵢ = Cᵢ/Sᵢ × 100), and has been widely adopted in Indian hydrochemical studies for its ease of communication to policymakers.",
    { indent: true }
  ));

  children.push(sectionHeading("2.3  Machine Learning in Water Quality Prediction"));
  children.push(body(
    "The application of supervised machine learning to water quality prediction has expanded rapidly since 2015. Random Forest (Breiman, 2001) and Gradient Boosting (Friedman, 2001) are ensemble methods particularly suited to small to medium tabular datasets due to their robustness to overfitting. Deep learning approaches including MLP regressors have been applied to WQI prediction with high accuracy (Ahmed et al., 2019; Sahu et al., 2021). XGBoost (Chen & Guestrin, 2016) has demonstrated state-of-the-art performance across tabular regression benchmarks. Support Vector Regression (Vapnik, 1995) performs well in high-dimensional, limited-sample settings due to structural risk minimisation.",
    { indent: true }
  ));
  children.push(body(
    "SHAP (SHapley Additive exPlanations; Lundberg & Lee, 2017) provides model-agnostic, theoretically grounded feature importance scores derived from cooperative game theory. SHAP has been widely applied in environmental ML to identify the key hydrochemical drivers of water quality indices, replacing simpler permutation-based importance metrics.",
    { indent: true }
  ));

  children.push(sectionHeading("2.4  Data Augmentation in Environmental Sciences"));
  children.push(body(
    "Small sample sizes (n < 50) are endemic in hydrochemical monitoring studies due to cost and access constraints. Common augmentation approaches include bootstrapping, SMOTE (Chawla et al., 2002), Gaussian copulas, and Variational Autoencoders. Multivariate Gaussian perturbation — generating synthetic samples from a covariance-inflated distribution while preserving inter-parameter correlations — has been applied in soil chemistry (Li et al., 2021) and sediment geochemistry (Zhang et al., 2023). The present study extends this approach with a 5-layer noise injection protocol (CMGP) specifically adapted for seasonal hydrochemical augmentation, requiring per-season perturbation to preserve seasonal signal integrity.",
    { indent: true }
  ));

  children.push(pageBreak());

  // ════════════════════════════════════════════
  //  CHAPTER 3 — MATERIALS AND METHODS
  // ════════════════════════════════════════════
  children.push(chapterHeading("CHAPTER 3: MATERIALS AND METHODS"));

  children.push(sectionHeading("3.1  Sampling Design"));
  children.push(body(
    "Groundwater samples were collected from 15 monitoring sites in April–May (Premonsoon), July–August (Monsoon), and October–November (Postmonsoon) 2024, yielding 45 original observations. Sampling was conducted from dug-wells, hand-pumps, and shallow tube-wells at 5–15 m depth following APHA (2017) standard procedures. Samples were collected in pre-cleaned polyethylene bottles; those for cation analysis were acidified to pH < 2 with HNO₃. Temperature was measured in-situ; EC and pH were determined within 24 hours of collection using calibrated meters.",
    { indent: true }
  ));

  children.push(sectionHeading("3.2  Analytical Methods"));
  children.push(body(
    "The 16 physicochemical parameters were determined using the following methods: pH and EC — digital meter (calibrated daily); TDS — gravimetric at 180°C; TH — EDTA titrimetry; Ca and Mg — atomic absorption spectrometry (AAS); Na and K — flame photometry; Fe — phenanthroline spectrophotometry; HCO₃ and Alkalinity — acid titrimetry; Cl — Mohr argentometric method; SO₄ — turbidimetric (BaCl₂); NO₃ — cadmium reduction and Griess spectrophotometry; F — SPADNS spectrophotometry; DO — azide modification of Winkler method. Charge balance errors (CBE) were computed as CBE% = (ΣCations − ΣAnions) / (ΣCations + ΣAnions) × 100; 42 of 45 samples had |CBE| ≤ 10.4%, meeting analytical acceptance criteria.",
    { indent: true }
  ));

  children.push(sectionHeading("3.3  Data Augmentation — CMGP Framework"));
  children.push(body(
    "To overcome the small-sample constraint (n = 45), a Controlled Multivariate Gaussian Perturbation (CMGP) framework was developed, implemented independently per season as follows:",
    { indent: true }
  ));
  children.push(body(
    "Let Xₛ ∈ ℝⁿˣᵖ be the seasonal data matrix (n=15, p=16). The 5-layer procedure is:",
    { indent: true }
  ));
  children.push(bullet("Step 1 — Covariance Inflation (α = 1.40): Σ′ = Σₛ with diag(Σ′) = α·diag(Σₛ). Widens the sampling envelope by 40% to simulate natural inter-annual variability.", 0));
  children.push(bullet("Step 2 — Mean Jitter (β = 0.06): μ′ = μₛ + U(−β, β) ⊙ σₛ. Perturbs the synthetic centroid to avoid perfect overlap with original samples.", 0));
  children.push(bullet("Step 3 — Multivariate Sampling: X_syn ~ N(μ′, Σ′), drawing 50 samples per season (150 total), preserving inter-parameter covariance.", 0));
  children.push(bullet("Step 4 — Independent Noise (γ = 0.08): X_syn += N(0, γ·σₛ). Introduces uncorrelated parameter-level noise simulating analytical uncertainty.", 0));
  children.push(bullet("Step 5 — Outlier Injection (δ = 0.05, λ = 2.5): 5% of synthetic samples are perturbed by ±λ·σₛ·U(0.3, 1.0) on 2–4 random parameters to simulate anomalous recharge events.", 0));
  children.push(body(
    "Post-augmentation validation confirmed: all 16 parameters PASS KS test (p > 0.05); average overlap coefficient 67.0%; Cohen's d = 0.077 (negligible effect); correlation preservation 92.6%; Mahalanobis distance 0.414; PCA subspace alignment (average cosine similarity PC1–PC3) = 0.9137.",
    { indent: true }
  ));

  children.push(sectionHeading("3.4  Water Quality Index (WQI)"));
  children.push(body(
    "The WQI was computed following Brown et al. (1970) using 13 parameters with established IS 10500:2012 standard values:",
    { indent: true }
  ));
  children.push(body(
    "WQI = Σᵢ (Wᵢ × qᵢ),   where qᵢ = (Cᵢ / Sᵢ) × 100",
    { center: true, bold: true }
  ));
  children.push(body(
    "Wᵢ is the relative weight of parameter i (proportional to inverse standard value), Cᵢ is the measured concentration, and Sᵢ is the IS 10500 permissible limit. WQI categories: Excellent (< 50), Good (50–100), Poor (100–200), Very Poor (200–300), Unsuitable for Drinking (> 300).",
    { indent: true }
  ));

  children.push(sectionHeading("3.5  IS 10500:2012 Compliance Assessment"));
  children.push(body(
    "Each of the 16 hydrochemical parameters was evaluated against the IS 10500:2012 acceptable (desirable) and permissible (relaxed) limits. Samples were classified as SAFE (within acceptable limits), CAUTION (between acceptable and permissible), or UNSAFE (exceeding permissible limit). Where no permissible limit was specified (e.g., for Cl at 250/1000 mg/L dual threshold), the acceptable limit was used for the SAFE/UNSAFE boundary.",
    { indent: true }
  ));
  children.push(makeTable(
    ["Parameter", "Acceptable Limit", "Permissible Limit", "Unit"],
    [
      ["pH",        "6.5 – 8.5",   "6.5 – 8.5 (no relaxation)", "–"],
      ["TDS",       "500",          "2000",                       "mg/L"],
      ["TH",        "200",          "600",                        "mg/L as CaCO₃"],
      ["Ca",        "75",           "200",                        "mg/L"],
      ["Mg",        "30",           "100",                        "mg/L"],
      ["Na",        "200",          "No relaxation",              "mg/L"],
      ["K",         "—",            "—",                          "mg/L"],
      ["Iron",      "0.3",          "No relaxation",              "mg/L"],
      ["Cl",        "250",          "1000",                       "mg/L"],
      ["SO₄",      "200",           "400",                        "mg/L"],
      ["NO₃",      "45",            "No relaxation",              "mg/L"],
      ["F",         "1.0",          "1.5",                        "mg/L"],
      ["Alkalinity","200",          "600",                        "mg/L"],
    ],
    [2000, 2000, 2600, 2066]
  ));
  children.push(body("Table 3.1: IS 10500:2012 permissible limits for key parameters.", { center: true, italic: true }));

  children.push(sectionHeading("3.6  Source Apportionment Methods"));
  children.push(body(
    "The following geochemical tools were applied to identify the dominant hydrochemical processes:",
    { indent: true }
  ));
  children.push(bullet("Piper trilinear diagram — classification of water into hydrochemical facies (Ca-HCO₃, Na-Cl, etc.).", 0));
  children.push(bullet("Gibbs diagram — distinguishing rock-water interaction, evaporation, and precipitation dominance domains.", 0));
  children.push(bullet("Ionic ratios — Na/Cl (silicate weathering vs. halite dissolution), Ca/Mg (calcite vs. dolomite dissolution), CAI (chloro-alkaline index for ion exchange).", 0));
  children.push(bullet("PCA — dimension reduction to identify latent hydrochemical factors; Kaiser criterion (eigenvalue > 1) for component retention.", 0));
  children.push(bullet("K-Means clustering — elbow method on WCSS for K selection; hierarchical clustering (Ward's linkage) for validation.", 0));

  children.push(sectionHeading("3.7  Machine Learning Pipeline"));
  children.push(body(
    "Target variables: TDS (mg/L), EC (µS/cm), and WQI (dimensionless index). Features: the remaining 13–15 hydrochemical parameters (target-dependent). The 195-sample augmented dataset was split 80:20 (train:test) stratified by season (random_seed = 42). Features were standardised using scikit-learn StandardScaler fit on training data only. Model selection: Random Forest (n_estimators=200, max_depth=10), Gradient Boosting (n_estimators=200, lr=0.1, max_depth=4), SVR (C=100, ε=0.1, RBF kernel), Neural Network (hidden layers 128-64-32, max_iter=1000, early stopping, α=0.001), XGBoost (n_estimators=200, lr=0.1, max_depth=4). Models were evaluated using 5-fold cross-validation R² (CV R²), Test R², RMSE, MAE, MAPE, Nash-Sutcliffe Efficiency (NSE), Generalisation Accuracy (GA), and RMSE-standard deviation ratio (RSR). SHAP TreeExplainer was used for RF and ensemble models; KernelExplainer for NN and SVR.",
    { indent: true }
  ));

  children.push(pageBreak());

  // ════════════════════════════════════════════
  //  CHAPTER 4 — RESULTS AND DISCUSSION
  // ════════════════════════════════════════════
  children.push(chapterHeading("CHAPTER 4: RESULTS AND DISCUSSION"));

  children.push(sectionHeading("4.1  Data Quality and Validation"));
  children.push(body(
    "The original 45 samples exhibited no missing values. Outlier analysis identified IQR-flagged outliers in pH (1), Mg (2), Na (2), Iron (1), HCO₃ (2), NO₃ (1, also Z-score), and DO (2). Charge balance errors ranged from −10.4% to +10.7%; 93.3% of samples (42/45) were within the ±10% acceptance criterion. The slight excess reflects small analytical imprecision in certain parameters — a common observation in field hydrochemical datasets.",
    { indent: true }
  ));
  children.push(body(
    "Post-CMGP augmentation validation confirmed statistical consistency across all 16 parameters. The combined dataset (n = 195) achieved a sample-to-variable ratio of 12.2:1, above the recommended 10:1 threshold (Harrell, 2015), adequately powering PCA and ML analyses.",
    { indent: true }
  ));

  children.push(safeImage("figures/task1_cleaning/fig_original_vs_synthetic.png", 520, 320));
  children.push(figCaption("Figure 2.1: Original (blue) vs. Synthetic (orange) sample distributions for all 16 parameters — QQ-comparison."));
  children.push(safeImage("figures/task2_validation/fig_defense_summary.png", 520, 280));
  children.push(figCaption("Figure 2.3: Synthetic data validation defense summary — all 16 parameters pass all metrics."));

  children.push(sectionHeading("4.2  Seasonal Hydrochemistry"));
  children.push(body(
    "Seasonal mean concentrations of all 16 parameters revealed dramatic monsoon-driven changes (Table 4.3). The monsoon season displayed the highest ionic concentrations across most parameters, reflecting enhanced dissolution of soil and aquifer minerals under increased recharge flux and accelerated weathering kinetics.",
    { indent: true }
  ));

  children.push(makeTable(
    ["Parameter", "Unit", "Premonsoon", "Monsoon", "Postmonsoon", "% Change (Pre→Mon)", "Sig."],
    [
      ["pH",         "–",        "6.29",   "5.93",   "5.94",   "−5.7%",   "*(p=0.0118)"],
      ["EC",         "µS/cm",    "391.71", "626.62", "445.59", "+59.97%", "***(p<0.0001)"],
      ["TDS",        "mg/L",     "246.06", "411.14", "292.73", "+67.09%", "***(p<0.0001)"],
      ["TH",         "mg/L",     "25.75",  "153.80", "163.22", "+497%",   "***(p<0.0001)"],
      ["Alkalinity", "mg/L",     "111.96", "80.70",  "56.34",  "−27.9%",  "***(p<0.0001)"],
      ["Ca",         "mg/L",     "33.19",  "49.73",  "38.61",  "+49.8%",  "***(p<0.0001)"],
      ["Mg",         "mg/L",     "7.07",   "10.24",  "10.54",  "+44.8%",  "***(p<0.0001)"],
      ["Na",         "mg/L",     "25.35",  "50.87",  "22.68",  "+100.6%", "***(p<0.0001)"],
      ["K",          "mg/L",     "6.58",   "14.59",  "6.70",   "+121.6%", "***(p<0.0001)"],
      ["Iron",       "mg/L",     "0.26",   "0.34",   "0.30",   "+30.8%",  "*(p=0.0141)"],
      ["HCO₃",      "mg/L",     "89.55",  "129.76", "64.56",  "+44.9%",  "***(p<0.0001)"],
      ["Cl",         "mg/L",     "43.06",  "87.24",  "86.04",  "+102.6%", "***(p<0.0001)"],
      ["SO₄",       "mg/L",     "16.84",  "21.07",  "19.09",  "+25.1%",  "*(p=0.0248)"],
      ["NO₃",       "mg/L",     "21.33",  "21.27",  "28.77",  "−0.3%",   "*(p=0.0293)"],
      ["F",          "mg/L",     "0.05",   "0.10",   "0.13",   "+100%",   "***(p<0.0001)"],
      ["DO",         "mg/L",     "6.43",   "5.02",   "6.09",   "−21.9%",  "***(p<0.0001)"],
    ],
    [1400, 800, 1100, 1100, 1200, 1600, 1466]
  ));
  children.push(body("Table 4.3: Seasonal mean concentrations of 16 hydrochemical parameters. Significance: *p<0.05, ***p<0.0001.", { center: true, italic: true }));

  children.push(body(
    "The most striking seasonal change was observed for Total Hardness, which increased by 497% from Premonsoon (25.75 mg/L) to Monsoon (153.80 mg/L), driven by intensified dissolution of Ca-Mg carbonate and silicate minerals under recharge. Sodium (+101%) and Chloride (+103%) showed >100% monsoon enrichment, attributable to silicate weathering (Na/Cl monsoon ratio = 1.36 > 1) and leaching of anthropogenic chloride from surface contamination. pH declined significantly in monsoon (6.29 → 5.93, ANOVA p = 0.0118) due to carbonic acid loading from CO₂-rich recharge. Dissolv Oxygen decreased by 21.9% in monsoon (6.43 → 5.02 mg/L, p < 0.0001), consistent with increased microbial activity and organic matter mineralisation during the rainy season.",
    { indent: true }
  ));

  children.push(safeImage("figures/task3_seasonal/fig_seasonal_boxplots.png", 520, 300));
  children.push(figCaption("Figure 3.3: Seasonal boxplots for key hydrochemical parameters showing monsoon enrichment."));
  children.push(safeImage("figures/task3_seasonal/fig_seasonal_heatmap.png", 520, 260));
  children.push(figCaption("Figure 3.4: Seasonal heatmap of mean parameter concentrations (z-score normalised)."));
  children.push(safeImage("figures/task3_seasonal/fig_seasonal_violins.png", 520, 340));
  children.push(figCaption("Figure 3.1: Violin plots of 16 hydrochemical parameters by season."));

  children.push(sectionHeading("4.3  IS 10500:2012 Compliance Assessment and WQI"));
  children.push(subHeading("4.3.1  Parameter-Level Compliance (195 samples)"));
  children.push(makeTable(
    ["Parameter", "% Safe", "% Caution", "% Unsafe", "Primary Concern"],
    [
      ["pH",        "24.6%",  "0.0%",   "75.4%",  "Acidity (pH < 6.5 in most samples)"],
      ["Iron",      "54.9%",  "0.0%",   "45.1%",  "Laterite dissolution, anoxic conditions"],
      ["K",         "71.8%",  "0.0%",   "28.2%",  "Fertiliser leaching in DY/IA zones"],
      ["NO₃",      "88.2%",  "0.0%",   "11.8%",  "Nitrification, sewer infiltration"],
      ["DO",        "55.4%",  "35.9%",  "8.7%",   "Monsoon O₂ depletion"],
      ["TDS",       "97.9%",  "2.1%",   "0.0%",   "Mostly within limits"],
      ["TH",        "81.0%",  "19.0%",  "0.0%",   "Monsoon hardness spikes"],
      ["EC",        "96.4%",  "3.6%",   "0.0%",   "Well within limits"],
      ["Ca",        "99.0%",  "1.0%",   "0.0%",   "Negligible concern"],
      ["Cl, SO₄, Na, Mg, F, Alkalinity, HCO₃", "100%", "0%", "0%", "Within IS 10500 limits"],
    ],
    [2200, 900, 900, 900, 3766]
  ));
  children.push(body("Table 4.5: IS 10500:2012 compliance summary (% of 195 samples).", { center: true, italic: true }));

  children.push(safeImage("figures/task4_safety/fig_is10500_compliance_bars.png", 520, 300));
  children.push(figCaption("Figure 4.1: IS 10500:2012 compliance bar chart — Safe, Caution, and Unsafe fractions for each parameter."));
  children.push(safeImage("figures/task4_safety/fig_is10500_compliance_heatmap.png", 520, 320));
  children.push(figCaption("Figure 4.2: IS 10500:2012 compliance heatmap — sample vs. parameter safety classification."));

  children.push(body(
    "pH non-compliance is the most critical finding: 75.4% of all 195 samples failed the IS 10500:2012 pH criterion (acceptable range 6.5–8.5), with most samples exhibiting acidic conditions (pH 5.0–6.5). This aligns with the regional geology: laterite-derived soils and basement weathering release carbonic and organic acids that are not sufficiently buffered. Iron exceeded the permissible limit of 0.3 mg/L in 45.1% of samples, with the highest concentrations in dumping yard zones (DY cluster mean Iron = 0.35 mg/L). The Iron exceedance is attributed to reductive dissolution of Fe-oxyhydroxide coatings on aquifer materials during monsoon-season anoxia.",
    { indent: true }
  ));

  children.push(subHeading("4.3.2  Sample-Level Safety and WQI"));
  children.push(body(
    "At the sample level (original 45), 91.1% of samples were classified as UNSAFE (41/45), 2.2% as CAUTION (1/45), and 6.7% as SAFE (3/45). The three SAFE samples were DY-3 Premonsoon, IA-4 Premonsoon, and PD-5 Premonsoon — all in the dry premonsoon season when recharge-driven dissolution is minimal. The single CAUTION sample was DY-5 Postmonsoon.",
    { indent: true }
  ));
  children.push(body(
    "Paradoxically, WQI analysis revealed that all 195 samples fell in the Excellent (< 50) or Good (50–100) categories: WQI range 30.81–77.04, mean 51.82 ± 8.92. Premonsoon WQI mean was 44.86 (75.4% Excellent), Monsoon was 58.63 (98.5% Good), and Postmonsoon was 51.98 (41.5% Excellent, 58.5% Good). The apparent contradiction between sample-level UNSAFE classification (based on single-parameter exceedance of pH) and good WQI scores reflects a key methodological distinction: the sample-level assessment uses any single parameter violation as grounds for UNSAFE classification, while WQI aggregates all parameters, and non-violated parameters (97.9% TDS compliant, 100% Cl/SO₄/Na compliant) dominate the weighted aggregate.",
    { indent: true }
  ));

  children.push(safeImage("figures/task4_safety/fig_wqi_analysis.png", 520, 260));
  children.push(figCaption("Figure 4.4: WQI analysis — distribution histogram by season, seasonal boxplot, and category pie chart."));

  children.push(sectionHeading("4.4  Hydrogeochemical Source Apportionment"));
  children.push(subHeading("4.4.1  Principal Component Analysis"));
  children.push(body(
    "PCA on the standardised 195-sample dataset retained 6 principal components under the Kaiser criterion (eigenvalue > 1), cumulatively explaining 73.15% of total hydrochemical variance (Table 4.7).",
    { indent: true }
  ));
  children.push(makeTable(
    ["PC", "Eigenvalue", "% Variance", "Cumulative %", "Key Loadings", "Interpretation"],
    [
      ["PC1", ">1", "29.29%", "29.29%", "EC (0.424), TDS (0.424), Ca (0.328), Na (0.319)", "Mineralization / Salinity"],
      ["PC2", ">1", "13.56%", "42.84%", "HCO₃ (0.490), Alkalinity (0.454)", "Carbonate weathering"],
      ["PC3", ">1", "9.81%",  "52.66%", "Mg (0.510), pH (0.439), NO₃ (−0.442)", "Silicate weathering / acidity"],
      ["PC4", ">1", "8.23%",  "60.89%", "Iron (0.629), DO (−0.389)", "Redox / laterite dissolution"],
      ["PC5", ">1", "6.49%",  "67.38%", "K (0.293), pH (0.398)", "Alkaline K-feldspar weathering"],
      ["PC6", ">1", "5.78%",  "73.15%", "SO₄ (−0.257), Na (−0.280)", "Sulphate/Na anthropogenic signal"],
    ],
    [600, 1000, 1100, 1200, 2800, 2966]
  ));
  children.push(body("Table 4.7: PCA — variance explained and key variable loadings per retained component.", { center: true, italic: true }));

  children.push(safeImage("figures/task5_source/fig_pca_scree.png", 520, 260));
  children.push(figCaption("Figure 5.4: PCA scree plot (left) and cumulative explained variance (right) — 6 components retained at 73.15%."));
  children.push(safeImage("figures/task5_source/fig_pca_loadings_heatmap.png", 520, 300));
  children.push(figCaption("Figure 5.5: PCA loadings heatmap — variable contributions to PC1–PC4."));
  children.push(safeImage("figures/task5_source/fig_pca_biplot.png", 520, 460));
  children.push(figCaption("Figure 5.6: PCA biplot — PC1 (35.7%) vs PC2 (14.5%) showing sample grouping by area type and variable loading vectors."));

  children.push(subHeading("4.4.2  K-Means Clustering"));
  children.push(body(
    "K-Means clustering with optimal K = 3 (elbow method; Fig. 5.2) identified three distinct hydrochemical assemblages:",
    { indent: true }
  ));
  children.push(makeTable(
    ["Cluster", "Dominant Season/Zone", "Mean EC (µS/cm)", "Mean TDS (mg/L)", "Mean TH (mg/L)", "Interpretation"],
    [
      ["0 (High mineral.)", "Monsoon (all zones)",    "636.86", "417.65", "165.86", "Highly mineralised monsoon recharge"],
      ["1 (Low mineral.)",  "Premonsoon (all zones)", "396.18", "250.33", "30.82",  "Dry-season baseline"],
      ["2 (Intermediate)",  "Postmonsoon (DY/IA)",   "435.08", "285.76", "160.00", "Post-monsoon residual mineralisation"],
    ],
    [1400, 2000, 1300, 1300, 1300, 2366]
  ));
  children.push(body("Table 4.8: K-Means cluster means (K=3).", { center: true, italic: true }));

  children.push(safeImage("figures/task5_source/fig_kmeans_pca.png", 520, 440));
  children.push(figCaption("Figure 5.3: K-Means (K=3) cluster boundaries in PC1-PC2 score space."));

  children.push(subHeading("4.4.3  Piper Diagram and Geochemical Facies"));
  children.push(body(
    "Piper trilinear classification revealed seasonal shifts in hydrochemical facies. In Premonsoon, Na-K-SO₄ (n=26) and Ca-HCO₃ (n=12) facies dominate, indicating silicate weathering and bicarbonate-rich recharge. In Monsoon, Na-K-HCO₃ (n=22) and Na-K-Cl (n=18) facies predominate, signalling intensified silicate and halite dissolution under increased recharge flux. In Postmonsoon, Ca-Cl (n=25) emerges as the dominant facies, reflecting reverse ion exchange — Ca replacing Na on soil exchange sites — as recharge diminishes and evaporative concentration operates.",
    { indent: true }
  ));
  children.push(safeImage("figures/task5_source/fig_piper_diagram.png", 520, 420));
  children.push(figCaption("Figure 5.7: Piper trilinear diagram showing seasonal hydrochemical facies evolution."));

  children.push(subHeading("4.4.4  Gibbs Diagram and Ionic Ratios"));
  children.push(body(
    "All 45 original samples plotted in the rock-water interaction domain of the Gibbs (1970) diagram, confirming that aquifer mineralogy — rather than precipitation dilution or evaporation concentration — is the primary control on dissolved ion chemistry across all seasons. Na/Cl ratios were > 1.2 in monsoon (mean 1.36), indicating silicate weathering contribution to sodium load beyond that of halite dissolution, and < 1.0 in postmonsoon (mean 0.51), consistent with reverse ion exchange depleting Na. Ca/Mg ratios consistently exceeded 2.0 (Premonsoon 2.97, Monsoon 3.18, Postmonsoon 4.46), indicating calcite/dolomite and silicate dissolution (rather than dolomite-only dissolution which would yield Ca/Mg ≈ 1.0).",
    { indent: true }
  ));
  children.push(safeImage("figures/task5_source/fig_gibbs_diagram.png", 480, 380));
  children.push(figCaption("Figure 5.8: Gibbs diagram — all samples plot in the rock-water interaction domain."));
  children.push(safeImage("figures/task5_source/fig_ionic_ratios.png", 520, 380));
  children.push(figCaption("Figure 5.9: Ionic ratio scatter plots — Na vs. Cl, Ca vs. Mg, and weathering balance plots."));

  children.push(sectionHeading("4.5  Machine Learning Results"));
  children.push(body(
    "All five ML models were trained and evaluated on the 195-sample augmented dataset. Performance metrics for the best model per target are summarised in Table 4.9.",
    { indent: true }
  ));
  children.push(makeTable(
    ["Target", "Best Model", "Train R²", "CV R²", "Test R²", "RMSE", "MAE", "MAPE", "NSE", "RSR"],
    [
      ["TDS", "Random Forest", "0.9690", "0.7527 ±0.022", "0.7637", "49.3 mg/L",   "38.4", "13.1%", "0.764", "0.486"],
      ["EC",  "Random Forest", "0.9693", "0.7711 ±0.028", "0.7570", "67.6 µS/cm",  "49.0", "8.8%",  "0.757", "0.493"],
      ["WQI", "Neural Network","0.9901", "0.9447 ±0.018", "0.9364", "2.1",         "1.6",  "2.9%",  "0.936", "0.252"],
    ],
    [800, 1400, 1000, 1400, 900, 1200, 900, 800, 800, 800]
  ));
  children.push(body("Table 4.9: Machine learning performance metrics for the best model per target variable.", { center: true, italic: true }));

  children.push(body(
    "Random Forest outperformed other models for TDS and EC prediction, achieving Test R² = 0.7637 and 0.7570 respectively. The modest test R² (compared to train R² ≈ 0.97) indicates moderate overfitting, likely because the 80:20 stratified split leaves only 39 test samples. The 5-fold CV R² (0.7527 for TDS, 0.7711 for EC) is more reliable and indicates adequate generalisation. NSE values of 0.764 and 0.757 satisfy the 'good' model performance threshold (> 0.75; Moriasi et al., 2007), and RSR values below 0.5 indicate good model efficiency.",
    { indent: true }
  ));
  children.push(body(
    "The Neural Network achieved exceptional WQI prediction (CV R² = 0.9447, Test R² = 0.9364, RMSE = 2.1, MAPE = 2.9%). Given that WQI is itself a computed function of the input parameters, its high predictability is expected — the salient finding is that the NN captures the non-linear WQI response surface more accurately than ensemble methods, likely due to its ability to model complex multiplicative interactions. The RSR of 0.252 places WQI prediction in the 'very good' category.",
    { indent: true }
  ));

  children.push(safeImage("figures/task6_ml/fig_actual_vs_predicted_tds.png", 490, 300));
  children.push(figCaption("Figure 6.1: Actual vs. Predicted TDS — Random Forest (Test R² = 0.7637)."));
  children.push(safeImage("figures/task6_ml/fig_actual_vs_predicted_ec.png", 490, 300));
  children.push(figCaption("Figure 6.2: Actual vs. Predicted EC — Random Forest (Test R² = 0.7570)."));
  children.push(safeImage("figures/task6_ml/fig_actual_vs_predicted_wqi.png", 490, 300));
  children.push(figCaption("Figure 6.3: Actual vs. Predicted WQI — Neural Network (Test R² = 0.9364)."));

  children.push(subHeading("4.5.1  SHAP Feature Importance"));
  children.push(makeTable(
    ["Target", "Rank 1", "SHAP", "Rank 2", "SHAP", "Rank 3", "SHAP"],
    [
      ["TDS", "Ca",  "0.425", "Na",   "0.286", "K",    "0.068"],
      ["EC",  "Na",  "0.459", "Ca",   "0.210", "K",    "0.118"],
      ["WQI", "EC",  "0.454", "NO₃", "0.137", "Iron", "0.128"],
    ],
    [1200, 1200, 900, 1200, 900, 1200, 966]
  ));
  children.push(body("Table 4.10: SHAP top-3 feature importances (mean |SHAP value|) per ML target.", { center: true, italic: true }));

  children.push(body(
    "SHAP analysis revealed that Ca (0.425) is the most influential predictor of TDS, followed by Na (0.286). This is consistent with the PCA finding that PC1 (mineralization axis) is co-loaded by EC, TDS, Ca, and Na — Ca-bearing silicate and carbonate minerals dominate the dissolved solid budget. For EC (conductance), Na dominates (0.459) because ionic mobility of Na⁺ in solution is high, making Na a disproportionately large contributor to electrical conductance relative to its mass concentration. For WQI, EC is the dominant driver (0.454) because EC is itself included in the WQI parameter pool and is inversely linked to water quality, followed by NO₃ (0.137) and Iron (0.128) — the parameters most frequently exceeding IS 10500 limits.",
    { indent: true }
  ));

  children.push(safeImage("figures/task6_ml/fig_shap_summary_tds.png", 500, 300));
  children.push(figCaption("Figure 6.7: SHAP summary plot — TDS predictor importance (Random Forest). Ca and Na dominate."));
  children.push(safeImage("figures/task6_ml/fig_shap_summary_ec.png", 500, 300));
  children.push(figCaption("Figure 6.8: SHAP summary plot — EC predictor importance (Random Forest). Na dominates."));
  children.push(safeImage("figures/task6_ml/fig_shap_summary_wqi.png", 500, 300));
  children.push(figCaption("Figure 6.9: SHAP summary plot — WQI predictor importance (Neural Network). EC, NO₃, Iron."));

  children.push(pageBreak());

  // ════════════════════════════════════════════
  //  CHAPTER 5 — INTEGRATED DISCUSSION
  // ════════════════════════════════════════════
  children.push(chapterHeading("CHAPTER 5: INTEGRATED DISCUSSION"));

  children.push(body(
    "The multi-disciplinary findings of this study converge to paint a coherent picture of groundwater quality dynamics in peri-urban Bhubaneswar. The dominant hydrogeochemical narrative is one of rock-water interaction modulated by seasonal recharge, operating across three land-use contexts with varying anthropogenic overprints.",
    { indent: true }
  ));

  children.push(sectionHeading("5.1  Seasonal Recharge as the Master Variable"));
  children.push(body(
    "The monsoon season acts as the primary driver of hydrochemical change, causing order-of-magnitude increases in TH (+497%), Na (+101%), and K (+122%). The PCA scores of both original and augmented samples clearly cluster by season along PC1 (K-Means Cluster 0 = high-mineralisation monsoon; Cluster 1 = low-mineralisation premonsoon; Cluster 2 = intermediate postmonsoon). K-Means and hierarchical cluster analysis both converge on this three-cluster solution, confirming that seasonal mineralogical flushing is the dominant structuring process in the dataset. This finding has direct operational implications: groundwater abstracted during the monsoon season carries higher dissolved ion loads and presents a higher risk of TH, Iron, and K exceedance.",
    { indent: true }
  ));

  children.push(sectionHeading("5.2  Zone-Specific Contamination Signals"));
  children.push(body(
    "Although all three zones (PD, IA, DY) are dominated by rock-water interaction in Gibbs space, subtle zone-specific signatures are discernible. Dumping yard sites show the highest Iron concentrations (Cluster 0 mean 0.35 mg/L) and elevated NO₃ in postmonsoon (DY cluster postmonsoon NO₃ mean ≈ 30 mg/L), consistent with leachate infiltration from waste piles. Industrial area sites exhibit higher EC in certain postmonsoon observations (IA-3 WQI = 77.04, the maximum observed), likely due to industrial effluent seepage enhancing conductance. Population density sites showed relatively lower mineralisation in premonsoon — the three SAFE samples (DY-3, IA-4, PD-5, all Premonsoon) reflect the pre-monsoon baseline when the aquifer is depleted and buffered against active leaching.",
    { indent: true }
  ));

  children.push(sectionHeading("5.3  Consistency between Geochemical and ML Findings"));
  children.push(body(
    "The convergence between PCA-derived process interpretation and SHAP-derived ML feature importance provides strong cross-validation. PCA identifies EC, TDS, and Ca as co-varying mineralization indicators (PC1 axis), while SHAP confirms Ca is the top TDS predictor (0.425) and Na is the top EC predictor (0.459) — both are dominant PC1 loading variables. The SHAP finding that Iron (0.128) and NO₃ (0.137) drive WQI variability directly mirrors the IS 10500 compliance analysis showing Iron (45.1% unsafe) and NO₃ (11.8% unsafe) as the key parameters contributing to composite water quality degradation. This alignment between classical hydrogeochemistry and data-driven feature importance provides strong confidence in both analytical frameworks.",
    { indent: true }
  ));

  children.push(sectionHeading("5.4  Limitations and Uncertainties"));
  children.push(body(
    "The primary limitation of this study is the small original sample size (n = 45). While the CMGP augmentation framework successfully validated as statistically consistent, the ML models trained on augmented data may exhibit uncertainty in extrapolation to unseen conditions. The train R² ≈ 0.97 versus test R² ≈ 0.76 for TDS/EC models reflects some overfitting that larger future datasets would resolve. Additionally, the study does not include bacterial/microbiological parameters (total coliforms, E. coli), trace heavy metals (Pb, As, Cr), or speciated nitrogen forms (NH₄⁺, NO₂⁻) that would provide a more complete potability assessment. Spatial interpolation and GIS mapping of contamination plumes would benefit from a denser sampling grid.",
    { indent: true }
  ));

  children.push(safeImage("figures/task7_insights/fig_seasonal_radar.png", 520, 400));
  children.push(figCaption("Figure 7.1: Seasonal radar chart — parameter-level deviation from IS 10500 limits by season and zone type, integrating all analysis findings."));

  children.push(pageBreak());

  // ════════════════════════════════════════════
  //  CHAPTER 6 — CONCLUSIONS AND RECOMMENDATIONS
  // ════════════════════════════════════════════
  children.push(chapterHeading("CHAPTER 6: CONCLUSIONS AND RECOMMENDATIONS"));

  children.push(sectionHeading("6.1  Conclusions"));
  children.push(body(
    "This study presented a comprehensive multi-seasonal hydrochemical characterisation of groundwater at 15 sites in Bhubaneswar, Odisha, for the year 2024. The key conclusions are:",
    { indent: true }
  ));
  children.push(bullet("Dataset augmentation using the CMGP framework successfully expanded 45 original samples to 195 while maintaining statistical fidelity (all 16 parameters PASS validation, Cohen's d = 0.077, correlation preservation 92.6%). The augmented dataset achieves a 12.2:1 sample-to-variable ratio, enabling robust PCA and ML analysis.", 0));
  children.push(bullet("All 16 hydrochemical parameters showed statistically significant seasonal variation (p < 0.05 by ANOVA or Kruskal-Wallis test). The monsoon season induced the largest ionic enrichment, particularly TH (+497%), Na (+101%), K (+122%), and Cl (+103%), driven by intensified rock-water interaction under monsoon recharge.", 0));
  children.push(bullet("IS 10500:2012 compliance assessment identified pH acidity as the most critical water quality issue: 75.4% of all 195 samples failed the acceptable pH criterion of 6.5–8.5. Iron was the second most critical parameter (45.1% unsafe). At the sample level, 91.1% of original samples were classified UNSAFE (primarily on account of pH and Iron exceedance).", 0));
  children.push(bullet("WQI (Brown et al., 1970) ranged from 30.81 to 77.04 (mean ± sd: 51.82 ± 8.92), with all 195 samples in the Excellent (39.5%) or Good (60.5%) category. Premonsoon had the lowest WQI (mean 44.86, mostly Excellent); Monsoon had the highest (58.63, 98.5% Good).", 0));
  children.push(bullet("PCA retained 6 components explaining 73.15% of total variance. PC1 (29.29%) represents the mineralization axis (EC, TDS, Ca, Na); PC2 (13.56%) carbonate weathering (HCO₃, Alkalinity); PC4 (8.23%) redox/laterite dissolution (Iron loading 0.629). Gibbs plots confirmed that rock-water interaction dominates across all seasons.", 0));
  children.push(bullet("K-Means clustering (K=3) and hierarchical clustering (Ward's method) both grouped samples into three assemblages aligned with seasonality: high-mineralisation monsoon (Cluster 0), low-mineralisation premonsoon (Cluster 1), and intermediate postmonsoon (Cluster 2). Piper diagrams showed Ca-Cl as the dominant postmonsoon facies and Na-K-HCO₃/Na-K-Cl in monsoon.", 0));
  children.push(bullet("Random Forest achieved the best performance for TDS prediction (CV R² = 0.7527, Test R² = 0.7637, RMSE = 49.3 mg/L, NSE = 0.764) and EC prediction (CV R² = 0.7711, Test R² = 0.7570, RMSE = 67.6 µS/cm). Neural Network best predicted WQI (CV R² = 0.9447, Test R² = 0.9364, RMSE = 2.1, MAPE = 2.9%). SHAP analysis identified Ca and Na as key TDS/EC drivers, and EC, NO₃, Iron as key WQI drivers, fully consistent with the geochemical source analysis.", 0));

  children.push(sectionHeading("6.2  Recommendations"));
  children.push(bullet("Immediate Water Treatment: Groundwater supplies in all three zone types should not be consumed without pH correction (lime/calcite dosing) and iron removal (aeration + sedimentation). Priority must be given to monsoon-season IAs and DYs where Iron and pH simultaneously fail IS 10500 limits.", 0));
  children.push(bullet("Monitoring Enhancement: Deploy continuous EC/pH loggers at 4–5 representative sites (at minimum PD-2, IA-1, DY-1) to capture real-time seasonal transitions and enable early warning of quality degradation.", 0));
  children.push(bullet("Augmented Dataset Deployment: The validated CMGP-augmented 195-sample dataset should be used as the training basis for a production-grade ML model that can be operationalised by BMC for real-time WQI prediction from routine field measurements (EC, pH, TDS).", 0));
  children.push(bullet("Broader Sampling: Extend sampling to include: (i) deeper confined aquifers to compare with shallow unconfined aquifer chemistry; (ii) additional parameters — As, Pb, total coliforms, NH₄⁺ — to complete the IS 10500:2012 parameter set; (iii) quarterly sampling to capture smaller-scale seasonal transitions.", 0));
  children.push(bullet("Policy: BMC and Odisha PHED should prioritise groundwater pH remediation in DY zones, institute a Proximity Exclusion Zone of ≥500 m around active landfills for potable wells, and commission annual hydrochemical surveys using the methodology developed in this study.", 0));

  children.push(pageBreak());

  // ════════════════════════════════════════════
  //  REFERENCES
  // ════════════════════════════════════════════
  children.push(chapterHeading("REFERENCES"));

  const refs = [
    "APHA (American Public Health Association), 2017. Standard Methods for the Examination of Water and Wastewater, 23rd ed. American Public Health Association, Washington D.C.",
    "BIS (Bureau of Indian Standards), 2012. Indian Standard: Drinking Water — Specification (Second Revision), IS 10500:2012. Bureau of Indian Standards, New Delhi.",
    "Breiman, L., 2001. Random Forests. Machine Learning, 45(1), 5–32.",
    "Brown, R.M., McClelland, N.I., Deininger, R.A., Tozer, R.G., 1970. A water quality index: do we dare? Water and Sewage Works, 117(10), 339–343.",
    "CGWB (Central Ground Water Board), 2022. Dynamic Ground Water Resources of India. Ministry of Jal Shakti, Government of India, New Delhi.",
    "Chawla, N.V., Bowyer, K.W., Hall, L.O., Kegelmeyer, W.P., 2002. SMOTE: Synthetic Minority Over-sampling Technique. Journal of Artificial Intelligence Research, 16, 321–357.",
    "Chen, T., Guestrin, C., 2016. XGBoost: A Scalable Tree Boosting System. Proceedings of the 22nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining, 785–794.",
    "Friedman, J.H., 2001. Greedy function approximation: a gradient boosting machine. Annals of Statistics, 29(5), 1189–1232.",
    "Gibbs, R.J., 1970. Mechanisms controlling world water chemistry. Science, 170(3962), 1088–1090.",
    "Hair, J.F., Black, W.C., Babin, B.J., Anderson, R.E., 2010. Multivariate Data Analysis, 7th ed. Pearson Prentice Hall, Upper Saddle River, NJ.",
    "Harrell, F.E., 2015. Regression Modeling Strategies: With Applications to Linear Models, Logistic and Ordinal Regression, and Survival Analysis, 2nd ed. Springer, New York.",
    "Li, X., Liu, X., Zhang, Q., 2021. Synthetic data augmentation for soil organic carbon prediction using machine learning. Geoderma, 382, 114714.",
    "Lundberg, S.M., Lee, S.I., 2017. A Unified Approach to Interpreting Model Predictions. Advances in Neural Information Processing Systems, 30, 4765–4774.",
    "Moriasi, D.N., Arnold, J.G., Van Liew, M.W., Bingner, R.L., Harmel, R.D., Veith, T.L., 2007. Model evaluation guidelines for systematic quantification of accuracy in watershed simulations. Transactions of the ASABE, 50(3), 885–900.",
    "Nagaraju, A., Suresh, S., Killham, K., Hudson-Edwards, K., 2014. Hydrogeochemistry of waters of Mangampeta barite mining area, Cuddapah Basin, Andhra Pradesh, India. Turkish Journal of Engineering and Environmental Sciences, 30(4), 203–219.",
    "Piper, A.M., 1944. A graphic procedure in the geochemical interpretation of water analyses. Transactions of the American Geophysical Union, 25(6), 914–928.",
    "Prusty, P., Farooq, S.H., Swain, D., Tripathy, S., 2020. Dissolved elemental flux from freshwater to the coastal ocean and the role of estuaries in biogeochemical cycling. Environmental Monitoring and Assessment, 192(1), 57.",
    "Sahu, A., Patel, P., Tiwari, M.K., 2021. Machine learning-based prediction of water quality index for groundwater in India. Water Resources Management, 35, 3381–3399.",
    "Shukla, S., Saxena, A., 2018. Groundwater quality and associated human health risk assessment in parts of Raebareli district, Uttar Pradesh, India. Groundwater for Sustainable Development, 7, 184–199.",
    "Thilagavathi, R., Chidambaram, S., Prasanna, M.V., Thivya, C., Singaraja, C., 2012. A study on groundwater geochemistry and water quality in layered aquifers system of Pondicherry region, southeast India. Applied Water Science, 2(4), 253–269.",
    "Vapnik, V., 1995. The Nature of Statistical Learning Theory. Springer-Verlag, New York.",
    "WHO (World Health Organization), 2011. Guidelines for Drinking-water Quality, 4th ed. World Health Organization, Geneva.",
    "Zhang, Q., Sun, X., Li, Y., 2023. Geochemical data augmentation for rare earth element classification using multivariate Gaussian perturbation. Computers and Geosciences, 171, 105280.",
  ];

  refs.forEach((ref, i) => {
    children.push(new Paragraph({
      spacing: { line: 360, lineRule: LineRuleType.AUTO, after: 120 },
      indent: { hanging: 360 },
      children: [new TextRun({ text: `[${i + 1}]  ${ref}`, size: SZ_BODY - 1, font: FONT })],
    }));
  });

  children.push(pageBreak());

  // ════════════════════════════════════════════
  //  INDIVIDUAL CONTRIBUTION
  // ════════════════════════════════════════════
  children.push(chapterHeading("INDIVIDUAL CONTRIBUTION"));

  children.push(makeTable(
    ["Sr.", "Task / Sub-task", "Contributor", "Effort (%)"],
    [
      ["1",  "Literature review and problem formulation",           "Both equally",                   "50/50"],
      ["2",  "Sampling site selection and fieldwork coordination",  "Lakshya Nayyar (Lead)",          "70/30"],
      ["3",  "Laboratory analysis and data entry",                  "Vaibhav Bhaskar (Lead)",         "30/70"],
      ["4",  "Data cleaning, CBE validation, outlier analysis",     "Vaibhav Bhaskar",                "100"],
      ["5",  "CMGP augmentation framework (Python implementation)", "Vaibhav Bhaskar (Lead)",         "70/30"],
      ["6",  "CMGP statistical defense and validation",             "Lakshya Nayyar (Lead)",          "30/70"],
      ["7",  "Seasonal statistical analysis (ANOVA/KW)",            "Both equally",                   "50/50"],
      ["8",  "IS 10500:2012 compliance assessment",                 "Lakshya Nayyar",                 "100"],
      ["9",  "WQI computation and analysis",                        "Vaibhav Bhaskar",                "100"],
      ["10", "PCA, Piper/Gibbs, ionic ratio analysis",              "Vaibhav Bhaskar (Lead)",         "70/30"],
      ["11", "K-Means and hierarchical clustering",                 "Lakshya Nayyar (Lead)",          "30/70"],
      ["12", "ML model training and benchmarking (all 5 models)",   "Both equally",                   "50/50"],
      ["13", "SHAP analysis and feature interpretation",             "Vaibhav Bhaskar (Lead)",         "70/30"],
      ["14", "Figure generation (all 47 figures)",                  "Vaibhav Bhaskar",                "100"],
      ["15", "Report writing and editing",                          "Both equally",                   "50/50"],
      ["16", "Presentation preparation",                            "Lakshya Nayyar (Lead)",          "30/70"],
    ],
    [500, 3800, 2200, 2166]
  ));

  children.push(...emptyLine(3));
  children.push(new Paragraph({
    children: [
      new TextRun({ text: "Signature of Student 1: ________________", size: SZ_BODY, font: FONT }),
      new TextRun({ text: "      Vaibhav Bhaskar (23053173)", size: SZ_BODY, font: FONT }),
    ],
    spacing: { after: 200 },
  }));
  children.push(new Paragraph({
    children: [
      new TextRun({ text: "Signature of Student 2: ________________", size: SZ_BODY, font: FONT }),
      new TextRun({ text: "      Lakshya Nayyar (23053133)", size: SZ_BODY, font: FONT }),
    ],
    spacing: { after: 200 },
  }));
  children.push(new Paragraph({
    children: [
      new TextRun({ text: "Signature of Supervisor: _______________", size: SZ_BODY, font: FONT }),
      new TextRun({ text: "     Dr. Ajit Kumar Pasayat", size: SZ_BODY, font: FONT }),
    ],
    spacing: { after: 200 },
  }));

  children.push(pageBreak());

  // ════════════════════════════════════════════
  //  PLAGIARISM DECLARATION
  // ════════════════════════════════════════════
  children.push(chapterHeading("PLAGIARISM DECLARATION"));

  children.push(body(
    "We, Vaibhav Bhaskar (Roll No. 23053173) and Lakshya Nayyar (Roll No. 23053133), students of B.Tech (Computer Science and Engineering), School of Computer Engineering, KIIT University, Bhubaneswar, hereby declare that:",
    { indent: true }
  ));
  children.push(bullet('The project report entitled \u201cHydrochemical Analysis and Machine Learning-Based Prediction of Groundwater Quality in Bhubaneswar, Odisha\u201d is entirely our original work.', 0));
  children.push(bullet("All external sources, data, figures, and references have been appropriately cited in accordance with academic norms.", 0));
  children.push(bullet("This work has not been submitted in whole or in part for any other degree, diploma, or academic qualification at any institution.", 0));
  children.push(bullet("We understand that any form of plagiarism is a serious academic offence and accept full responsibility for the originality of this work.", 0));
  children.push(bullet("This report has been scanned through KIIT University's plagiarism detection software (Turnitin/Urkund/iThenticate) and the similarity index is within the permissible limit (< 20%).", 0));

  children.push(...emptyLine(4));
  children.push(new Paragraph({
    children: [new TextRun({ text: "Vaibhav Bhaskar (23053173)          Lakshya Nayyar (23053133)", size: SZ_BODY, font: FONT })],
    spacing: { after: 160 },
  }));
  children.push(body("Signature: ___________________          Signature: ___________________"));
  children.push(...emptyLine(2));
  children.push(body("Date: _______________"));
  children.push(body("Place: Bhubaneswar, Odisha"));

  return {
    children,
    ...sectionProps({
      type: SectionType.NEXT_PAGE,
      header: hdr,
      footer: ftr,
      pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL },
    }),
  };
}

// ══════════════════════════════════════════════════════════════════════════
//  MAIN — assemble document and write file
// ══════════════════════════════════════════════════════════════════════════
async function main() {
  console.log("Building document sections...");

  const coverSection      = buildCoverSection();
  const certificateSection = buildCertificateSection();
  const prelimsSection    = buildPrelimsSection();
  const chaptersSection   = buildChaptersSection();

  const doc = new Document({
    creator: "Vaibhav Bhaskar & Lakshya Nayyar, KIIT University",
    title: "Hydrochemical Analysis and ML-Based Prediction of Groundwater Quality in Bhubaneswar",
    description: "Mini Project Report — School of Computer Engineering, KIIT University, 2024–25",
    styles: {
      default: {
        document: {
          run: { font: FONT, size: SZ_BODY },
          paragraph: { spacing: { line: 360, lineRule: LineRuleType.AUTO } },
        },
      },
    },
    sections: [
      coverSection,
      certificateSection,
      prelimsSection,
      chaptersSection,
    ],
  });

  console.log("Serialising to DOCX...");
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(OUT, buffer);
  console.log(`\n  Report written to: ${OUT}`);
  console.log(`  Size: ${(buffer.length / 1024).toFixed(1)} KB`);
}

main().catch(err => {
  console.error("ERROR:", err.message || err);
  process.exit(1);
});
