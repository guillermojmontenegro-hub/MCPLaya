# Setup and tool reference

MCPLaya: https://github.com/guillermojmontenegro-hub/MCPLaya
Python >=3.10 and uv are required. The user installs the server separately:

```sh
git clone https://github.com/guillermojmontenegro-hub/MCPLaya.git
cd MCPLaya
uv sync --frozen
```

Add this server to a client supporting stdio MCP. Replace the absolute project
path and uv executable as needed:

```json
{"mcpServers":{"mcplaya":{"command":"uv","args":["--directory","/ABSOLUTE/PATH/MCPLaya","run","--frozen","mcplaya"],"env":{"LAYA_DEVICE":"cpu"}}}}
```

For VS Code Copilot, use `.vscode/mcp.json` with a top-level `servers` object,
not `mcpServers`, and add `"type":"stdio"` to the server entry. Restart/reload
according to your client's MCP UI and verify `laya_status` is discoverable.
First inference downloads official weights from Hugging Face. Later inference
uses the cache. Startup/status do not download weights. No API key is required
for public checkpoints. `LAYA_ACTION_MODEL` can select an existing compatible
local checkpoint; its license and task accuracy must be reviewed separately.
`MCPLAYA_DB` overrides the SQLite history path; otherwise it is stored under
`$XDG_STATE_HOME/mcplaya` or `~/.local/state/mcplaya`. Avoid secrets in observations.

## Example sequence

Start:
```json
{"goal":"Find why the test fails and verify a fix","max_steps":8,"min_confidence":0.75,"model":"auto"}
```
Send that to `laya_start_sequence`. Using its returned ID and revision:
```json
{"sequence_id":"RETURNED_ID","revision":0,"observation":"A test fails with missing database table; migration status has not been inspected.","actions":[{"id":"inspect","description":"Read migration status in the local test database without modifying it"},{"id":"read-test","description":"Read the failing test fixture to verify schema setup"}]}
```
Send to `laya_next_decision`. If it recommends `inspect`, execute that exact
inspection with an agent tool. Then record (the next revision is illustrative):
```json
{"sequence_id":"RETURNED_ID","revision":1,"decision_id":"RETURNED_DECISION_ID","outcome":"succeeded","observation":"Migration status shows the test schema has not been initialized."}
```
Use `laya_record_outcome`. It returns revision 2. Observe again, propose the next
candidates and repeat. If reviewing/rejecting a proposal, record `skipped` instead.
Action execution and its permissions always belong to the calling agent.

## Tools

- `laya_status()` reports model initialization and device preference.
- `laya_predict(state, questions, model="auto")` returns typed answers plus a warning.
- `laya_choose_action(goal, observation, actions, min_confidence=0.7, model="auto")`
  returns `action_id`, `confidence`, `requires_review`, `recommended_action_id`.
- `laya_start_sequence(goal, max_steps=20, min_confidence=0.7, model="auto")`
  returns durable initial state and revision 0.
- `laya_next_decision(sequence_id, revision, observation, actions)` returns a pending
  `decision_id` and increments revision. At most one pending decision is allowed.
- `laya_record_outcome(sequence_id, revision, decision_id, outcome, observation)`
  clears pending state, appends observed history and increments revision.
- `laya_get_sequence(sequence_id)` recovers full state including pending candidates.
- `laya_close_sequence(sequence_id, revision, reason)` closes and increments revision.

Three consecutive failed outcomes block further decisions. Each recorded outcome,
including skipped proposals, consumes a step. Unknown IDs, duplicate candidates,
stale revisions, closed sequences and exhausted budgets produce MCP tool errors.
History survives server restarts. No external action is executed by these tools.
Inference sends only the last five outcome records plus the current observation;
keep observations concise to fit the selected checkpoint's context window.

Typed questions:
```json
{"state":{"message":"I was charged twice"},"questions":{"department":{"type":"choice","instructions":"Which team owns this issue?","criteria":{"billing":"Charges and refunds","technical":"Software defects"}},"urgency":{"type":"score","instructions":"How urgent?","criteria":["low","medium","high"]},"duplicate":{"type":"noul","instructions":"Does the message report a duplicate charge?"}},"model":"auto"}
```
`model` accepts `auto`, `english`, `multilingual`, `typed-decisions`. The specialized
model is intended for its trained workflows, not arbitrary navigation.
