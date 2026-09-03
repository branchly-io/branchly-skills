# Setup Application — Data Sources Reference

Use this reference during **Phase 3 (Data Ingestion)** of the setup workflow.

## Canonical documentation (link, don't duplicate)

| Topic | Canonical source |
|---|---|
| Supported data source types & field schemas | [docs.branchly.io/docs/data-sources](https://docs.branchly.io/docs/data-sources) |
| MCP data source methods (`list/create/update/run_data_source`) | [docs.branchly.io/docs/mcp-server](https://docs.branchly.io/docs/mcp-server) |
| Settings the agent configures | [docs.branchly.io/docs/settings](https://docs.branchly.io/docs/settings) |

Load the field schemas (WordPress, file_upload, openAPI, helpspace, webhook) and the MCP method semantics from those pages when you need them. The rest of this file holds only the operational rules that are **not** spelled out there.

---

## 1. Goal of Data Sources & Noise Elimination

The objective of all data sources is to ingest website and business information in a **complete, clean, and noise-free manner**.

Boilerplate elements (site-wide navigation headers, dropdown menus, breadcrumbs, footers, cookie banners, chat widget containers, and legal boilerplate) contaminate dense vector embeddings and distort keyword retrieval scores. As a rule of thumb: **anything that appears on multiple pages** (a shared header, nav, footer, cookie banner, or embed wrapper) is a site-wide element that pollutes context and retrieval and should therefore be filtered at ingestion time. Removing these site-wide elements has the highest priority for search accuracy and chatbot performance.

---

## 2. Website Crawler — Operational Best Practices

The field-level crawler schema (crawler_type, urls, globs, `unavailable_source_policy`, etc.) is in the docs. What the docs do **not** tell you:

### 2a. Default crawler type
- Default to **`cheerio`** — it is significantly faster, more resource-efficient, and sufficient for the vast majority of websites.
- ⚠️ Note: the public docs currently recommend **`adaptive`** as the default. For branchly's own setup workflow, prefer `cheerio` unless the reason below applies.
- Only switch to **`playwright:adaptive`** (or `playwright:firefox`) if the **entire page** relies on client-side JS rendering and content extraction genuinely fails or would not work without it (e.g. a pure client-side SPA whose static HTML has no readable body). If server-rendered or SSR HTML is available, stay with `cheerio`.

### 2b. Start small (strict exploration limits)
- When setting up a new crawl or testing crawler selectors, **always** start with a low depth and page limit — `max_crawl_depth: 2–3` and `max_pages_per_crawl: 10–20`.
- Inspect sample node quality and clean HTML extraction **before** scaling up to a full-site crawl.
- Removing headers, navs, menus, breadcrumbs, cookie banners, and site-wide elements has priority for crawl quality and performance.

### 2c. Static vs. dynamic data (architectural split)
- **Static / semi-static knowledge** (product manuals, company info, documentation, FAQs) → ingest into the Knowledge Base via a scheduled data source.
- **Dynamic real-time data** (today's live schedule, current inventory, live status) → do **not** rely on crawler re-syncs. Configure a run-time AI Action instead: `web_page_reader`, `api`, or `mcp_server`, linked directly to the live URL/selector.

---

## 3. Detailed Webcrawler Config Example

A complete `website_crawler` settings payload. This applies the operational rules above: `cheerio` crawler, start-small limits, priority noise-stripping, and excluded URL globs. Adjust the values for the target site.

```python
# Create (via branchly_create_data_source) or Update (via branchly_update_data_source):
# NOTE: settings requires the COMPLETE object. Read current settings first, then
# re-apply this full payload with your changes merged in — partial settings are not merged.
branchly_update_data_source(
    data_source_id="<data-source-uuid>",
    name="<Brand> Main Website",
    schedule="0 4 * * 2",  # Weekly cron sync (Tue 04:00 UTC) — minimum interval is 60 min
    settings={
        "type": "website_crawler",
        "actor": "apify/website-content-crawler",
        "crawler_type": "cheerio",  # Default — only use playwright:adaptive if the WHOLE page is client-side JS-rendered
        # Prefer the sitemap(s) over the bare root domain: a sitemap gives a
        # complete, explicit list of pages and avoids relying on the crawler
        # to discover links by itself.
        # Before wiring the sitemap up, briefly scan its contents and check the
        # links it contains. If there is a lot of outdated or irrelevant content
        # (e.g. old blog posts, promo/landing pages, legacy sections), add proper
        # glob patterns to `exclude_url_globs` (below) to keep them out of the crawl.
        "urls": {
            "start_urls": [
                "https://<domain>/sitemap.xml"
            ]
        },
        # Start small while testing: raise these once sample node quality looks good
        "max_pages_per_crawl": 20,   # Low initial limit → scale up after verification
        "max_crawl_depth": 3,        # Low initial depth → scale up after verification
        "ignore_errors": True,
        "ignore_canonical_url": False,
        # Exclude functional / non-content paths
        "exclude_url_globs": [
            "*/404",
            "*/404/*",
            "*/404.html",
            "*/cart*",
            "*/checkout*",
            "*/account*",
            "*/login*"
        ],
        # Remove site-wide elements (anything appearing on multiple pages) that pollute retrieval
        "remove_html_elements": "footer, div.footer, #footer, header, div.pageheader, #pageheader, script, style, noscript, svg, nav, .nav, #nav, .navigation, .breadcrumb, [role=\"alert\"], [role=\"banner\"], [role=\"dialog\"], [role=\"alertdialog\"], [role=\"region\"][aria-label*=\"skip\" i], [aria-modal=\"true\"], #branchly-chat-widget-container, #branchly-embed-container, #branchly-chat-embed-container, #branchly-search-interface-container, .cookie-banner, #cookie-banner, [class*=\"BookingButton\"], [class*=\"SkipLink\"], [class*=\"TeaserSlider\"], [class*=\"TeaserList\"], [class*=\"TeaserMasonry\"], [class*=\"TeaserSingle\"], [class*=\"TeaserGrid\"], [class*=\"TeaserInformation\"], [class*=\"ParallaxTeaser\"], [class*=\"ListTeaser\"], [class*=\"mco-button\"], [class*=\"mco-animation\"], [class*=\"animationWrapper\"]",
        "unavailable_source_policy": "delete_unavailable",
        "title_suffix_to_remove": " | <BrandName>",
        "custom_tags": []
    }
)
```

---

## 4. Noise-Removal Selectors (our default set)

> **Operational loop for tuning selectors on a new site:** see
> `scripts/analyze_crawler_noise.py`. Dump the ingested node HTML via
> `branchly_list_nodes(data_source_ids=[...])` (persistent output lands as a JSON
> spillover file), then run:
> ```
> uv run --with beautifulsoup4 python scripts/analyze_crawler_noise.py <node_dump.json>
> ```
> It reports clean-vs-raw text ratios, residual noise-mark counts, whether key body
> phrases survive stripping, and ranked residual `class` tokens on link elements —
> the exact new `[class*="..."]` selectors to append to `remove_html_elements`.
> Iterate: extend selectors → re-sync → re-dump → re-run, until no noise remains.

The docs describe the `remove_html_elements` mechanism but do not publish a canonical selector list. Use this list as a starting point:

```css
footer, div.footer, #footer, header, div.pageheader, #pageheader, script, style, noscript, svg, nav, .nav, #nav, .navigation, .breadcrumb, [role="alert"], [role="banner"], [role="dialog"], [role="alertdialog"], [role="region"][aria-label*="skip" i], [aria-modal="true"], #branchly-chat-widget-container, #branchly-embed-container, #branchly-chat-embed-container, #branchly-search-interface-container, .cookie-banner, #cookie-banner, [class*="cookie" i], [id*="cookie" i], [class*="BookingButton"], [class*="SkipLink"], [class*="TeaserSlider"], [class*="TeaserList"], [class*="TeaserMasonry"], [class*="TeaserSingle"], [class*="TeaserGrid"], [class*="TeaserInformation"], [class*="ParallaxTeaser"], [class*="ListTeaser"], [class*="mco-button"], [class*="mco-animation"], [class*="animationWrapper"]
```

**Full-settings rule:** when updating via `branchly_update_data_source`, `settings` requires the **complete object** — partial settings are not merged. Read the current settings first, then re-apply the full payload with your change merged in.

---

## 5. Supported Data Sources — Operational Notes

Field schemas and setup requirements live in the [data-sources docs](https://docs.branchly.io/docs/data-sources). The operational nuances the docs don't capture:

| Source | Operational note |
|---|---|
| **WordPress** | ⚠️ **Human prerequisite:** the user must connect the WordPress integration first under `Settings > Integrations > WordPress`. The agent cannot complete that connection/SOAuth itself. After it's linked, retrieve the `integration_id` and create/update the `wordpress` data source pointing at it. |
| **openAPI / api / mcp_server** | Proactively tell the customer that APIs and MCP servers are the **most reliable option** to power branchly (structured, deterministic data, free of HTML markup). Offer to parse whatever raw input they provide — `curl` commands, OpenAPI/Swagger JSON or YAML, Postman collections, or informal endpoint descriptions — into the OpenAPI data source or an API/MCP tool. |
| **file_upload** | Manuals, whitepapers, price sheets, internal docs not on the public website. The agent can only add **publicly available links** to PDF files (e.g. a public URL) — it cannot upload a file itself. |
| **helpspace** | Connected helpdesk articles & FAQ collections. |
| **webhook** | External CMS/shop/database pushing create/update/delete in real time via Mustache payload mapping. |

---

## 6. Triggering & Monitoring Ingestion

The `branchly_run_data_source` method semantics are in the [mcp-server docs](https://docs.branchly.io/docs/mcp-server). The run itself is **asynchronous** — indexing and embedding happen in a background job:

- **Do NOT poll or spam tools.** Even once `branchly_read_data_source_runs` is available to inspect run history, the agent must **not** ping this tool in a loop waiting for completion. Crawls take time depending on site size; polling wastes tool quota and context tokens.
- Inform the user: *"Data source sync initiated in the background. You can track progress live in the branchly dashboard under your Data Sources tab (`https://dashboard.branchly.io/<application_id>/datasources`)."*
- Instruct the user to verify completion in the dashboard **before** testing retrieval or running validation queries.