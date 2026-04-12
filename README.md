# Claude Skills — evidence-backed AI agent skills

## Methodology

Every rule, checklist item, and review criterion traces to one of:

- **Academic research** — arxiv.org, peer-reviewed papers, Google Scholar, PubMed
- **Technical standards** — RFCs, official specifications, language/framework documentation
- **Human-tested** — double-checked and reviewed by a human before commit

## Skills

| Skill | Description |
|--|--|
| `/research` | Web research with source verification and critical analysis |
| `/java-reviewer` | Deep Java code review with parallel specialist agents and verification. [Details](plugins/java-reviewer/skills/java-reviewer/README.md) |
| `/context-engineer` | Audit and optimize any AI agent context: CLAUDE.md, SKILL.md, prompts, instructions. Adapt project docs for AI consumption |
| `/clean-code` | Improve code readability and maintainability |

## Installation

Add the marketplace:

```
/plugin marketplace add rootbr/claude-skills
```

Install skills:

```
/plugin install <skill-name>@rootbr/claude-skills
```

## License

Apache 2.0
