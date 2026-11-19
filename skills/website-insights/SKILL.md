---
name: website-insights
description: |
  Generate a plain-language, CMO-ready analytics insight report about what is
  happening on a branchly-powered website: engagement, customer demand signals,
  friction, funnel and market opportunities. Output is executive-level,
  action-first (content plans, funnel fixes, campaign/geography inputs).

  Triggers when user mentions:
  - "website analytics report" / "what is happening on our website"
  - "customer insights" / "what are users asking"
  - "marketing report" / "CMO dashboard"
  - "how is our chatbot/AI search performing"
  - "where are we losing users" / "what should marketing focus on"
license: MIT
metadata:
  author: branchly-io
  version: "1.0.0"
---

## Website Insights Workflow for branchly Applications

Use the branchly MCP server throughout this workflow to analyze real visitor
sessions, searches, and engagement on the customer's website and turn them into
an executive marketing report.

---

## Goal

Produce a **plain-language, CMO-ready "Website Analytics Insight Report"** for
marketing leadership (VP Marketing / Head of Marketing / CMO). The audience is
**not technical**. The report answers, in plain language:

1. **What is happening on our website?**
2. **What do our customers want?**
3. **What is broken or causing friction?**
4. **What should we do next?**

Every insight ends in a **marketing action** (content, page updates, campaigns,
localization, funnel fixes, human handoff) — never in RAG/internal configuration
details. Technical bot tuning belongs to `optimize-application`; editorial content
plans belong to `content-ideas`.

**Scope:** This skill is strictly **analytical and read-only**. It analyzes and
recommends; it never changes production configuration. Recommended actions are
for humans to execute.

---

## Rules — Non-Negotiable

1. **Executive audience:** Never use RAG/internal jargon in the main report (no
   `retrieve_documents`, `score_boost`, `data_source_ids_filter`, "embed dupe",
   crawler selectors, node IDs). Such terms may appear only in a clearly-marked
   optional "Technical appendix" at the end. The main report must read like a
   marketing brief.
2. **Every finding maps to an action.** Each report section ends with "→ Do X",
   where X is a marketing lever: create/edit content, add an FAQ section on
   page Y, run a campaign, add a locale/translation, fix a funnel step, or set
   up a human-handoff.
3. **Small-n discipline:** Flag any finding based on fewer than ~10 sessions as
   "signal, not proof". Never dramatize a single-session delta. Repeat the
   small-n caveat in the Executive Summary.
4. **Filter noise explicitly:** Exclude dev/staging/localhost URLs,
   gibberish/emoji/foreign-script test inputs, "testy"-type manual queries,
   404-page-derived content, and boilerplate pages from marketing numbers.
   Report exclusions as "removed as test/technical noise (n)".
5. **Sentiment is often degenerate:** Sentiment distributions are frequently
   ~100% neutral. Never report sentiment aggregates as a headline. If a
   negative or positive case exists, open the session and present it as a
   qualitative case study (what happened, why, what to do).
6. **Origin vs. clicked pages are different signals:** Interaction sources =
   where users had to **ask** (potential friction). Clicked URLs = what they
   found **useful**. Report both and their ratio; a high ask-rate with a low
   click-rate on the same page means ambiguous content worth fixing.
7. **Searches are the voice of the customer:** Top searches, top tags, trending
   topics/intents, languages, locales, and geographies are the most
   CMO-valuable data. Dedicate a prominent report section to them.
8. **Compare windows, never single snapshots:** Always analyze a current vs. a
   prior period. Only label something a trend when both windows have
   non-trivial volume.
9. **Verify before claiming a content gap:** Use
   `branchly_list_nodes(query=..., locale=...)` to check whether the topic is
   missing, only thinly mentioned, or exists but does not retrieve well
   (a retrieval-quality issue, not a content issue). Keep this consistent with
   the `content-ideas` classifications.
10. **Read-only:** This skill NEVER calls `update_data_source`, `update_tool`,
    `create_prompt`, `update_node`, or any other mutation. It analyzes and
    recommends; humans execute.

---

## Time Windows

Every branchly analytics call accepts a `time_filter`. Use **two explicit date
ranges** — a current window and the directly preceding prior window — so every
metric has a comparison (Rule 8):

