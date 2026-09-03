# Setup Application — Discovery & Interview Guide

Use this guide during **Phase 2 (Structured User Alignment)** of the setup workflow.

Before asking these questions, complete **Phase 1** by reading `branchly_get_application()`, visiting the target website, and running web searches (`"what does <domain> do"`) so you present informed preliminary assumptions rather than asking blind questions.

---

## 1. Domain & Brand Identity

Present your initial understanding of the company and confirm:
- **Core Value Proposition:** What product or service does the company provide, and what makes it unique?
- **Brand Spelling & Capitalization:** Always note branchly-specific rules (e.g. branchly is always written lowercase `"branchly"`) and the customer's exact brand formatting.
- **Tone of Voice:**
  - Formal B2B (concise, professional, consultative).
  - Informal / Friendly B2C (approachable, personal, welcoming).
  - Support for Bavarian/regional greetings or simplified language ("Leichte Sprache") if requested.
- **Language Scope & Adaptation Strategy:**
  - Single-language or multilingual?
  - How should the interface adapt across languages? Explain the two primary dimensions:
    1. **Reply in User Language (`reply_in_user_language`):** Automatically detects the language of a user's typed chat message and replies in kind.
    2. **Use Browser Language (`use_browser_locale`):** Translates all static interface elements (buttons, placeholders, suggested questions) into the visitor's browser language. For visitors outside configured `valid_locales`, switches retrieval to dense multilingual semantic search and responds in their browser language backed by nearest content.

---

## 2. Interface Selection

Confirm which branchly interface will be deployed:

| Interface | Best For | Prompt Type Needed |
|---|---|---|
| **Chat Widget (Floating Bubble)** | Omnipresent site-wide assistant; handles multi-turn Q&A, lead capture, and guided navigation. | `chat` (`routing_instructions` + `output_instructions`) |
| **Chat (Inline Embed)** | Dedicated help center, advisory page, or customer portal embed. | `chat` (`routing_instructions` + `output_instructions`) |
| **Search Interface (Modal / Inline)** | Fast hybrid instant search with AI answer synthesis, keyword highlighting, and source links. | `search_answering` |
| **Smart AI Form** | Conversational form that answers FAQs inline and captures structured inquiries. | `form` AI action + `chat` / `form` prompts |
| **Headless API** | Integration into custom mobile apps, WhatsApp for Business, Slack, or internal tooling. | `chat` / `api` prompts |

---

## 3. Core Use Cases & Primary Flows

Identify the top 3–5 recurring intents the application must handle:
1. **Product / Service Inquiries:** What are the most common questions visitors ask?
2. **Specific Scenarios & Business Interaction Rules:**
   - How should specific situations be handled? (e.g. *"Never output a phone number directly in text — always trigger the contact 'form' tool or present a callback button"*).
   - What happens when a user asks for direct contact, booking an appointment, or a quote?
3. **Primary Conversion Actions:**
   - Schedule meeting / demo (e.g. Calendly action).
   - Submit inquiry / quote request (e.g. `form` action).
   - Direct purchase or product catalog lookup.

---

## 4. Data Sources & Tooling Architecture (Static vs. Dynamic Data)

Establish how company knowledge is ingested and retrieved. Proactively explain the core architectural distinction:
- **Static vs. Dynamic Data Division:**
  - **Static / Semi-Static Knowledge:** Information that changes infrequently (e.g. product manuals, company info, documentation, FAQs). Ingested into the branchly Knowledge Base via scheduled Data Sources.
  - **Dynamic Real-Time Data:** Information that changes continuously or requires live status (e.g. today's live schedule, real-time inventory, order tracking, current ticket status). Handled via AI Actions / Tools (`api`, `mcp_server`, or `web_page_reader`) executed at run-time.
- **Existing Systems & Data Ingestion:**
  - What CMS or platform powers the website? (e.g. WordPress, Webflow, Shopify, custom).
  - Which data sources do they want to connect? (Website crawl, uploaded PDFs/CSVs, HelpSpace docs).
  - Do they have existing REST APIs, OpenAPI/Swagger specs, or MCP servers?
  - *Proactive guidance:* Emphasize that connecting **MCP Servers and APIs** is the **most reliable and robust option** to power branchly, and offer to parse raw `curl` commands, OpenAPI specs, or endpoint descriptions.
  - *Pre-built Integrations:* Mention that branchly offers pre-built MCP connections for **destination.one** (branchly-built), **Venus Social Knowledge Graph** (branchly-built), **DHL parcel tracking** (branchly-built), and **Infomaxx** (directly from infomaxx), plus ready-to-use API templates like **Holidu Whitelabel** for vacation rentals.

---

## 5. Company-Specific Limitations & Guardrails (What NOT to Answer)

Note: General safety, prompt injection resistance, and polite conduct are already handled by branchly's built-in system prompts. **Do not repeat system-level safety rules.**

Focus strictly on **company-specific boundaries**:
- **Competitors:** Policy on competing brands (standard branchly best practice: never mention competitors by name; redirect to company differentiators).
- **Domain Boundaries:** What industry topics should the assistant explicitly refuse to answer? (e.g. legal advice, medical assessments, unreleased product roadmaps).
- **Promotions & Offers:** Explicit instructions not to invent discount codes, custom pricing, or negotiate terms.

---

## 6. Fallback Behavior & Output Prompting for Missing Knowledge

In the live conversation, the agent does not receive an explicit `no_knowledge` classification at runtime (classifications like `no_knowledge` are derived post-hoc in analytics). 

Therefore, fallback behavior must be governed deterministically through the **Output Instructions prompt**:
- **Transparent Admission:** What exact wording should the AI use when retrieved context does not contain the answer? (e.g. *"I don't have that specific information in my current documentation."*).
- **Proactive Escalation Path:** What concrete alternative should the output prompt offer?
  - Instruct the user to type `"Kontakt"` to open the interactive lead/contact `form`.
  - Display dedicated button links to human support or email.
- **Handling Frustrated / Escalating Visitors:** How should the output prompt direct difficult inquiries? (Acknowledge calmly and present the contact form immediately).

