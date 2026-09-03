---
name: optimize-application
description: |
  Systematically debug and optimize a branchly RAG chatbot application.
  Covers session triage, retrieval quality, prompt/tool alignment, and data source health.

  Triggers when user mentions:
  - "optimize my branchly application"
  - "chatbot is not answering correctly" or "bot gives wrong answers"
  - "no_knowledge" or "outside_scope" responses
  - "debug my chatbot" or "chatbot retrieval issue"
  - "improve retrieval" or "fix bot responses"
license: MIT
---

## Optimization Workflow for branchly Applications

You have access to the branchly MCP server. Use it throughout this workflow.

---

## Mental Model — The Three Contracts

Every branchly chatbot failure breaks exactly ONE of these contracts:

```
Content contract    → KB has accurate, clean, complete information
Retrieval contract  → Right content surfaces for right queries
Routing contract    → Bot uses the right tool for the right intent
```

**Identify which contract is broken before touching anything. Each has a different fix.**

---

## Step 1 — Triage: Classify the Failure

Start by understanding which embed surfaces are driving traffic:

```
branchly_get_active_sessions_by_embed(time_filter="last_30_days")
```

This shows a time series broken down by embed type (chat, chat_widget, navigator, search_interface, voice, api). Use it to prioritize which surface to optimize first.

Then pull recent sessions with problematic answer types:

```
branchly_read_sessions(
  answer_types=["no_knowledge", "outside_scope"],
  interactions=["chat"],
  limit=10
)
```

For each flagged session, read the full detail:

```
branchly_read_session_detail(session_id="...")
```

**Decision tree from session data:**

| What you see | Root cause | Fix layer |
|---|---|---|
| No tool called at all | Routing failure | Routing prompt |
| Tool called, no documents returned | Retriever didn't fire | Tool config / data source |
| Documents returned, none relevant | Retrieval ranking failure | score_boost, node content, noise removal |
| Relevant docs returned, wrong answer | Prompt/reasoning failure | Output prompt |
| No relevant docs exist anywhere | Content gap | Add KB node |

> **Never assume content is missing until you've confirmed the retriever had nothing useful to return.**

### 1b. Correct misclassified answer types

During triage you may find sessions where the `answer_type` is wrong — e.g. `no_knowledge` when the bot actually answered, or `outside_scope` for an in-scope question. Use:

```
branchly_update_chat_request_analytics(
  chat_request_id="...",
  answer_type="complete",
  sentiment="positive"
)
```

Fields you can update: `summary`, `tags`, `answer_type`, `sentiment`, `classification_topic_id`, `classification_intent_id`. Only provided fields are changed.

---

## Step 2 — Audit Retrieval Quality

### 2a. Check for no_knowledge misclassification

If the answer_type is `no_knowledge`, verify whether the knowledge actually existed in the context:
- Read the session detail, then use `read_chat_request_documents` / `read_chat_request_tool_calls` to inspect the exact context and tool results the model was grounded on
- If a `search_knowledge_base` tool was called, check what it returned
- If the topic-relevant content **does exist** in the KB but wasn't retrieved → **retrieval issue**, not a content gap

The request-level IDs are visible in the session's full history. Inspect the actual grounding:

```
branchly_read_chat_request_documents(chat_request_id="...")
branchly_read_chat_request_tool_calls(chat_request_id="...")
```

### 2b. Check for content noise in nodes

Sample several nodes from the data source that returned low-quality results:

```
branchly_list_nodes(data_source_ids=["<ds-id>"], limit=10)
branchly_read_node(node_id="...")
```

You can also search the knowledge base by content to find relevant nodes:

```
branchly_list_nodes(query="user's search terms", locale="de", limit=10)
```

Look for: navigation menus, footer links, cookie banners, repeated header text, legal boilerplate embedded in content.

To quantify the noise and derive the selectors to strip, run the bundled helper script (pure Python stdlib, no packages needed) on the raw node HTML:

```
python3 scripts/analyze_node_noise.py <node_dump.json> --phrases "<key body phrase>"
```

