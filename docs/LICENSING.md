# Distribution review — 2026-11-13

## Finding

The PyPI release used here, `laya==0.3.20`, declares Apache-2.0. Upstream source
LICENSE and all three official model cards also declare Apache-2.0. This permits
commercial use, modification and redistribution, including paid distribution,
subject to the license conditions. It does not grant ownership of Laya or a right
to imply endorsement. Apache-2.0 grants no general trademark license.

Sources inspected:
- https://pypi.org/pypi/laya/0.3.20/json
- https://github.com/NandhaKishorM/laya/blob/main/LICENSE
- https://huggingface.co/convaiinnovations/laya/blob/main/README.md
- https://huggingface.co/convaiinnovations/laya-multilingual/blob/main/README.md
- https://huggingface.co/convaiinnovations/laya-typed-decisions/blob/main/README.md
- https://www.apache.org/licenses/LICENSE-2.0 (particularly sections 2, 4, 6)

This is a review of the published declarations, not an audit of the provenance
of training data, base models or every transitive dependency. Model-card `main`
can change; archive and review the exact revision if you redistribute weights.

## Packaging decision

MCPLaya is new wrapper code and skill text under Apache-2.0. It uses Laya as a
pinned external dependency, installed by the buyer. No upstream implementation,
model binaries or base-model assets are copied into the repository, Python wheel
or skill ZIP. The ZIP includes the wrapper's license and attribution.
`LAYA_ACTION_MODEL` is user supplied and is outside this license finding.

## If distributing Laya itself or weights later

- Include a complete copy of Apache-2.0 with the distributed work.
- Retain applicable copyright, patent, trademark and attribution notices.
- Mark modified files prominently when modifying upstream files.
- Preserve any upstream NOTICE attribution required by section 4(d), if present
  in the actual artifact/revision being distributed. This review does not assert
  that every upstream artifact has been checked for NOTICE files.
- Audit licenses/notices of bundled third-party dependencies and base assets;
  do not assume Laya's license relicenses them.
- Do not imply Laya/Convai endorsement, exclusivity, or restrict Apache rights
  in an upstream copy by a marketplace's proprietary terms.

Agensi's paid-skill delivery rules can differ from open-source redistribution
rights. Choose compatible listing terms and disclose Apache-2.0; do not promise
exclusive paid content when publishing the same skill in a public repository.
