import json
import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st
from app.core import DB_PATH, TOOLS, execute
from app.models import ExecuteRequest
from app.evaluation import run_evaluation

st.set_page_config(page_title="GraphGuard", layout="wide")
st.title("GraphGuard")
st.caption("Risk-aware security and evaluation framework. Every action uses offline mock data.")
tabs = st.tabs(["Overview", "Agent Playground", "Interaction Graph", "Risk Analysis", "Approval Center", "Security Evaluation", "Audit Logs"])
with tabs[0]:
    with sqlite3.connect(DB_PATH) as conn:
        executions = pd.read_sql_query("SELECT * FROM executions ORDER BY created_at DESC", conn)
        approvals = pd.read_sql_query("SELECT * FROM approvals ORDER BY created_at DESC", conn)
    counts = executions.decision.value_counts() if not executions.empty else pd.Series(dtype=int)
    cells = st.columns(5)
    for cell, label, value in zip(cells, ["Executions", "Allowed", "Blocked", "Pending approvals", "Detected attacks"], [len(executions), int(counts.get("ALLOW",0)), int(counts.get("BLOCK",0)), int((approvals.status=="PENDING").sum()) if not approvals.empty else 0, int(counts.get("BLOCK",0))]): cell.metric(label, value)
    st.subheader("Recent activity"); st.dataframe(executions[["id","created_at","decision"]].head(10), use_container_width=True)
with tabs[1]:
    instruction=st.text_area("User instruction", "Search normal project documentation")
    permissions=st.multiselect("Agent permissions", sorted({t.permission for t in TOOLS.values()}), default=["search"])
    content=st.text_area("Retrieved content (untrusted)", "")
    requested=st.multiselect("Requested tool override (optional)", list(TOOLS))
    if st.button("Execute guarded agent"):
        result=execute(ExecuteRequest(instruction=instruction, agent_permissions=permissions, retrieved_content=content, requested_tools=requested))
        st.session_state["latest"] = result
        st.success(result["decision"]); st.json(result["outcomes"])
with tabs[2]:
    result=st.session_state.get("latest")
    if result: st.dataframe(pd.DataFrame([{"event":n[1]["event_type"],"timestamp":n[1]["timestamp"],"metadata":n[1]["metadata"]} for n in result["graph"]["nodes"]]),use_container_width=True)
    else: st.info("Execute an agent request to inspect its ordered interaction graph.")
with tabs[3]:
    result=st.session_state.get("latest")
    if result:
        for outcome in result["outcomes"]:
            st.subheader(outcome["tool"]); st.metric("Risk score", outcome["risk"]["score"]); st.write(outcome["reasons"]); st.json(outcome["risk"]["factors"])
    else: st.info("Risk factors appear after an execution.")
with tabs[4]:
    st.dataframe(approvals,use_container_width=True)
    st.caption("Use REST approval endpoints in Swagger for reviewer actions. Approval returns the mock tool result.")
with tabs[5]:
    if st.button("Run deterministic evaluation"): st.session_state["evaluation"] = run_evaluation()
    report=st.session_state.get("evaluation")
    if not report and Path("reports/latest_evaluation.json").exists(): report=json.loads(Path("reports/latest_evaluation.json").read_text())
    if report: st.dataframe(pd.DataFrame(report["metrics"]),use_container_width=True); st.image(report["artifacts"]["chart"])
with tabs[6]: st.dataframe(executions[["id","created_at","decision"]] if not executions.empty else executions,use_container_width=True)
