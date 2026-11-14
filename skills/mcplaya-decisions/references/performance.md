# Fast decisions and model choice

## Reduce avoidable work

1. Use `laya_predict` directly for classification or independent questions.
   Use `laya_choose_action` for one bounded action; create a sequence only when
   later choices actually depend on prior action results.
2. Keep the MCP connection and server process alive across requests. The
   backend retains loaded models in memory. Process restarts lose this benefit;
   disk-cached weights still need loading into memory.
3. Group independent questions about the same short state in one call. This
   avoids repeated MCP round trips and can share the inference work. Several
   documents packed into one state are not an independent-record batch.
4. Keep input and criteria concise. Remove irrelevant boilerplate while
   preserving decisive evidence. A large character allowance is not a guarantee
   that the checkpoint will see all input tokens.
5. Use a small relevant label set, with no more than 20 choices. Hierarchical
   classification can preserve a large taxonomy, but each additional stage has
   latency and error cost; preserve a review path after an uncertain first stage.
6. Reuse a stable schema across records. Repeated identical input may be cached
   by the caller only when text, rubric, checkpoint identity and relevant context
   match; MCPLaya does not provide a result cache.

`laya_status` is lazy: it reports initialization but does not warm a checkpoint
or test a prediction. If model acquisition is already authorized, a small real
prediction can warm the selected model. Do not silently trigger a large first
download just because a skill was loaded. Report missing model files or offline
errors instead of repeatedly retrying them.

## Select a model deliberately

| Value | Prefer it for | Important limit |
|---|---|---|
| `auto` | General use when language is unknown | Routes language; it does not automatically choose the task specialist here |
| `english` | Known English input, including evaluated English score rubrics | English checkpoint can be confidently wrong on other languages |
| `multilingual` | Known non-English or mixed-language text | Evaluate each target language; upstream reports ordinal position bias |
| `typed-decisions` | English data resembling the four specialist workflows in the use-case reference | Explicit opt-in, not a universal reasoning or navigation model |

`LAYA_ACTION_MODEL` overrides the router for **all inference tools**, including
`laya_predict`. When it is configured, the `model` argument does not switch
between the official checkpoints. `laya_status` reports a custom checkpoint only
after it is loaded, so a false `custom_checkpoint_loaded` flag does not establish
that no override is configured. Inspect the local setting when available.

The router's default memory limit is two loaded checkpoints. Switching among
all three model names can cause eviction and reloads. Prefer stable model
selection based on language and validated task fit rather than switching as an
attempt to make repeated guesses agree.

CPU works by default. CUDA and Apple MPS depend on the installation and hardware;
device changes belong to setup, not to an ordinary classification request.

## What this wrapper actually exposes

The available inference tools are `laya_predict`, `laya_choose_action` and
`laya_next_decision`. There is no `laya_classify`, `laya_batch`, `laya_preset`,
`laya_route`, warmup or preload tool in MCPLaya.

`laya_predict` accepts only `state`, `questions` and `model`. Do not send
`max_len`, `batch_size`, `min_confidence`, `preset`, `labels`, `task`, `lang`,
`lang_guess` or `return_details` as extra arguments. In particular, the current
question validator does not preserve the upstream optional `labels` field;
do not copy label-override examples from newer/direct Laya APIs.

There is no exposed long-document/windowed inference setting, multi-record
batch API, embedding shortlisting, generated explanation or direct filesystem
reader. Ask one call per independent record; this backend serializes inference
with a lock, so parallel client calls are not a model-throughput optimization.
For long text, use relevant excerpts or a caller-controlled chunking policy.
An "any section matches" detector and a document-wide category require different
aggregation rules; do not silently average away the decisive excerpt.

## Handle uncertainty and verify gains

Upstream 0.3.20 documents binary-label sensitivity, multilingual ordinal bias,
and weak general-checkpoint performance on specialist workflows. Explicit binary
criteria clarify the task but do not fix those model limitations. If a binary
question behaves inconsistently on known positives and negatives, evaluate a
two-option `choice` alternative or fall back to review; do not relabel a score
as calibrated truth.

Evaluate a representative labeled sample before adopting a workflow. Include
out-of-domain and ambiguous inputs, each target language and each category.
For independent tags, measure each tag; for routing, track review rate and
errors among accepted decisions. Select thresholds from the cost of errors,
not from a generic confidence number copied from an example.

For speed, distinguish first-request time (download/load may dominate) from
subsequent requests in the same process. Measure end-to-end MCP latency for
the intended text length, question count, model and device; use repeated warm
requests to report a median and a tail percentile when enough observations
exist. MCPLaya's response does not include latency or routing metadata, so use
caller-side timing. Report the environment and whether weights were cached.
An upstream accelerator benchmark is not a promise about a user's CPU.
