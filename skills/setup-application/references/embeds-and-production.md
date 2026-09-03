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

For every interface (Chat Widget, Inline Chat, Search, Form), fetch the exact `<script>` + container markup from **[how-to-embed](https://docs.branchly.io/docs/how-to-embed)** — or, better, copy the snippet straight from the **Dashboard > User Interface** so the token/`src` are correct for the app.

**Current embedding surface (docs):**
- **Chat Widget** — floating bubble (`branchly-chat-widget-container`); also available as a standalone `<branchly-chat-widget>` custom element.
- **Chat** — inline page embed (`branchly-chat-embed-container`).
- **Search Interface** — `branchly-search-interface-container`, with `data-view-mode="search-button"` (modal) or `"inline"`; a custom trigger button can be created with `data-branchly-search-trigger`.
- **Form** — `branchly-form-container`.

> ⚠️ The docs — not this file — are the source of truth for script URLs and attributes. Always fetch the current markup from the docs or dashboard; don't copy markup from other sources that may be outdated.

---

## 2. Optional Enhancements (not required for v1)

The settings below are **optional, mutually independent** features that can improve **performance, analytical value, or UX** once the application is live. They are **not required** to deliver a working v1 application. For an initial setup, the AI agent should **only briefly mention that they exist** (and be able to enable them on request later) — not configure or dwell on them now.

Field-level detail lives in the [settings docs](https://docs.branchly.io/docs/settings).

### 2a. Retrieval customization & boosting
- **Custom Boosting:** per-node `score_boost` to prioritize high-value content (key landing pages, FAQs, contact node) — `mode="mult"`, active for `search` + `chat`.
- **Datetime reranking (`datetime_reranking`):** pushes `published_date`/`modified_date`-recent content higher — useful for news/blogs/fast-moving docs.
- **Record-source reranking (`record_source_reranking`):** tune title vs. body match weights (e.g. `title_boost: 1.5`, `text_boost: 0.75`).

### 2b. Classification mode
- **`classification_mode: "active"`** clusters sessions into semantic **topics** + **intents** — powers dashboard trends and the weekly digest email. Optional but recommended.
- It is recommended to provide your own topics/intents beforehand so classifications align with your systems.

### 2c. Follow-up actions
- **`follow_up_actions: true`** adds context-aware follow-up question pills + navigation next-steps (internal links navigate in-frame, external open in new tab).

### 2d. Cross-lingual adaptation (`use_browser_locale`)
- **Enable** for international visitors in languages you haven't fully indexed — branchly localizes UI text to the browser language and falls back to dense multilingual semantic search for unsupported locales.
- **Disable (default)** for single-language / homogeneous sites or strict `/{lang}/` path segregation (widget matches the page locale).
- Related: `reply_in_user_language` detects a visitor's *typed* chat language and replies in kind.

### 2e. Interaction & element tracking
- **Anchor & button rules** — capture clicks on `<a>` and `<button>` globally, or target specific CSS selectors (e.g. add-to-cart button).
- **Custom conversion tags** — `data-branchly="<label>"` on high-value elements (hero CTA, feature cards, pricing tiers).
- Widget-internal events (click citation/source, follow-up questions, etc.) are auto-captured inside branchly.

> For a v1 setup, none of the above need to be configured. Mention them in one line and offer to enable them later if the user wants the extra performance, analytics, or UX.

---

## 3. Production Go-Live Checklist

1. **Set Environment to Production:** In Dashboard > Settings > General, switch from `development` to `production` — enables production caching, routing, analytics retention, and live session monitoring.
2. **Register Allowed Domains (`embed_location`):** every production + staging domain the widget appears on must be listed under **Website Location**, or the embed fails to initialize (security-restricted).
3. **Content Security Policy:** if the site enforces CSP, whitelist branchly endpoints (`script-src`/`connect-src`/`frame-src` for the branchly.io embed domains, plus `style-src 'unsafe-inline'`).
4. **Locale tagging:** ensure `<html lang>` (or container `lang`) matches configured `valid_locales`.