```bash
# Current window (example: trailing 30 days)
time_filter="2026-10-20,2026-11-19"

# Prior window (the 30 days before)
time_filter="2026-09-20,2026-10-19"
```

- Compute both ranges from today's date.
- Default cadence: trailing 30 days vs. the prior 30 days. Use weekly or
  monthly windows when the user asks for them.
- Fetch every comparison metric for **both** windows.

---

## Step 0 — Context

Before querying analytics, understand what business this website serves:

```bash
# Overall app: name, domains, embed surfaces, valid_locales
branchly_get_application()

# Active prompts: domain, target audience, use case, scope
branchly_list_prompts(is_active=true)

# Data sources: what website content feeds the answers
branchly_list_data_sources()

# Active tools: CTAs/actions available to visitors (forms, bookings, ...)
branchly_list_tools(active=true)
```

Establish:
- **Domain & audience:** what business this website serves and who visits it.
- **Surfaces:** which embeds (chat, search, navigator, ...) run where.
- **Locales:** `valid_locales` — which languages the site officially serves.
- **Actions:** what visitors can do (contact forms, booking links, ...).

Out-of-scope topics (e.g. sport results, stock prices, general trivia) get no
marketing recommendations.

---

## Step 1 — Engagement & Traffic

```bash
# Sessions per day over the current window
branchly_get_active_sessions_over_time(time_filter="<current_start>,<current_end>")

# Sessions by embed surface (chat, search_interface, navigator, ...)
branchly_get_active_sessions_by_embed(time_filter="<current_start>,<current_end>")

# Answer quality — current vs. prior window
branchly_get_answer_type_distribution(time_filter="<current_start>,<current_end>")
branchly_get_answer_type_distribution(time_filter="<prior_start>,<prior_end>")

# Device mix
branchly_get_top_devices(time_filter="<current_start>,<current_end>")
```

**Report:** active sessions/day trend, breakdown by embed, answer quality
(complete / no_knowledge / outside_scope / small_talk / follow_up), device mix,
and a current-vs-prior comparison table for answer types.

**What to look for:**
- Which surfaces carry the traffic, and whether that shifted vs. the prior window.
- Answer quality: what share of questions ended in a complete answer? A rising
  no_knowledge / outside_scope share means content and demand are drifting apart
  (→ content or campaign actions in Step 4).
- A mobile-heavy device mix prioritizes mobile clarity in any copy fix.

---

## Step 2 — Voice of Customer (Demand)

```bash
branchly_get_top_searches(time_filter="<current_start>,<current_end>", limit=20)
branchly_get_top_tags(time_filter="<current_start>,<current_end>", limit=15)
branchly_get_trending_classifications(classification_type="topic", time_filter="<current_start>,<current_end>")
branchly_get_trending_classifications(classification_type="intent", time_filter="<current_start>,<current_end>")
branchly_get_top_languages(time_filter="<current_start>,<current_end>", limit=10)
branchly_get_top_locales(time_filter="<current_start>,<current_end>", limit=10)
branchly_get_top_geographies(time_filter="<current_start>,<current_end>", limit=10)
```

**Report:** what customers ask, the intent mix (e.g. information_request /
booking / contact), languages vs. locales, and geographies.

**What to look for:**
- **Journey stages:** group intents into customer-journey stages where the
  domain supports it (Awareness → Consideration → Booking/Contact → Support).
- **Language/locale mismatch:** e.g. German-language questions against an
  English-only locale list = localization gap (→ translation/locale action).
- **Geographies:** growing regions suggest campaign or locale expansion (e.g.
  "Add Spanish locale for growing LATAM traffic").
- Filter noise per Rule 4 (test queries, gibberish, foreign-script probes) and
  note the removal count.

---

## Step 3 — Journey & Friction (Where Are We Losing People?)

```bash
# Where users had to ASK (potential friction)
branchly_get_top_interaction_sources(time_filter="<current_start>,<current_end>", limit=15)

# What they found USEFUL enough to click
branchly_get_top_clicked_urls(time_filter="<current_start>,<current_end>", limit=15)

# Sentiment (usually ~all-neutral — see Rule 5)
branchly_get_sentiment_distribution(time_filter="<current_start>,<current_end>")

# Recent struggling sessions
branchly_read_sessions(answer_types=["no_knowledge", "outside_scope", "follow_up_question"], interactions=["chat"], limit=10, time_filter="<current_start>,<current_end>")
```

