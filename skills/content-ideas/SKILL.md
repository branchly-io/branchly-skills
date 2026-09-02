---
name: content-ideas
description: |
  Turn branchly MCP analytics into a prioritized content/optimization To-Do list.
  Gathers the most-important pages, most-cited KB nodes, tags, topics and intents,
  then ranks content gaps and opportunities by user impact. The output feeds
  downstream content work: generating FAQs, updating page copy, or creating new
  pages (blog posts, articles).

  Triggers when user mentions:
  - "what content should we create" / "content ideas"
  - "which pages/topics to prioritize"
  - "generate FAQs" / "what questions are users asking"
  - "find content gaps" / "what is missing in our knowledge base"
  - "what should we write about next"
license: MIT
---

## Content Ideas Workflow for branchly Applications

You have access to the branchly MCP server. Use it throughout this workflow.

> **Time filter quirk:** many analytics tools reject the string `"last_7_days"`.
> Use a preset enum (`last_30_days`, `last_6_months`, …) or an explicit range
> `"YYYY-MM-DD,YYYY-MM-DD"` (inclusive). Default for this skill is `last_30_days`.

---

## Goal

Produce a **prioritized To-Do list** of content/optimization opportunities for a
branchly application — ranked by real usage signal and by evidence of missing or
misleading content. The output is a structured Markdown report that a downstream
process can turn into FAQs, page edits, or new pages (blog posts, articles).

**Scope:** this skill delivers the prioritized list + a concrete recommendation
per item. It does **not** draft the actual FAQ/content copy — that happens
downstream.

---

## Step 1 — Gather the "what users care about" signals

Run these analytics tools to understand demand and where it originates. All use
`time_filter="last_30_days"` unless the user asks for a different window.

```bash
# Pages users were ON when they engaged the embed (origin pages → where content lives)
branchly_get_top_interaction_sources(time_filter="last_30_days", limit=15)

# URLs users actually clicked from inside the embed (what they found useful)
branchly_get_top_clicked_urls(time_filter="last_30_days", limit=15)

# KB nodes most cited in answers (what is load-bearing / working)
branchly_get_top_cited_sources(time_filter="last_30_days", limit=15)

# Topical breakdown of chat traffic (tags)
branchly_get_top_tags(time_filter="last_30_days", limit=15)

# Trending topics (subject matter) and intents (user goals)
branchly_get_trending_classifications(classification_type="topic", time_filter="last_30_days")
branchly_get_trending_classifications(classification_type="intent", time_filter="last_30_days")
```

Capture for each result: the name/URL/vertex, the count, and what it implies about
demand. This is the **demand side** of the prioritization.

---

## Step 2 — Find missing & misleading content (the "gaps")

### 2a. Answer-quality health

```bash
branchly_get_answer_type_distribution(time_filter="last_30_days")
branchly_get_sentiment_distribution(time_filter="last_30_days")
```

A high `no_knowledge` / `outside_scope` / `follow_up_question` share, or rising
negative sentiment, flags content gaps or confusing answers.

### 2b. What users actually search / ask

```bash
branchly_get_top_searches(time_filter="last_30_days", limit=15)
```

Top searches are direct evidence of unmet intent. Pair each search with sessions
to see whether it was answered well:

```bash
branchly_read_sessions(search_query="<the search term>", interactions=["chat"], limit=10)
```

### 2c. Confirm whether a gap is real (never assume)

For any topic that looks missing or poorly answered, verify against the KB before
flagging it as a gap:

```bash
branchly_list_nodes(query="<topic>", locale="de", limit=10)
```

If relevant nodes exist but weren't retrieved → **retrieval/ranking issue**, not a
content gap. If nothing relevant exists → **genuine content gap**.

### 2d. Inspect the worst sessions for root cause

For `no_knowledge` / `outside_scope` sessions, read the detail and grounding to
classify the failure:

```bash
branchly_read_sessions(answer_types=["no_knowledge", "outside_scope"], interactions=["chat"], limit=10)
branchly_read_session_detail(session_id="...")
branchly_read_chat_request_documents(chat_request_id="...")
branchly_read_chat_request_tool_calls(chat_request_id="...")
```

Classify each into: routing failure, retrieval failure, ranking failure, prompt
failure, or genuine content gap.

---

## Step 3 — Build the prioritized To-Do list

Combine demand (Step 1) with gaps (Step 2). Score each opportunity on three axes:

1. **Demand** — how many sessions/searches/citations point at it (access numbers).
2. **Gap severity** — is content missing, hard to retrieve, or misleading?
3. **Effort** — FAQ node (low) vs. page edit (medium) vs. new page/blog (high).

Rank by **user impact first** (demand × gap severity), then by effort.

For each item, output a row with:

| Priority | Opportunity | Evidence (counts) | Type | Recommendation |
|---|---|---|---|---|
| P1 | e.g. "How to integrate with TYPO3" | 6 searches, 2 no_knowledge | FAQ node | Add a manual FAQ node with a direct docs link |
| P2 | e.g. "Pricing comparison" | top cited source, 40 tags | Page edit | Expand /pricing copy; clarify package tiers |
| P3 | e.g. "MCP protocol explainer" | trending topic up 3× | New page | Draft a blog post / glossary article |

**Recommendation types map to downstream work:**
- **FAQ node** → generate FAQ entries for the knowledge base.
- **Page edit** → supplement or correct content on an existing page.
- **New page** → create a blog post / article / glossary page.

---

## Step 4 — Deliver the report

Produce a **structured Markdown report** (no JSON/CSV unless the user asks):

1. **Coverage** — time window analyzed + what surface(s) (chat, search, …).
2. **Demand snapshot** — top pages, top cited nodes, top tags, top topics/intents with counts.
3. **Gap findings** — answer-type/sentiment health + confirmed gaps (with the evidence).
4. **Prioritized To-Do list** — the table from Step 3, ranked P1 → P3.
5. **Notes** — anything needing a human decision (e.g. "9 soft-404 nodes need a link fix", "sentiment signal is always neutral").

Flag anything that requires a product/editorial decision rather than an autonomous
change. Do not edit prompts, tools, nodes, or crawlers based on this analysis
unless the user explicitly asks — this skill is about **deciding what content to
create**, not applying config changes.

---

## Pitfalls

- **Never call a gap a content gap until you've confirmed the retriever had nothing
  useful** (`list_nodes(query=...)`). A retrieval failure is not a missing page.
- **Respect the time-filter quirk** — use enums or explicit ranges, not `last_7_days`.
- **Distinguish origin pages (`get_top_interaction_sources`) from clicked URLs
  (`get_top_clicked_urls`)** — one says where users came from, the other what they
  clicked through to. Both matter for different recommendations.
- **Trends need a comparison window** — to say a topic is "rising", compare the
  current window against a prior one, not just a single snapshot.
- **Keep the output human-first** — a directly readable prioritized list is the
  deliverable; machine-readable artifacts are opt-in.