from __future__ import annotations

import json
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import networkx as nx

from .models import Decision, ExecuteRequest, ToolRequest

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "graphguard.db"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    permission: str
    sensitivity: int
    category: str
    handler: Callable[[], dict[str, Any]]

def _result(label: str) -> Callable[[], dict[str, Any]]:
    return lambda: {"mock": True, "message": label}

TOOLS: dict[str, Tool] = {
    "search_documents": Tool("search_documents", "Search a simulated document index", "search", 10, "read", _result("Found 2 simulated documents.")),
    "read_customer_record": Tool("read_customer_record", "Read a mock customer record", "read", 45, "sensitive_data", _result("Mock record: customer C-1042, tier Gold.")),
    "get_account_balance": Tool("get_account_balance", "Read a mock account balance", "read_financial", 55, "financial", _result("Mock balance: INR 12,500.")),
    "send_email": Tool("send_email", "Send a simulated external email", "email", 50, "external_action", _result("Mock email queued. No message was sent.")),
    "transfer_funds": Tool("transfer_funds", "Perform a simulated funds transfer", "transfer", 90, "financial", _result("Mock transfer recorded. No money moved.")),
    "delete_record": Tool("delete_record", "Delete a simulated record", "delete", 85, "destructive", _result("Mock deletion recorded. No record changed.")),
}

INJECTION_RE = re.compile(r"ignore (all |any |the )?(previous|prior)|system prompt|developer message|bypass|override.*instruction|exfiltrat|send .*password", re.I)

class InteractionGraph:
    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self.graph = nx.DiGraph(execution_id=execution_id)
        self.last: str | None = None

    def add(self, event_type: str, metadata: dict[str, Any]) -> str:
        node_id = str(uuid.uuid4())
        self.graph.add_node(node_id, id=node_id, timestamp=now(), event_type=event_type, metadata=metadata)
        if self.last:
            self.graph.add_edge(self.last, node_id, relationship="next")
        self.last = node_id
        return node_id

    def export(self) -> dict[str, Any]:
        return {"execution_id": self.execution_id, "nodes": list(self.graph.nodes(data=True)), "edges": list(self.graph.edges(data=True))}

class RiskEngine:
    weights = {"tool_sensitivity": 0.32, "permission_gap": 0.22, "source": 0.16, "sequence": 0.15, "injection": 0.15}

    def analyze(self, request: ToolRequest) -> dict[str, Any]:
        tool = TOOLS.get(request.tool)
        if not tool:
            return {"score": 100.0, "factors": {"unknown_tool": 100}, "injection_detected": False, "rationale": ["Tool is not registered."]}
        text = f"{request.instruction} {request.retrieved_content}"
        injection = bool(INJECTION_RE.search(text))
        permission_gap = tool.permission not in request.agent_permissions
        untrusted = bool(request.retrieved_content.strip())
        sensitive_sequence = tool.name in {"transfer_funds", "send_email"} and any(x in {"read_customer_record", "get_account_balance"} for x in request.prior_tools)
        raw = {
            "tool_sensitivity": tool.sensitivity,
            "permission_gap": 100 if permission_gap else 0,
            "source": 70 if untrusted and tool.sensitivity >= 45 else 0,
            "sequence": 85 if sensitive_sequence else 0,
            "injection": 100 if injection else 0,
        }
        score = round(sum(raw[k] * self.weights[k] for k in self.weights), 2)
        rationale = [f"{k.replace('_', ' ')} contributed {v * self.weights[k]:.1f} points." for k, v in raw.items() if v]
        if not rationale: rationale = ["Registered low-sensitivity action with matching permission and no suspicious context."]
        return {"score": score, "factors": raw, "injection_detected": injection, "permission_gap": permission_gap, "sensitive_sequence": sensitive_sequence, "rationale": rationale}

