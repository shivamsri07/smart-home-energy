# backend/app/modules/conversational_ai/service.py

from abc import ABC, abstractmethod
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from app.models.user import User
from app.models.device import Device, Telemetry
from .parser import DeterministicParser, LLMParser

class ConversationalService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.executor = None # No longer needed, logic is in the Executable objects
        self.parsers = [
            DeterministicParser(),
            LLMParser(),
        ]

    def answer_question(self, question: str) -> Dict[str, Any]:
        executable_query: Optional[ExecutableQuery] = None
        
        for parser in self.parsers:
            executable_query = parser.parse(question, self.user.devices)
            if executable_query:
                print(f"Successfully parsed with {parser.__class__.__name__}")
                break

        print(f"executable_query: {executable_query.__class__.__name__}")
        if executable_query:
            try:
                result_data = executable_query.execute(self.db, self.user)
                summary = self._format_summary(result_data)
                return {"summary": summary, "data": result_data.get("data"), "sql_query_for_debug": result_data.get("sql_query")}
            except PermissionError as e:
                return {"summary": f"Execution denied: {e}"}
            except Exception as e:
                print(str(e))
                return {"summary": f"{str(e)}"}
    
        return {"summary": "I'm sorry, I couldn't understand that question."}

    def _format_summary(self, result: Dict) -> str:
        metric = result.get("metric")
        if metric == "RAW_SQL":
            return result.get("summary_template", "Here is the data I found.")
        
        kwargs = result.get("kwargs", {})
        device_str = kwargs.get("device_name") or "all your devices"
        value = result.get('value')
        
        if value is None:
            return f"I found no data for {device_str} in the specified time period."

        if metric in ["SUM", "AVG", "MIN", "MAX"]:
            return f"The {metric.lower()} energy usage for {device_str} was {value:.2f} Watts."

        return "Here is the data I found."