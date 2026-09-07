from pathlib import Path
import json
import shutil
from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
EVALUATION_DIR = BASE_DIR / "evaluation"

FIGURES_DIR = EVALUATION_DIR / "figures"
DATA_DIR = EVALUATION_DIR / "data"
REPORTS_DIR = EVALUATION_DIR / "reports"

PDF_PATH = EVALUATION_DIR / "ProDiag_AI_V2_ML_Evaluation_Report.pdf"
MANIFEST_PATH = EVALUATION_DIR / "evaluation_manifest.json"


# ============================================================
# CLEAN / CREATE PACKAGE DIRECTORIES
# ============================================================

for directory in [FIGURES_DIR, DATA_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# Remove previously packaged files
for directory in [FIGURES_DIR, DATA_DIR, REPORTS_DIR]:
    for item in directory.iterdir():
        if item.is_file():
            item.unlink()


# ============================================================
# COPY ALL RESULTS INTO CORRECT FOLDERS
# ============================================================

copied_files = {
    "figures": [],
    "data": [],
    "reports": [],
}


for source_file in RESULTS_DIR.iterdir():

    if not source_file.is_file():
        continue

    suffix = source_file.suffix.lower()

    # --------------------------------------------------------
    # Images → figures
    # --------------------------------------------------------
    if suffix == ".png":

        destination = FIGURES_DIR / source_file.name
        shutil.copy2(source_file, destination)

        copied_files["figures"].append(source_file.name)

    # --------------------------------------------------------
    # CSV + JSON → data
    # --------------------------------------------------------
    elif suffix in [".csv", ".json"]:

        destination = DATA_DIR / source_file.name
        shutil.copy2(source_file, destination)

        copied_files["data"].append(source_file.name)

    # --------------------------------------------------------
    # TXT → reports
    # --------------------------------------------------------
    elif suffix == ".txt":

        destination = REPORTS_DIR / source_file.name
        shutil.copy2(source_file, destination)

        copied_files["reports"].append(source_file.name)


# Sort file lists
for key in copied_files:
    copied_files[key].sort()


# ============================================================
# LOAD EXPERIMENT RESULTS
# ============================================================

model_comparison_path = RESULTS_DIR / "model_comparison.csv"
health_comparison_path = RESULTS_DIR / "health_score_model_comparison.csv"

failure_df = None
health_df = None

if model_comparison_path.exists():
    failure_df = pd.read_csv(model_comparison_path)

if health_comparison_path.exists():
    health_df = pd.read_csv(health_comparison_path)


# ============================================================
# PDF STYLES
# ============================================================

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleCustom",
    parent=styles["Title"],
    fontSize=22,
    leading=26,
    alignment=TA_CENTER,
    spaceAfter=18,
)

subtitle_style = ParagraphStyle(
    "SubtitleCustom",
    parent=styles["Normal"],
    fontSize=11,
    leading=16,
    alignment=TA_CENTER,
    spaceAfter=20,
)

heading_style = ParagraphStyle(
    "HeadingCustom",
    parent=styles["Heading2"],
    fontSize=15,
    leading=19,
    spaceBefore=12,
    spaceAfter=10,
)

body_style = ParagraphStyle(
    "BodyCustom",
    parent=styles["BodyText"],
    fontSize=9.5,
    leading=14,
    spaceAfter=8,
)


# ============================================================
# PDF DOCUMENT
# ============================================================

doc = SimpleDocTemplate(
    str(PDF_PATH),
    pagesize=A4,
    rightMargin=40,
    leftMargin=40,
    topMargin=40,
    bottomMargin=40,
)

story = []


# ============================================================
# TITLE PAGE
# ============================================================

story.append(
    Paragraph(
        "ProDiag AI V2",
        title_style,
    )
)

story.append(
    Paragraph(
        "Machine Learning Evaluation Report",
        subtitle_style,
    )
)

story.append(
    Paragraph(
        "Agentic Predictive Maintenance Copilot for Industrial Assets",
        subtitle_style,
    )
)

story.append(Spacer(1, 20))

story.append(
    Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        body_style,
    )
)

