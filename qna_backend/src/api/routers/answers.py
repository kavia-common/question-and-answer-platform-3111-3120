from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.models import Answer, Question, User
from src.api.schemas import AnswerOut, GenerateAnswerRequest
from src.api.services.openai_service import call_openai_chat

router = APIRouter(prefix="", tags=["Answers"])


@router.get(
    "/answers",
    response_model=List[AnswerOut],
    summary="List answers",
    description="List all answers, newest first.",
)
def list_answers(db: Session = Depends(get_db)):
    """
    PUBLIC_INTERFACE
    Returns all answers.
    """
    items = db.query(Answer).order_by(Answer.created_at.desc()).all()
    return items


@router.post(
    "/answers",
    response_model=AnswerOut,
    summary="Create/generate answer",
    description="Create an answer for a question. If use_ai is true, the server will call OpenAI to generate an answer.",
    responses={
        400: {"description": "Bad request"},
        404: {"description": "Question not found"},
        401: {"description": "Unauthorized (if manual answer creation by user)"},
    },
)
async def create_answer(
    payload: GenerateAnswerRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(lambda: None),  # Optional auth for AI answers
):
    """
    PUBLIC_INTERFACE
    Creates an answer. When use_ai is true, generates answer content using OpenAI Chat Completions.

    Parameters:
    - payload: GenerateAnswerRequest - question_id, use_ai, body (optional)

    Returns:
    - AnswerOut
    """
    q = db.get(Question, payload.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")

    is_ai = False
    answer_body = payload.body

    if payload.use_ai:
        is_ai = True
        prompt = f"Provide a helpful, concise answer to the following question:\n\nTitle: {q.title}\n\nDetails: {q.body}"
        answer_body = await call_openai_chat(prompt)
    else:
        if not answer_body:
            raise HTTPException(status_code=400, detail="Manual answer requires 'body'.")
        if current_user is None:
            raise HTTPException(status_code=401, detail="Authentication required for manual answers.")

    ans = Answer(
        question_id=q.id,
        user_id=None if is_ai else current_user.id if current_user else None,
        body=answer_body,
        is_ai_generated=is_ai,
    )
    db.add(ans)
    db.commit()
    db.refresh(ans)
    return ans


@router.get(
    "/questions/{question_id}/answers",
    response_model=List[AnswerOut],
    summary="List answers for a question",
    description="Retrieve all answers for a specific question.",
)
def list_answers_for_question(question_id: int, db: Session = Depends(get_db)):
    """
    PUBLIC_INTERFACE
    Returns answers for a given question ID.
    """
    answers = db.query(Answer).filter(Answer.question_id == question_id).order_by(Answer.created_at.desc()).all()
    return answers
