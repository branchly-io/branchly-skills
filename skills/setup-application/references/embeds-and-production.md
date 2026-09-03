# Setup Application — Embed Snippets & Production Checklist

Use this reference during **Phase 8 (Embed Delivery & Production Handover)**.

Documentation references:
- Embed Guide: [docs.branchly.io/docs/how-to-embed](https://docs.branchly.io/docs/how-to-embed)
- Application Settings: [docs.branchly.io/docs/settings](https://docs.branchly.io/docs/settings)

---

## 1. Production HTML Embed Snippets

### 1a. Floating Chat Widget
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

### 1b. Inline Chat Embed
Embed directly into a page container (e.g. `/help` or `/contact`):
```html
<script async type="module" src="https://embed.branchly.io/assets/index.js"></script>
<div
  id="branchly-chat-embed-container"
  data-token="<APPLICATION_TOKEN>">
</div>
```

---

### 1c. Search Interface (Button / Modal Mode)
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

## 2. Advanced Analytics, Retrieval Customization & Interaction Tracking

branchly provides enterprise tracking, retrieval tuning, and analytics capabilities that should be reviewed and configured before launch:

### 2a. Retrieval Customization & Custom Boosting Options
Under Application Settings > Search / Rerank Settings:
- **Custom Boosting (`custom_boosting`):** Uses the `score_boost` numeric field on individual knowledge base nodes to prioritize specific high-value content (e.g. key landing pages, official FAQs, primary contact nodes). Configurable for `search` and `chat` interfaces (`mode="mult"`).
- **Time-Based Datetime Reranking (`datetime_reranking`):** Automatically boosts newer or recently modified content higher in search/retrieval results. Evaluated by `published_date` or `modified_date` — essential for news, blogs, and fast-evolving documentation.
- **Record Source Reranking (`record_source_reranking`):** Independently adjusts ranking weights based on matches in the `title` (e.g. `title_boost: 1.5`) vs. `text` body (e.g. `text_boost: 0.75`).

### 2b. Classification Modes (`classification_mode`)
- **`active` (Recommended):** Real-time conversational clustering. The AI automatically classifies every chat session into semantic **topics** (subject matter trends) and **intents** (user goals). Drives trend analytics in the dashboard and weekly automated digest reports.
- **`deactivated`:** Turns off topic/intent categorization if classification is not desired.
- Analyze trends over time via `branchly_get_trending_classifications(classification_type="topic"|"intent")`.

### 2c. Follow-Up Questions (`follow_up_actions=true/false`)
- **Enabled (`true` - Recommended):** Dynamically generates suggested follow-up questions and next-step navigation pills at the end of assistant answers.
  - Links to your configured domain navigate within the host site frame.
  - External links open safely in a new tab.
- **Disabled (`false`):** Delivers clean text answers without appending suggested questions or follow-up action pills.

### 2d. Cross-Lingual Adaptation (`use_browser_locale=true/false`)
Translates all user interfaces into the visitor's browser language and manages cross-lingual search:
- **How it works:**
  1. **UI Text Localisation:** All static UI elements (input placeholders, button labels, disclaimers, suggestions, error messages) are dynamically served in the visitor's browser language.
  2. **Cross-Lingual Retrieval:** If a visitor's browser locale is not in your configured `valid_locales` (e.g. a Japanese visitor on an EN/DE site), branchly automatically switches to **dense multilingual semantic search** (bypassing language-specific BM25 keyword search) and instructs the AI to reply in the visitor's language backed by the nearest available content.
- **When to enable:**
  - **Enable (`true`):** If your site receives international visitors whose languages you have not fully indexed into dedicated locale nodes.
  - **Disable (`false` - Default):** If your site is single-language with a homogeneous audience or strictly serves language-segregated paths (`/de/`, `/en/`) where the widget should strictly match the page language.

### 2e. Interaction & Element Tracking (Anchor Tags & Buttons)
Configure fine-grained user journey tracking under `Settings > Tracking`:
- **Track Page Navigations / Link Clicks:** Toggle on to trace complete visitor pathways across Docusaurus, documentation, or marketing layouts.
- **Global Anchor & Button Tracking:** Define tracking rules to automatically capture all clicks on anchor links (`<a>`) and buttons (`<button>`) across the website.
- **Custom Element Tracking (`data-branchly`):**
  - Add the `data-branchly="<label>"` attribute to specific UI elements (e.g. hero CTA buttons, feature cards, pricing tiers) to track high-value conversion milestones.
- **Dashboard Auto-Exclusion:** Interaction events inside the branchly widgets themselves are automatically filtered out to prevent skewing website analytics.

---

## 3. Production Deployment Security Checklist

1. **Set Environment to Production:**
   - In the branchly dashboard under Application Settings > General, switch the **Environment / Status** from `development` to `production`.
   - Ensures production routing, proper caching, active analytics retention, and live session monitoring.
2. **Allowed Website Locations (`embed_location`):**
   - For security, branchly blocks widgets loaded on unlisted domains.
   - All production domains (e.g. `https://example.com`, `https://www.example.com`) and staging environments must be registered under **Website Location** in branchly Application Settings.
3. **Content Security Policy (CSP):**
   If the target website enforces strict CSP headers, whitelist the branchly endpoints:
   - `script-src`: `https://chat-widget.branchly.io https://search.branchly.io https://embed.branchly.io`
   - `connect-src`: `https://api.branchly.io`
   - `frame-src`: `https://chat-widget.branchly.io https://search.branchly.io https://embed.branchly.io`
   - `style-src`: `'unsafe-inline'`
4. **Locale Tagging:**
   branchly automatically respects the page language via `<html lang="de">` or `<div data-token="..." lang="de">`. Ensure language tags match configured `valid_locales`.