It reports per-node clean-vs-raw text ratios, ranks site-wide boilerplate class tokens (the `[class*="..."]` selectors to append to `remove_html_elements`), and verifies your key body phrases survive stripping (over-strip guard). It also accepts raw HTML files, so you can validate selectors on a page before triggering a re-crawl.

> **Prefer stable CSS selectors.** When extending `remove_html_elements`, favor selectors that stay valid across redesigns and deploys: element types (`nav`, `footer`, `aside`), IDs (`#footer`), semantic class/role/aria-attribute selectors (`[role="banner"]`, `[aria-modal="true"]`, `.cookie-banner`). Avoid volatile selectors such as auto-generated hashes, build-output class names, or index/position-based selectors (`div > div:nth-child(3)`) — they break silently on the next deploy and can then under-strip (noise returns) or, worse, over-strip when a hash collides with new content. Treat script-derived `[class*="..."]` suggestions as candidates to verify, and prefer a stable equivalent when one exists.

**If found → fix at the crawler config level:**

> ⚠️ **Settings require the full object.** `website_crawler` requires `urls` and other fields — you cannot send only `remove_html_elements`. Always read first, then send the complete settings with your change merged in.

```
# 1. Read the full current settings first
branchly_list_data_sources()
// → copy the full settings object from the relevant data source

# 2. Update with the COMPLETE settings object, changing only remove_html_elements
branchly_update_data_source(
  data_source_id="...",
  settings={
    "type": "website_crawler",
    "urls": { "start_urls": ["<existing-url-1>", "..."] },  // keep as-is
    "crawler_type": "<existing>",                            // keep as-is
    "max_pages_per_crawl": <existing>,                       // keep as-is
    "max_crawl_depth": <existing>,                           // keep as-is
    "ignore_errors": <existing>,                             // keep as-is
    "remove_html_elements": "footer, div.footer, #footer, header, nav, .nav, #nav, .navigation, .breadcrumb, .cookie-banner, script, style, noscript, svg, aside, .sidebar"
    // include ALL other existing fields unchanged
  }
)
```

> **Cross-check with 3–5 different nodes before committing** — ensure you're not removing content that matters.
> After updating, inform the user: *"I've updated the crawler config to strip [X]. Please re-run the data source sync to apply this change."*

### 2c. Retrieval failure root causes

| Cause | Diagnosis | Fix |
|---|---|---|
| Term mismatch | User phrasing not in KB text | Enrich node text with user's natural language |
| Signal dilution | Right content buried in noise | Strip noise via `remove_html_elements` |
| Score competition | Irrelevant keyword-heavy pages win | Apply `score_boost` to high-value nodes |
| Chunk boundary | Answer split across two chunks | Consolidate into single node or use `parent_context` retrieval |

**Find which nodes are load-bearing before boosting any:** `get_top_cited_sources` ranks the KB nodes most cited in answers, so you know exactly what to surface more often.

```
branchly_get_top_cited_sources(time_filter="last_30_days")
```

**Before setting any score_boost, always read the current node first:**

```
branchly_read_node(node_id="...")
// Check existing score_boost value
branchly_update_node(node_id="...", score_boost=1.5)
```

### 2d. Retrieval settings recommendations

Tell the user as a recommendation (these require backend/dashboard changes, not MCP):
- Migrate to **hybrid search mode** for better recall on keyword + semantic queries
- Switch embedding model to **`embedding-gemma-300m`** or **`multilingual-e5`** for better multilingual support

### 2e. Knowledge base tool adjustments

If a `search_knowledge_base` tool exists, check if it can be tuned:

```
branchly_list_tools(active=true)
branchly_read_tool(tool_id="...")
```

Consider:
- **Filter by data source**: if the tool searches everything but the relevant content lives in one specific source (e.g., an API data source for events), add `data_source_ids_filter`
- **Increase document limits**: bump `document_limit_default` from 15 → 20–25 for broader recall
- **Switch to parent_context retrieval**: set `retrieval_method: "parent_context"` to inject surrounding chunk context

