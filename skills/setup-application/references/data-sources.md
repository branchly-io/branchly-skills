# Setup Application — Data Sources Reference

Use this reference during **Phase 3 (Data Ingestion)** of the setup workflow.

Documentation references:
- Data Sources Overview: [docs.branchly.io/docs/data-sources](https://docs.branchly.io/docs/data-sources)
- MCP Server Reference: [docs.branchly.io/docs/mcp-server](https://docs.branchly.io/docs/mcp-server)

---

## 1. Goal of Data Sources & Noise Elimination

The objective of all data sources is to ingest website and business information in a **complete, clean, and noise-free manner**. 

Boilerplate elements (site-wide navigation headers, dropdown menus, breadcrumbs, footers, cookie banners, chat widget containers, and legal boilerplate) contaminate dense vector embeddings and distort keyword retrieval scores. Removing them at ingestion time has the highest priority for search accuracy and chatbot performance.

---

## 2. Website Crawler Data Source (`website_crawler`)

### Best Practices for Crawling:
1. **Default Crawler Type:** Always use `cheerio` as the default crawler. It is significantly faster, more resource-efficient, and sufficient for the vast majority of websites.
2. **Dynamic / Client-Side JS Sites:** Only switch `crawler_type` to `playwright:adaptive` (or `playwright:firefox`) if the entire page relies on client-side JS rendering and content extraction genuinely fails or would not work without it (e.g. pure client-side SPAs where static HTML has no readable body). If standard server-rendered HTML or SSR is available, stay with `cheerio`.
3. **Start Small (Strict Exploration Limits):**
   - **Crucial Rule:** When setting up a new crawl or testing crawler selectors, **always set a low limit for `max_crawl_depth` (e.g. 2–3) and `max_pages_per_crawl` (e.g. 10–20)** before scaling up.
   - Verify sample node quality and clean HTML extraction before initiating full site crawls.
4. **Static Crawling vs. Real-Time Dynamic Data:**
   - The website crawler is designed for **static/semi-static** knowledge that updates on a schedule.
   - For information that changes in real time (e.g. live inventory, current events, live pricing, today's schedule, dynamic status), **do NOT rely on crawler re-syncs**.
   - Instead, configure the **`web_page_reader`** AI Action (or custom API tool) and link it directly to the specific live URL/selector so the agent fetches real-time data at run-time.

### Standard Noise-Removal Selectors:
Always include these comma-separated selectors in `remove_html_elements`:
```css
footer, div.footer, #footer, header, div.pageheader, #pageheader, script, style, noscript, svg, nav, .nav, #nav, .navigation, .breadcrumb, [role="alert"], [role="banner"], [role="dialog"], [role="alertdialog"], [role="region"][aria-label*="skip" i], [aria-modal="true"], #branchly-chat-widget-container, #branchly-embed-container, #branchly-chat-embed-container, #branchly-search-interface-container, .cookie-banner, #cookie-banner, [class*="cookie" i], [id*="cookie" i]
```

### Full Settings Payload Example:
> ⚠️ **Settings require the complete object.** When updating via `branchly_update_data_source`, send the entire `settings` dictionary.

```python
# Create (if branchly_create_data_source is available) or Update:
branchly_update_data_source(
    data_source_id="<data-source-uuid>",
    name="Website Main",
    schedule="0 4 * * 2",  # Weekly cron sync
    settings={
        "type": "website_crawler",
        "actor": "apify/website-content-crawler",
        "crawler_type": "cheerio",  # Default; only use playwright:adaptive if whole page requires client-side JS rendering and wouldn't work without it
        "urls": {"start_urls": ["https://<domain>/"]},
        "max_pages_per_crawl": 20,  # Low limit during initial setup/testing
        "max_crawl_depth": 3,  # Low depth during initial setup/testing
        "ignore_errors": True,
        "ignore_canonical_url": False,
        "exclude_url_globs": [
            "*/404",
            "*/404/*",
            "*/404.html",
            "*/cart*",
            "*/checkout*",
            "*/account*",
            "*/login*",
        ],
        "remove_html_elements": "footer, div.footer, #footer, header, div.pageheader, #pageheader, script, style, noscript, svg, nav, .nav, #nav, .navigation, .breadcrumb, [role=\"alert\"], [role=\"banner\"], [role=\"dialog\"], [role=\"alertdialog\"], [aria-modal=\"true\"], #branchly-chat-widget-container, #branchly-embed-container, #branchly-chat-embed-container, #branchly-search-interface-container, .cookie-banner, #cookie-banner",
        "unavailable_source_policy": "delete_unavailable",
        "title_suffix_to_remove": " | <BrandName>",
        "custom_tags": [],
    },
)
```

---

## 3. Supported Data Sources & Setup Requirements

branchly supports multiple ingestion methods for content outside standard web pages:

### A. WordPress (`wordpress`)
Connects to WordPress via REST API v2 (`/wp-json/wp/v2`) and syncs Posts, Pages, or custom post types.
- **Prerequisite (Human Action Required):**
  > ⚠️ The user **must create the WordPress integration in the dashboard first** under `Settings > Integrations > WordPress`. The agent cannot complete OAuth or generate the integration connection autonomously.
- **Agent Role:**
  After the user connects WordPress in the dashboard, the agent retrieves the `integration_id` and configures the `wordpress` data source:
  ```python
  settings = {
      "type": "wordpress",
      "api_path": "/wp-json/wp/v2",
      "post_types": ["posts", "pages"],
      "post_status": ["publish"],
      "default_site_locale": "de",
      "locale_detection": "static",  # or "path_prefix", "subdomain", "query_param", "wpml"
      "unavailable_source_policy": "delete_unavailable",
      "verify_ssl": True,
  }
  ```

### B. Uploaded Documents & PDFs (`file_upload`)
Processes uploaded PDF and CSV documents into structured knowledge nodes.
- Useful for product manuals, whitepapers, price sheets, or internal documentation not published on the public website.
- Inferred locale and semantic heading chunking (`split_documents`).
- Settings structure:
  ```python
  settings = {
      "type": "file_upload",
      "files": [
          {"file_name": "manual.pdf", "url": "https://.../manual.pdf", "is_external": False}
      ]
  }
  ```

### C. OpenAPI Specification (`openAPI`)
Syncs structured data directly from REST APIs by importing an OpenAPI JSON specification.
- **Why API / OpenAPI:** Using APIs and MCP servers is the **most reliable option** to use branchly because data is structured, deterministic, and free of HTML markup artifacts.
- **Customer Input & Agent Parsing:**
  - Proactively inform the customer that connecting APIs or MCP servers yields the highest reliability and request this information if available.
  - The agent should try its best to parse whatever raw input the customer provides — whether that is raw `curl` commands, OpenAPI/Swagger JSON or YAML specs, Postman collections, or informal endpoint descriptions.
  - From this raw input, the agent extracts the `base_url`, headers/auth, the relevant endpoint (`operation_id`), response schema, and writes the `data_template_mapping`.
- Calls a specified `operation_id` on the API endpoint and maps JSON responses into knowledge nodes using Mustache templating.
- Settings structure:
  ```python
  settings = {
      "type": "openAPI",
      "openapi_spec": "<raw_json_or_url>",
      "operation_id": "listArticles",
      "response_content_path": "items",  # dot-notation path to item array
      "data_template_mapping": {
          "title": "{{title}}",
          "text": "{{description}} - {{content}}",
          "source": "{{url}}",
          "custom_metadata": {"tags": "{{category}}"},
      },
      "extra_options": {"base_url": "https://api.example.com/v1"},
      "unavailable_source_policy": "delete_unavailable",
  }
  ```

### D. HelpSpace Docs (`helpspace`)
Direct integration with HelpSpace help centers.
- Ingests helpdesk articles and FAQ collections.
- Requires:
  - `client_id` (from HelpSpace `Settings > Access Token`)
  - `api_token` (Read-only token)
  - `site_id` (HelpSpace Docs site ID)

### E. Webhooks (`webhook`)
Allows external CMSs, e-commerce platforms, or databases to push content updates in real time using Mustache payload mapping.

---

## 4. Managing Data Sources via MCP

Interact with data sources programmatically using the following MCP methods:

### 4a. Inspect Existing Sources
Before making changes, always list active data sources and read their current configuration:
```bash
branchly_list_data_sources()
```
Examine `type`, `last_run_status`, schedule, and existing `settings`.

### 4b. Create a New Data Source
When introducing a new ingestion pipeline (e.g. an OpenAPI integration or a secondary crawler):
```python
branchly_create_data_source(
    name="Product Documentation",
    type="website_crawler",
    schedule="0 3 * * 1",  # Weekly Monday 03:00 UTC
    settings={...},  # Full settings schema for the given type
)
```

### 4c. Update Data Source Settings
When updating crawler selectors, sync schedules, or template mappings, remember that **`settings` requires the complete object** (partial settings are not merged):
```python
# 1. Inspect current settings first
sources = branchly_list_data_sources()
target = next(s for s in sources["items"] if s["name"] == "Main Website")

# 2. Re-apply the full settings payload with your modifications
branchly_update_data_source(
    data_source_id=target["id"],
    settings={
        **target["settings"],
        "remove_html_elements": "<updated comma-separated selectors>",
        "max_pages_per_crawl": 20,
    },
)
```

### 4d. Trigger Synchronization & Monitor Progress
Triggering a sync runs an **asynchronous background crawler / ingestion job**:
```python
branchly_run_data_source(data_source_id="<data-source-uuid>")
```

Because indexing and embedding generation happen in the background:
- Inform the user: *"Data source sync initiated in the background. You can track progress live in the branchly dashboard under your Data Sources tab (`https://dashboard.branchly.io/<application_id>/datasources`)."*
- Wait for the job to complete in the dashboard before testing retrieval or running validation queries.
