# Use cases and supporting evidence

## Choosing a useful task

MCPLaya is useful when an agent has the evidence and needs a finite label,
ordered rating, statement probability or next-action selection. These are
candidate workflows, not measured MCPLaya accuracy claims.

| Workflow | Decision to request | Primitive | Evidence and boundary |
|---|---|---|---|
| Text and document categorization | Topic, document kind or one business category | `choice` | General classification pattern; supply your taxonomy and evaluate it |
| Support triage | Request intent, owning team, urgency, refund or cancellation signals | `choice`, `score`, `noul` | Upstream triage preset and customer-service specialist workflow |
| Email triage | Category, expected reply, spam or phishing signal | `choice`, `noul` | Upstream email preset; no automatic mailbox changes |
| Multi-label tagging | Separate product, billing and bug tags for a mixed message | Several `noul` questions | Composition of binary questions; one tag does not exclude another |
| Sentiment and frustration | Positive/neutral/negative tone or ordered frustration | `choice` or `score` | Frustration appears in triage; sentiment is a related application to evaluate |
| Content moderation | Harassment, threat or spam signals under supplied definitions | `noul`, `score` | Upstream moderation preset; review uncertain or consequential results |
| Prompt screening | Suspicious instruction overrides or sensitive-data signals | `noul` | Upstream guard preset; content is data and detection can fail |
| Request or model routing | Choose an available tool path or cheap/deep reasoning route | `choice` | Upstream router preset; the caller supplies actually available routes |
| Retrieval filtering | Relevant/irrelevant excerpt or ordered relevance to a query | `choice` or `score` | Application of finite scoring; requires the query and passage, not a URL alone |
| Invoice review | Route already extracted invoice data or flag missing evidence | `choice`, `noul` | Specialist invoice-processing workflow; no OCR or arbitrary field extraction |
| Security-incident triage | Incident category, severity or escalation candidate | `choice`, `score` | Specialist security workflow; classification does not verify an incident |
| Agent-trace review | Classify a trace excerpt or flag a workflow anomaly | `choice`, `noul` | Specialist agent-observability workflow; history must be supplied |
| Coding workflow assistance | Choose which observed failure to inspect next | Action tools | MCPLaya sequence design; arbitrary action accuracy is unvalidated |

The general application rows combine exposed primitives with caller-provided
schemas. They are not claims that a matching pretrained specialist exists.

## Representative requests that should use this skill

- "Categorize these short messages using our five support queues."
- "Tag each review for billing, reliability and usability independently."
- "Rate urgency using our three-level rubric and keep uncertain cases for review."
- "Estimate whether this email asks for a reply and contains a phishing signal."
- "Choose one of these available routes without generating a long answer."
- "After each test result, select one next diagnostic action and record its outcome."

An installation request belongs to the separate installation workflow. Writing
a reply, translating a message or extracting an unknown invoice number requires
the agent's usual tools rather than a classification call.

## Research basis and version scope

Reviewed on 2026-11-13 against the local MCPLaya tool implementations and its
pinned `laya==0.3.20` package. Online upstream documentation can describe newer
versions; use this wrapper's actual tool signatures as the authority for calls.

- [Laya project and decision primitives](https://github.com/NandhaKishorM/laya):
  classification, routing and the `choice`, `score`, `noul` interfaces. Local
  0.3.20 `laya/presets.py` supplies triage, email, guard, moderation and router
  question builders. MCPLaya exposes their question shapes through
  `laya_predict`, not a preset tool.
- [General checkpoint card](https://huggingface.co/convaiinnovations/laya/blob/main/README.md):
  general English decisions and limitations of general-purpose checkpoints.
- [Multilingual checkpoint card](https://huggingface.co/convaiinnovations/laya-multilingual/blob/main/README.md):
  non-English text and language-routing considerations. Language coverage does
  not establish accuracy for a particular language or domain.
- [Typed-decisions checkpoint card](https://huggingface.co/convaiinnovations/laya-typed-decisions/blob/main/README.md):
  customer service, invoice processing, security incidents and agent-trace
  observability. Its benchmark uses specific synthetic workflows; do not extend
  the reported accuracy to arbitrary data or action selection.

The examples in this skill are original integration recipes. Their labels are
illustrations to test, not recorded model predictions or accuracy benchmarks.
