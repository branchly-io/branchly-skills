# Setup Application — Prompt & AI Action Templates

Use these templates during **Phase 4 (Prompts)** and **Phase 5 (AI Actions)** of the setup workflow.

Documentation references:
- Prompting Guide: [docs.branchly.io/docs/prompting-guide](https://docs.branchly.io/docs/prompting-guide)
- AI Actions: [docs.branchly.io/docs/AI-actions](https://docs.branchly.io/docs/AI-actions)

---

## 1. Prompt Architecture: Routing vs. Output

branchly uses a two-tier prompt architecture for chat:
- **Routing Prompt / Prompt Persona (`subtype="routing_instructions"`):** Decides which AI Action to call. Has **zero effect** on final output tone or response formatting. Also drives automatic session evaluation.
- **Output Instructions (`subtype="output_instructions"`):** Shapes the final response (formatting, tone, language, URL styling). Has **zero effect** on tool routing.
- **Search Answering (`type="search_answering"`):** Direct answer synthesis for the Search interface.

---

## 2. Prompt Engineering Standards & Guidelines

When authoring, revising, or tuning prompts for branchly, adhere strictly to these proven engineering guidelines:

1. **Address the Assistant Persona Directly:** Use second person imperative or direct affirmative framing ("You are...", "Your task is to...", "You must...").
2. **Authoritative, Definitive Language:** Use directive verbs defining concrete behavior rather than conversational suggestions.
3. **Additive & Subtractive Refinement (Never Blind Rewrites):**
   - Read existing active prompts first via `branchly_list_prompts(is_active=true)`.
   - Build upon existing proven instructions. Add or subtract specific rules to improve behavior without wiping out established domain rules.
   - Fix grammatical errors and typos in existing custom prompts while strictly preserving the underlying intent.
4. **No System Prompt Duplication:**
   - branchly provides built-in system-level prompts (e.g. "answer based on provided context", "cite sources in events", default safety).
   - **NEVER** duplicate or repeat built-in system prompt mechanics into the user-facing Prompt Persona or Output Instructions.
   - Do not add rules that contradict system-level instructions.
5. **Format as a Clean, One-Level-Deep Markdown List:**
   - Present instructions as flat bulleted items (`- ...`).
   - Deep nested hierarchies confuse LLM instruction-following; keep statements simple, clear, and focused.
6. **Strict Scope Discipline:**
   - Focus exclusively on the company's domain, target topics, and explicit user requirements.
   - Do not invent random personality traits or rules that the user did not ask for.
7. **Special Tool Triggers:**
   - For tools like `access_website_content` or `web_page_reader`, instruct the AI to call them **only when a specific URL is provided by the user** or clearly required for a designated live check.

---

## 3. Injecting Context Nodes into Prompts (`routing_context_nodes` / `generation_context_nodes`)

branchly supports injecting manually created knowledge nodes (`node_editor`) directly into prompts via `routing_context_nodes` and `generation_context_nodes`.

> ⚠️ **Use Sparingly (Not Default Behavior):**  
> Context node injection is an **advanced feature** and should **NOT** be used as the default way to provide knowledge. Standard knowledge belongs in regular data sources and knowledge base retrieval (`retrieve_documents`).

### When to Use:
- Use **only** when the AI is struggling with **extremely complex mappings between entities** (e.g. multi-tiered department escalation matrices, cross-brand routing tables, or deeply nested taxonomies that standard RAG chunks struggle to preserve).
- Or when critical dynamic operational data (regularly updated by a scheduled sync) must govern the routing decisions of every single query without relying on retrieval variance.

### How to Apply:
1. Create or edit a clean structured node using `branchly_create_node` with label `content`.
2. Reference the node UUID in the application configuration under `routing_context_nodes` (for Prompt Persona) or `generation_context_nodes` (for Output Instructions).

---

## 4. Prompt Templates

### 4a. Chat Routing Instructions (`Prompt Persona`)
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

### 4b. Chat Output Instructions (`Output Instructions`)
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

## 5. AI Action (Tool) Templates

### 5a. Knowledge Base Retrieval Tool (`knowledge_base`)
Tune the standard RAG retriever:
```python
branchly_update_tool(
    tool_id="<kb-tool-uuid>",
    name="retrieve_documents",
    description="Default tool to call. Search internal knowledge base to answer questions about {{company_name}}, products, pricing, and services. Use a reformulated question based on user input.",
    function_arguments={
        "object": "knowledge_base_tool_arguments",
        "document_limit_default": 20,
        "document_limit_rerank": 30,
        "rerank": True,
        "retrieval_method": "default",  # Or "parent_context" if chunk context is critical
        "formatter": "chunks_with_source",
    },
)
```

### 5b. Interactive Lead Capture / Contact Form Tool (`form`)
Deploy dynamic lead capture or support escalation:
```python
branchly_update_tool(
    tool_id="<form-tool-uuid>",
    active=True,
    name="form",
    description="Use this tool when the user wants to contact {{company_name}}, request a demo, get a quote, ask for a callback, or writes 'Kontakt'.",
    tool_config={
        "properties": [
            {
                "name": "name",
                "field_type": "string",
                "format": "text",
                "description": "Full name of the user",
                "required": True,
            },
            {
                "name": "email",
                "field_type": "string",
                "format": "email",
                "description": "Valid email address of the user",
                "required": True,
            },
            {
                "name": "message",
                "field_type": "text_area",
                "format": "text",
                "description": "Summary of the inquiry or request",
                "required": True,
            },
        ]
    },
    function_arguments={
        "object": "form_tool_arguments",
        "form_title": {
            "en": "Contact {{company_name}}",
            "de": "Kontakt zu {{company_name}}",
        },
        "submit_button_text": {"en": "Send Message", "de": "Absenden"},
        "submit_message": {
            "en": "Thank you for reaching out. We will get back to you shortly.",
            "de": "Vielen Dank. Wir melden uns zeitnah bei Ihnen.",
        },
        "notification_email": "{{notification_email}}",
    },
)
```

### 5c. Google Maps Directions Link Tool (`google_maps_link`)
For local businesses or offices:
```python
branchly_update_tool(
    tool_id="<maps-tool-uuid>",
    active=True,
    name="generate_maps_link",
    description="Generate a Google Maps directions link for the user to reach {{company_name}} office or location.",
    function_arguments={
        "object": "google_maps_link_tool_arguments",
        "default_travelmode": "driving",
    },
)
```

### 5d. Web Page Reader Tool (`web_page_reader`)
Use for dynamic real-time data access (e.g. today's live events, current inventory, up-to-the-minute status) where relying on scheduled crawler syncs is inadequate:
```python
# Create (via branchly_create_tool) or Update:
branchly_update_tool(
    tool_id="<web-page-reader-uuid>",
    active=True,
    name="read_live_status",
    description="Fetch current, real-time status and live schedule from {{company_name}}'s live page. Use only when the visitor explicitly asks for real-time status, today's schedule, or current availability.",
    function_arguments={
        "object": "web_page_reader_tool_arguments",
        "url": "https://<domain>/live-status",
        "target_selector": "main .live-schedule",  # Scopes extraction to the specific dynamic element
    },
)
```

### 5e. API Calling Tool (`api`)
For directly querying backend APIs during chat conversations (e.g. order tracking, availability checks, dynamic calculations):
- **Why API & MCP Tools:** Mention to the customer that using MCP Servers and API actions is the **most reliable and robust option** to power branchly, as it guarantees live, structured data execution without scraping delays or HTML fragility.
- **Parsing Raw Customer Input:**
  - Ask the customer to provide their endpoint details.
  - Parse whatever raw input the customer provides: `curl` snippets, API docs, Swagger snippets, or informal descriptions.
  - Automatically extract the HTTP method, endpoint URL, query/path parameters, and map them to Mustache placeholders (e.g. `{{order_id}}`).
```python
branchly_create_tool(
    name="track_order",
    description="Check real-time order status when the customer provides their order ID or asks for parcel tracking.",
    active=True,
    tool_type="api",
    tool_config={
        "object": "api_tool_config",
        "parameters": [
            {
                "name": "order_id",
                "description": "The customer's order ID or tracking code",
                "type": "text",
                "required": True,
            }
        ],
    },
    function_arguments={
        "object": "api_tool_arguments",
        "method": "GET",
        "url": "https://api.example.com/v1/orders/{{order_id}}",
        "headers": {"Authorization": "Bearer YOUR_SECRET_OR_KEY"},
        "response_path": "order.status",
    },
)
```

### 5f. MCP Server Tool (`mcp_server`)
Connect any external MCP server to give the branchly AI agent direct access to custom enterprise tools:
- **Bring-Your-Own-Tools:** Emphasize to the customer that connecting MCP servers provides maximum flexibility and bulletproof reliability for backend workflows.
- Accepts an `mcp_url` endpoint and optional custom headers (auth tokens):
```python
branchly_create_tool(
    name="ecommerce_mcp",
    description="Interface with internal e-commerce systems for product lookup, inventory checks, and return tracking via MCP.",
    active=True,
    tool_type="mcp_server",
    function_arguments={
        "object": "mcp_server_tool_arguments",
        "mcp_url": "https://mcp.internal.example.com/sse",
        "headers": {"Authorization": "Bearer MCP_API_KEY"},
    },
)
```

### 5g. Additional Built-In AI Actions (Catalog Overview)

branchly provides a rich ecosystem of specialized AI Actions. Refer to the official [AI Actions Documentation](https://docs.branchly.io/docs/AI-actions) for in-depth parameter schemas and setup details:

| Tool Type | Name | Purpose | Key Parameters / Use Case |
|---|---|---|---|
| `buttons` | `buttons` | Send up to 3 interactive CTA buttons (link buttons or action buttons) directly in chat responses. | `buttons`: list of button objects (`type="link_button"`, `text`, `url`). Great for "Book Demo", "Call Support", or guided paths. |
| `calendly` | `calendly` | Allow visitors to schedule meetings and calls directly inside the chat interface. | Requires connected Calendly integration under Settings > Integrations. |
| `web_search` | `web_search` | Real-time web search for facts outside internal documentation. | `limit`: maximum search results (up to 5). |
| `node_lookup` | `node_lookup` | Directly retrieve specific high-priority knowledge base nodes without full vector search variance. | `node_ids`: exact node UUIDs to fetch (ideal for deterministic contact/legal lookups). |
| `weather` | `get_weather` | Real-time weather and temperature for specific locations. | Location inferred from user query or fixed to company premises. |
| `google_maps_embed` | `google_maps_embed` | Embed interactive Google Maps iframe directly into the chat window. | Requires `GOOGLE_MAPS_API_KEY`; supports travel modes (`driving`, `transit`, etc.). |
| `regiondo` | `regiondo` | Direct booking of guided tours, tickets, and activities for leisure/tourism websites. | Requires Regiondo `public_key` and `secret_key`. |
| `venus_knowledge_graph` | `venus_knowledge_graph` | Access regional tourism points of interest, destinations, and public events. | `projects`, `channels`, `domain`. Renders as interactive carousel frontend events. |
| `bayern_cloud` | `bayern_cloud` | Integrates BayernCloud tourism and regional knowledge data. | Tourism portal integrations in southern Germany/Bavaria. |
| `send_email` | `send_email` | Direct email forwarding for urgent inquiries (note: prefer `form` for structured input). | `sender_email`: notification recipient address. |

---

## 6. MCP Tool Creation Tools

When defining new tools from scratch, use `branchly_create_tool` (if available in the MCP server) with matching `tool_type`, `name`, `description`, `function_arguments`, and `tool_config`. When updating existing tools created during initial app provisioning, use `branchly_update_tool`.
