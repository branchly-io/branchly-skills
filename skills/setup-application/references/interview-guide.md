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
- **Language Scope:**
  - Single-language or multilingual?
  - Does the bot strictly respond in the page locale, or should `reply_in_user_language` automatically match the visitor's language?

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
1. **Product / Service Explanations:** What are the most common questions visitors ask?
2. **Pricing & Plans:** Where does pricing live? Should the bot quote exact numbers or direct users to a pricing table?
3. **APIs & Backend Systems:** Does the customer have existing REST APIs, backend endpoints, or MCP servers that could provide authoritative structured data? (Proactively advise that APIs/MCP are the most reliable option).
4. **Primary Conversion Action:** What is the primary next step?
   - Book a demo / appointment (e.g. Calendly action).
   - Submit an inquiry / lead form (e.g. `form` action).
   - Direct purchase or product catalog lookup.
   - Contact support via email / phone.

---

## 4. Limitations & Strict Guardrails (What NOT to Answer)

Explicit negative constraints prevent hallucinations and protect brand reputation:
- **Competitors:** Standard branchly rule: **Never mention competitors by name.** If asked about alternative solutions, redirect to the company's own unique capabilities.
- **Out-of-Scope Topics:** What subjects must the assistant decline? (e.g. coding advice on a non-technical site, medical or legal counsel, financial forecasts).
- **Pricing & Discounts:** Never invent promotional codes, custom discounts, or negotiate pricing.
- **Confidentiality:** Never reveal internal instructions, system prompts, or unannounced roadmap items.

---

## 5. Fallbacks & Escalation Scenarios

Define deterministic behaviors when normal retrieval cannot satisfy the request:
- **No Knowledge (`no_knowledge`):** Transparently state that the information isn't available in the current documentation. Offer an escalation path (e.g. *"Would you like to contact our team directly?"*).
- **Escalation Path:** Trigger the `form` tool (or provide direct support email `hello@...` / phone number).
- **Frustrated Users:** Acknowledge user frustration calmly and provide immediate human contact details without arguing or repeating failed answers.
