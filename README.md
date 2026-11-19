# branchly-skills

Skills for managing, optimizing, and creating content for [branchly](https://branchly.io) applications.

## Skills

### `optimize-application`

Systematically debug and optimize a branchly application. Covers session triage, retrieval quality, prompt/tool alignment, and data source health. Includes `scripts/analyze_node_noise.py` (pure Python stdlib) for quantifying boilerplate noise in crawled node HTML and deriving `remove_html_elements` selectors.

**Triggers when you mention:**
- "optimize my branchly application"
- "chatbot is not answering correctly" / "bot gives wrong answers"
- `no_knowledge` or `outside_scope` responses
- "debug my chatbot" / "chatbot retrieval issue"
- "improve retrieval" / "fix bot responses"

### `setup-application`

Guide and execute end-to-end setup, configuration, and validation for an existing branchly application. Conducts website research, interviews the user on use case and guardrails, configures data sources, prompts, and tools via MCP, and validates response quality and tool routing.

**Triggers when you mention:**
- "set up my branchly application" / "setup branchly app"
- "configure a new branchly chatbot" / "onboard my website to branchly"
- "create initial prompts and tools for branchly"
- "help me configure branchly for my domain"
- "initial branchly configuration"
- "configure and test my branchly chatbot"

### `content-ideas`

Analyze branchly analytics to generate prioritized website content recommendations (page updates, targeted FAQ question lists, and new article/blog topics). Optimizes website content for AI search and user clarity.

**Triggers when you mention:**
- "what content should we create" / "content ideas"
- "which pages/topics to prioritize on our website"
- "what questions should we add as FAQs"
- "find content gaps on our website"
- "improve AI search content" / "what should we write about next"

### `website-insights`

Generate a plain-language, CMO-ready analytics insight report about what is happening on a branchly-powered website: engagement, customer demand signals, friction, and funnel and market opportunities. Output is executive-level and action-first (content plans, funnel fixes, campaign/geography inputs).

**Triggers when you mention:**
- "website analytics report" / "what is happening on our website"
- "customer insights" / "what are users asking"
- "marketing report" / "CMO dashboard"
- "how is our chatbot/AI search performing"
- "where are we losing users" / "what should marketing focus on"

### `create-faqs`

Create FAQ entries for a branchly-powered website from real visitor demand signals. Consumes question sets and demand evidence from content-ideas (searches, classification topics, tags, interaction sources, top cited nodes), reads the chat and search prompt personas for the use case, verifies every answer 100% against website content with cited source passages, and delivers the FAQs in the output format chosen upfront — a file, branchly nodes, or CMS-ready page content.

**Triggers when you mention:**
- "create FAQs" / "generate FAQs" / "add an FAQ section to page X"
- "answer the questions visitors keep asking"
- "turn our chat/search questions into FAQs"
- "publish FAQ nodes" / "write the FAQ copy"
- "use the FAQ question list from content-ideas"

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
npx skills add branchly-io/branchly-skills --skill create-faqs
npx skills add branchly-io/branchly-skills --skill optimize-application
npx skills add branchly-io/branchly-skills --skill setup-application
npx skills add branchly-io/branchly-skills --skill website-insights
```

## Requirements

- [OpenCode](https://opencode.ai) or any other agent platform (Claude Code, Codex, Gemini CLI, Cursor, etc.) with the [branchly MCP server](https://branchly.io/en/docs/mcp-server) configured
- branchly MCP server connected (provides `branchly_*` tools)

## License

MIT
