# backend/app/modules/conversational_ai/endpoints.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User
from ..auth.dependencies import get_current_user
from . import schemas
from .service import ConversationalService

router = APIRouter(
    prefix="/query",
    tags=["Conversational AI"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=schemas.QueryResponse)
def get_query_answer(
    request: schemas.QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accepts a natural language question and returns a structured answer.
    """
    service = ConversationalService(db=db, user=current_user)
    answer = service.answer_question(question=request.question)
    return answer