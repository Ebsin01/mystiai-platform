from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.model.personality_report import PersonalityReport
from app.services.pdf_service import create_pdf

router = APIRouter(
    prefix="/pdf",
    tags=["PDF"]
)


@router.get("/{analysis_id}")
def download_pdf(
    analysis_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    report = (
        db.query(PersonalityReport)
        .options(joinedload(PersonalityReport.user))
        .filter(
            PersonalityReport.analysis_id == analysis_id,
            PersonalityReport.user_id == current_user.id,
        )
        .first()
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    pdf_bytes = create_pdf(report)

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="AI_Report_{analysis_id}.pdf"'
        },
    )