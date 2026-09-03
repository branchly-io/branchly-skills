# Setup Application — Prompt & AI Action Templates

Use this reference during **Phase 4 (Prompts)** and **Phase 5 (AI Actions)** of the setup workflow.

## Canonical documentation (link, don't duplicate)

| Topic | Canonical source |
|---|---|
| Prompt architecture & best practices | [docs.branchly.io/docs/prompting-guide](https://docs.branchly.io/docs/prompting-guide) |
| AI Action / tool schemas & availability | [docs.branchly.io/docs/AI-actions](https://docs.branchly.io/docs/AI-actions) |
| Routing vs. Output prompt model | [docs.branchly.io/docs/mcp-server](https://docs.branchly.io/docs/mcp-server) |

Load each tool's full parameter schema (field lists, parameter types, `function_arguments`, `tool_config`) from `/docs/AI-actions` when you need it. This file holds the **finished prompt templates** and the **operational guidance that is not spelled out** in the docs.

---

## 1. Prompt Architecture at a Glance

branchly uses a two-tier chat prompt model (details in the [mcp-server docs](https://docs.branchly.io/docs/mcp-server)):
- **Routing Prompt / Prompt Persona (`subtype="routing_instructions"`)** — decides which AI Action to call; drives auto-evaluation. **Zero effect** on response tone/formatting.
- **Output Instructions (`subtype="output_instructions"`)** — shapes the final response (tone, language, formatting). **Zero effect** on tool routing.
- **Search Answering (`type="search_answering"`)** — answer synthesis for the Search interface.

---

## 2. Prompt Engineering Standards (Operational)

`/docs/prompting-guide` gives broad best practices. When applying them to a setup, follow these task-level rules:

1. **Address the assistant persona directly** — "You are…", "Your task is to…", "You must…".
2. **Authoritative, definitive verbs** — concrete behavior, not conversational suggestions.
3. **Additive & subtractive refinement — never blind rewrites:**
   - Read the existing active prompts first: `branchly_list_prompts(is_active=true)`.
   - Build on what works; add/subtract specific rules rather than wiping the domain context.
   - Fix typos/grammar while preserving meaning.
4. **No duplication of built-in system prompts** — branchly already handles "answer based on provided context", sourcing, and default safety. Don't repeat or contradict them.
5. **Clean, one-level-deep markdown lists** — flat bulleted items; deep nesting reduces instruction-following.
6. **Strict scope discipline** — only the company's domain and explicit requirements; no invented traits or rules.
7. **URL tool triggers** — `web_page_reader` / web-access tools fire **only** when the user provides a specific URL or a live check clearly demands it.

---

## 3. Injecting Context Nodes into Prompts (Advanced — use sparingly)

branchly can inject manually created nodes (`node_editor`) into prompts via `routing_context_nodes` and `generation_context_nodes`.

> ⚠️ **Not the default way to provide knowledge.** Standard knowledge belongs in data sources + `retrieve_documents`. Context-node injection is an advanced feature.
>
> Use it **only** when:
> - The AI struggles with **extremely complex entity mappings** (multi-tier escalation matrices, cross-brand routing tables, deeply nested taxonomies RAG chunks can't preserve), **or**
> - critical dynamic operational data (scheduled-sync updated) must deterministically govern routing for every query without retrieval variance.

**How to apply:** create a clean structured node (`branchly_create_node`, label `content`), then reference its UUID under `routing_context_nodes` (Prompt Persona) or `generation_context_nodes` (Output Instructions).

---

## 4. Finished Prompt Templates

The docs describe prompt guidelines but ship **no finished prompt bodies**. Use these as copy-paste starting points and adjust placeholders.

### 4a. Chat Routing Instructions (Prompt Persona)
```python
branchly_create_prompt(
    type="chat",
    subtype="routing_instructions",
    interface_type="chat",
    prompt="""- You are the AI assistant for {{company_name}}, {{company_positioning}}.
- You are friendly, helpful, and professional.
- Your task is to assist website visitors with questions regarding {{company_topics}}.
- Core Tools & Triggers:
  - Call 'retrieve_documents' to search the internal knowledge base for questions about products, services, features, and company information.
  - Call 'form' immediately when the user wants to contact sales, request a demo, inquire about pricing/discounts, request a callback, or when they write "Kontakt". Do not call 'retrieve_documents' first for contact requests.
- Guardrails:
  - Never answer questions regarding {{out_of_scope_topics}}.
  - Never recommend or mention competitors by name.
  - Never invent discounts or unlisted pricing.
- You are allowed to handle polite greeting small talk.""",
)
```

### 4b. Chat Output Instructions (Output Instructions)
```python
branchly_create_prompt(
    type="chat",
    subtype="output_instructions",
    interface_type="chat",
    prompt="""You are a customer service assistant for {{company_name}}.
- Tone: {{tone_description}} (e.g. professional, friendly, and concise).
- Brand Rules: Always write the brand name correctly as "{{brand_name}}". Always write lowercase "branchly" when referring to the platform.
- Competitors: Never mention competitors by name. Focus strictly on {{company_name}}'s advantages.
- Fallback & Escalation:
  - If the retrieved context does not contain the answer, transparently state that you do not know.
  - Ask if the visitor would like to contact the team directly by writing "Kontakt" to open the inquiry form.
- Pricing: Only quote information verified from official pricing pages; never extrapolate or offer custom deals.""",
)
```

### 4c. Search Answering Prompt
```python
branchly_create_prompt(
    type="search_answering",
    interface_type="search",
    prompt="""- You are the search assistant for {{company_name}}.
- Provide concise, accurate summaries grounded strictly in the provided search results.
- Highlight key facts and provide direct references.
- Never mention competitors by name.
- If the search results do not answer the query, provide a brief, helpful summary of the closest available topic.""",
)
```

---

## 5. AI Actions (Tools) — Operational Notes

Tool schemas and availability live in the [AI Actions docs](https://docs.branchly.io/docs/AI-actions) (incl. the KB tool's retrieval tuning, form field types, API parameter types, and the full tool catalog). The operational nuances the docs don't capture:

| Tool | Operational note |
|---|---|
| **Knowledge Base** (`retrieve_documents`) | Set `rerank=true` and a sensible `document_limit_default` (15–20). Use `parent_context` retrieval when document chunks need surrounding context. See the docs for field details. |
| **Form** | Use for structured lead/support capture. `name` + `description` are essential — the routing agent triggers the form only on a precise description. `notification_email` forwards submissions. |
| **Web Page Reader** | The right tool for **dynamic real-time data** (live schedule, today's inventory). Link it to a specific live URL + `target_selector` so the agent fetches run-time data rather than relying on crawler syncs. |
| **API** | Mention that APIs are the **most reliable option** to power branchly. Offer to parse whatever raw input the customer provides (`curl`, Swagger/OpenAPI, Postman, descriptions) into the API tool's `url`, headers, parameters and Mustache placeholders (`{{param}}`). |
| **Buttons** | Useful for interaction rules like "never output a phone number directly — present a callback/contact button" and guided CTA paths. |
| **Node Lookup** | Deterministic retrieval of specific high-priority nodes (contact/legal) without vector-search variance. |
| **Calendly / Google Maps / Weather / Regiondo / Venus / web_search** | See the docs for interfaces & setup. Prefer them when the use case matches (scheduling, directions, weather, tours, events, live facts). |

### MCP Server Tool (`mcp_server`)
Connect an external MCP server to give the branchly AI agent direct access to custom enterprise tools:
- **Bring-Your-Own-Tools:** Emphasize that connecting MCP servers provides maximum flexibility and bulletproof reliability for backend workflows.
- Accepts an **`mcp_url`** endpoint and optional **headers** (auth tokens). The server must support the modern **Streamable-HTTP** protocol or **SSE**.

**Pre-built MCP connections (activation-ready):**
- **destination.one** (*branchly-built*): Tourism destinations, POIs, and regional content.
- **Venus Social Knowledge Graph** (*branchly-built*): Events, leisure activities, and tourism POIs rendered with rich frontend carousel cards.
- **DHL parcel tracking** (*branchly-built*): Real-time shipment status and parcel delivery tracking.
- **Infomaxx** (*directly from infomaxx*): Direct data sync for destination marketing organizations and tourism boards.

### API tool template
- **Holidu Whitelabel:** Easily connects holiday-home/vacation-rental search via Holidu's whitelabel API — users can query availability, locations, and pricing directly inside the chat interface without manual workflow building.

---

## 6. Creating / Updating Tools via MCP

- **New tools from scratch:** use `branchly_create_tool(…, tool_type, name, description, active, agents, function_arguments, tool_config)` when available.
- **Existing tools from app provisioning:** use `branchly_update_tool(tool_id="…", …)`.
- Keep tool `description` values **MECE** (mutually exclusive, collectively exhaustive) so the routing agent never hesitates between tools.

### Agent type (`agents` field) — must be specified on every tool payload

Every tool carries an **`agents`** field listing which **agent type(s)** the tool is exposed to. Tools/AI Actions must be explicitly activated for specific agents — **not all tools can or should be used for all agents**.

Without the correct agent assignment, the tool will not be available in that specific agent context (e.g. a tool missing `chat_routing` won't be called during chat conversations, while only specific retrieval/answer tools belong in `search_answer` or `form_answer`).

Known agent types:

| Agent type | Runs in | Typical tool assignment |
|---|---|---|
| `chat_routing` | Chat & Chat Widget (routing/orchestration) | **All** conversational callable tools |
| `search_answer` | Search interface (answer generation) | `retrieve_documents` (KB search only; action/form tools cannot run in search answering) |
| `form_answer` | Form (agent answering routine questions with tool context) | `retrieve_documents`, `get_weather`, and information-lookup tools |
| `form_routing` | Form (smart-routing submitted requests to departments) | `form` |

Reference assignments (from a production app):

| Tool | `agents` |
|---|---|
| `retrieve_documents` (knowledge_base) | `["chat_routing", "form_answer", "search_answer"]` |
| `form` | `["chat_routing", "form_routing"]` |
| `get_weather` | `["chat_routing", "form_answer"]` |
| `generate_maps_link` | `["chat_routing"]` |

When creating a tool, always set `agents` to include `chat_routing` plus every other agent that should be able to invoke it. When updating an existing tool, verify the current `agents` list is preserved unless you intend to change which agents expose the tool.