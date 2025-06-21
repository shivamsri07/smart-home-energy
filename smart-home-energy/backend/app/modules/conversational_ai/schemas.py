# backend/app/modules/conversational_ai/schemas.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    """The JSON body for a /query API request."""
    question: str

class QueryResponse(BaseModel):
    """The final JSON response sent to the user."""
    summary: str
    data: Optional[List[Dict[str, Any]]] = None
    sql_query_for_debug: Optional[str] = None