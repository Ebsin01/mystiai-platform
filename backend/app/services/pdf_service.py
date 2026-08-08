from io import BytesIO
from datetime import datetime
import os
import html
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import inch

from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# =========================================================
# SAFE TEXT
# =========================================================

def safe_text(value):

    if value is None:
        return ""

    return html.escape(str(value))


# =========================================================
# PAGE FOOTER
# =========================================================

def add_page_footer(canvas, doc):

    canvas.saveState()

    width, height = A4

    canvas.setStrokeColor(
        colors.HexColor("#D0D7DE")
    )

    canvas.setLineWidth(0.5)

    canvas.line(
        40,
        35,
        width - 40,
        35,
    )

    canvas.setFont(
        "Helvetica",
        8,
    )

    canvas.setFillColor(
        colors.HexColor("#6B7280")
    )

    canvas.drawString(
        40,
        22,
        "AI Palmistry Intelligence Platform",
    )

    canvas.drawRightString(
        width - 40,
        22,
        f"Page {doc.page}",
    )

    canvas.restoreState()


# =========================================================
# FIND PALM IMAGE
# =========================================================

def find_palm_image(report):

    """
    Finds the palm image associated with the analysis.

    image_filename comes from PalmAnalysis.image_filename.
    """

    analysis = getattr(report, "analysis", None)

    if not analysis:
        print("PDF PALM IMAGE: no analysis on report")
        return None

    image_filename = getattr(analysis, "image_filename", None)

    if not image_filename:
        print("PDF PALM IMAGE: analysis.image_filename is empty or None")
        return None

    # Normalize values
    db_value = str(image_filename)
    basename = os.path.basename(db_value)

    # Determine backend base directory (two levels up from this file -> backend folder)
    backend_dir = Path(__file__).resolve().parents[2]

    # Candidate directories to search
    candidate_paths = []

    # If DB contains absolute path, check it first
    if Path(db_value).is_absolute():
        candidate_paths.append(Path(db_value))

    # If DB value contains a relative path (e.g. uploads/palms/xxx.jpg), join with backend_dir
    candidate_paths.append(backend_dir.joinpath(db_value))

    # Common upload locations
    candidate_paths.append(backend_dir.joinpath('uploads', basename))
    candidate_paths.append(backend_dir.joinpath('uploads', 'palms', basename))
    candidate_paths.append(backend_dir.joinpath('app', 'uploads', basename))
    candidate_paths.append(backend_dir.joinpath('static', basename))
    candidate_paths.append(backend_dir.joinpath('images', basename))

    # Also try backend root + basename
    candidate_paths.append(backend_dir.joinpath(basename))

    # Helper: case-insensitive resolver within the parent dir
    def resolve_case_insensitive(p: Path):
        if p.exists():
            return p
        parent = p.parent
        if not parent.exists():
            return None
        try:
            for f in parent.iterdir():
                if f.name.lower() == p.name.lower():
                    return f
        except Exception:
            return None
        return None

    # Logging
    print("PDF PALM IMAGE - db filename:", db_value)
    print("PDF PALM IMAGE - basename:", basename)
    print("PDF PALM IMAGE - backend_dir:", str(backend_dir))

    # Search candidates
    for p in candidate_paths:
        try:
            p = Path(p)
            resolved = resolve_case_insensitive(p)
            exists = resolved is not None and resolved.is_file()
            print("PDF PALM IMAGE - checking:", str(p), "-> exists:", exists)
            if exists:
                final = str(resolved)
                print("PDF PALM IMAGE FOUND:", final)
                return final
        except Exception as e:
            print("PDF PALM IMAGE - error checking path:", p, e)

    print("PDF PALM IMAGE NOT FOUND:", db_value)
    return None


# =========================================================
# CREATE PDF
# =========================================================