For each flagged session, read the full detail:

```bash
branchly_read_session_detail(session_id="...")
```

**Classify each case:**
- **Missing info:** the website does not cover the topic (verify with
  `branchly_list_nodes` per Rule 9 before claiming a gap).
- **Ambiguous page copy:** the page exists but visitors keep asking the same
  basic question → page/FAQ fix.
- **Routing & handoff opportunity:** e.g. a user asks "is a human here?" →
  contact-form handoff intent.
- **Genuinely non-automatable:** note it; no marketing action.

Report ask-vs-click per page and flag "high asks, low clicks" pages (Rule 6).
Present negative or positive sentiment cases as short qualitative case studies
(what happened, why, what to do) — never as percentages (Rule 5).

---

## Step 4 — Opportunity & Plan Synthesis

Combine Steps 1–3 into **P1–P3 marketing actions**. Each action contains:

- **Opportunity** — in plain language.
- **Evidence** — spelled-out counts and the window they come from.
- **Marketing lever** — content plan / FAQ section / page update / campaign /
  locale expansion / funnel fix / human-handoff setup.
- **Recommendation** — concrete, e.g. "Add a FAQ section on /pricing answering
  the top-3 pricing questions users typed", or "Add Spanish locale for growing
  LATAM traffic."

Before classifying anything as a content gap, verify (Rule 9):

```bash
branchly_list_nodes(query="<topic or search term>", locale="<locale>", limit=10)
```

Classify the result:
- **Missing:** no page covers the topic → new page/article (hand off to
  `content-ideas`).
- **Thin mention:** the keyword appears (logo wall, footer) but nothing answers
  the question → page update or FAQ section.
- **Retrieval-quality:** content exists but does not surface → an
  `optimize-application` fix; mention only in the Technical appendix.

---

## Step 5 — Deliver the Executive Report

Write the report in the user's language. Deliver it in your response; if a file
is useful, save it as a dated Markdown file in the working directory (e.g.
`website-insights-report-2026-11-19.md`).

```markdown
# <Domain> — Website Analytics Insight Report

**Coverage:** <current window> (vs. <prior window>) · <surface(s)>
**Prepared for:** Marketing / Product leadership

## 1. Executive Summary
- <insight 1> → <action>
- <insight 2> → <action>
- ...

*Small-n caveat: findings based on fewer than ~10 sessions are directional
signals, not proof.*

## 2. Engagement & Traffic
| Metric | Current | Prior | Δ |
|---|---|---|---|
| ... | ... | ... | ... |

## 3. Voice of Customer
**Top searches:** ... · **Topics:** ... · **Intents:** ...
**Languages vs. locales:** ... (mismatch = localization gap)
**Geographies:** ...

## 4. Journey & Friction
**Where users ask vs. click:** ...
**Case study (negative feedback):** ...
**Handoff opportunities:** ...

## 5. Prioritized Marketing Plans
| P | Opportunity | Evidence | Lever | Recommendation |
|---|---|---|---|---|
| P1 | ... | ... | ... | ... |

## 6. Technical Appendix (optional — internal)
<Only if genuinely helpful; clearly mark as internal. No RAG jargon above
this line.>
```

---

## Pitfalls to Avoid

- **Filter dev/test traffic:** Remove localhost/staging URLs, gibberish, emoji,
  and "test"-type queries from marketing numbers; report "removed as
  test/technical noise (n)".
- **Sentiment is not a metric:** Expect ~all-neutral distributions; open
  individual sessions and write case studies instead of quoting percentages.
- **Do not fabricate content gaps:** Verify every claimed gap with
  `branchly_list_nodes(query=...)` first.
- **Distinguish origin vs. clicked URLs:** Interaction sources are friction
  points; clicked URLs are useful content. Never conflate them.
- **No RAG/internal jargon in the main report:** Crawler settings, retrieval
  scores, node IDs, and prompt internals belong in the Technical appendix at
  most.
- **Never change production config:** This skill is read-only; recommendations
  are for humans to execute.
- **No recommendations for out-of-scope topics:** Sport results, stock prices,
  and trivia questions get ignored, not marketed.
