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

## 2. Production Deployment Security Checklist

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
