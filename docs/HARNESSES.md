# Usage skill packages for agent harnesses

The shared usage skill is `skills/mcplaya-decisions/SKILL.md`, with its supporting
`references/` directory. Each harness package places those same files in a
documented project-level discovery directory. The Codex package also includes
the existing `agents/openai.yaml` UI metadata.

The JSON files under `skills/mcplaya-decisions/agents/profiles/` are **MCPLaya
export profiles**, read by `scripts/export_usage_skill.py`. They are not native
harness configuration files. Other harnesses discover the generated `SKILL.md`
through their own folder layout; they do not need an invented `claude.yaml`,
`cursor.yaml` or other OpenAI-style metadata file.

## Harnesses and native layouts

The following project discovery locations were checked against official
documentation on 2026-11-13. Append `/mcplaya-decisions/SKILL.md` to each directory.

| Export ID | Harness | Project skill directory | Official documentation |
|---|---|---|---|
| `codex` | OpenAI Codex | `.agents/skills/` | [Skills](https://learn.chatgpt.com/docs/build-skills) |
| `claude-code` | Claude Code | `.claude/skills/` | [Skills](https://code.claude.com/docs/en/skills) |
| `cursor` | Cursor | `.cursor/skills/` | [Agent Skills](https://cursor.com/docs/skills) |
| `copilot` | GitHub Copilot | `.github/skills/` | [Agent Skills in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills) |
| `opencode` | OpenCode | `.opencode/skills/` | [Skills](https://opencode.ai/docs/skills/) |
| `gemini-cli` | Gemini CLI | `.gemini/skills/` | [Agent Skills](https://geminicli.com/docs/cli/skills/) |
| `cline` | Cline | `.cline/skills/` | [Skills](https://docs.cline.bot/customization/skills) |
| `roo-code` | Roo Code | `.roo/skills/` | [Skills](https://roocodeinc.github.io/Roo-Code/features/skills/) |

These are portable instruction packages for current versions supporting the
documented skill format. Discovery, invocation and tool availability still need
verification in the installed harness version; archive tests do not establish a
live integration result.

## Generate packages

From the repository checkout or extracted Python source distribution:

```sh
uv run --frozen python scripts/export_usage_skill.py --list
uv run --frozen python scripts/export_usage_skill.py --harness all
```

Export a single harness or choose a different output folder:

```sh
uv run --frozen python scripts/export_usage_skill.py --harness claude-code
uv run --frozen python scripts/export_usage_skill.py --harness cursor --output-dir dist/cursor
```

The script uses only the Python standard library. With an available Python
3.10–3.12 interpreter, it can also be run directly without `uv run` or the
inference dependencies.

The default output is `dist/mcplaya-decisions-<export-id>.zip`. Each archive
contains a native project directory, for example:

```text
.claude/
  skills/
    mcplaya-decisions/
      SKILL.md
      references/
        use-cases.md
        recipes.md
        performance.md
      LICENSE
      NOTICE
```

The archives use regular UTF-8 files, relative paths and fixed timestamps.
They contain no symlinks, Python environments, weights, credentials, executable
hooks, global settings or MCP connection configuration. Exporting writes ZIP
files only; it does not activate a skill in any agent.

## Use a package

Extract the selected archive into the target project's root, preserving its
leading hidden directory. For example, the Claude Code archive creates
`.claude/skills/mcplaya-decisions/` there. When updating an existing copy, review
any local edits before replacing its skill folder. Keep the `references/`
directory beside `SKILL.md` so relative links continue to work.

Reload or restart the harness if the skill is not discovered immediately, then
ask it to use `mcplaya-decisions` to categorize a short text. Claude Code and
Cursor provide skill selection through their `/` interface; Gemini CLI has
`/skills list`; OpenCode can load a skill by its ID. In other harnesses, use the
skill selector or a request matching its description.

The local MCPLaya stdio connection must also be configured and expose the tools.
Skill discovery does not install or start the server. Use the
[installation guide](INSTALLATION.md) for that separate step. Keep the MCP
client local to the user's computer; a cloud harness cannot launch a subprocess
on that computer without a local connector.

If several harnesses share the same project, use only the discovery locations
you need. Some harnesses read other tools' compatibility directories too;
duplicate copies with the same skill name can override each other or appear
more than once. Re-export from the canonical skill when updating it.
