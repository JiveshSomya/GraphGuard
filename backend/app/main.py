from __future__ import annotations
import json, sqlite3
from fastapi import FastAPI, HTTPException
from .core import DB_PATH, TOOLS, RiskEngine, PolicyEngine, execute, init_db
from .models import ExecuteRequest, ToolRequest, ApprovalAction
from .evaluation import run_evaluation

app=FastAPI(title="GraphGuard",version="1.0.0",description="Offline risk-aware policy enforcement demo for tool-using agents.")
@app.on_event("startup")
def startup(): init_db()
@app.get("/health")
def health(): return {"status":"ok","mode":"offline mock tools only"}
@app.get("/tools")
def tools(): return [{k:v for k,v in t.__dict__.items() if k!="handler"} for t in TOOLS.values()]
@app.post("/agent/execute")
def agent_execute(req: ExecuteRequest): return execute(req)
@app.post("/risk/analyze")
def risk(req: ToolRequest): return RiskEngine().analyze(req)
@app.post("/policy/evaluate")
def policy(req: ToolRequest):
    r=RiskEngine().analyze(req); d,reasons=PolicyEngine().evaluate(req,r); return {"decision":d,"reasons":reasons,"risk":r}
@app.get("/executions")
def executions():
    init_db();
    with sqlite3.connect(DB_PATH) as c: return [{"id":x[0],"created_at":x[1],"decision":x[2]} for x in c.execute("SELECT id,created_at,decision FROM executions ORDER BY created_at DESC")]
@app.get("/executions/{execution_id}")
@app.get("/graph/{execution_id}")
def execution(execution_id:str):
    init_db();
    with sqlite3.connect(DB_PATH) as c: row=c.execute("SELECT payload FROM executions WHERE id=?",(execution_id,)).fetchone()
    if not row: raise HTTPException(404,"Execution not found")
    return json.loads(row[0])
@app.get("/approvals")
def approvals():
    init_db();
    with sqlite3.connect(DB_PATH) as c: return [{"id":x[0],"execution_id":x[1],"tool":x[2],"status":x[3],"created_at":x[4],"reviewer":x[5]} for x in c.execute("SELECT * FROM approvals ORDER BY created_at DESC")]
def decide_approval(approval_id:str, status:str, body:ApprovalAction):
    init_db();
    with sqlite3.connect(DB_PATH) as c:
        if c.execute("SELECT 1 FROM approvals WHERE id=?",(approval_id,)).fetchone() is None: raise HTTPException(404,"Approval not found")
        c.execute("UPDATE approvals SET status=?, reviewer=? WHERE id=?",(status,body.reviewer,approval_id)); c.commit()
    return {"approval_id":approval_id,"status":status,"reviewer":body.reviewer}
@app.post("/approvals/{approval_id}/approve")
def approve(approval_id:str, body:ApprovalAction): return decide_approval(approval_id,"APPROVED",body)
@app.post("/approvals/{approval_id}/reject")
def reject(approval_id:str, body:ApprovalAction): return decide_approval(approval_id,"REJECTED",body)
@app.post("/evaluation/run")
def evaluation_run(): return run_evaluation()
@app.get("/evaluation/results")
def evaluation_results():
    from pathlib import Path
    path=Path(__file__).resolve().parents[1]/"reports"/"latest_evaluation.json"
    if not path.exists(): raise HTTPException(404,"No evaluation has run yet")
    return json.loads(path.read_text())
@app.get("/evaluation/results/{run_id}")
def evaluation_result(run_id:str):
    data=evaluation_results()
    if data["run_id"]!=run_id: raise HTTPException(404,"Run not found")
    return data
@app.get("/evaluation/report")
def report(): return evaluation_results()
