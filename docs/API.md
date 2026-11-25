# API Reference

| Endpoint | Purpose |
|---|---|
| `GET /health` | Confirms offline service availability |
| `GET /tools` | Lists registered mock tools and permissions |
| `POST /agent/execute` | Runs simulator and returns graph, policy and outcomes |
| `POST /risk/analyze` | Returns explainable risk factors |
| `POST /policy/evaluate` | Returns risk and enforcement decision |
| `GET /graph/{execution_id}` | Retrieves serialized execution graph |
| `GET /executions` | Lists execution audit records |
| `GET /approvals` | Lists approval state |
| `POST /approvals/{id}/approve` | Approves and executes the queued mock action |
| `POST /approvals/{id}/reject` | Rejects a queued action |
| `POST /evaluation/run` | Runs the deterministic evaluation suite |
| `GET /evaluation/results` | Returns latest evaluation metadata |

Example `POST /agent/execute` body:

```json
{"instruction":"Transfer INR 100","agent_permissions":["transfer"],"requested_tools":["transfer_funds"]}
```

This returns `REQUIRE_HUMAN_APPROVAL`; an approved action returns only a mock result.
