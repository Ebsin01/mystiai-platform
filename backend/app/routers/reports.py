from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.auth.dependencies import get_current_user

from app.model.palm_analysis import PalmAnalysis
from app.model.personality_report import PersonalityReport

from app.services.personality_engine import generate_personality_report
from app.services.notification_service import create_notification

router = APIRouter(
    prefix="/reports",
    tags=["Personality Reports"]
)

@router.post("/{analysis_id}")
def create_report(
    analysis_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    analysis = (
        db.query(PalmAnalysis)
        .filter(
            PalmAnalysis.id == analysis_id,
            PalmAnalysis.user_id == current_user.id
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Palm analysis not found"
        )

    existing = (
        db.query(PersonalityReport)
        .filter(PersonalityReport.analysis_id == analysis_id)
        .first()
    )

    if existing:
        return existing

    report = generate_personality_report(analysis)

    new_report = PersonalityReport(
        analysis_id=analysis.id,
        user_id=current_user.id,

        optimism=report["optimism"],
        leadership=report["leadership"],
        confidence=report["confidence"],
        creativity=report["creativity"],
        communication=report["communication"],
        decision_making=report["decision_making"],

        emotional_intelligence=report["emotional_intelligence"],
        stress_management=report["stress_management"],
        adaptability=report["adaptability"],
        risk_taking=report["risk_taking"],
        emotional_balance=report["emotional_balance"],

        personality_type=report["personality_type"],

        strengths=report["strengths"],
        weaknesses=report["weaknesses"],

        career=report["career"],
        relationship=report["relationship"],
        health=report["health"],

        summary=report["summary"]
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    create_notification(
    db=db,
    user_id=current_user.id,
    title="Personality Report Ready",
    message="Your AI personality report has been generated successfully.",
    notification_type="report"
    )

    return new_report