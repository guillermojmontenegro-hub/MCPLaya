"""Check skill links and request recipes against the actual MCP schemas, offline."""
import asyncio
import inspect
import json
import re
from pathlib import Path

import jsonschema
import yaml
from laya.mcp.tools import validate_questions, validate_state

from mcplaya import server as server_module
from mcplaya.engine import candidates, threshold

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/mcplaya-decisions"


async def main():
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
    if not frontmatter:
        raise ValueError("SKILL.md needs YAML frontmatter")
    metadata = yaml.safe_load(frontmatter.group(1))
    if metadata.get("name") != SKILL.name or not metadata.get("description"):
        raise ValueError("Skill name and description must identify this skill")
    if "[TODO:" in content:
        raise ValueError("Unfinished skill scaffold")
    tools = {tool.name: tool.input_schema for tool in await server_module.server.list_tools()}
    seen = set()
    examples = 0
    for path in sorted(SKILL.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)", content):
            if "://" in link or link.startswith("#"):
                continue
            target = (path.parent / link.split("#")[0]).resolve()
            if not target.is_relative_to(SKILL.resolve()) or not target.is_file():
                raise ValueError(f"{path.relative_to(ROOT)}: missing or nonportable link {link}")
        blocks = re.findall(r"^```json[ \t]*\n(.*?)^```[ \t]*$", content, re.MULTILINE | re.DOTALL)
        for number, block in enumerate(blocks, 1):
            try:
                request = json.loads(block)
                if set(request) != {"tool", "arguments"}:
                    raise ValueError("Recipe must name a tool and its arguments")
                name, args = request["tool"], request["arguments"]
                jsonschema.validate(args, tools[name])
                inspect.signature(getattr(server_module, name)).bind(**args)
                if name == "laya_predict":
                    validate_state(args["state"])
                    cleaned = validate_questions(args["questions"])
                    if cleaned != args["questions"]:
                        raise ValueError("Question validator would discard or rewrite a recipe field")
                    for question in cleaned.values():
                        if question["type"] == "choice" and len(question["criteria"]) > 20:
                            raise ValueError("Choice recipe exceeds the wrapper's 20-option limit")
                        if question["type"] == "noul" and set(question.get("criteria", {})) != {"false", "true"}:
                            raise ValueError("Binary recipe needs explicit false/true criteria")
                if "actions" in args:
                    candidates(args["actions"])
                if "min_confidence" in args:
                    threshold(args["min_confidence"])
                if args.get("model", "auto") not in {"auto", "english", "multilingual", "typed-decisions"}:
                    raise ValueError("Unknown recipe model")
                seen.add(name)
                examples += 1
            except Exception as exc:
                raise ValueError(f"{path.relative_to(ROOT)}, JSON example {number}: {exc}") from exc
    if seen != set(tools):
        raise ValueError(f"Missing tool recipes: {sorted(set(tools) - seen)}")
    print(f"Usage skill validated: {examples} request recipes, all {len(tools)} MCP tools, portable links")


if __name__ == "__main__":
    asyncio.run(main())
