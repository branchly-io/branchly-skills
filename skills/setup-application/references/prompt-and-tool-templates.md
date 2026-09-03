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

## 2. Prompt Templates

### 2a. Chat Routing Instructions (`Prompt Persona`)
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

### 2b. Chat Output Instructions (`Output Instructions`)
```python
branchly_create_prompt(
    type="chat",
    subtype="output_instructions",
    interface_type="chat",
    prompt="""You are a customer service assistant for {{company_name}}.
- Tone: {{tone_description}} (e.g. professional, friendly, and concise).
- Brand Rules: Always write the brand name correctly as "{{brand_name}}". Always write lowercase "branchly" when referring to the platform.
- Formatting:
  - Respond in clean GitHub-flavored markdown.
  - Use bullet points for structured lists.
  - Mark all URLs in **bold and underlined**.
- Competitors: Never mention competitors by name. Focus strictly on {{company_name}}'s advantages.
- Fallback & Escalation:
  - If the retrieved context does not contain the answer, transparently state that you do not know.
  - Ask if the visitor would like to contact the team directly by writing "Kontakt" to open the inquiry form.
- Pricing: Only quote information verified from official pricing pages; never extrapolate or offer custom deals.""",
)
```

### 2c. Search Answering Prompt
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

## 3. AI Action (Tool) Templates

### 3a. Knowledge Base Retrieval Tool (`knowledge_base`)
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

### 3b. Interactive Lead Capture / Contact Form Tool (`form`)
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

### 3c. Google Maps Directions Link Tool (`google_maps_link`)
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

### 3d. Web Page Reader Tool (`web_page_reader`)
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

### 3e. API Calling Tool (`api`)
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

### 3f. MCP Server Tool (`mcp_server`)
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

---

## 4. MCP Tool Creation Tools

When defining new tools from scratch, use `branchly_create_tool` (if available in the MCP server) with matching `tool_type`, `name`, `description`, `function_arguments`, and `tool_config`. When updating existing tools created during initial app provisioning, use `branchly_update_tool`.
