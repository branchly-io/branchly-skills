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

> **Precondition**: The branchly application already exists (created during signup/onboarding) and its API key is connected via MCP. This skill configures crawler ingestion, prompt architecture, AI actions, baseline nodes, and validates that the system responds accurately.

Official documentation: [docs.branchly.io/docs](https://docs.branchly.io/docs)

---

## Linked Reference Files

Load these specialized references as needed during each phase:
- `references/interview-guide.md` — Discovery questionnaire (audience, tone, flows, guardrails, fallbacks).
- `references/prompt-and-tool-templates.md` — Complete prompt texts (routing vs. output) and tool schemas.
- `references/crawler-and-embeds.md` — Crawler noise-reduction selectors, full settings payloads, and embed code.

---

## Workflow Overview

```
Phase 1: App Audit & Discovery  → Read existing app settings & research target website context
Phase 2: User Alignment         → Structured interview on audience, interface, flows & guardrails
Phase 3: Data Ingest Tuning     → Audit data sources & configure crawler with noise-stripping CSS
Phase 4: Two-Tier Prompts       → Establish routing persona vs. output instructions
Phase 5: AI Actions Alignment   → Tune KB retriever & configure lead/contact forms
Phase 6: Seed Baseline KB       → Create essential baseline nodes (contact, company overview)
Phase 7: End-to-End Validation  → Run validation test matrix & verify grounding/reasoning
Phase 8: Embed Delivery         → Provide verified embed snippets & production checklist
```

---

## Phase 1 — App Audit & Web Discovery

Before asking questions, inspect the connected application and gather domain context:

1. **Inspect Connected Application:**
   ```bash
   branchly_get_application()
   ```
   Note `embed_location`, `valid_locales`, `search_mode`, `chat_strategy`, and existing prompt text.
2. **Fetch Domain & Web Context:**
   - Access the target domain root (`https://<domain>`) and key pages (`/about`, `/pricing`, `/contact`).
   - Run a web search: `"what does <domain or company name> do"` to discover primary offerings, customer persona, and tone of voice.

---

## Phase 2 — Structured User Alignment (Interview)

Load and follow `references/interview-guide.md`. Present your Phase 1 findings as assumptions and align with the user on:
1. **Audience & Tone:** Target personas, brand spelling, formal/informal tone, language policy.
2. **Interface Selection:** Floating Chat Widget, Inline Chat Embed, Search Interface, or API.
3. **Core Use Cases:** Top 3–5 recurring questions and conversion goals (e.g. demo, quote, support).
4. **Guardrails & Limits:** Competitor rule (never mention competitors by name), pricing/discount policy, out-of-scope topics.
5. **Fallbacks & Escalation:** Transparent admission of no-knowledge and direct escalation path (`form` tool, email, phone).

---

## Phase 3 — Data Ingestion & Crawler Configuration

Clean data ingestion prevents noisy navigation and boilerplate from contaminating vector embeddings:
1. **Audit Data Sources:** Run `branchly_list_data_sources()` to inspect current status and crawler settings.
2. **Update Crawler Settings:** See `references/crawler-and-embeds.md`.
   - ⚠️ **Always send the complete settings object** (partial settings are rejected).
   - Apply standard noise-stripping CSS selectors (`remove_html_elements`).
   - Set exclude URL globs (`*/404`, `*/cart*`, `*/login*`) and a weekly sync schedule.
   - Remind the user to trigger a manual sync in the dashboard if they want immediate re-indexing.

---

## Phase 4 — Two-Tier Prompt Architecture

branchly strictly decouples routing logic from response formatting. Refer to `references/prompt-and-tool-templates.md` for full prompt text.

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
2. **Tune Knowledge Base Retriever (`retrieve_documents`):**
   - Ensure `rerank: true` for semantic ranking precision.
   - Set `document_limit_default: 20` and `retrieval_method: "default"` (or `"parent_context"`).
3. **Configure Lead Capture / Contact Form (`form`):**
   - Define field schemas (`name`, `email`, `message`) and configure `notification_email`.
   - Set descriptive action description so the router triggers it deterministically.
4. **Verify MECE Descriptions:** Tool descriptions must be mutually exclusive and collectively exhaustive.

---

## Phase 6 — Seed Baseline Knowledge Base Nodes

Automated web crawling may miss core company facts or direct support escalation. Create structured baseline nodes via `branchly_create_node`:
1. **Company Overview Node (`label="content"`):** Core value proposition, key offerings, and target audience.
2. **Contact & Escalation Node (`label="contact"`, `score_boost=1.5`):** Explicit support contacts, hours, and routing instructions.

---

## Phase 7 — End-to-End Validation & Quality Testing

**Do not finish setup without validating that the application actually works.**

1. **Verify Content Retrieval:**
   ```bash
   branchly_list_nodes(query="<key product/service>", locale="de", limit=5)
   ```
   Confirm relevant nodes exist and are free of HTML noise. Apply `score_boost` if high-priority topics rank low.
2. **Execute Validation Test Matrix:**
   - **In-Scope Query:** Confirms `retrieve_documents` fires and output is accurate.
   - **Contact / Lead Intent ("Kontakt"):** Confirms `form` tool fires immediately.
   - **Competitor / Guardrail Check:** Confirms AI refuses to mention competitor and redirects to brand strengths.
   - **No-Knowledge Fallback:** Confirms AI admits missing knowledge and offers contact escalation.
3. **Inspect Grounding & Reasoning (If Sessions Exist):**
   - `branchly_read_sessions(limit=5)` → `branchly_read_session_detail(session_id="...")`.
   - `branchly_read_chat_request_documents(...)` and `branchly_read_chat_request_tool_calls(...)`.
   - Check the Three Contracts: Content contract (clean KB), Retrieval contract (right docs surfaced), Routing contract (right tool called).

---

## Phase 8 — Embed Delivery & Production Handover

1. **Health Check:** Re-read `branchly_get_application()`, `branchly_list_prompts(is_active=true)`, and `branchly_list_tools(active=true)` to confirm all changes landed.
2. **Deliver Embed Snippets:** Provide the user with exact `<script>` and `<div>` snippets from `references/crawler-and-embeds.md`.
3. **Production Reminders:**
   - Ensure domain is listed in `embed_location` in branchly Application Settings.
   - Whitelist `*.branchly.io` in website Content Security Policy (CSP).
   - Brand convention: Always write the platform name lowercase `"branchly"`.
