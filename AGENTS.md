# Morrow — Agent Development Guide

## 1. Project Identity

**Project:** Morrow

**Tagline:** Evidence-Driven Long-Horizon Agentic Memory

Morrow is a Python-first agentic system designed to maintain persistent, evidence-grounded memory across long-running research and knowledge-work tasks.

The central idea is:

> Morrow should remember not only what happened, but why it happened, what evidence supports it, and how that history should influence future actions.

Morrow is not intended to be a generic chatbot.

It is a persistent agent runtime with:

- long-term memory
- evidence-grounded retrieval
- multi-agent orchestration
- agent handoffs
- durable execution
- sandboxed tool execution
- human-in-the-loop approval
- observability
- automated evaluation
- memory formation and consolidation

The system should be useful for real research and technical work such as:

- understanding previous experiments
- investigating code repositories
- retrieving previous decisions
- analyzing project history
- finding evidence for conclusions
- performing controlled technical tasks
- continuing interrupted long-running workflows

---

# 2. Core Design Principle

Morrow follows this loop:

```
Remember → Reason → Act → Observe → Learn → Remember
```

Every major architectural decision should support this loop.

The system should not simply generate answers.

It should:

1. retrieve relevant historical context
2. identify supporting evidence
3. reason over that context
4. use tools when necessary
5. delegate work when appropriate
6. request human approval for sensitive actions
7. execute safely
8. record what happened
9. learn what is worth remembering
10. make that knowledge available to future runs

---

# 3. Primary Technical Stack

## Backend

- Python
- FastAPI
- asyncio
- Pydantic
- SQLModel
- PostgreSQL
- NeonDB
- pgvector
- pytest

## Agentic AI

- LangGraph
- RAG
- LiteLLM
- MCP
- Ollama
- optional vLLM

## Observability

- Langfuse

## Evaluation

- Ragas
- DeepEval
- custom evaluation framework

## Frontend

- React
- TypeScript
- Vite
- WebSockets

The frontend should be a thin client over the Python backend.

Do NOT introduce Next.js unless there is a concrete architectural reason.

## Infrastructure

- Docker
- GitHub Actions
- CI/CD

Kubernetes, Helm, Terraform, Kafka, Spark, Airflow, MLflow and Elasticsearch/OpenSearch are NOT core dependencies.

Introduce them only if a demonstrated project requirement justifies them.

---

# 4. Architectural Philosophy

Prefer:

```
simple architecture
explicit boundaries
typed interfaces
testable components
observable execution
recoverable workflows
least-privilege tools
```

Avoid:

```
unnecessary abstractions
framework-driven architecture
duplicated orchestration systems
excessive microservices
technology added only for CV value
hidden state
untraceable agent decisions
```

Every technology must solve a real problem.

---

# 5. High-Level Architecture

The intended architecture is:

```
React + Vite
      |
      | REST / WebSocket
      v
   FastAPI
      |
      +--------------------+
      |                    |
      v                    v
Agent Runtime        Memory Engine
      |                    |
  LangGraph           RAG / Retrieval
      |                    |
      +---------+----------+
                |
                v
          Workflow Engine
                |
         Durable Execution
                |
      +---------+---------+
      |                   |
      v                   v
  Sandbox            Human Approval
      |
      v
  Tool Execution
      |
      v
    NeonDB
 PostgreSQL/pgvector
```

Observability:
 Langfuse

Evaluation:
 Ragas + DeepEval + custom benchmark

---

# 6. Repository Structure

Prefer the following structure:

