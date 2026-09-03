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
