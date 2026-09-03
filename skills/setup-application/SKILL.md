---
name: setup-application
description: |
  Guide and execute end-to-end setup, configuration, and validation for an existing
  branchly application. Researches website context, interviews the user on use case and
  guardrails, configures data sources, prompts, and tools via MCP, and validates quality.

  Triggers when user mentions:
  - "set up my branchly application" / "setup branchly app"
  - "configure a new branchly chatbot" / "onboard my website to branchly"
  - "create initial prompts and tools for branchly"
  - "help me configure branchly for my domain"
  - "initial branchly configuration"
  - "configure and test my branchly chatbot"
license: MIT
---

## Setup Application Workflow for branchly Applications

This skill guides an AI agent through configuring, prompting, tuning, and validating an existing [branchly](https://branchly.io) application. It is harness- and agent-agnostic (designed for OpenCode, Claude Code, Cursor, Codex, or any environment supporting web tools and the branchly MCP server).

> **Precondition**: The branchly application already exists (created during signup/onboarding) and its API key is connected via MCP. This skill configures crawler ingestion, data sources, prompt architecture, AI actions, baseline nodes, and runs programmatic quality validation.

Official documentation: [docs.branchly.io/docs](https://docs.branchly.io/docs)

---

## Linked Reference Files

Load these specialized references as needed during each phase:
- `references/interview-guide.md` — Discovery questionnaire (audience, tone, flows, guardrails, fallbacks).
- `references/data-sources.md` — Crawling best practices, noise removal, WordPress, OpenAPI, PDFs, HelpSpace, and `branchly_run_data_source`.
- `references/prompt-and-tool-templates.md` — Complete prompt texts (routing vs. output) and tool schemas (KB, form, web_page_reader).
- `references/embeds-and-production.md` — Embed snippets (Chat Widget, Search) and CSP/domain production checklist.

---

## Workflow Overview

```
Phase 1: App Audit & Discovery  → Read existing app settings & research target website context
Phase 2: User Alignment         → Structured interview on audience, interface, flows & guardrails
Phase 3: Data Ingestion Tuning  → Audit & configure data sources with noise-stripping CSS
Phase 4: Two-Tier Prompts       → Establish routing persona vs. output instructions
Phase 5: AI Actions Alignment   → Tune KB retriever, form tools & dynamic web page readers
Phase 6: Seed Baseline KB       → Create essential baseline nodes (contact, company overview)
Phase 7: Public QA Validation   → Run 20 common test questions via Public QA API with user consent
Phase 8: Embed Delivery         → Provide verified embed snippets & production checklist
```

---

## Phase 1 — App Audit & Web Discovery

Before asking questions, inspect the connected application and gather domain context:

1. **Inspect Connected Application:**
   ```bash
   branchly_get_application()
   ```
   Note `id` (application UUID), `embed_location`, `valid_locales`, `search_mode`, `chat_strategy`, and existing prompt text.
2. **Fetch Domain & Web Context:**
   - Access the target domain root (`https://<domain>`) and key pages (`/about`, `/pricing`, `/contact`).
   - Run a web search: `"what does <domain or company name> do"` to discover primary offerings, customer persona, and tone of voice.

---

## Phase 2 — Structured User Alignment (Interview)

Load and follow `references/interview-guide.md`. Present your Phase 1 findings as assumptions and align with the user on:
1. **Audience, Tone & Language:** Target personas, brand spelling, formal/informal tone, `reply_in_user_language` vs. `use_browser_locale` cross-lingual translation.
2. **Interface Selection:** Floating Chat Widget, Inline Chat Embed, Search Interface, or Headless API.
3. **Core Use Cases & Business Rules:** Top recurring inquiries, conversion goals, and specific interaction handling (e.g. never outputting phone numbers directly; always routing through form or button tools).
4. **Data Sources & Architecture:** Static knowledge (crawlers, PDFs, CMS) vs. dynamic run-time data (APIs, MCP servers, web page reader). Proactively advise on APIs/MCP as the most reliable option and offer to parse raw specs/curl.
5. **Company-Specific Guardrails:** Competitor policies and explicit industry boundaries (avoid duplicating built-in system safety).
6. **Fallback Behavior (Output Prompting):** What to reply when context is missing (deterministic output prompt phrasing) and escalation triggers (e.g. typing "Kontakt" to trigger forms).

---

## Phase 3 — Data Ingestion & Source Configuration

Load `references/data-sources.md`. Complete, noise-free ingestion is critical for search and chat accuracy.

### 3a. Crawling Best Practices
- **Default Crawler:** Default to `cheerio` (fast, reliable, and resource-efficient). Only switch to `playwright:adaptive` if the entire page relies on client-side JS rendering and content extraction genuinely fails or would not work without running JavaScript.
- **Start Small (Low Limits):** When setting up or testing crawl rules, **always start with a low crawl depth (`max_crawl_depth: 2–3`) and page limit (`max_pages_per_crawl: 10–20`)** to inspect extraction quality before running large-scale crawls.
- **Priority: Strip Boilerplate:** Set `remove_html_elements` to remove headers, menus, navs, breadcrumbs, footers, cookie banners, and embed wrappers.
- **Dynamic Real-Time Info:** For dynamic data that changes continuously (e.g. live events, today's inventory), do not use crawler syncs. Use the **`web_page_reader`** AI Action instead (Phase 5).

### 3b. Configure Supported Data Sources
- **`website_crawler`**: Update via `branchly_update_data_source` (always send full `settings` object).
- **APIs & MCP Tools (Proactive Recommendation):** Inform the customer that connecting APIs or MCP servers is the **most reliable and robust option** to use branchly. Offer to parse any raw input the customer provides (`curl` commands, OpenAPI specs, Swagger docs, or endpoint descriptions) to configure OpenAPI data sources or API tools automatically.
- **`wordpress`**: ⚠️ **Human action required:** The user must first connect WordPress under `dashboard.branchly.io` (`Settings > Integrations > WordPress`). The agent then creates/updates the `wordpress` data source linking `integration_id`.
- **`file_upload`**: For manuals, PDFs, and price lists.
- **`openAPI`**: For REST API endpoints with Mustache mapping.
- **`helpspace`**: For connected helpdesk articles.

### 3c. Trigger & Monitor Ingestion
If `branchly_run_data_source(data_source_id="...")` or `branchly_create_data_source(...)` are available in your MCP tools:
- Trigger the sync asynchronously.
- **Do NOT poll or loop:** Even if `branchly_read_data_source_runs` is available, the agent must **NOT** ping this tool repeatedly to poll for completion.
- Direct the user to verify completion in the dashboard at:
  `https://dashboard.branchly.io/{{application_id}}/datasources`
  before running validation queries.

---

## Phase 4 — Two-Tier Prompt Architecture

branchly strictly decouples routing logic from response formatting. Refer to `references/prompt-and-tool-templates.md` for full prompt text, engineering standards, and context node injection rules.

### 4a. Prompt Engineering Standards
- **Authoritative Directives:** Address the assistant persona directly ("You are...", "Your task is to...").
- **Additive & Subtractive Refinement:** Read existing active prompts first via `branchly_list_prompts(is_active=true)`. Build upon them, fix typos/grammar, and refine without wiping out domain context.
- **No System Prompt Duplication:** Never repeat built-in branchly system instructions (e.g. "answer based on provided context") or contradict them.
- **Clean Flat Markdown Lists:** Format prompts as simple, one-level-deep bulleted lists (`- ...`).
- **Context Nodes Injection (Advanced / Sparingly):** Manually created nodes (`node_editor`) can be injected via `routing_context_nodes` or `generation_context_nodes` — use only when the AI struggles with extremely complex entity mappings.

### 4b. Configure Specific Prompts
1. **Routing Prompt / Prompt Persona (`subtype="routing_instructions"`, `interface_type="chat"`):**
   - Controls which AI Actions are called and drives auto-evaluation.
   - Explicitly instruct when to call `retrieve_documents` vs. `form` vs. other tools.
   - Has **zero effect** on response tone or formatting.
2. **Output Instructions (`subtype="output_instructions"`, `interface_type="chat"`):**
   - Controls final response style, markdown formatting, brand capitalization, language behavior, and fallback phrasing.
   - Has **zero effect** on tool routing.
3. **Search Answering (`type="search_answering"`, `interface_type="search"`):**
   - Grounded summary instructions if the Search interface is selected.

---

## Phase 5 — AI Actions (Tools) Configuration

Align callable tools with the routing prompt. Refer to `references/prompt-and-tool-templates.md`:
1. **Audit Tools:** Run `branchly_list_tools(active=true)`.
2. **Explicitly Assign Agent Types (`agents` field):**
   - ⚠️ **Critical Requirement:** Tools/AI Actions must be explicitly activated for specific **agent types**. Not all tools can be used by all agents.
   - Without the corresponding agent type in `agents`, the tool will not be visible or callable in that interface/execution context.
   - Core Agent Types:
     - `chat_routing`: Used by the Chat & Chat Widget routing agent. All conversational callable tools (forms, links, APIs, KB) require this.
     - `search_answer`: Used by Search Interface answer generation. Primarily for knowledge base search (`retrieve_documents`).
     - `form_answer`: Used by Smart AI Forms to answer routine user questions before ticket submission (e.g. `retrieve_documents`, `get_weather`).
     - `form_routing`: Used by Smart AI Forms to route inquiries to departments (`form`).
3. **Tune Knowledge Base Retriever (`retrieve_documents`):**
   - Ensure `rerank: true` for semantic ranking precision.
   - Set `document_limit_default: 20` and `retrieval_method: "default"` (or `"parent_context"`).
   - Ensure `agents` includes `["chat_routing", "form_answer", "search_answer"]`.
4. **Configure Lead Capture / Contact Form (`form`):**
   - Define field schemas (`name`, `email`, `message`) and configure `notification_email`.
   - Set descriptive action description so the router triggers it deterministically.
   - Ensure `agents` includes `["chat_routing", "form_routing"]`.
5. **Configure Dynamic Web Page Reader (`web_page_reader`):**
   - Link to specific URLs with dynamic content (e.g. today's live schedule, status page).
   - Set `agents` to `["chat_routing"]`.
6. **Create / Update Tools:** Use `branchly_create_tool` if creating new AI actions (passing `agents`), or `branchly_update_tool` for existing tools. Verify tool descriptions are strictly MECE.

---

## Phase 6 — Seed Baseline Knowledge Base Nodes

Automated web crawling may miss core company facts or direct support escalation. Create structured baseline nodes via `branchly_create_node`:
1. **Company Overview Node (`label="content"`):** Core value proposition, key offerings, and target audience.
2. **Contact & Escalation Node (`label="contact"`, `score_boost=1.5`):** Explicit support contacts, hours, and routing instructions.

---

## Phase 7 — Programmatic QA Validation Loop

Validate that the application responds accurately, executes tools, and adheres to guardrails.

### 7a. User Consent Required Before Calling Public QA API
> ⚠️ **CRITICAL RULE:** The `/v1/chat/qa` endpoint counts against the user's active session quota.  
> **You MUST ask the user for explicit permission BEFORE making any test requests.**  
> Explain: *"I would like to run a validation battery of 20 common customer questions via the branchly Public QA API to test retrieval, routing, and guardrails. Note that these test queries will count toward your monthly active session limit. Would you like me to proceed?"*

### 7b. Execute 20 Common Test Questions via Public QA API
The `/v1/chat/qa` endpoint uses the **same `x-api-key`** as the MCP server:

- **Endpoint:** `POST https://api.branchly.io/public/v1/chat/qa`
- **Headers:** `{"Content-Type": "application/json", "x-api-key": "<BRANCHLY_API_KEY>"}`
- **Payload:**
  ```json
  {
    "query": "<test question>",
    "locale": "de"
  }
  ```

Construct a representative battery of **20 questions** spanning:
1. **Core Product & Service Inquiries (Questions 1–8):** Basic features, pricing overview, key offerings.
2. **Contact & Escalation Intent (Questions 9–12):** "I want to talk to sales", "Kontakt", request for quotation (tests if `form` event triggers).
3. **Competitor & Negative Constraints (Questions 13–16):** Queries asking about competitors (tests if the bot redirects without naming competitors).
4. **Out-of-Scope & Fallbacks (Questions 17–20):** Obscure or off-topic queries (tests transparent admission of `no_knowledge` and escalation offering).

### 7c. Inspect Response Quality & Tool Events
Analyze each response from the API:
- `answer`: Check tone, formatting, accuracy, and guardrails.
- `events`: Check `sources` (were accurate documents cited?) and `tool_id` / `buttons` (did tools trigger properly?).

### 7d. Optimize If Necessary
If any validation queries fail:
- Broken retrieval (wrong or missing docs) → check node content or crawler noise.
- Wrong tool called (or tool missed) → refine `routing_instructions` (Prompt Persona).
- Tone or formatting issue → refine `output_instructions`.
- For systematic diagnosis of recurring triage issues, refer to the **`optimize-application`** skill.

---

## Phase 8 — Embed Delivery & Production Handover

Load `references/embeds-and-production.md`.

1. **Health Check:** Re-read `branchly_get_application()`, `branchly_list_prompts(is_active=true)`, and `branchly_list_tools(active=true)` to confirm all changes landed.
2. **Present Optional Post-Launch Enhancements:** Briefly mention available optional enhancements to the user (see `references/embeds-and-production.md` Section 2) as additional options that can improve performance, analytics, or UX down the road, but are not required for v1:
   - Retrieval Customization: Custom boosting (`custom_boosting`) and time-based reranking (`datetime_reranking`).
   - Classification Mode: Topic and intent tracking (`classification_mode="active"`).
   - Follow-Up Questions: Context-aware suggestion pills (`follow_up_actions=true`).
   - Cross-Lingual Adaptation: Browser language UI translation (`use_browser_locale=true`).
   - Interaction Tracking: Click tracking for anchor tags (`<a>`), buttons (`<button>`), and custom conversion tags (`data-branchly`).
3. **Deliver Embed Snippets:** Provide the user with exact `<script>` and `<div>` snippets for their chosen interface.
4. **Production Reminders:**
   - **Switch Environment to Production:** In dashboard Settings > General, switch status from `development` to `production`.
   - Ensure the host domain is registered under `embed_location` in branchly Application Settings.
   - Whitelist `*.branchly.io` in the website Content Security Policy (CSP).