```
morrow/
├── apps/
│   ├── api/
│   └── worker/
│
├── agents/
│   ├── orchestrator/
│   ├── research/
│   ├── code/
│   ├── analysis/
│   └── critic/
│
├── memory/
│   ├── ingestion/
│   ├── retrieval/
│   ├── formation/
│   ├── consolidation/
│   └── ranking/
│
├── workflows/
│   ├── definitions/
│   ├── checkpoints/
│   └── recovery/
│
├── tools/
│   ├── filesystem/
│   ├── git/
│   └── research/
│
├── sandbox/
│   ├── policies/
│   ├── executor/
│   └── limits/
│
├── evaluation/
│   ├── datasets/
│   ├── ragas/
│   ├── deepeval/
│   └── metrics/
│
├── db/
│   ├── models/
│   ├── repositories/
│   └── migrations/
│
├── api/
│   ├── routes/
│   ├── schemas/
│   └── websocket/
│
├── frontend/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── evaluation/
│   └── security/
│
├── docs/
├── scripts/
├── docker-compose.yml
├── pyproject.toml
└── AGENTS.md
```

The exact structure may evolve, but boundaries should remain clear.

---

# 7. Core Domain Concepts

Morrow has several important domain concepts.

## Memory

A persistent piece of information worth retaining.

Memory types include:

- semantic
- episodic
- procedural
- decision
- evidence

A memory should contain enough metadata to understand:

- what it says
- where it came from
- when it was created
- which project it belongs to
- why it matters
- how reliable it is
- what evidence supports it

Do not treat all memories as interchangeable text chunks.

---

## Evidence

Evidence is the source supporting a claim.

Examples:

- document
- experiment result
- Git commit
- source file
- tool result
- previous agent execution
- user-provided statement

Answers should preferentially reference evidence rather than relying on unsupported model generation.

---

## Agent Run

An execution of an agent or workflow.

A run should have:

- unique ID
- parent run if applicable
- status
- timestamps
- model information
- token/cost information where available
- events
- tool calls
- retrieved memories
- handoffs
- human interventions
- final result

---

## Agent Event

Agent execution must be observable through structured events.

Examples:

```
RunStarted
AgentStarted
AgentCompleted
MemorySearchStarted
MemoryRetrieved
ToolCallStarted
ToolCallCompleted
AgentHandoff
ApprovalRequested
ApprovalGranted
ApprovalRejected
WorkflowCheckpointed
WorkflowResumed
RunCompleted
RunFailed
```

Do not rely solely on log strings for important state transitions.

---

# 8. Memory Architecture

Morrow's memory system is a core research component.

Do not implement memory as:

```
text → embedding → vector database
```

only.

The intended retrieval pipeline is:

```
Query
  |
  +--> semantic similarity
  |
  +--> metadata filtering
  |
  +--> project relevance
  |
  +--> recency
  |
  +--> importance
  |
  v
Candidate memories
  |
  v
Re-ranking
  |
  v
Evidence-aware context
  |
  v
Agent
```

The ranking strategy must be measurable.

Avoid hardcoding arbitrary scoring formulas without evaluating them.

---

# 9. Memory Formation

Not every interaction should become a memory.

The system should distinguish between:

```
transient context
useful information
important decisions
reusable procedures
historical events
evidence
```

Example:

```
"User opened VS Code."
```

should generally NOT become a long-term memory.

Whereas:

```
"XGBoost was selected because it achieved the highest F1
while satisfying the latency constraint."
```

should be a candidate memory.

Memory formation should use:

- importance
- novelty
- future usefulness
- evidence quality
- project relevance

---

# 10. Memory Consolidation

Morrow should eventually consolidate related memories.

Example:

```
Memory A:
XGBoost performed well.

Memory B:
Experiment 42 achieved F1 = 0.86.

Memory C:
XGBoost was selected for the final experiment.
```

These can be consolidated into a higher-level decision memory:

```
XGBoost was selected for project X because it achieved
the strongest measured performance under the project's
latency constraint.
```

The consolidated memory must retain links to its supporting evidence.

Never discard source evidence merely because memories were consolidated.

---

# 11. RAG Requirements

RAG must be evidence-oriented.

The system should distinguish:

```
retrieved context
supporting evidence
generated interpretation
```

Do not allow the LLM to present unsupported claims as established facts.

Where possible, responses should expose:

- source
- evidence
- relevance
- confidence
- memory IDs
- document IDs

---

# 12. Agent Architecture

Start with a single agent.

Do not begin with a complex multi-agent architecture.

The progression should be:

```
Single agent
    ↓
Tool-using agent
    ↓
Orchestrator
    ↓
Specialized subagents
    ↓
Agent handoffs
    ↓
Critic/evaluator
```

Initial specialized agents:

- Research Agent
- Code Agent
- Analysis Agent
- Critic Agent

Do not create agents simply to make the architecture look more advanced.

A subagent should exist because it has:

- a distinct responsibility
- different tools
- different context
- a different evaluation criterion
- or a meaningful specialization

---

# 13. Agent Handoff

Handoffs must be explicit and observable.

Example:

```
Orchestrator
    ↓
Analysis Agent
    ↓
needs code context
    ↓
Code Agent
    ↓
returns evidence
    ↓
Analysis Agent
    ↓
Critic
```

Record:

- source agent
- destination agent
- reason
- context transferred
- result

Avoid implicit hidden delegation.

---

# 14. Durable Execution

Long-running workflows must be recoverable.

A workflow should be able to survive:

- process termination
- worker restart
- temporary API failure
- tool failure
- human waiting periods

Example:

```
Start
  ↓
Retrieve Context
  ↓ checkpoint
Research
  ↓ checkpoint
Analysis
  ↓ checkpoint
Human Approval
  ↓ checkpoint
Execution
  ↓
Complete
```

A restarted workflow must continue from a valid checkpoint.

Activities should be designed to be idempotent where possible.

Do not claim "durable execution" merely because state is written to a JSON file.

---

# 15. Human-in-the-Loop

Human approval is a first-class workflow state.

Use approval for meaningful or potentially destructive actions.

Examples:

- modifying files
- committing code
- deleting information
- executing risky commands
- external side effects

Do not ask humans to approve every read-only operation.

Approval should:

1. pause the workflow
2. persist workflow state
3. display proposed action and evidence
4. wait indefinitely if necessary
5. resume from the checkpoint after approval

---

# 16. Sandboxing

Agent-generated code must never execute directly on the host.

The execution path should be:

```
Agent
  ↓
Tool Policy
  ↓
Sandbox
  ↓
Execute
  ↓
Capture Output
  ↓
Agent
```

Sandboxing should enforce:

- filesystem isolation
- restricted network access
- CPU limits
- memory limits
- execution timeout
- command restrictions
- controlled environment variables

Never expose host secrets to the sandbox.

Never mount the entire host filesystem.

Treat all agent-generated code as untrusted.

---

# 17. MCP

MCP should expose controlled capabilities.

Initial tools should be limited to a few meaningful integrations:

- filesystem
- Git
- research/document search

Every tool should have:

- typed input
- typed output
- clear description
- permission requirements
- timeout
- error handling

Do not expose unrestricted shell access as an MCP tool.

---

# 18. Model Abstraction

Use LiteLLM where model portability is useful.

Do not couple business logic directly to one model provider.

The system should conceptually support:

```
cheap model
reasoning model
local model
embedding model
```

Model selection may eventually depend on:

- task complexity
- privacy
- latency
- cost
- required reasoning quality

Do not build model routing until the basic system works.

---

# 19. Observability

Langfuse should provide end-to-end traces.

Trace:

```
user request
   ↓
workflow
   ↓
agent
   ↓
LLM call
   ↓
retrieval
   ↓
tool call
   ↓
subagent
   ↓
final response
```

Capture where appropriate:

- latency
- token usage
- cost
- model
- prompt/version
- retrieval results
- tool calls
- errors
- handoffs
- human interventions

Do not log secrets, credentials or sensitive data unnecessarily.

---

# 20. Evaluation

Evaluation is a core part of Morrow, not an afterthought.

Use Ragas for RAG/retrieval-oriented evaluation.

Use DeepEval for agent/task/trajectory-oriented evaluation.

Maintain a versioned evaluation benchmark.

Categories should eventually include:

- memory retrieval
- answer correctness
- evidence grounding
- faithfulness
- tool selection
- tool execution
- task completion
- agent trajectory
- safety
- hallucination
- cost
- latency

Evaluation results should be reproducible.

Never claim an improvement without a baseline.

