# backend/app/modules/conversational_ai/executables.py

from abc import ABC, abstractmethod
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import uuid
from datetime import datetime

from app.models.user import User
from app.models.device import Telemetry

class ExecutableQuery(ABC):
    """An abstract class representing a query that can be executed."""
    @abstractmethod
    def execute(self, db: Session, user: User) -> Dict[str, Any]:
        """Executes the query and returns a dictionary of results."""
        pass

class StructuredExecutable(ExecutableQuery):
    """An executable query built from structured, trusted parameters."""
    def __init__(self, metric: str, device_ids: List[uuid.UUID], time_start: datetime, time_end: datetime, **kwargs):
        self.metric = metric
        self.device_ids = device_ids
        self.time_start = time_start
        self.time_end = time_end
        self.kwargs = kwargs

    def execute(self, db: Session, user: User) -> Dict[str, Any]:
        user_owned_device_ids = {str(d.id) for d in user.devices}
        query_device_ids = {str(d_id) for d_id in self.device_ids}
        if not query_device_ids.issubset(user_owned_device_ids):
            raise PermissionError("Attempted to query unauthorized devices.")

        base_query = db.query(Telemetry).filter(
            Telemetry.device_id.in_(self.device_ids),
            Telemetry.timestamp >= self.time_start,
            Telemetry.timestamp <= self.time_end,
        )

        if self.metric in ["SUM", "AVG", "MIN", "MAX"]:
            metric_map = {"SUM": func.sum(Telemetry.energy_usage), "AVG": func.avg(Telemetry.energy_usage), "MIN": func.min(Telemetry.energy_usage), "MAX": func.max(Telemetry.energy_usage)}
            aggregate_function = metric_map[self.metric]
            result_value = base_query.with_entities(aggregate_function).scalar()
            return {"metric": self.metric, "value": float(result_value) if result_value else None, "kwargs": self.kwargs}
        
        if self.metric == "LIST":
            results = base_query.order_by(Telemetry.timestamp.desc()).limit(100).all()
            return {"metric": "LIST", "data": [{"timestamp": r.timestamp, "energy_usage": float(r.energy_usage)} for r in results], "kwargs": self.kwargs}

        raise ValueError(f"Unsupported metric: {self.metric}")

class RawSQLExecutable(ExecutableQuery):
    """An executable query built from a raw SQL string, with security gates."""
    def __init__(self, sql_query: str, summary_template: str):
        self.sql_query = sql_query.strip()
        self.summary_template = summary_template

    def execute(self, db: Session, user: User) -> Dict[str, Any]:
        if not self.sql_query.upper().startswith("SELECT"):
            raise PermissionError("Execution denied: Only SELECT queries are allowed.")
        
        params = {"user_id": str(user.id)}
        print(f"params: {params}")
        result_proxy = db.execute(text(self.sql_query), params)
        print(f"result_proxy: {result_proxy}")
        results = [row._asdict() for row in result_proxy]
        
        return {"metric": "RAW_SQL", "data": results, "summary_template": self.summary_template, "sql_query": self.sql_query}