```
branchly_update_tool(
  tool_id="...",
  function_arguments={
    "object": "knowledge_base_tool_arguments",
    "document_limit_default": 20,
    "retrieval_method": "parent_context",
    "data_source_ids_filter": ["<specific-ds-id>"]  // if applicable
  }
)
```

### 2f. Content gap — genuine missing information

Before concluding a content gap, search the knowledge base to confirm the content truly doesn't exist:

```
branchly_list_nodes(
  query="the topic the user asked about",
  locale="de",
  limit=10
)
```

If after all checks the content truly doesn't exist:
- Inform the user clearly: *"This topic isn't covered in your knowledge base."*
- Suggest: *"Add a manual FAQ node with a clear title and the answer text. This is the fastest way to cover this gap."*

---

## Step 3 — Audit AI Actions & Prompt Alignment

> **Terminology**: branchly calls configured callable functions **"AI Actions"** in the UI and official docs. The MCP API exposes them via `branchly_list_tools` / `branchly_update_tool`. Both terms refer to the same thing.

> **Interface types**: Prompts are scoped by `interface_type` — `chat`, `navigator`, `search`, or `api`. A `chat` prompt applies to chat/chat_widget/voice embeds, a `navigator` prompt to search embeds, a `search` prompt to search_interface embeds, and an `api` prompt to API embeds. Always specify `interface_type` when listing or creating prompts to target the right surface.

### 3a. Read all active AI Actions and prompts

```
branchly_list_tools(active=true)
branchly_list_prompts(is_active=true)
```

Read the chat prompts (routing + output) for a specific interface:

```
branchly_list_prompts(prompt_type="chat", interface_type="chat", is_active=true)
```

For search-answering prompts, use the appropriate interface type:

```
branchly_list_prompts(prompt_type="search_answering", interface_type="search", is_active=true)
```

### 3b. Check each AI Action against the routing prompt

For every AI Action, verify:
1. **Is the action's trigger condition explicitly named in the routing prompt?** If not → action never fires
2. **Does the action description accurately describe when to call it?** Vague = misfires
3. **Do routing and output instructions contradict each other?** Inconsistent behavior

**Common failure patterns:**

| Pattern | Symptom |
|---|---|
| AI Action with no routing mention | Action never fires |
| Vague action description | Action misfires or under-fires |
| Keyword CTA without action mapping | Bot waits for keyword but doesn't act |
| Output and routing contradict each other | Inconsistent behavior |
| Prompt copy-pasted across contexts | Dead instructions in wrong context |

### 3c. Key distinction — routing prompt (Prompt Persona) vs. output prompt

> **UI vs. API naming:**
> | Dashboard label | API `subtype` |
> |---|---|
> | **Prompt Persona** | `routing_instructions` |
> | **Output Instructions** | `output_instructions` |
>
> In the branchly dashboard, the routing prompt is labeled **"Prompt Persona"**. It controls which AI Actions are called, reformulates answers, and drives automatic evaluation. The output prompt controls response style and formatting only.

- **Routing prompt / Prompt Persona** (`subtype="routing_instructions"`): decides which AI Action(s) to call. Has **zero effect** on response style/tone. Also used during auto-evaluation.
- **Output prompt** (`subtype="output_instructions"`): generates the final response. Has **zero effect** on routing decisions.

Misplacing instructions (e.g., putting response formatting in the Prompt Persona) is a common misconfiguration.

### 3d. Fix AI Action descriptions and routing prompt

Update AI Action descriptions to be **MECE** (mutually exclusive, collectively exhaustive) — minimal overlap between actions so the routing agent can decide deterministically:

```
branchly_update_tool(
  tool_id="...",
  description="Updated description that clearly scopes when this action fires"
)
```

Update the routing prompt (Prompt Persona) when trigger conditions are missing or wrong:

