import io
import csv
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def build_candidate_csv(candidates: list[dict]) -> bytes:
    output = io.StringIO()
    fieldnames = [
        "rank",
        "resume_id",
        "filename",
        "overall_score",
        "skill_score",
        "experience_score",
        "education_score",
        "keyword_score",
        "matched_skills",
        "missing_skills",
        "reasoning"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for candidate in candidates:
        row = candidate.copy()
        row["matched_skills"] = ", ".join(candidate.get("matched_skills", []))
        row["missing_skills"] = ", ".join(candidate.get("missing_skills", []))
        writer.writerow(row)

    return output.getvalue().encode("utf-8")

def build_candidate_pdf(candidates: list[dict]) -> bytes:
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm
    )
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle("Cell", parent=styles["BodyText"], fontSize=7, leading=9)

    header = [
        "Rank",
        "Resume",
        "Overall",
        "Skill",
        "Experience",
        "Education",
        "Keyword",
        "Matched Skills",
        "Reasoning"
    ]

    rows = [header]

    for candidate in candidates:
        rows.append([
            str(candidate.get("rank", "")),
            Paragraph(str(candidate.get("filename", "")), body_style),
            str(candidate.get("overall_score", "")),
            str(candidate.get("skill_score", "")),
            str(candidate.get("experience_score", "")),
            str(candidate.get("education_score", "")),
            str(candidate.get("keyword_score", "")),
            Paragraph(", ".join(candidate.get("matched_skills", [])), body_style),
            Paragraph(str(candidate.get("reasoning", "")), body_style)
        ])

    table = Table(rows, colWidths=[12 * mm, 40 * mm, 16 * mm, 14 * mm, 20 * mm, 20 * mm, 16 * mm, 48 * mm, 91 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1"))
    ]))

    document.build([table])
    return buffer.getvalue()