def create_pdf(report):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,

        rightMargin=40,
        leftMargin=40,
        topMargin=45,
        bottomMargin=50,
    )

    # =====================================================
    # STYLES
    # =====================================================

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#123B6D"),
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#6B7280"),
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#123B6D"),
        spaceBefore=8,
        spaceAfter=10,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=16,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#374151"),
        spaceAfter=8,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#6B7280"),
    )

    personality_style = ParagraphStyle(
        "Personality",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#7C3AED"),
        spaceAfter=15,
    )

    score_header_style = ParagraphStyle(
        "ScoreHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=colors.white,
        alignment=TA_CENTER,
    )

    score_text_style = ParagraphStyle(
        "ScoreText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=colors.HexColor("#374151"),
    )

    # =====================================================
    # STORY
    # =====================================================

    story = []

    # =====================================================
    # LOGO
    # =====================================================

    logo = os.path.join(
        "assets",
        "download.png"
    )

    if os.path.exists(logo):

        img = Image(logo)

        img.drawWidth = 1.25 * inch
        img.drawHeight = 1.25 * inch

        img.hAlign = "CENTER"

        story.append(img)

        story.append(
            Spacer(1, 10)
        )

    # =====================================================
    # TITLE
    # =====================================================

    story.append(
        Paragraph(
            "AI PALMISTRY",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "INTELLIGENCE REPORT",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "AI-assisted palm analysis and personality interpretation",
            subtitle_style,
        )
    )

    # =====================================================
    # USER INFORMATION
    # =====================================================

    user_name = "N/A"
    user_email = "N/A"

    if getattr(report, "user", None):

        user_name = (
            report.user.full_name
            if report.user.full_name
            else "N/A"
        )

        user_email = (
            report.user.email
            if report.user.email
            else "N/A"
        )

    created_date = datetime.now().strftime(
        "%d %B %Y"
    )

    user_data = [
        [
            Paragraph(
                "<b>User</b>",
                score_text_style,
            ),
            Paragraph(
                safe_text(user_name),
                score_text_style,
            ),
        ],
        [
            Paragraph(
                "<b>Email</b>",
                score_text_style,
            ),
            Paragraph(
                safe_text(user_email),
                score_text_style,
            ),
        ],
        [
            Paragraph(
                "<b>Report Date</b>",
                score_text_style,
            ),
            Paragraph(
                created_date,
                score_text_style,
            ),
        ],
        [
            Paragraph(
                "<b>Analysis ID</b>",
                score_text_style,
            ),
            Paragraph(
                safe_text(report.analysis_id),
                score_text_style,
            ),
        ],
    ]

    user_table = Table(
        user_data,
        colWidths=[
            120,
            330,
        ],
    )

    user_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#EEF4FA"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    colors.HexColor("#D1D5DB"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#E5E7EB"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(user_table)

    story.append(
        Spacer(1, 25)
    )

    # =====================================================
    # PALM IMAGE
    # =====================================================

    story.append(
        Paragraph(
            "Analyzed Palm",
            heading_style,
        )
    )

    palm_image_path = find_palm_image(report)

    if palm_image_path:

        try:

            palm_image = Image(
                palm_image_path
            )

            # Keep image inside A4 content area
            max_width = 3.8 * inch
            max_height = 4.5 * inch

            original_width = palm_image.imageWidth
            original_height = palm_image.imageHeight

            if original_width and original_height:

                scale = min(
                    max_width / original_width,
                    max_height / original_height,
                )

                palm_image.drawWidth = (
                    original_width * scale
                )

                palm_image.drawHeight = (
                    original_height * scale
                )

            palm_image.hAlign = "CENTER"

            story.append(
                palm_image
            )

            story.append(
                Spacer(1, 10)
            )

            story.append(
                Paragraph(
                    "Palm image used for AI analysis",
                    small_style,
                )
            )

            story.append(
                Spacer(1, 20)
            )

        except Exception as e:

            print(
                "PDF IMAGE ERROR:",
                e
            )

            story.append(
                Paragraph(
                    "Palm image could not be loaded.",
                    small_style,
                )
            )

            story.append(
                Spacer(1, 15)
            )

    else:

        story.append(
            Paragraph(
                "Palm image is not available.",
                small_style,
            )
        )

        story.append(
            Spacer(1, 15)
        )

    # =====================================================
    # PALM ANALYSIS
    # =====================================================

    story.append(
        Paragraph(
            "Palm Analysis",
            heading_style,
        )
    )

    analysis = getattr(
        report,
        "analysis",
        None,
    )

    if analysis:

        palm_data = [
            [
                Paragraph(
                    "Feature",
                    score_header_style,
                ),
                Paragraph(
                    "Result",
                    score_header_style,
                ),
            ],
            [
                Paragraph(
                    "Palm Shape",
                    score_text_style,
                ),
                Paragraph(
                    safe_text(
                        getattr(
                            analysis,
                            "palm_shape",
                            "N/A",
                        )
                    ),
                    score_text_style,
                ),
            ],
            [
                Paragraph(
                    "Heart Line",
                    score_text_style,
                ),
                Paragraph(
                    safe_text(
                        getattr(
                            analysis,
                            "heart_line",
                            "N/A",
                        )
                    ),
                    score_text_style,
                ),
            ],
            [
                Paragraph(
                    "Head Line",
                    score_text_style,
                ),
                Paragraph(
                    safe_text(
                        getattr(
                            analysis,
                            "head_line",
                            "N/A",
                        )
                    ),
                    score_text_style,
                ),
            ],
            [
                Paragraph(
                    "Life Line",
                    score_text_style,
                ),
                Paragraph(
                    safe_text(
                        getattr(
                            analysis,
                            "life_line",
                            "N/A",
                        )
                    ),
                    score_text_style,
                ),
            ],
        ]

        palm_table = Table(
            palm_data,
            colWidths=[
                180,
                270,
            ],
        )

        palm_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#123B6D"),
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.6,
                        colors.HexColor("#D1D5DB"),
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.HexColor("#F9FAFB"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                ]
            )
        )

        story.append(
            palm_table
        )

        story.append(
            Spacer(1, 25)
        )

    # =====================================================
    # PERSONALITY TYPE
    # =====================================================

    story.append(
        Paragraph(
            "Personality Profile",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            safe_text(
                report.personality_type
            ),
            personality_style,
        )
    )

    # =====================================================
    # SUMMARY
    # =====================================================

    story.append(
        Paragraph(
            "AI Personality Summary",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            safe_text(report.summary),
            body_style,
        )
    )

    story.append(
        Spacer(1, 15)
    )

    # =====================================================
    # PERSONALITY SCORES
    # =====================================================

    story.append(
        Paragraph(
            "Personality Scores",
            heading_style,
        )
    )

    score_fields = [
        ("Optimism", report.optimism),
        ("Leadership", report.leadership),
        ("Confidence", report.confidence),
        ("Creativity", report.creativity),
        ("Communication", report.communication),
        ("Decision Making", report.decision_making),
        (
            "Emotional Intelligence",
            report.emotional_intelligence,
        ),
        (
            "Stress Management",
            report.stress_management,
        ),
        ("Adaptability", report.adaptability),
        ("Risk Taking", report.risk_taking),
        (
            "Emotional Balance",
            report.emotional_balance,
        ),
    ]

    score_data = [
        [
            Paragraph(
                "Trait",
                score_header_style,
            ),
            Paragraph(
                "Score",
                score_header_style,
            ),
        ]
    ]

    for trait, score in score_fields:

        display_score = (
            "N/A"
            if score is None
            else str(round(float(score), 1))
        )

        score_data.append(
            [
                Paragraph(
                    trait,
                    score_text_style,
                ),
                Paragraph(
                    display_score,
                    score_text_style,
                ),
            ]
        )

    score_table = Table(
        score_data,
        colWidths=[
            300,
            150,
        ],
        repeatRows=1,
    )

    score_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#123B6D"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#D1D5DB"),
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.HexColor("#F9FAFB"),
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (1, -1),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(
        score_table
    )

    story.append(
        Spacer(1, 25)
    )

    # =====================================================
    # AI INTERPRETATIONS
    # =====================================================

    sections = [
        (
            "Career Recommendation",
            report.career,
        ),
        (
            "Relationship Analysis",
            report.relationship,
        ),
        (
            "Health & Wellbeing",
            report.health,
        ),
        (
            "Strengths",
            report.strengths,
        ),
        (
            "Weaknesses",
            report.weaknesses,
        ),
    ]

    for heading, content in sections:

        story.append(
            Paragraph(
                safe_text(heading),
                heading_style,
            )
        )

        story.append(
            Paragraph(
                safe_text(content),
                body_style,
            )
        )

        story.append(
            Spacer(1, 10)
        )

    # =====================================================
    # DISCLAIMER
    # =====================================================

    story.append(
        Spacer(1, 20)
    )

    disclaimer_data = [
        [
            Paragraph(
                "<b>Disclaimer</b><br/>"
                "This report is generated using AI-assisted palm "
                "analysis and is intended for entertainment and "
                "self-reflection purposes. It should not be treated "
                "as scientific, medical, psychological, financial, "
                "or professional advice.",
                small_style,
            )
        ]
    ]

    disclaimer_table = Table(
        disclaimer_data,
        colWidths=[450],
    )

    disclaimer_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#FFF7ED"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor("#FED7AA"),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
            ]
        )
    )

    story.append(
        disclaimer_table
    )

    # =====================================================
    # BUILD
    # =====================================================

    doc.build(
        story,
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer,
    )

    pdf = buffer.getvalue()

    buffer.close()

    return pdf