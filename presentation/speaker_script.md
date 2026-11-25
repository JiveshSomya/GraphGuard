# GraphGuard Speaker Script (10 minutes)

## Slides 1-6 | Jivesh Somya | 0:00-3:20

**Slide 1, 0:00-0:30. Terms: tool-using agent, GraphGuard.** Good morning. We are Jivesh Somya, Gaurav Garg and Himanshu Meena. Our project, GraphGuard, is a risk-aware security and evaluation framework for tool-using large language model agents. We built it as an offline demonstrator, so every action is safe to inspect. **Transition:** I will first explain the problem.

**Slide 2, 0:30-1:00. Terms: interaction graph, audit trail.** GraphGuard follows an agent from a user request to a tool result. It records retrieved content, tool choice, permission check, risk score and policy decision. That gives a reviewer a readable audit trail. **Transition:** Modern agents make this necessary.

**Slide 3, 1:00-1:35. Terms: API, prompt injection.** Agents can search documents, read records and call external services. Those capabilities also let a malicious instruction influence a real action. Prompt injection and excessive permissions are security risks, not only response-quality issues. **Transition:** The problem is larger than one prompt.

**Slide 4, 1:35-2:05. Terms: provenance, action sequence.** A retrieved document can contain malicious content, and a later transfer can misuse data collected earlier. We must consider where instructions came from and what the agent has already done. **Transition:** Basic controls leave this gap.

**Slide 5, 2:05-2:40. Terms: static permissions, context.** An unprotected agent follows all requests. Static permission control checks a capability but cannot understand untrusted retrieval or suspicious action sequences. GraphGuard adds those signals and preserves an explanation. **Transition:** Here is our solution.

**Slide 6, 2:40-3:20. Terms: mock agent, policy engine.** Our system uses mock tools, so it never contacts real banking, email or customer systems. It builds a NetworkX graph, scores risk and returns allow, block or human approval. Gaurav will explain the design. **Transition:** Over to Gaurav.

## Slides 7-11 | Gaurav Garg | 3:20-6:40

**Slide 7, 3:20-4:00. Terms: FastAPI, SQLite.** FastAPI exposes the backend with Pydantic validation. The simulator writes graph events, the permission checker and risk engine feed policy, and SQLite keeps executions and approvals. A reviewer must approve a queued action before its mock tool runs. **Transition:** The graph is our central evidence model.

**Slide 8, 4:00-4:35. Terms: directed graph, metadata.** Each execution creates ordered nodes for instruction, retrieval, model decision, tool call, permission check, risk, policy and result. Nodes include IDs, timestamps and metadata. JSON export supports the dashboard and audit log. **Transition:** Next is our scoring model.

**Slide 9, 4:35-5:25. Terms: weighted score, hard restriction.** We weight tool sensitivity at 32 percent, permission gap at 22, untrusted source at 16, sequence at 15 and injection at 15. Scores under 35 allow, middle risk requests approval and high risk blocks. Unknown tools, missing permission and detected injection always block. Transfers and deletes need approval. **Transition:** We evaluate this policy systematically.

**Slide 10, 5:25-6:00. Terms: deterministic scenarios, baseline.** We created twenty deterministic scenarios spanning benign use, direct and indirect injection, unauthorized access, sensitive exposure, excessive permissions, suspicious sequences and legitimate sensitive work. We run every scenario through three approaches and save CSV, JSON and charts. **Transition:** The approaches make the comparison fair.

**Slide 11, 6:00-6:40. Terms: unprotected agent, static permission control.** The unprotected baseline allows all requests. Static permissions only verify capability. GraphGuard considers capability, context and impact, while preserving a human path for legitimate high-impact work. Himanshu will present actual results. **Transition:** Over to Himanshu.

## Slides 12-14 | Himanshu Meena | 6:40-10:00

**Slide 12, 6:40-7:45. Terms: attack success rate, F1, latency.** Our actual latest run used twenty scenarios per approach. The unprotected agent had 100 percent attack success. Static permissions had 75 percent. GraphGuard had zero percent attack success, blocked all twelve dangerous actions, retained 100 percent task success, had zero false positives and F1 of one for block detection. Average measured latency was 14.16 milliseconds. **Transition:** Results need careful interpretation.

**Slide 13, 7:45-8:55. Terms: heuristic, provenance, SDG 9.** GraphGuard shows that context changes the appropriate decision. But keyword injection detection is heuristic: it can miss novel attacks and flag benign text. A production system needs signed provenance, sandboxed tools, stronger authorization and red-team testing. This work supports SDG 9 through safer digital infrastructure. **Transition:** I will close with our contribution.

**Slide 14, 8:55-10:00. Terms: explainability, reproducibility, auditability.** GraphGuard combines a dynamic interaction graph, explainable scoring, enforceable decisions, human approval and reproducible evaluation. It is a working offline demonstration, not a claim that mock data represents a production LLM. Thank you. We welcome your questions.
