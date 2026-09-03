# Setup Application — Crawler Settings & Embed Snippets

Use this reference during **Phase 3 (Data Ingestion)** and **Phase 8 (Embed Delivery)**.

Documentation references:
- Data Sources: [docs.branchly.io/docs/data-sources](https://docs.branchly.io/docs/data-sources)
- Embed Guide: [docs.branchly.io/docs/how-to-embed](https://docs.branchly.io/docs/how-to-embed)
- Application Settings: [docs.branchly.io/docs/settings](https://docs.branchly.io/docs/settings)

---

## 1. Website Crawler Noise-Reduction Configuration

When updating a `website_crawler` data source, **always send the complete settings object** (partial settings are rejected or cause errors).

### Standard Production HTML Exclusion Selectors
The following CSS selectors remove boilerplate headers, footers, cookie notices, and embed containers that contaminate vector embeddings:

```css
footer, div.footer, #footer, header, div.pageheader, #pageheader, script, style, noscript, svg, nav, .nav, #nav, .navigation, .breadcrumb, [role="alert"], [role="banner"], [role="dialog"], [role="alertdialog"], [role="region"][aria-label*="skip" i], [aria-modal="true"], #branchly-chat-widget-container, #branchly-embed-container, #branchly-chat-embed-container, #branchly-search-interface-container, .cookie-banner, #cookie-banner, [class*="cookie"], [id*="cookie"]
```

### Full Data Source Update Payload
```python
# 1. Read existing data source
data_sources = branchly_list_data_sources()
target_ds = data_sources["items"][0]

# 2. Update with clean settings
branchly_update_data_source(
    data_source_id=target_ds["id"],
    schedule="0 4 * * 2",  # Weekly cron sync
    settings={
        "type": "website_crawler",
        "actor": "apify/website-content-crawler",
        "crawler_type": "playwright:adaptive",  # Handles JS hydration
        "urls": {"start_urls": ["https://<domain>/"]},
        "max_pages_per_crawl": 200,
        "max_crawl_depth": 50,
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

## 2. Production HTML Embed Snippets

### 2a. Floating Chat Widget
Embed before the closing `</body>` tag on all desired pages:
```html
<script async type="module" src="https://chat-widget.branchly.io/assets/index.js"></script>
<div
  id="branchly-chat-widget-container"
  data-token="<APPLICATION_TOKEN>"
  data-custom-styles="false"
  data-open-default="false">
</div>
```

**Attributes:**
- `data-token`: Unique application token from branchly dashboard.
- `data-custom-styles`: Set `"false"` to use default styles; set `"true"` to style via custom CSS classes.
- `data-open-default`: Set `"true"` to open the chat window on initial page load.
- `data-chat-popup="questions"`: Display suggested questions as clickable pills above the closed bubble.

---

### 2b. Inline Chat Embed
Embed directly into a page container (e.g. `/help` or `/contact`):
```html
<script async type="module" src="https://embed.branchly.io/assets/index.js"></script>
<div
  id="branchly-chat-embed-container"
  data-token="<APPLICATION_TOKEN>">
</div>
```

---

### 2c. Search Interface (Button / Modal Mode)
Embed inside the site header, navigation bar, or hero section:
```html
<script async type="module" src="https://search.branchly.io/assets/index.js"></script>
<div
  id="branchly-search-interface-container"
  data-token="<APPLICATION_TOKEN>"
  data-view-mode="search-button">
</div>
```

**Attributes:**
- `data-view-mode="search-button"`: Shows an input-styled button that opens the search modal on click.
- `data-view-mode="inline"`: Embeds the search interface directly inside the page without a modal.

---

## 3. Production Deployment Security Checklist

1. **Allowed Website Locations (`embed_location`):**
   - For security, branchly blocks widgets loaded on unlisted domains.
   - All production domains (e.g. `https://example.com`, `https://www.example.com`) and staging environments must be registered under **Website Location** in branchly Application Settings.
2. **Content Security Policy (CSP):**
   If the target website enforces strict CSP headers, whitelist the branchly endpoints:
   - `script-src`: `https://chat-widget.branchly.io https://search.branchly.io https://embed.branchly.io`
   - `connect-src`: `https://api.branchly.io`
   - `frame-src`: `https://chat-widget.branchly.io https://search.branchly.io https://embed.branchly.io`
   - `style-src`: `'unsafe-inline'`
3. **Locale Tagging:**
   branchly automatically respects the page language via `<html lang="de">` or `<div data-token="..." lang="de">`. Ensure language tags match configured `valid_locales`.
