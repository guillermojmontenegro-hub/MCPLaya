# Agensi submission kit

Verified against the following official pages on 2026-11-13:
- https://www.agensi.io/sell
- https://www.agensi.io/learn/how-to-sell-skills-on-agensi
- https://www.agensi.io/learn/skill-md-creator-checklist

## Deliverable

Generate `dist/laya-decisions.zip` with `python scripts/package_skill.py`.
The archive contains one top-level `laya-decisions/` folder, with SKILL.md,
references/usage.md, LICENSE and NOTICE. Only text files, no weights, credentials,
symlinks, virtual environment or server binaries. Install the server separately
from the GitHub repository. Agensi hosting of a skill is not remote MCP hosting.

## Suggested listing (English)

Title: Laya Decisions — MCP Decision Sequences for Coding Agents

Summary: Delegate bounded choices to a local Laya model. Maintain an explicit
observe-decide-act loop with durable history, fresh observations, confidence
review and bounded steps.

Description: For agent workflows that repeatedly choose the next concrete action,
this skill connects a coding agent to MCPLaya. It explains when to use a single
choice versus a dependent sequence, how to submit candidates, record observed
outcomes and recover pending decisions after reconnecting. Execution stays with
the agent's normal tools. Includes schemas and a worked sequence. Requires a
separately installed local Python MCP server and initial Hugging Face model
download. General checkpoints require task-specific evaluation; no accuracy,
latency or token-saving guarantee is made. Code and skill are Apache-2.0 and
publicly available on GitHub.

Category: Agents & Orchestration
Tags: laya, mcp, decision-making, sequential-decisions, workflow, local-inference
Compatibility: Clients with stdio MCP and Markdown skill instructions. Connection
formats vary. Claude Code, Cursor and VS Code Copilot examples are supplied;
live behavior in these clients still needs manual validation.
Pricing: Owner chooses in Creator Studio; no price has been set by this project.

## Submission steps

1. Run tests, build server artifacts and inspect the ZIP.
2. Before submission, test the skill in a real agent and preferably a second client;
   confirm trigger discovery, tool setup, a successful loop, low-confidence review,
   recovery and output quality. Unit/MCP protocol tests do not establish client UX
   or model accuracy. Evaluate actual decisions on representative domain examples.
3. Sign in, enable Creator Mode, and create a skill submission in Creator Dashboard.
4. Upload ZIP and enter the listing metadata. Disclose the separate MCP dependency
   and Apache-2.0 availability. Choose free or paid and owner-approved price.
5. Configure payouts if paid. Review platform terms for compatibility with the
   open-source license. Submit to the platform's automated and human review.

No listing has been uploaded or published. Agensi approval and live client/model
validation are external steps; the prepared archive is the submission artifact.