```
branchly_create_prompt(
  type="chat",
  subtype="routing_instructions",
  interface_type="chat",
  prompt="<updated routing prompt text>"
)
```

Update the output prompt for the same interface:

```
branchly_create_prompt(
  type="chat",
  subtype="output_instructions",
  interface_type="chat",
  prompt="<updated output prompt text>"
)
```

> `create_prompt` automatically deactivates the previous active prompt of the same type/subtype/interface_type.
>
> **Required `interface_type` by prompt type**: `chat` prompts require `interface_type` of `chat` or `api`. `search_answering` prompts require `interface_type` of `navigator`, `search`, or `api`. `suggested_questions` and `chat_evaluation` prompts do not require `interface_type`.

---

## Step 4 — Data Source Health Check

### 4a. Check data source status

```
branchly_list_data_sources()
```

Look for:
- Failed sync runs (check `last_run_status` or equivalent)
- Data sources that haven't synced recently

**Supported data source types** (shown in `type` field of each source):

| Type | Description |
|---|---|
| `website_crawler` | Crawls public websites via Apify |
| `custom_website_crawler` | Crawl with custom HTML markers and graph builder |
| `file_upload` | Uploaded PDFs or documents |
| `openAPI` | API endpoint synced via OpenAPI spec |
| `helpspace` | Connected helpspace/help center |
| `webhook` | Data pushed via webhook with custom mapping |
| `node_editor` | Manually created/edited nodes |

> The `website_crawler` settings pattern (read-first, full object write) applies to `custom_website_crawler` as well. Other types have their own settings schemas.

### 4b. Check for outdated nodes

Nodes older than 3 months from dynamic sources (API, webcrawler, file upload, helpspace, custom crawler) may be stale:

```
branchly_list_nodes(
  sort_parameters=[{"field": "updated_at", "direction": "asc"}],
  limit=10
)
```

Flag and report outdated content to the user. Suggest a resync or manual review.

---

## Step 5 — AI Action Suggestions by Use Case

After auditing, suggest relevant AI Actions the application might be missing:

| Use Case | Suggested AI Actions |
|---|---|
| **Travel / Tourism** | Google Maps embed, Regiondo (guided tours), weather API action, MCP servers (venus, destination.one, infomax), web page reader for traffic/tide data |
| **Any call-to-action** | Buttons action (show CTAs inline), contact form action |
| **E-Commerce** | DHL parcel tracking API action |
| **Specific info lookup** (contacts, hours) | `node_lookup` action for precise node retrieval |
| **Always-on context** | Run an action (e.g., weather, events API) in parallel with KB search to enrich every response |

---

## Step 6 — Validate Every Change

After each fix:

1. **Re-read** the updated entity to confirm the change landed:
   ```
   branchly_read_node(node_id="...")
   branchly_read_tool(tool_id="...")
   branchly_list_prompts(prompt_type="chat", interface_type="chat", is_active=true)
   ```

2. **Check for side effects** — does this fix affect other nodes/tools/prompts?

3. **Generalize** — if one node had noisy HTML, all nodes from the same crawler likely do. If one tool had a vague trigger, audit all tools.

> Single fixes that don't generalize leave the same bug in five other places.

---

## Fix Layer Reference

| Problem | Fix layer | Tool |
|---|---|---|
| Missing information | Add KB node | `branchly_create_node` |
| Retrieval ranking | score_boost, node enrichment | `branchly_update_node` |
| Noisy indexed content | Crawler config | `branchly_update_data_source` |
| Wrong AI Action trigger | Routing prompt (Prompt Persona) | `branchly_create_prompt` (type: `chat`, interface_type: `chat`, subtype: `routing_instructions`) |
| Wrong tone/format | Output prompt | `branchly_create_prompt` (type: `chat`, interface_type: `chat`, subtype: `output_instructions`) |
| AI Action never fires | Action description + routing | `branchly_update_tool` + `branchly_create_prompt` |

**Principle: Fix the lowest layer possible. A retrieval fix shouldn't require a prompt change. A content fix shouldn't require a score boost.**
