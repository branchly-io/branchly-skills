# Setup Application — Embed Delivery & Production Checklist

Use this reference during **Phase 8 (Embed Delivery & Production Handover)**.

## Canonical documentation (link, don't duplicate)

| Topic | Canonical source |
|---|---|
| Embed scripts & container markup (per interface) | [docs.branchly.io/docs/how-to-embed](https://docs.branchly.io/docs/how-to-embed) |
| Application settings (analytics, retrieval, tracking, locale) | [docs.branchly.io/docs/settings](https://docs.branchly.io/docs/settings) |

The docs own the exact embed markup and the full setting-by-setting descriptions. This file holds only the **setup-decision recommendations** — what to review before launch, the recommended values, and the production go-live checklist.

---

## 1. Embed Snippets — get them from the docs / dashboard

For every interface (Chat Widget, Inline Chat, Search, Form, Navigator), fetch the exact `<script>` + container markup from **[how-to-embed](https://docs.branchly.io/docs/how-to-embed)** — or, better, copy the snippet straight from the **Dashboard > User Interface** so the token/`src` are correct for the app.

**Current embedding surface (docs):**
- **Chat Widget** — floating bubble (`branchly-chat-widget-container`); also available as a standalone `<branchly-chat-widget>` custom element.
- **Chat** — inline page embed (`branchly-chat-embed-container`).
- **Search Interface** — `branchly-search-interface-container`, with `data-view-mode="search-button"` (modal) or `"inline"`; a custom trigger button can be created with `data-branchly-search-trigger`.
- **Form** — `branchly-form-container`.
- **Navigator** — `branchly-embed-container`.

> ⚠️ The docs — not this file — are the source of truth for script URLs and attributes. They have moved (e.g. custom-element + trigger-attribute embedding) and the exact domains differ by interface, so don't copy stale markup.

---

## 2. Settings to Review Before Launch

Review these in **Application Settings** and set the recommended values. Field-level detail lives in the [settings docs](https://docs.branchly.io/docs/settings).

### 2a. Retrieval customization & boosting
- **Custom Boosting:** Set per-node `score_boost` (via `branchly_update_node`) to prioritize high-value content (key landing pages, official FAQs, contact node) — `mode="mult"`, active for `search` + `chat`.
- **Datetime reranking (`datetime_reranking`):** Enable for news/blogs/fast-moving docs to push `published_date`/`modified_date`-recent content higher.
- **Record-source reranking (`record_source_reranking`):** Tune title vs. body match weights (e.g. `title_boost: 1.5`, `text_boost: 0.75`).

### 2b. Classification mode
- Set **`classification_mode: "active"`** so sessions are clustered into semantic **topics** + **intents** — powers dashboard trends and the weekly digest email.
- Read trends via `branchly_get_trending_classifications(classification_type="topic"|"intent")`.

### 2c. Follow-up actions
- **`follow_up_actions: true` (recommended):** AI adds context-aware follow-up question pills + navigation next-steps (internal links navigate in-frame, external open in new tab).
- **`false`:** clean answers, no suggestion pills.

### 2d. Cross-lingual adaptation (`use_browser_locale`)
- **Enable** if your site gets international visitors in languages you haven't fully indexed — branchly localizes UI text to the browser language and falls back to dense multilingual semantic search for unsupported locales.
- **Disable (default)** for single-language / homogeneous sites or strict `/{lang}/` path segregation (widget matches the page locale).
- Related: `reply_in_user_language` detects a visitor's *typed* chat language and replies in kind.

### 2e. Interaction & element tracking
- **Track page navigation / link clicks** — on, to trace visitor journeys across Docusaurus/docs/marketing layouts.
- **Anchor & button rules** — capture all clicks on `<a>` and `<button>` globally, or target CSS selectors.
- **Custom conversion tags** — add `data-branchly="<label>"` to high-value elements (hero CTA, feature cards, pricing tiers).
- Widget-internal events are auto-excluded from your website analytics.

---

## 3. Production Go-Live Checklist

1. **Set Environment to Production:** In Dashboard > Settings > General, switch from `development` to `production` — enables production caching, routing, analytics retention, and live session monitoring.
2. **Register Allowed Domains (`embed_location`):** every production + staging domain the widget appears on must be listed under **Website Location**, or the embed fails to initialize (security-restricted).
3. **Content Security Policy:** if the site enforces CSP, whitelist branchly endpoints (`script-src`/`connect-src`/`frame-src` for the branchly.io embed domains, plus `style-src 'unsafe-inline'`).
4. **Locale tagging:** ensure `<html lang>` (or container `lang`) matches configured `valid_locales`.
5. **Brand convention:** always write the platform name lowercase `"branchly"`.