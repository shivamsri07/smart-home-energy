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
from app.core.config import settings
import anthropic

class ConversationalService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.parsers = [
            # DeterministicParser(),
            LLMParser(),
        ]
        # Initialize LLM client for haiku generation
        if settings.ANTHROPIC_API_KEY:
            self.llm_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            self.llm_client = None

    def answer_question(self, question: str) -> Dict[str, Any]:
        executable_query: Optional[ExecutableQuery] = None
        
        for parser in self.parsers:
            print(f"question: {question}")
            print(f"user devices: {self.user.devices}")
            executable_query = parser.parse(question, self.user.devices)
            if executable_query:
                print(f"Successfully parsed with {parser.__class__.__name__}")
                break

        print(f"executable_query: {executable_query.__class__.__name__}")
        if executable_query:
            try:
                result_data = executable_query.execute(self.db, self.user)
                summary = self._format_summary(result_data, question)
                return {"summary": summary, "data": result_data.get("data"), "sql_query_for_debug": result_data.get("sql_query")}
            except PermissionError as e:
                return {"summary": f"Execution denied: {e}"}
            except Exception as e:
                print(str(e))
                return {"summary": f"{str(e)}"}
    
        return {"summary": "I'm sorry, I couldn't understand that question."}

    def _format_summary(self, result: Dict, question: str) -> str:
        try:
            # Convert data to JSON-serializable format
            data = result.get("data", [])
            serializable_data = self._make_json_serializable(data)
            
            prompt = f"""
            You are a helpful assistant that summarizes data from a SQL query.
            The user's question is: {question}
            The data is in the following format: {serializable_data}
            Please summarize the data in a concise and informative way. No need to provide any extra information.
            """
            response = self.llm_client.messages.create(
                model="claude-3-5-haiku-20241022",
                system=prompt,
                messages=[{"role": "user", "content": str(serializable_data)}],
                max_tokens=1000
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error summarizing data: {e}")
            return "I'm sorry, I couldn't summarize the data."

    def _make_json_serializable(self, data):
        """Convert data to JSON-serializable format by handling Decimal and other non-serializable types."""
        if isinstance(data, list):
            return [self._make_json_serializable(item) for item in data]
        elif isinstance(data, dict):
            return {key: self._make_json_serializable(value) for key, value in data.items()}
        elif hasattr(data, '__dict__'):
            # Handle SQLAlchemy Row objects
            return {key: self._make_json_serializable(value) for key, value in data.__dict__.items() if not key.startswith('_')}
        elif hasattr(data, 'isoformat'):
            # Handle datetime objects
            return data.isoformat()
        elif hasattr(data, 'quantize'):
            # Handle Decimal objects
            return float(data)
        else:
            return data