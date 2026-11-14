---
name: mcplaya-decisions
description: Use the local MCPLaya MCP to classify or tag text, route requests, score urgency or sentiment, assess explicit statements, and select bounded actions over observed facts. Use for fast structured decisions and dependent observe-decide-act sequences. Requires connected MCPLaya tools; does not install the server or generate free-form content.
---

# MCPLaya decisions

Delegate a finite question to the local Laya model. The agent supplies evidence
and a compact schema, reads the typed answer, and performs any authorized action
with its own tools. MCPLaya returns decisions; it does not execute them.

## Connect the task to a tool

Check that `laya_predict` or the needed action tool is connected; client prefixes
may vary. Use `laya_status` when initialization status matters. If tools are
missing, report the missing local MCP connection and refer to the project's
installation documentation. Loading this usage skill does not authorize software
installation, model downloads or changes to agent configuration.

| Need | Tool and question shape |
|---|---|
| One category, intent, topic, document type or routing destination | `laya_predict` with `choice` |
| Several independent tags on the same text | Separate `noul` questions in one `laya_predict` call |
| An ordered rating such as urgency, frustration or relevance | `laya_predict` with `score` |
| Probability that a specific statement is true | `laya_predict` with `noul` |
| Select one next action from observed alternatives | `laya_choose_action` |
| Repeated decisions that depend on action results | Sequence tools, one fresh observation per step |

For task ideas, read [use cases and evidence](references/use-cases.md). For exact
arguments and runnable request shapes, read [recipes](references/recipes.md).
For repeated workloads, latency or model selection, read
[performance and model choice](references/performance.md). Load only the
references relevant to the current task.

## Make a compact request

- Put the actual source text or observed facts in a nonempty `state` object.
  Preserve negation, amounts, deadlines and other decisive evidence. A local
  filename alone does not give the model access to the file.
- Use `choice` for one mutually exclusive label. Supply at most 20 concise,
  distinguishable label descriptions. Include an `other` or `insufficient_info`
  option when it represents a real possibility. For larger taxonomies, select
  a coarse category and then a relevant subgroup in a second call.
- Use `noul` for independent yes/no statements, with `criteria` keyed exactly
  `false` and `true`. For several tags, ask one statement per tag; a `choice`
  returns only one label. Do not infer a multi-label answer from small nonzero
  choice probabilities.
- Use `score` with an ordered list of concrete rubric levels. The result is an
  expected zero-based level and may be fractional; it is not a percentage.
- Group independent questions about the same observed state in one call. If
  question B depends on A's answer or on a new observation, use a later call.
  For many documents, classify one document per call and preserve its ID.
- Use `model="auto"` by default. For known non-English or mixed-language text,
  explicitly use `multilingual` when needed; do not translate away useful source
  evidence just to use English. Read the model guidance for specialized tasks.

## Read the answer correctly

`laya_predict` returns `answers` and `warning`. Read each answer by its question
ID: `choice` is the label, `score` is the ordinal expectation, and `noul` is
P(the statement is true). For `noul`, a confident negative prediction is still
negative: `answer_confidence` is not P(true).

For review decisions prefer `answer_confidence` when present. Legacy `confidence`
has different meanings across question types; do not silently treat the two
fields as equivalent probabilities. Inspect `probabilities` on `choice` or
`score` when ambiguity matters. Do not use `action.act_probability` as a signal
that the agent should act. Do not invent a rationale the model did not return.

`laya_predict` does **not** apply a confidence threshold or return
`requires_review`. Apply the user's evaluation policy at the agent layer.
Missing confidence, uncertain evidence or conflicting labels should remain
unresolved or go to review. Do not invent a universal threshold. For a binary
detector, a calibrated two-threshold policy can distinguish positive, negative
and review cases; a bare P(true) of 0.5 is not positive evidence.

Action tools return `requires_review` and `recommended_action_id`. When review
is required, do not automatically execute the returned proposal. The selected
action must also fit the observed facts and the user's authorization.

## Dependent decisions

1. Call `laya_start_sequence` with a goal, step budget and review threshold.
   Retain the returned `sequence_id` and `revision`.
2. Gather fresh evidence. Call `laya_next_decision` with the current revision
   and 2–20 concrete candidates with unique `id` and `description` fields.
3. Review the proposal and execute at most that action with the agent's tools.
   Record actual evidence using `laya_record_outcome`, the returned
   `decision_id` and current revision. Outcomes are `succeeded`, `failed` or
   `skipped`; use `skipped` for a rejected proposal. Keep the new revision.
4. Repeat from observed results. Close with `laya_close_sequence` when complete,
   cancelled or no longer able to progress. All recorded outcomes consume the
   budget; three consecutive failures block further decisions.

On reconnect or a stale revision, call `laya_get_sequence` and inspect the real
environment before retrying a pending action: it may already have happened.

## Fit and limits

Use a direct rule, parser or calculation for exact deterministic checks. Use
the agent's normal capabilities for writing, translation, summaries, code,
open-ended reasoning, extracting arbitrary names/amounts, or interpreting image
pixels. MCPLaya accepts caller-provided text/JSON and returns finite decisions.

Treat use cases as workflows to evaluate, not proof of accuracy. The base models
are not validated for arbitrary next-action selection. Upstream documents
weaknesses in binary questions and ordinal scoring; test positive, negative,
ambiguous and out-of-domain examples before relying on them. Security screening
is an advisory signal, not a complete security boundary. Confidence alone does
not establish correctness, permission or a completed action.

Report the requested label, score or proposed action concisely, with uncertainty
and any observed outcome. For multiple records, preserve IDs and the same schema.
Do not claim a cold model is warm, promise millisecond latency, or claim measured
accuracy, token savings or executed actions without evidence.
