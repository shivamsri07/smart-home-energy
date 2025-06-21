# backend/app/modules/conversational_ai/parser.py

from typing import Optional, List
from datetime import datetime, timedelta, timezone
import json
import anthropic
from abc import ABC, abstractmethod

from .executable import ExecutableQuery, StructuredExecutable, RawSQLExecutable
from app.models.device import Device
from app.core.config import settings
import anthropic



class QueryParser(ABC):
    @abstractmethod
    def parse(self, question: str, user_devices: List[Device]) -> Optional[ExecutableQuery]:
        pass

class DeterministicParser(QueryParser):
    def parse(self, question: str, user_devices: List[Device]) -> Optional[ExecutableQuery]:
        q_lower = question.lower()
        try:
            metric = self._extract_metric(q_lower)
            target_devices = self._extract_devices(q_lower, user_devices)
            time_start, time_end = self._extract_timeframe(q_lower)
            if not target_devices: return None
            device_name = target_devices[0].name if len(target_devices) == 1 else None
            return StructuredExecutable(metric=metric, device_ids=[d.id for d in target_devices], time_start=time_start, time_end=time_end, device_name=device_name)
        except ValueError:
            return None

    def _extract_metric(self, q: str) -> str:
        if "how much" in q or "total" in q: return "SUM"
        if "average" in q or "avg" in q: return "AVG"
        if "highest" in q or "max" in q or "most" in q: return "MAX"
        if "lowest" in q or "min" in q or "least" in q: return "MIN"
        if "list" in q or "show me" in q: return "LIST"
        raise ValueError("No deterministic metric found.")

    def _extract_devices(self, q: str, devices: List[Device]) -> List[Device]:
        found_devices = [device for device in devices if device.name.lower() in q]
        if found_devices: return found_devices
        if "device" in q or "devices" in q: return devices
        return devices

    def _extract_timeframe(self, q: str) -> (datetime, datetime):
        now = datetime.now(timezone.utc)
        if "yesterday" in q:
            start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0)
            end = start.replace(hour=23, minute=59, second=59)
            return start, end
        if "last week" in q:
            start = (now - timedelta(days=now.weekday(), weeks=1)).replace(hour=0, minute=0, second=0)
            end = (start + timedelta(days=6)).replace(hour=23, minute=59, second=59)
            return start, end
        return now - timedelta(days=1), now

class LLMParser(QueryParser):
    def __init__(self):
        if settings.ANTHROPIC_API_KEY:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            self.client = None

    def parse(self, question: str, user_devices: List[Device]) -> Optional[ExecutableQuery]:
        if not self.client: return None
        system_prompt = self._build_prompt(user_devices)
        try:
            # --- Real API call to Claude would be here ---
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                system=system_prompt,
                messages=[{"role": "user", "content": question}],
                max_tokens=1000
            )
            raw_json = message.content[0].text

            llm_response = json.loads(raw_json)
            sql_query, summary = llm_response.get("sql"), llm_response.get("summary")
            if not sql_query or not summary: return None

            print(f"sql_query: {sql_query}")
            print(f"summary: {summary}")
            return RawSQLExecutable(sql_query=sql_query, summary_template=summary)
        except Exception as e:
            print(f"Claude LLM Parser failed: {e}")
            return None

    def _build_prompt(self, devices: List[Device]) -> str:
        device_list_str = ", ".join([f'name: "{d.name}", id: "{d.id}"' for d in devices])
        return f"""You are a PostgreSQL expert data analyst. 
        Your job is to parse a user's question and return a single, valid JSON object containing a SQL query and a human-readable summary.
        The user's ID will be available as a named parameter ':user_id'. 
        The SQL query will be executed by sql alchemy in parameterised way.
        You MUST scope all queries to this user's devices by adding 'WHERE owner_id = :user_id' or joining on the devices table. 
        The available tables are 'devices' (columns: id, name, owner_id) and 'telemetry' (columns: device_id, timestamp, energy_usage). 
        The user's devices are: [{device_list_str}]. The JSON must have two keys: "sql" and "summary". 
        Do not include any other text or markdown."""