story.append(
    Paragraph(
        "This report summarizes the predictive maintenance ML experiments, "
        "model comparison, feature analysis, threshold analysis, and health "
        "score regression evaluation performed for ProDiag AI V2.",
        body_style,
    )
)

story.append(PageBreak())


# ============================================================
# 1. EXPERIMENT OVERVIEW
# ============================================================

story.append(
    Paragraph(
        "1. Experiment Overview",
        heading_style,
    )
)

story.append(
    Paragraph(
        "The ProDiag AI V2 ML pipeline evaluates supervised models for "
        "failure prediction and machine health-score estimation. "
        "Isolation Forest remains part of the anomaly-detection layer.",
        body_style,
    )
)

overview_data = [
    ["Component", "Purpose"],
    ["Failure Prediction", "Predict whether failure occurs within the next 1 hour"],
    ["Health Score", "Estimate continuous machine health from 0–100"],
    ["Anomaly Detection", "Detect unusual sensor behaviour using Isolation Forest"],
    ["Feature Analysis", "Evaluate sensor, trend and equipment features"],
    ["Threshold Analysis", "Select an operating threshold for failure prediction"],
]

table = Table(overview_data, colWidths=[150, 340])

table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
        ]
    )
)

story.append(table)
story.append(Spacer(1, 20))


# ============================================================
# 2. FAILURE PREDICTION
# ============================================================

story.append(
    Paragraph(
        "2. Failure Prediction Model Evaluation",
        heading_style,
    )
)

story.append(
    Paragraph(
        "Three supervised classification approaches were evaluated: "
        "Logistic Regression, Random Forest and XGBoost. "
        "The primary model-selection metric was F1-score, with recall "
        "treated as especially important because missed failures can "
        "represent significant maintenance risk.",
        body_style,
    )
)

if failure_df is not None:

    display_df = failure_df.copy()

    # Round numeric columns
    for column in display_df.select_dtypes(include="number").columns:
        display_df[column] = display_df[column].round(4)

    table_data = [display_df.columns.tolist()] + display_df.values.tolist()

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[100] * len(display_df.columns),
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    story.append(table)

story.append(Spacer(1, 15))

story.append(
    Paragraph(
        "<b>Selected failure model: XGBoost</b><br/>"
        "XGBoost achieved the highest F1-score in the evaluated comparison, "
        "with strong precision, recall and ranking performance.",
        body_style,
    )
)


# ============================================================
# 3. HEALTH SCORE
# ============================================================

story.append(
    Paragraph(
        "3. Health Score Regression Evaluation",
        heading_style,
    )
)

story.append(
    Paragraph(
        "Health-score estimation was evaluated as a regression problem. "
        "Linear Regression, Random Forest and XGBoost were compared using "
        "MAE, RMSE and R².",
        body_style,
    )
)

if health_df is not None:

    display_df = health_df.copy()

    for column in display_df.select_dtypes(include="number").columns:
        display_df[column] = display_df[column].round(4)

    table_data = [display_df.columns.tolist()] + display_df.values.tolist()

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[100] * len(display_df.columns),
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    story.append(table)

story.append(Spacer(1, 15))

story.append(
    Paragraph(
        "<b>Selected health-score model: XGBoost</b><br/>"
        "XGBoost achieved the strongest evaluated regression performance "
        "across the primary error and goodness-of-fit metrics.",
        body_style,
    )
)


# ============================================================
# 4. FEATURE IMPORTANCE
# ============================================================

story.append(
    Paragraph(
        "4. Feature Importance & Explainability",
        heading_style,
    )
)

story.append(
    Paragraph(
        "XGBoost feature importance and SHAP analysis were performed to "
        "understand which sensor and trend features contributed most to "
        "the model's predictions.",
        body_style,
    )
)

feature_file = RESULTS_DIR / "xgboost_feature_importance.csv"

if feature_file.exists():

    feature_df = pd.read_csv(feature_file)

    for column in feature_df.select_dtypes(include="number").columns:
        feature_df[column] = feature_df[column].round(4)

    feature_df = feature_df.head(10)

    table_data = [feature_df.columns.tolist()] + feature_df.values.tolist()

    table = Table(
        table_data,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ]
        )
    )

    story.append(table)


