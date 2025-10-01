from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.auth import get_current_user
from src.api.database import get_db
from src.api.models import Question, User
from src.api.schemas import QuestionCreate, QuestionOut

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post(
    "",
    response_model=QuestionOut,
    summary="Create question",
    description="Create a new question. Requires authentication.",
    responses={
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
    },
)
def create_question(
    question_in: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    PUBLIC_INTERFACE
    Creates a question associated with the authenticated user.

    Parameters:
    - question_in: QuestionCreate - title, body

    Returns:
    - QuestionOut
    """
    q = Question(
        title=question_in.title,
        body=question_in.body,
        user_id=current_user.id,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


@router.get(
    "",
    response_model=List[QuestionOut],
    summary="List questions",
    description="Retrieve list of all questions ordered by newest first.",
)
def list_questions(db: Session = Depends(get_db)):
    """
    PUBLIC_INTERFACE
    Returns a list of all questions.
    """
    items = db.query(Question).order_by(Question.created_at.desc()).all()
    return items


@router.get(
    "/{question_id}",
    response_model=QuestionOut,
    summary="Get question by ID",
    description="Retrieve a single question by its ID.",
)
def get_question(question_id: int, db: Session = Depends(get_db)):
    """
    PUBLIC_INTERFACE
    Get a question by ID.
    """
    q = db.get(Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")
    return q
