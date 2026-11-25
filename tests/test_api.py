from app.main import app

def test_health_and_tools():
    routes = {route.path: route.endpoint for route in app.routes}
    assert routes["/health"]()["status"] == "ok"
    assert len(routes["/tools"]()) == 6

def test_execute_graph_and_approval_flow():
    from app.models import ExecuteRequest, ApprovalAction
    from app.main import agent_execute, approve
    body = agent_execute(ExecuteRequest(instruction="Transfer INR 100", agent_permissions=["transfer"], requested_tools=["transfer_funds"]))
    assert body["decision"] == "REQUIRE_HUMAN_APPROVAL"
    assert any(n[1]["event_type"] == "PERMISSION_CHECK" for n in body["graph"]["nodes"])
    approval_id = body["outcomes"][0]["approval_id"]
    approved = approve(approval_id, ApprovalAction(reviewer="qa"))
    assert approved["result"]["mock"]

def test_evaluation_endpoint():
    from app.main import evaluation_run
    assert evaluation_run()["scenario_count"] == 20
