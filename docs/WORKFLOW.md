# Delegate decisions to Laya

Use Laya for bounded choices over observed facts. The agent gathers evidence,
proposes concrete candidates and executes authorized actions. Laya selects;
it does not browse, run commands, inspect image pixels or generate plans.
For writing, coding or open-ended reasoning, use the agent's own capabilities.

## Prerequisite

Check for `laya_status` in the connected tools (client prefixes may differ).
If unavailable, install and connect MCPLaya using the
[installation guide](INSTALLATION.md). See the [tool reference](TOOLS.md) for
schemas and request examples.

## A sequence of dependent decisions

1. Define the user's goal, completion evidence and a bounded step budget.
   Call `laya_start_sequence`; retain its `sequence_id` and `revision`.
2. Inspect the current environment using the agent's normal tools. Send a concise
   textual observation and 2-20 available candidates to `laya_next_decision`.
   Each candidate needs a unique `id` and a specific `description` including its
   target. Include an inspect, wait, stop or ask-user option when applicable.
3. Match the returned ID to the submitted candidates. If `requires_review` is
   true, gather better evidence or ask the user when their judgment is needed;
   never treat confidence as authorization. Record a rejected proposal as `skipped`.
   Even a high-confidence recommendation must fit the user's authorization and facts.
4. Execute at most that one action through the agent's tools. Observe its actual
   result and call `laya_record_outcome` with `decision_id`, current `revision`,
   `succeeded`, `failed` or `skipped`, and post-action evidence. Keep the new revision.
5. Repeat from a fresh observation. Do not predict an entire dependent chain from
   the initial state. Do not report a proposed action as executed. Close with
   `laya_close_sequence` when evidence confirms completion, the budget ends,
   the user cancels or progress is blocked. A `blocked` status requires reassessment.

On reconnection or stale revision, use `laya_get_sequence` and inspect the real
world before retrying a pending action: it may already have happened.
The server persists history locally and enforces one pending decision at a time;
these records are supplied by the caller, not independent execution verification.

## Individual or independent decisions

For one finite choice use `laya_choose_action`. For independent questions over the
same state use `laya_predict` with `choice`, `score` or `noul` schemas. `noul` is a
probability of true, not a boolean; score criteria are ordered from level zero.
Do not batch dependent questions as though their answers were already observed.
Shortlist more than 20 options using explicit relevance to observed facts before
calling Laya. Preserve a fallback if the available evidence cannot distinguish them.

## Report

Briefly state the decision, observed outcome and remaining obstacle, if any.
At sequence end state the goal outcome, number of actions actually taken and
unresolved decisions. Do not claim general checkpoints are validated for navigation
or that confidence guarantees correctness. Domain-specific accuracy needs evaluation.
