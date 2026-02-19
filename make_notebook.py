"""Generate Jupyter notebook from the analysis script."""
import json, re

def make_cell(cell_type, source_lines):
    """Create a notebook cell."""
    # Ensure each line ends with \n except the last
    formatted = []
    for i, line in enumerate(source_lines):
        if i < len(source_lines) - 1:
            formatted.append(line + "\n")
        else:
            formatted.append(line)
    cell = {
        "cell_type": cell_type,
        "metadata": {},
        "source": formatted
    }
    if cell_type == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
    return cell

cells = []

# ---- MARKDOWN: Title ----
cells.append(make_cell("markdown", [
    "# Publication-Quality Hydrochemical Intelligence Report",
    "## Groundwater Quality Analysis — Bhubaneswar, 2024",
    "### Three Seasons: Premonsoon, Monsoon, Postmonsoon",
    "",
    "**Target Journals:** Environmental Monitoring & Assessment (Springer) / Journal of Hydrology",
    "",
    "**Abstract:** This report presents a comprehensive hydrochemical analysis of groundwater quality across 15 monitoring stations in Bhubaneswar, sampled during premonsoon, monsoon, and postmonsoon seasons of 2024. The study integrates exploratory data analysis, seasonal dynamics, drinking water safety assessment (IS 10500:2012), multivariate statistical techniques (PCA, cluster analysis), hydrochemical facies classification (Piper & Gibbs diagrams), and machine learning models (Random Forest, SVR, Gradient Boosting, Neural Network) for water quality prediction. Results reveal dominant Ca-Cl type groundwater with rock-weathering as the primary controlling mechanism, seasonal variability driven by monsoon recharge and premonsoon concentration effects, and actionable insights for sustainable groundwater management."
]))

# ---- CODE: Imports ----
cells.append(make_cell("markdown", [
    "## 1. Setup and Configuration"
]))

# Read the full script
with open(r'c:\Users\KIIT0001\Desktop\Water\hydrochemical_analysis.py', 'r', encoding='utf-8') as f:
    full_code = f.read()

# Split by the major section markers
# Pattern: lines starting with "# ===" (70+ equals signs)
lines = full_code.split('\n')

# Find section boundaries
section_starts = []
for i, line in enumerate(lines):
    if line.strip().startswith('# ====') and len(line.strip()) > 50:
        section_starts.append(i)

# Group into sections (each section = header_line, content until next header)
sections = []
for idx, start in enumerate(section_starts):
    end = section_starts[idx + 1] if idx + 1 < len(section_starts) else len(lines)
    section_lines = lines[start:end]
    # Find the title (non-separator line within the header block)
    title = ""
    for sl in section_lines[:5]:
        sl_stripped = sl.strip().lstrip('#').strip()
        if sl_stripped and not sl_stripped.startswith('===') and not sl_stripped.startswith('---'):
            title = sl_stripped
            break
    sections.append((title, section_lines))

# Now create code cells for each section
# First section is imports (before any TASK/STEP)
# Let me find meaningful split points

# Strategy: create cells at each section boundary
md_titles = {
    "IMPORTS": "### Imports",
    "CONFIGURATION": "## 2. Configuration",
    "UTILITY": "## 3. Utility Functions",
    "TASK 1": "## 4. Task 1: Data Loading & Cleaning",
    "SYNTHETIC": "## 5. Synthetic Data Generation",
    "TASK 2": "## 6. Task 2: Data Validation",
    "TASK 3": "## 7. Task 3: EDA & Seasonal Dynamics",
    "TASK 4": "## 8. Task 4: Drinking Water Risk Intelligence (IS 10500:2012)",
    "TASK 5": "## 9. Task 5: Source Analysis",
    "TASK 6": "## 10. Task 6: Machine Learning",
    "TASK 7": "## 11. Task 7: Scientific Insights",
    "MAIN": "## 12. Run Pipeline",
}

for title, section_lines in sections:
    # Add markdown header
    md_title = None
    for key, val in md_titles.items():
        if key in title.upper():
            md_title = val
            break
    
    if md_title:
        cells.append(make_cell("markdown", [md_title]))
    
    # Strip the separator lines from the code
    code_lines = []
    for sl in section_lines:
        if sl.strip().startswith('# ====') and len(sl.strip()) > 50:
            continue
        code_lines.append(sl)
    
    # Remove leading/trailing empty lines
    while code_lines and not code_lines[0].strip():
        code_lines.pop(0)
    while code_lines and not code_lines[-1].strip():
        code_lines.pop()
    
    if code_lines:
        cells.append(make_cell("code", code_lines))

# Build notebook
notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0",
            "mimetype": "text/x-python",
            "file_extension": ".py"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open(r'c:\Users\KIIT0001\Desktop\Water\Hydrochemical_Analysis_Report.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print(f"Notebook created with {len(cells)} cells")
for i, c in enumerate(cells):
    ct = c['cell_type']
    preview = c['source'][0][:60] if c['source'] else ''
    print(f"  Cell {i+1} [{ct}]: {preview}")
