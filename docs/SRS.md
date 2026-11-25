# Software Requirements Specification

## Scope

GraphGuard evaluates simulated tool-using agent actions before execution. It supports allow, block and human-approval outcomes. It never contacts real bank, email, customer, or production systems.

## Functional requirements

The system shall register six mock tools, validate permissions, construct an execution graph, score risk, persist audit records, queue sensitive actions for approval, run deterministic scenarios, export CSV/JSON/chart evidence, and offer REST and dashboard interfaces.

## Non-functional requirements

The application shall run offline on Python 3.11+, provide reproducible scenario results, validate request payloads, preserve structured audit evidence in SQLite, and expose API documentation at `/docs`.

## Acceptance mapping

`/health` proves availability. `/agent/execute` proves graph and policy flow. `/approvals` proves the reviewer workflow. `/evaluation/run` creates comparison evidence. Pytest covers core and API paths.
