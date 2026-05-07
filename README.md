# branchly-skills

OpenCode skills for [branchly](https://branchly.io) applications.

## Skills

### `optimize-application`

Systematically debug and optimize a branchly application. Covers session triage, retrieval quality, prompt/tool alignment, and data source health.

**Triggers when you mention:**
- "optimize my branchly application"
- "chatbot is not answering correctly" / "bot gives wrong answers"
- `no_knowledge` or `outside_scope` responses
- "debug my chatbot" / "chatbot retrieval issue"
- "improve retrieval" / "fix bot responses"

## Installation

```bash
npx skills add branchly-io/branchly-skills
```

Or to install a specific skill only:

```bash
npx skills add branchly-io/branchly-skills --skill optimize-application
```

## Requirements

- [OpenCode](https://opencode.ai) with the [branchly MCP server](https://docs.branchly.io/docs/mcp-server) configured
- branchly MCP server connected (provides `branchly-app_*` tools)

## License

MIT
