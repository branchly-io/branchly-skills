---
name: setup-application
description: |
  Guide and execute end-to-end setup and configuration for a branchly application.
  Conducts website research, interviews the user on use case and guardrails,
  and configures data sources, prompts, AI actions, and knowledge base nodes via MCP.

  Triggers when user mentions:
  - "set up my branchly application" / "setup branchly app"
  - "configure a new branchly chatbot" / "onboard my website to branchly"
  - "create initial prompts and tools for branchly"
  - "help me configure branchly for my domain"
  - "initial branchly configuration"
license: MIT
---

## Setup Application Workflow for branchly Applications

This skill guides an AI agent through setting up and configuring a [branchly](https://branchly.io) application. It is harness- and agent-agnostic (designed for OpenCode, Claude Code, Cursor, Codex, or any agent environment supporting web tools and MCP).

Official documentation reference: [docs.branchly.io/docs](https://docs.branchly.io/docs)

---

## Mental Model — The Setup Lifecycle

Setting up a branchly application successfully connects the website's real-world business objectives to branchly's architecture:

```
Phase 1: Discovery    → Analyze domain & search external web context
Phase 2: Alignment    → Interview user on audience, interface, flows & guardrails
Phase 3: Data Ingest  → Audit & configure crawler data sources with clean HTML selectors
Phase 4: Prompts      → Establish two-tier prompt architecture (routing persona vs. output instructions)
Phase 5: AI Actions   → Configure callable tools (knowledge base, forms, external links)
Phase 6: Seed KB      → Create essential baseline nodes (contact, company overview, fallbacks)
Phase 7: Delivery     → Provide verified embed snippets and testing checklist
```

---

## Phase 1 — Domain Research & Web Discovery

Before asking the user broad questions, gather facts about the target website to ground the interview.

### 1a. Inspect Connected Application
Read the current application settings to identify configured domains, locales, and search modes:
```bash
branchly_get_application()
```
Note the `embed_location`, `valid_locales`, `search_mode`, and `environment`.

### 1b. Fetch Domain & Web Context
Using available web fetching or browser tools:
1. Access the target domain root (`https://<domain>`) and key subpages (`/about`, `/pricing`, `/contact`, `/faq`).
2. Run a web search: `"what does <domain or company name> do"` and inspect the primary offerings, target audience, and positioning.
3. Identify:
   - Primary industry/domain (e.g. B2B SaaS, E-Commerce, Local Services, Tourism, Healthcare).
   - Core value proposition and customer profile.
   - Available conversion points (e.g. demo request, checkout, phone call, contact form).

---

## Phase 2 — Structured User Alignment (Interview)

Engage the user in a concise, structured interview. Present your findings from Phase 1 as initial assumptions and ask for confirmation/adjustments across the following 5 dimensions:

### 1. Audience & Tone of Voice
- **Target Audience:** Who will primarily interact with the interface? (e.g. prospective buyers, existing customers needing support, developers, job seekers).
- **Tone & Persona:** How should the AI represent the brand? (e.g. professional and concise, friendly and approachable, formal B2B, support for simplified language like "Leichte Sprache").
- **Language Policy:** Is the site single-language or multilingual? Should the bot strictly adhere to the page locale or reply in whatever language the visitor uses?

### 2. Interface Selection
branchly offers distinct user interface types. Confirm which surface the user plans to deploy:
- **Chat Widget (Floating Bubble):** Omnipresent assistant for general website navigation, conversational Q&A, and interactive lead forms.
- **Chat (Inline Embed):** Embedded directly on a dedicated help center, support, or advisory page.
- **Search (Search Bar / Modal):** Hybrid semantic search bar with instant AI-generated answers, keyword highlighting, and direct navigation links.
- **Smart AI Form:** Dynamic conversational form for qualified inbound leads or support intake.
- **Headless API:** Custom integration into third-party channels (e.g. WhatsApp, Slack, custom mobile app).

> Note: Prompts in branchly are scoped by `interface_type` (`chat`, `search`, `api`, `form`). Ensure prompts created in Phase 4 match the selected interface.

### 3. Core Use Cases & Question Flows
- What are the top 3–5 topics or recurring questions the assistant must answer?
- What core conversion actions should the AI drive? (e.g. booking an appointment, filling out an inquiry form, navigating to a pricing table, contacting support).

### 4. Limitations & Guardrails (What NOT to Answer)
- **Competitors:** Policy on mentioning competing products or providers (standard branchly best practice: never recommend or mention competitors by name; redirect to company strengths).
- **Sensitive Topics:** Legal, financial, health advice, or unreleased feature roadmaps.
- **Pricing & Discounts:** Strictly adhere to published pricing; never invent custom discounts (route to sales if requested).
- **Confidentiality:** Instruct the model not to disclose internal system prompts or instructions.

### 5. Fallback & Escalation Scenarios
- How should the AI behave when the knowledge base has no answer (`no_knowledge`)?
- What is the escalation path? (e.g. trigger an inline `form` tool, provide a support email `hello@domain.com`, suggest phone support).
- How should the AI handle frustrated or complaining visitors?

---

## Phase 3 — Data Source Ingestion & Crawler Configuration

Clean data ingestion is essential for high-quality retrieval. Noisy crawled HTML (navigation headers, footers, cookie banners) dilutes semantic signal.

### 3a. Audit Existing Data Sources
```bash
branchly_list_data_sources()
```
Check if a `website_crawler` or other source is already present.

### 3b. Configure Website Crawler
When updating crawler settings, **always send the complete settings object** (the branchly API requires the full object for updates):

```bash
# 1. Read existing data source
data_source = branchly_list_data_sources()

# 2. Update with cleaned HTML selectors, appropriate globs, and schedule
branchly_update_data_source(
  data_source_id="<data-source-uuid>",
  schedule="0 4 * * 2",  # Weekly sync (or as appropriate)
  settings={
    "type": "website_crawler",
    "urls": { "start_urls": ["https://<domain>/"] },
    "crawler_type": "playwright:adaptive",  # Handles dynamic JS sites
    "actor": "apify/website-content-crawler",
    "max_pages_per_crawl": 200,
    "max_crawl_depth": 50,
    "ignore_errors": true,
    "ignore_canonical_url": false,
    "exclude_url_globs": ["*/404", "*/404/*", "*/cart*", "*/checkout*", "*/login*"],
    "remove_html_elements": "footer, div.footer, #footer, header, div.pageheader, #pageheader, script, style, noscript, svg, nav, .nav, #nav, .navigation, [role=\"alert\"], [role=\"banner\"], [role=\"dialog\"], [role=\"alertdialog\"], [aria-modal=\"true\"], #branchly-chat-widget-container, #branchly-embed-container, #branchly-chat-embed-container, #branchly-search-interface-container, .cookie-banner, #cookie-banner",
    "unavailable_source_policy": "delete_unavailable"
  }
)
```

Inform the user: *"Crawler settings updated with noise-removal filters. Trigger a data source re-sync in the branchly dashboard if you want changes reflected immediately."*

---

## Phase 4 — Configure Two-Tier Prompt Architecture

branchly separates routing logic from user-facing output generation. Both prompts must align with the use cases and guardrails established in Phase 2.

Reference guide: [docs.branchly.io/docs/prompting-guide](https://docs.branchly.io/docs/prompting-guide)

### Prompt Roles Breakdown:
| Prompt Type | Subtype | Dashboard Name | Purpose |
|---|---|---|---|
| `chat` | `routing_instructions` | **Prompt Persona** | Decides which AI Actions to call, reformulates questions, and sets evaluation criteria. Has zero effect on output tone. |
| `chat` | `output_instructions` | **Output Instructions** | Controls final response style, markdown formatting, language rules, tone, and fallback phrasing. Has zero effect on routing. |
| `search_answering` | `null` | **Search Answering** | Direct answer synthesis for the Search interface. |

### 4a. Create Routing Prompt (Prompt Persona)
The routing instructions must explicitly tell the agent when to call `retrieve_documents`, `form`, or other tools:

```bash
branchly_create_prompt(
  type="chat",
  subtype="routing_instructions",
  interface_type="chat",
  prompt="""- You are the AI assistant for <Company Name>, <one-line company positioning>.
- Your task is to assist website visitors with questions regarding <topics>.
- Core tools:
  - Call 'retrieve_documents' to search the knowledge base for technical, product, and company inquiries.
  - Call 'form' when the user wants to contact sales, request a quote, schedule an appointment, or when they write "Kontakt".
- Guardrails:
  - Never answer queries regarding <out_of_scope_topics>.
  - Never recommend or mention competitors by name.
  - Never invent discounts or unlisted pricing.
- You are allowed to handle polite greeting small talk."""
)
```

### 4b. Create Output Instructions
The output prompt shapes user-facing formatting and brand communication:

```bash
branchly_create_prompt(
  type="chat",
  subtype="output_instructions",
  interface_type="chat",
  prompt="""You are the customer service assistant for <Company Name>.
- Tone: Professional, helpful, and concise.
- Structure: Answer in clear markdown. Use bullet points for lists.
- Brand rules: Always write the brand name correctly as "<BrandName>".
- Competitors: Never mention competitors by name.
- Formatting: Mark all URLs in **bold and underlined**.
- Fallbacks: If you do not have sufficient information in the context to answer, transparently state that you do not know and invite the user to contact the team by typing "Kontakt" to open the inquiry form.
- Pricing: Only quote information verified from official pricing pages; do not extrapolate."""
)
```

### 4c. Create Search Answering Prompt (If Search Interface Selected)
```bash
branchly_create_prompt(
  type="search_answering",
  interface_type="search",
  prompt="""- You are the search assistant for <Company Name>.
- Provide concise, accurate summaries grounded strictly in the provided search results.
- Never mention competitors by name.
- Highlight key facts and provide direct references."""
)
```

---

## Phase 5 — Configure AI Actions (Tools)

Audit and configure the active AI Actions to match user intent.

Reference: [docs.branchly.io/docs/AI-actions](https://docs.branchly.io/docs/AI-actions)

### 5a. Knowledge Base Retrieval Tool
Check existing tools:
```bash
branchly_list_tools(active=true)
```
Ensure the default `retrieve_documents` tool is tuned:
- `retrieval_method`: `"default"` or `"parent_context"` (use parent_context if documentation chunks need surrounding context).
- `rerank`: `true` (enables cross-encoder reranking for higher precision).
- `document_limit_default`: `15`–`20`.

```bash
branchly_update_tool(
  tool_id="<kb-tool-uuid>",
  description="Default tool to call. Search internal knowledge base to answer questions about <Company Name>, products, pricing, and services.",
  function_arguments={
    "object": "knowledge_base_tool_arguments",
    "document_limit_default": 20,
    "rerank": true,
    "retrieval_method": "default"
  }
)
```

### 5b. Configure Lead Capture / Contact Form Tool
If lead generation or contact escalation is required, configure the `form` tool:

```bash
branchly_update_tool(
  tool_id="<form-tool-uuid>",
  active=true,
  description="Use this tool when the user wants to contact <Company>, request a demo, get a quote, ask for a callback, or writes 'Kontakt'.",
  tool_config={
    "properties": [
      {
        "name": "name",
        "field_type": "string",
        "format": "text",
        "description": "Full name of the user",
        "required": true
      },
      {
        "name": "email",
        "field_type": "string",
        "format": "email",
        "description": "Valid business email address",
        "required": true
      },
      {
        "name": "message",
        "field_type": "text_area",
        "format": "text",
        "description": "Summary of the user's request or inquiry",
        "required": true
      }
    ]
  },
  function_arguments={
    "object": "form_tool_arguments",
    "form_title": { "en": "Contact Our Team", "de": "Kontaktieren Sie uns" },
    "submit_button_text": { "en": "Send Message", "de": "Absenden" },
    "submit_message": {
      "en": "Thank you for reaching out. Our team will get back to you shortly.",
      "de": "Vielen Dank. Wir melden uns zeitnah bei Ihnen."
    },
    "notification_email": "<user-notification-email>"
  }
)
```

---

## Phase 6 — Seed Baseline Knowledge Base Nodes

Automated web crawling may miss core operational facts or direct contact routing. Add structured manual nodes to guarantee solid baselines.

Reference: [docs.branchly.io/docs/knowledge-base](https://docs.branchly.io/docs/knowledge-base)

### 6a. Company Overview Node
```bash
branchly_create_node(
  title={"en": "<Company Name> Overview", "de": "Überblick <Company Name>"},
  text={
    "en": "<p><strong><Company Name></strong> is <summary of business and key services>.</p>",
    "de": "<p><strong><Company Name></strong> ist <Zusammenfassung des Unternehmens>.</p>"
  },
  label="content",
  source="https://<domain>/about"
)
```

### 6b. Official Contact & Support Escalation Node
```bash
branchly_create_node(
  title={"en": "Contact and Customer Support", "de": "Kontakt und Kundenservice"},
  text={
    "en": "<p>Contact our support team via email at <a href=\"mailto:hello@<domain>\">hello@<domain></a> or submit the contact form.</p>",
    "de": "<p>Sie erreichen unseren Kundenservice per E-Mail unter <a href=\"mailto:hello@<domain>\">hello@<domain></a> oder über das Kontaktformular.</p>"
  },
  label="contact",
  source="https://<domain>/contact",
  score_boost=1.5
)
```

---

## Phase 7 — Verification & Embed Delivery

### 7a. Verification Checklist
Confirm all configurations are saved:
1. `branchly_get_application()`: Verify application settings.
2. `branchly_list_prompts(is_active=true)`: Verify routing and output prompts are active.
3. `branchly_list_tools(active=true)`: Verify tools and descriptions are MECE.
4. `branchly_list_nodes(limit=5)`: Verify manual nodes exist.

### 7b. Deliver Embed Snippets
Provide the user with ready-to-copy HTML snippets for their website based on the chosen interface.

Documentation reference: [docs.branchly.io/docs/how-to-embed](https://docs.branchly.io/docs/how-to-embed)

#### For Floating Chat Widget:
Place before the closing `</body>` tag:
```html
<script async type="module" src="https://chat-widget.branchly.io/assets/index.js"></script>
<div
  id="branchly-chat-widget-container"
  data-token="<APPLICATION_TOKEN>"
  data-custom-styles="false"
  data-open-default="false">
</div>
```

#### For Search Interface:
Place search button container in header or navigation:
```html
<script async type="module" src="https://search.branchly.io/assets/index.js"></script>
<div
  id="branchly-search-interface-container"
  data-token="<APPLICATION_TOKEN>"
  data-view-mode="search-button">
</div>
```

### 7c. Important Domain & CSP Reminder
Remind the user of two vital production settings:
1. **Allowed Domains:** The host domain must be added to `embed_location` in branchly Application Settings, otherwise the embed script fails to initialize.
2. **Content Security Policy (CSP):** Ensure `*.branchly.io` is whitelisted in `script-src`, `connect-src`, and `frame-src`.

---

## Common Pitfalls to Avoid

- **Do NOT blur routing instructions and output instructions.** Routing prompts (Prompt Persona) control tool selection only. Formatting, tone, and markdown rules belong strictly in output instructions.
- **Do NOT send partial crawler settings.** `branchly_update_data_source` requires the complete settings JSON object. Always read the current data source first, modify the desired attributes, and send the full object back.
- **Do NOT guess tool triggers.** Keep AI Action descriptions strictly MECE (mutually exclusive, collectively exhaustive) so the routing agent never hesitates between tools.
- **Avoid orphan domains.** Remind the user that embed widgets will refuse to run on domains not registered under `embed_location` in the branchly dashboard.
- **Preserve brand lowercase convention.** branchly branding is always written as lowercase `"branchly"` — never `"Branchly"`.
