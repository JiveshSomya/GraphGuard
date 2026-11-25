# Architecture

```mermaid
flowchart LR
U[User instruction] --> A[Mock agent]
R[Retrieved content] --> G[Interaction graph]
A --> G
G --> P[Permission check]
P --> K[Risk engine]
K --> E{Policy engine}
E -->|ALLOW| T[Mock tool]
E -->|BLOCK| L[SQLite audit]
E -->|REQUIRE HUMAN APPROVAL| H[Approval queue]
H -->|approved| T
T --> L
```

FastAPI exposes orchestration and evidence endpoints. NetworkX creates an ordered directed graph per execution. SQLite stores serialized executions and approval states. The Streamlit dashboard calls the same Python service layer for local offline demonstrations.

Each graph has user, retrieved-content, model-decision, tool-call, permission-check, risk-assessment, policy-decision, and optional tool-result nodes. Every node contains a UUID, UTC timestamp, type and contextual metadata.
