# branchly-skills

Skills for managing, optimizing, and creating content for [branchly](https://branchly.io) applications.

## Skills

### `optimize-application`

Systematically debug and optimize a branchly application. Covers session triage, retrieval quality, prompt/tool alignment, and data source health.

**Triggers when you mention:**
- "optimize my branchly application"
- "chatbot is not answering correctly" / "bot gives wrong answers"
- `no_knowledge` or `outside_scope` responses
- "debug my chatbot" / "chatbot retrieval issue"
- "improve retrieval" / "fix bot responses"

### `content-ideas`

Analyze branchly analytics to generate prioritized website content recommendations (page updates, targeted FAQ question lists, and new article/blog topics). Optimizes website content for AI search and user clarity.

**Triggers when you mention:**
- "what content should we create" / "content ideas"
- "which pages/topics to prioritize on our website"
- "what questions should we add as FAQs"
- "find content gaps on our website"
- "improve AI search content" / "what should we write about next"

## Installation

### Install all skills at once (recommended)

Install all available skills from this repository to your detected AI agents without interactive prompts:

```bash
npx skills add branchly-io/branchly-skills --all
```

Or globally across all your projects:

```bash
npx skills add branchly-io/branchly-skills --all -g
```

### Install interactively or select specific skills

Install interactively (prompts to pick skills and target agents):

```bash
npx skills add branchly-io/branchly-skills
```

Or install a specific skill directly:

```bash
npx skills add branchly-io/branchly-skills --skill content-ideas
npx skills add branchly-io/branchly-skills --skill optimize-application
```

## Requirements

- [OpenCode](https://opencode.ai) or any other agent platform (Claude Code, Codex, Gemini CLI, Cursor, etc.) with the [branchly MCP server](https://docs.branchly.io/docs/mcp-server) configured
- branchly MCP server connected (provides `branchly_*` tools)

## License

MIT