---

# 21. Research Direction

A central research question is:

> How does persistent, evidence-grounded memory affect the reliability and efficiency of long-horizon AI agents?

Potential experimental conditions:

```
A: no persistent memory
B: vector memory
C: hybrid memory
D: hybrid memory + consolidation
```

Compare:

- retrieval accuracy
- task completion
- hallucination
- evidence grounding
- latency
- token usage
- tool calls
- human interventions

This research component should remain separate from the application logic.

---

# 22. Frontend

The frontend should be an agent operations interface, not a marketing website.

Primary views:

## Chat

Interact with Morrow.

## Run Inspector

Show live execution:

```
Planner ✓
Memory Retrieval ✓
Research Agent ✓
Code Agent ⟳
Human Approval ⏸
```

## Memory Explorer

Show:

- semantic memories
- episodic memories
- procedural memories
- decisions
- evidence

## Evidence View

Show why a response was generated.

## Evaluation Dashboard

Show:

- retrieval metrics
- agent metrics
- latency
- cost
- failure rates

The existing `harness-engineering` frontend may be used as inspiration or as a source of reusable UI components where its license permits. Do not blindly copy the entire application architecture.

---

# 23. API Design

Prefer explicit REST endpoints.

Examples:

```
POST /runs
GET /runs/{run_id}
POST /runs/{run_id}/cancel

GET /memories
GET /memories/{memory_id}
POST /memories
PATCH /memories/{memory_id}

GET /projects
GET /projects/{project_id}

GET /evaluations
GET /evaluations/{evaluation_id}

POST /approvals/{approval_id}/approve
POST /approvals/{approval_id}/reject
```

Use WebSockets for live execution events.

Do not use WebSockets as a replacement for ordinary REST operations.

---

# 24. Database Rules

Neon/PostgreSQL is the source of truth for persistent application state.

Use migrations.

Do not silently mutate schemas from application startup.

Use transactions around important state transitions.

Important state changes should be auditable.

Avoid storing arbitrary unstructured JSON when a proper relational model is appropriate.

Use JSON/JSONB for genuinely flexible metadata.

---

# 25. Python Engineering Rules

Prefer:

- type hints
- small functions
- explicit dependencies
- Pydantic models
- async I/O
- dependency injection where useful
- structured exceptions
- deterministic tests
- clear interfaces

Avoid:

- global mutable state
- giant agent functions
- deeply nested conditionals
- hidden side effects
- untyped dictionaries everywhere
- unnecessary metaprogramming
- framework-specific logic in domain code

Use `asyncio` for I/O-bound concurrency.

Do not use async merely because it sounds modern.

---

# 26. Testing Strategy

Tests should exist at several levels.

## Unit tests

Test:

- memory ranking
- parsing
- policy decisions
- schemas
- scoring
- workflow transitions

## Integration tests

Test:

- FastAPI + database
- retrieval
- LangGraph workflows
- MCP tools
- sandbox
- WebSockets

## Evaluation tests

Test:

- retrieval quality
- answer quality
- tool usage
- agent trajectories

## Security tests

Test:

- prompt injection
- path traversal
- unauthorized tools
- malicious documents
- sandbox restrictions
- secret leakage

Do not mock everything.

Important integration boundaries must be tested against realistic dependencies.

---

# 27. Development Order

Implement in this order unless there is a strong reason not to:

### Phase 1 — Foundation

1. repository
2. Python configuration
3. FastAPI
4. PostgreSQL/Neon
5. migrations
6. pytest
7. Docker
8. CI

### Phase 2 — Memory

9.  ingestion
10. embeddings
11. pgvector
12. basic retrieval
13. hybrid retrieval
14. evidence model

### Phase 3 — Agent

15. LangGraph
16. tools
17. single agent
18. event model
19. WebSockets
20. React/Vite UI

### Phase 4 — Multi-agent

21. orchestrator
22. Research Agent
23. Code Agent
24. Analysis Agent
25. Critic Agent
26. handoffs

### Phase 5 — Reliability