class PolicyEngine:
    def evaluate(self, request: ToolRequest, risk: dict[str, Any]) -> tuple[Decision, list[str]]:
        tool = TOOLS.get(request.tool)
        if not tool: return Decision.BLOCK, ["Hard restriction: unknown tool."]
        if risk["injection_detected"]: return Decision.BLOCK, ["Hard restriction: prompt-injection indicator detected."]
        if risk["permission_gap"]: return Decision.BLOCK, [f"Hard restriction: missing '{tool.permission}' permission."]
        if tool.name in {"transfer_funds", "delete_record"}: return Decision.REQUIRE_HUMAN_APPROVAL, ["High-impact action requires human approval."]
        if risk["score"] >= 70: return Decision.BLOCK, ["Risk score exceeds block threshold (70)."]
        if risk["score"] >= 35 or tool.sensitivity >= 55: return Decision.REQUIRE_HUMAN_APPROVAL, ["Risk requires an accountable reviewer."]
        return Decision.ALLOW, ["Risk is below the approval threshold and permission is present."]

def infer_tools(instruction: str) -> list[str]:
    text = instruction.lower()
    mapping = [("transfer", "transfer_funds"), ("delete", "delete_record"), ("email", "send_email"), ("balance", "get_account_balance"), ("customer", "read_customer_record"), ("search", "search_documents")]
    return [tool for token, tool in mapping if token in text] or ["search_documents"]

def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS executions (id TEXT PRIMARY KEY, created_at TEXT, decision TEXT, payload TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS approvals (id TEXT PRIMARY KEY, execution_id TEXT, tool TEXT, status TEXT, created_at TEXT, reviewer TEXT)")
        conn.commit()

def save_execution(execution_id: str, decision: str, payload: dict[str, Any]) -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR REPLACE INTO executions VALUES (?,?,?,?)", (execution_id, now(), decision, json.dumps(payload)))
        conn.commit()

def execute(request: ExecuteRequest) -> dict[str, Any]:
    execution_id = str(uuid.uuid4())
    graph = InteractionGraph(execution_id)
    graph.add("USER_INSTRUCTION", {"instruction": request.instruction})
    if request.retrieved_content: graph.add("RETRIEVED_CONTENT", {"content": request.retrieved_content, "source_trust": "untrusted"})
    chosen = request.requested_tools or infer_tools(request.instruction)
    outcomes: list[dict[str, Any]] = []
    engine, policy = RiskEngine(), PolicyEngine()
    for tool_name in chosen:
        graph.add("MODEL_DECISION", {"tool": tool_name, "mock_agent": True})
        graph.add("TOOL_CALL", {"tool": tool_name})
        tr = ToolRequest(tool=tool_name, agent_permissions=request.agent_permissions, instruction=request.instruction, retrieved_content=request.retrieved_content, prior_tools=[x["tool"] for x in outcomes])
        tool = TOOLS.get(tool_name)
        graph.add("PERMISSION_CHECK", {"tool": tool_name, "required_permission": tool.permission if tool else None, "granted": bool(tool and tool.permission in request.agent_permissions)})
        risk = engine.analyze(tr); graph.add("RISK_ASSESSMENT", risk)
        decision, reasons = policy.evaluate(tr, risk); graph.add("POLICY_DECISION", {"decision": decision.value, "reasons": reasons})
        item: dict[str, Any] = {"tool": tool_name, "risk": risk, "decision": decision.value, "reasons": reasons}
        if decision == Decision.ALLOW:
            item["result"] = TOOLS[tool_name].handler(); graph.add("TOOL_RESULT", item["result"])
        elif decision == Decision.REQUIRE_HUMAN_APPROVAL:
            approval_id = str(uuid.uuid4()); init_db()
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("INSERT INTO approvals VALUES (?,?,?,?,?,?)", (approval_id, execution_id, tool_name, "PENDING", now(), "")); conn.commit()
            item["approval_id"] = approval_id
        outcomes.append(item)
    overall = Decision.BLOCK.value if any(x["decision"] == Decision.BLOCK.value for x in outcomes) else (Decision.REQUIRE_HUMAN_APPROVAL.value if any(x["decision"] == Decision.REQUIRE_HUMAN_APPROVAL.value for x in outcomes) else Decision.ALLOW.value)
    payload = {"execution_id": execution_id, "scenario_id": request.scenario_id, "decision": overall, "outcomes": outcomes, "graph": graph.export(), "created_at": now()}
    save_execution(execution_id, overall, payload)
    return payload
