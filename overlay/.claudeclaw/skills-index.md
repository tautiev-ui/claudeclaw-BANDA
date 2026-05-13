# BANDA skills index

This starter kit does not bundle third-party or upstream skills.

Agents can use skills installed in the local Claude Code / ClaudeClaw environment, for example `~/.claude/skills/`, if the user has installed them separately.

## Recommended optional skills

| Skill | Useful for |
|---|---|
| `systematic-debugging` | debugging and root-cause work |
| `quality-check` | final review / OTK |
| `writing-plans` | implementation planning |
| `deep-research-pro` | web/source research |
| `code-review` | code review |
| `dep-audit` | dependency and license audit |
| `audit-website` | website audit |
| `excalidraw` | diagrams |
| `minimax-docx` | DOCX work, if installed separately |
| `minimax-pdf` | PDF work, if installed separately |
| `minimax-xlsx` | spreadsheet work, if installed separately |
| `pptx-generator` | presentations, if installed separately |

If a skill is missing, agents should say so and continue with base tools instead of pretending it exists.
