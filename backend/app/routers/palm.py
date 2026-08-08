from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)

from sqlalchemy.orm import Session

import os
import uuid


# ============================================================
# SERVICES
# ============================================================

from app.services.palm_service import (
    process_palm_image
)

from app.services.palm_analysis_engine import (
    analyze_palm
)

from app.services.ai_interpretation_service import (
    generate_ai_interpretation
)


# ============================================================
# DATABASE
# ============================================================

from app.database import (
    get_db
)

from app.model.palm_analysis import (
    PalmAnalysis
)

from app.model.palm_interpretation import (
    PalmInterpretation
)


# ============================================================
# AUTHENTICATION
# ============================================================

from app.auth.dependencies import (
    get_current_user
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(

    prefix="/palm",

    tags=["Palm Analysis"]

)


# ============================================================
# UPLOAD FOLDER
# ============================================================

UPLOAD_FOLDER = "uploads/palms"


os.makedirs(

    UPLOAD_FOLDER,

    exist_ok=True

)


# ============================================================
# 1. ANALYZE PALM IMAGE
# ============================================================

@router.post("/analyze")
async def analyze_palm_image(

    file: UploadFile = File(...),

    current_user=Depends(

        get_current_user

    ),

    db: Session = Depends(

        get_db

    )

):

    # ========================================================
    # VALIDATE FILE TYPE
    # ========================================================

    if not file.content_type:

        raise HTTPException(

            status_code=400,

            detail="File type is missing"

        )


    if not file.content_type.startswith(

        "image/"

    ):

        raise HTTPException(

            status_code=400,

            detail="Only image files are allowed"

        )


    # ========================================================
    # READ IMAGE
    # ========================================================

    image_bytes = await file.read()


    if not image_bytes:

        raise HTTPException(

            status_code=400,

            detail="Uploaded image is empty"

        )


    # ========================================================
    # CREATE UNIQUE FILE NAME
    # ========================================================

    original_filename = (

        file.filename

        or

        "palm_image.jpg"

    )


    unique_filename = (

        str(uuid.uuid4())

        + "_"

        + original_filename

    )


    image_path = os.path.join(

        UPLOAD_FOLDER,

        unique_filename

    )


    # ========================================================
    # SAVE IMAGE
    # ========================================================

    with open(

        image_path,

        "wb"

    ) as image_file:

        image_file.write(

            image_bytes

        )


    # ========================================================
    # MEDIAPIPE PROCESSING
    # ========================================================

    result = process_palm_image(

        image_bytes

    )


    # ========================================================
    # CHECK HAND DETECTION
    # ========================================================

    if not result.get(

        "hand_detected"

    ):

        raise HTTPException(

            status_code=400,

            detail=result.get(

                "message",

                "No hand detected"

            )

        )


    # ========================================================
    # EXTRACT BASIC PALM FEATURES
    # ========================================================

    palm_features = result.get(

        "palm_features",

        {}

    )


    # ========================================================
    # RUN PALM ANALYSIS ENGINE
    # ========================================================

    try:

        classification_result = analyze_palm(

            image_path

        )


    except Exception as error:

        print(

            "Palm classification error:",

            error

        )


        classification_result = {

            "palm_shape": {

                "value": "Unknown",

                "confidence": 0.0

            },

            "heart_line": {

                "classification": "Unknown",

                "confidence": 0.0

            },

            "head_line": {

                "classification": "Unknown",

                "confidence": 0.0

            },

            "life_line": {

                "classification": "Unknown",

                "confidence": 0.0

            }

        }


    # ========================================================
    # EXTRACT CLASSIFICATION DATA
    # ========================================================

    palm_shape_data = (

        classification_result.get(

            "palm_shape",

            {}

        )

    )


    heart_line_data = (

        classification_result.get(

            "heart_line",

            {}

        )

    )


    head_line_data = (

        classification_result.get(

            "head_line",

            {}

        )

    )


    life_line_data = (

        classification_result.get(

            "life_line",

            {}

        )

    )


    # ========================================================
    # CREATE DATABASE RECORD
    # ========================================================

    analysis = PalmAnalysis(

        user_id=current_user.id,


        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        image_filename=original_filename,


        # ----------------------------------------------------
        # BASIC PALM FEATURES
        # ----------------------------------------------------

        palm_width=palm_features.get(

            "palm_width"

        ),


        palm_length=palm_features.get(

            "palm_length"

        ),


        index_finger_length=palm_features.get(

            "index_finger_length"

        ),


        middle_finger_length=palm_features.get(

            "middle_finger_length"

        ),


        # ----------------------------------------------------
        # HAND LANDMARKS
        # ----------------------------------------------------

        landmarks=result.get(

            "landmarks"

        ),


        # ====================================================
        # PALM SHAPE
        # ====================================================

        palm_shape=palm_shape_data.get(

            "value"

        ),


        palm_shape_confidence=palm_shape_data.get(

            "confidence"

        ),


        # ====================================================
        # HEART LINE
        # ====================================================

        heart_line=heart_line_data.get(

            "classification"

        ),


        heart_line_confidence=heart_line_data.get(

            "confidence"

        ),


        # ====================================================
        # HEAD LINE
        # ====================================================

        head_line=head_line_data.get(

            "classification"

        ),


        head_line_confidence=head_line_data.get(

            "confidence"

        ),


        # ====================================================
        # LIFE LINE
        # ====================================================

        life_line=life_line_data.get(

            "classification"

        ),


        life_line_confidence=life_line_data.get(

            "confidence"

        )

    )


    # ========================================================
    # SAVE TO DATABASE
    # ========================================================

    db.add(

        analysis

    )


    db.commit()


    db.refresh(

        analysis

    )


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {

        "message":

            "Palm analyzed successfully",


        "analysis_id":

            analysis.id,


        "image_filename":

            original_filename,


        "palm_features":

            palm_features,


        "classification":

            classification_result,


        "landmarks":

            result.get(

                "landmarks"

            )

    }


# ============================================================
# 2. GET ALL ANALYSES
# ============================================================

@router.get("/analyses")
def get_my_analyses(

    current_user=Depends(

        get_current_user

    ),

    db: Session = Depends(

        get_db

    )

):

    analyses = (
    db.query(PalmAnalysis)
    .filter(
        PalmAnalysis.user_id == current_user.id
    )
    .order_by(
        PalmAnalysis.id.desc()
    )
    .all()
)


    return {

        "count": len(

            analyses

        ),

        "analyses": analyses

    }


# ============================================================
# 3. GET SINGLE ANALYSIS
# ============================================================

@router.get(

    "/analyses/{analysis_id}"

)

def get_analysis_by_id(

    analysis_id: int,


    current_user=Depends(

        get_current_user

    ),


    db: Session = Depends(

        get_db

    )

):

    analysis = (

        db.query(

            PalmAnalysis

        )

        .filter(

            PalmAnalysis.id

            == analysis_id,


            PalmAnalysis.user_id

            == current_user.id

        )

        .first()

    )


    if not analysis:

        raise HTTPException(

            status_code=404,

            detail="Palm analysis not found"

        )


    return analysis


# ============================================================
# 4. DELETE ANALYSIS
# ============================================================

@router.delete(

    "/analyses/{analysis_id}"

)

def delete_analysis(

    analysis_id: int,


    current_user=Depends(

        get_current_user

    ),


    db: Session = Depends(

        get_db

    )

):

    analysis = (

        db.query(

            PalmAnalysis

        )

        .filter(

            PalmAnalysis.id

            == analysis_id,


            PalmAnalysis.user_id

            == current_user.id

        )

        .first()

    )


    if not analysis:

        raise HTTPException(

            status_code=404,

            detail="Palm analysis not found"

        )


    db.delete(

        analysis

    )


    db.commit()


    return {

        "message":

            "Palm analysis deleted successfully",


        "analysis_id":

            analysis_id

    }


# ============================================================
# 5. GET PALM HISTORY
# ============================================================

@router.get(

    "/history"

)

def get_palm_history(

    current_user=Depends(

        get_current_user

    ),


    db: Session = Depends(

        get_db

    )

):

    analyses = (
    db.query(PalmAnalysis)
    .filter(
        PalmAnalysis.user_id == current_user.id
    )
    .order_by(
        PalmAnalysis.id.desc()
    )
    .all()
)


    return analyses


# ============================================================
# 6. GENERATE AI INTERPRETATION
# ============================================================

@router.post(

    "/analyses/{analysis_id}/interpret"

)

def interpret_analysis(

    analysis_id: int,


    current_user=Depends(

        get_current_user

    ),


    db: Session = Depends(

        get_db

    )

):

    # ========================================================
    # FIND ANALYSIS
    # ========================================================

    analysis = (

        db.query(

            PalmAnalysis

        )

        .filter(

            PalmAnalysis.id

            == analysis_id,


            PalmAnalysis.user_id

            == current_user.id

        )

        .first()

    )


    if not analysis:

        raise HTTPException(

            status_code=404,

            detail="Palm analysis not found"

        )


    # ========================================================
    # CHECK EXISTING INTERPRETATION
    # ========================================================

    existing_interpretation = (

        db.query(

            PalmInterpretation

        )

        .filter(

            PalmInterpretation.analysis_id

            == analysis_id

        )

        .first()

    )


    if existing_interpretation:

        return existing_interpretation


    # ========================================================
    # USE STORED PALM SHAPE
    # ========================================================

    palm_shape = (

        analysis.palm_shape

        or

        "Unknown"

    )


    # ========================================================
    # GENERATE AI INTERPRETATION
    # ========================================================

    interpretation_data = (

        generate_ai_interpretation(

            palm_shape=palm_shape,


            palm_width=analysis.palm_width,


            palm_length=analysis.palm_length,


            index_finger_length=(

                analysis.index_finger_length

            ),


            middle_finger_length=(

                analysis.middle_finger_length

            ),


            landmarks=analysis.landmarks

        )

    )


    # ========================================================
    # CREATE INTERPRETATION RECORD
    # ========================================================

    new_interpretation = PalmInterpretation(

        analysis_id=analysis.id,


        user_id=current_user.id,


        palm_shape=palm_shape,


        personality_interpretation=(

            interpretation_data.get(

                "personality"

            )

        ),


        career_interpretation=(

            interpretation_data.get(

                "career"

            )

        ),


        relationship_interpretation=(

            interpretation_data.get(

                "relationships"

            )

        ),


        life_interpretation=(

            interpretation_data.get(

                "life"

            )

        ),


        overall_interpretation=(

            interpretation_data.get(

                "overall_summary"

            )

        )

    )


    # ========================================================
    # SAVE INTERPRETATION
    # ========================================================

    db.add(

        new_interpretation

    )


    db.commit()


    db.refresh(

        new_interpretation

    )


    return new_interpretation


# ============================================================
# 7. GET EXISTING INTERPRETATION
# ============================================================

@router.get(

    "/analyses/{analysis_id}/interpretation"

)

def get_interpretation(

    analysis_id: int,


    current_user=Depends(

        get_current_user

    ),


    db: Session = Depends(

        get_db

    )

):

    interpretation = (

        db.query(

            PalmInterpretation

        )

        .filter(

            PalmInterpretation.analysis_id

            == analysis_id,


            PalmInterpretation.user_id

            == current_user.id

        )

        .first()

    )


    if not interpretation:

        raise HTTPException(

            status_code=404,

            detail="Palm interpretation not found"

        )


    return interpretation