27. durable workflows
28. checkpoints
29. retries
30. recovery
31. human approval

### Phase 6 — Safety

32. sandbox
33. tool permissions
34. resource limits
35. security tests

### Phase 7 — Evaluation

36. Langfuse
37. benchmark
38. Ragas
39. DeepEval
40. custom metrics

### Phase 8 — Intelligence

41. memory formation
42. memory consolidation
43. model routing
44. local/private mode

### Phase 9 — Research

45. define hypotheses
46. establish baselines
47. run experiments
48. analyze results
49. document findings

Do not skip ahead just because a later technology is interesting.

---

# 28. What NOT to Add

Do not add technology merely because it appears on a learning checklist.

Avoid initially:

- Kubernetes
- Helm
- Terraform
- Kafka
- Spark
- Airflow
- Prefect
- Elasticsearch
- OpenSearch
- MLflow
- LoRA
- custom model training
- multiple cloud providers

These may be useful elsewhere but are not required for Morrow.

The project should not become a technology showcase.

---

# 29. Definition of Done

Morrow should eventually be able to perform a task like:

> "Investigate why my latest experiment performed worse than the previous version and tell me what I should change."

A successful execution should look approximately like:

```
User request
    ↓
Orchestrator
    ↓
Retrieve relevant memories
    ↓
Research Agent
    ↓
Code Agent
    ↓
Analysis Agent
    ↓
Evidence collection
    ↓
Critic
    ↓
Human approval if action is required
    ↓
Sandboxed execution
    ↓
Evaluation
    ↓
Memory formation
    ↓
Durable completion
```

The user should be able to inspect the entire trajectory.

---

# 30. Definition of a High-Quality Morrow Implementation

A high-quality implementation is NOT:

```
"It uses 15 AI frameworks."
```

A high-quality implementation is:

```
"It reliably remembers useful information,
 retrieves the right evidence,
 chooses appropriate tools,
 delegates when useful,
 survives failures,
 asks humans when necessary,
 executes safely,
 and can demonstrate through evaluation
 that its behavior improved."
```

Prioritize correctness, reliability, observability and measurable improvement over feature count.

---

# 31. Rules for AI Coding Agents

When modifying this repository:

1. Read `AGENTS.md` before making architectural changes.
2. Inspect existing code before creating new abstractions.
3. Reuse existing interfaces where appropriate.
4. Do not introduce a new dependency without explaining why it is needed.
5. Do not introduce a new framework to solve a problem already handled by the current stack.
6. Keep domain logic independent from framework-specific code where practical.
7. Add tests with meaningful behavioral coverage.
8. Do not silently change database schemas.
9. Do not expose secrets.
10. Do not execute arbitrary agent-generated code on the host.
11. Do not bypass sandbox or approval mechanisms for convenience.
12. Preserve observability for important agent actions.
13. Preserve durable workflow semantics.
14. Make important state transitions explicit.
15. Prefer incremental changes over large rewrites.
16. When a requirement is ambiguous, inspect the repository and existing architecture before inventing behavior.
17. Before completing a change, run formatting, static checks, and tests: `uv run ruff format --check .`, `uv run ruff check .`, `uv run mypy .`, and `uv run pytest`.
18. If a requested feature conflicts with this architecture, explain the conflict before implementing a workaround.

---

# 32. Current Priority

The immediate objective is NOT to build the complete system.

Build the smallest useful version first:

```
local documents
    ↓
ingestion
    ↓
NeonDB + pgvector
    ↓
retrieval
    ↓
evidence-grounded answer
```

Then progressively introduce:

```
agent
tools
events
frontend
subagents
handoffs
durable execution
human approval
sandbox
observability
evaluation
memory consolidation
```

The project should remain usable after every major stage.

---

# 33. North Star

The ultimate goal of Morrow is:

> **No important work should disappear just because a conversation ended, a process crashed, or a day passed.**

Morrow should turn previous work into persistent, evidence-grounded context that makes future agent actions more reliable.

Remember:

```
Yesterday's work
        ↓
     Morrow
        ↓
Tomorrow's intelligence
```