# ============================================================
# 5. THRESHOLD ANALYSIS
# ============================================================

story.append(
    Paragraph(
        "5. Failure Prediction Threshold Analysis",
        heading_style,
    )
)

story.append(
    Paragraph(
        "Multiple probability thresholds were evaluated to understand "
        "the precision/recall trade-off. The operating threshold should "
        "be treated as an engineering decision rather than a universal "
        "ML default.",
        body_style,
    )
)

threshold_file = RESULTS_DIR / "xgboost_threshold_analysis.csv"

if threshold_file.exists():

    threshold_df = pd.read_csv(threshold_file)

    for column in threshold_df.select_dtypes(include="number").columns:
        threshold_df[column] = threshold_df[column].round(4)

    table_data = [threshold_df.columns.tolist()] + threshold_df.values.tolist()

    table = Table(
        table_data,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ]
        )
    )

    story.append(table)


# ============================================================
# 6. FIGURES
# ============================================================

story.append(PageBreak())

story.append(
    Paragraph(
        "6. Evaluation Visualizations",
        heading_style,
    )
)

# Important visualizations
preferred_figures = [
    "model_comparison.png",
    "roc_curve_comparison.png",
    "precision_recall_comparison.png",
    "confusion_matrices.png",
    "xgboost_feature_importance.png",
    "xgboost_shap_summary.png",
    "xgboost_threshold_analysis.png",
    "health_score_model_comparison.png",
    "health_score_predicted_vs_actual.png",
    "health_score_residual_distribution.png",
]

for figure_name in preferred_figures:

    figure_path = RESULTS_DIR / figure_name

    if not figure_path.exists():
        continue

    story.append(
        Paragraph(
            figure_name.replace("_", " ").replace(".png", "").title(),
            body_style,
        )
    )

    try:
        image = Image(str(figure_path))

        # Keep figures inside A4 page width
        max_width = 500
        max_height = 330

        scale = min(
            max_width / image.imageWidth,
            max_height / image.imageHeight,
            1,
        )

        image.drawWidth = image.imageWidth * scale
        image.drawHeight = image.imageHeight * scale

        story.append(image)
        story.append(Spacer(1, 15))

    except Exception as exc:
        print(f"[WARNING] Could not add {figure_name}: {exc}")


# ============================================================
# BUILD PDF
# ============================================================

doc.build(story)


# ============================================================
# CREATE MANIFEST
# ============================================================

manifest = {
    "project": "ProDiag AI V2",
    "package_type": "ML Evaluation Package",
    "generated_at": datetime.now().isoformat(),
    "source_directory": str(RESULTS_DIR),
    "package_directory": str(EVALUATION_DIR),
    "structure": {
        "figures": copied_files["figures"],
        "data": copied_files["data"],
        "reports": copied_files["reports"],
        "pdf": PDF_PATH.name,
    },
    "counts": {
        "figures": len(copied_files["figures"]),
        "data_files": len(copied_files["data"]),
        "reports": len(copied_files["reports"]),
    },
}


with open(MANIFEST_PATH, "w", encoding="utf-8") as file:
    json.dump(manifest, file, indent=2)


# ============================================================
# FINAL OUTPUT
# ============================================================

print()
print("=" * 65)
print("PRODIAG AI V2 - ML EVALUATION PACKAGE CREATED")
print("=" * 65)

print()
print("Evaluation folder:")
print(EVALUATION_DIR)

print()
print("Figures:")
print(f"  {FIGURES_DIR}")
print(f"  {len(copied_files['figures'])} files")

print()
print("Data:")
print(f"  {DATA_DIR}")
print(f"  {len(copied_files['data'])} files")

print()
print("Reports:")
print(f"  {REPORTS_DIR}")
print(f"  {len(copied_files['reports'])} files")

print()
print("PDF:")
print(f"  {PDF_PATH}")

print()
print("Manifest:")
print(f"  {MANIFEST_PATH}")

print()
print("=" * 65)
print("PACKAGE COMPLETE")
print("=" * 65)
