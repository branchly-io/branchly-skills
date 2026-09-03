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

### `setup-application`

Guide and execute end-to-end setup and configuration for a branchly application. Conducts website research, interviews the user on use case and guardrails, and configures data sources, prompts, AI actions, and knowledge base nodes via MCP.

**Triggers when you mention:**
- "set up my branchly application" / "setup branchly app"
- "configure a new branchly chatbot" / "onboard my website to branchly"
- "create initial prompts and tools for branchly"
- "help me configure branchly for my domain"
- "initial branchly configuration"

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
npx skills add branchly-io/branchly-skills --skill setup-application
```

## Requirements

- [OpenCode](https://opencode.ai) or any other agent platform (Claude Code, Codex, Gemini CLI, Cursor, etc.) with the [branchly MCP server](https://docs.branchly.io/docs/mcp-server) configured
- branchly MCP server connected (provides `branchly_*` tools)

## License

MIT
