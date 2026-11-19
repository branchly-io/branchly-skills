---
name: create-faqs
description: |
  Create and publish FAQ entries for a branchly-powered website from real visitor
  questions. Mines actual searches and chat sessions for recurring questions, grounds
  every answer in existing knowledge-base content, publishes FAQ nodes via the
  branchly MCP server, and delivers a website-ready FAQ section with FAQPage
  JSON-LD. Downstream of content-ideas.

  Triggers when user mentions:
  - "create FAQs" / "generate FAQs" / "add an FAQ section to page X"
  - "answer the questions visitors keep asking"
  - "turn our chat/search questions into FAQs"
  - "publish FAQ nodes" / "write the FAQ copy"
  - "use the FAQ question list from content-ideas"
license: MIT
metadata:
  author: branchly-io
  version: "1.0.0"
---

## Create FAQs Workflow for branchly Applications

Use the branchly MCP server throughout this workflow: mine what visitors actually
ask, ground every answer in existing knowledge-base content, and publish the
finished FAQs as knowledge-base nodes so chat and search answer them instantly.

---

## Goal

Turn real visitor questions into **published, grounded FAQ entries**:

1. **Questions come from real demand** — searches and chat sessions, not guesswork.
2. **Answers are grounded** — written from retrieved knowledge-base content, so the
   FAQ page and the AI assistant never contradict each other.
3. **Published via MCP** — each FAQ becomes a knowledge-base node
   (`branchly_create_node`), so the assistant answers the question immediately.
4. **Website-ready output** — a paste-ready FAQ section plus FAQPage JSON-LD for
   search-engine rich results.

**Position in the skill family:** `content-ideas` identifies which pages need FAQs
and which questions to answer (upstream input). This skill writes and publishes
the FAQ entries. `optimize-application` handles retrieval tuning;
`website-insights` measures the impact.

**Scope:** This skill creates and updates FAQ *nodes* via MCP. It does not edit
website pages — the website FAQ section is delivered as paste-ready Markdown for
the site owner.

---

## Rules — Non-Negotiable

1. **Real questions only.** FAQ questions come from actual visitor searches and
   sessions (or an explicit question list provided by the user, e.g. from
   `content-ideas`). Never invent questions. Keep the visitor's phrasing — clean
   it for grammar only.
2. **Ground every answer.** Write answers ONLY from content retrieved via
   `branchly_list_nodes` / `branchly_read_node` (or facts the user provided). If
   nothing grounds the answer, mark the question "needs human input" and collect
   it in the report. Never fabricate.
3. **One canonical question per node.** Never create a wall-of-text FAQ mega-node;
   single-question nodes retrieve reliably, mega-nodes do not.
4. **No duplicates.** Before creating, search the existing FAQ nodes
   (`labels=["faq"]`). If a near-duplicate exists, enrich it with
   `branchly_update_node` instead of creating a second node.
5. **Respect scope, filter noise.** No FAQs for out-of-scope topics (sport
   results, stocks, trivia). Exclude dev/localhost/test/gibberish queries and
   report them as "removed as test/technical noise (n)".
6. **Verify after publishing.** Re-query with the visitors' original phrasings;
   every phrasing variant must surface the new node. If it does not, tighten the
   question title with the keywords visitors actually type.
7. **Publish in the right locales.** `text` is a locale-keyed map. Publish each
   FAQ in every locale it was asked in (within `valid_locales`); a question asked
   in German gets a German answer.

---

## Step 0 — Context

```bash
# App: name, domains, valid_locales
branchly_get_application()

# Active prompts: tone, audience, scope
branchly_list_prompts(is_active=true)

# Data sources: which content is authoritative
branchly_list_data_sources()

# Active tools: actions visitors can take (contact form, booking, ...)
branchly_list_tools(active=true)
```

Establish: domain, tone of voice, `valid_locales`, and which data sources carry
authoritative content for grounding.

---

## Step 1 — Collect the Real Questions

If the user provides a question list (e.g. the FAQ Recommendations from
`content-ideas`), use it and continue with Step 2 — but still ground every
answer in Step 3.

Otherwise, mine the analytics (default: trailing 30 days):

```bash
# What visitors type into search and chat
branchly_get_top_searches(time_filter="<start>,<end>", limit=20)

# Which pages provoke the questions (→ target page for each FAQ)
branchly_get_top_interaction_sources(time_filter="<start>,<end>", limit=15)

# How many questions end without a proper answer
branchly_get_answer_type_distribution(time_filter="<start>,<end>")

# The actual unanswered and follow-up conversations
branchly_read_sessions(answer_types=["no_knowledge", "outside_scope", "follow_up_question"], interactions=["chat"], limit=10, time_filter="<start>,<end>")
```

For each flagged session, read the full detail:

```bash
branchly_read_session_detail(session_id="...")
```

**What to look for:**
- `no_knowledge` / `outside_scope` sessions = unanswered demand, phrased in the
  visitor's own words.
- `follow_up_question` sessions are gold: the visitor got an answer but still
  needed more — exactly the nuance an FAQ should capture.
- Interaction sources tell you **where** each question lives: the page the
  visitor was on is the page that needs the FAQ section (same target-page logic
  as `content-ideas`).

---

## Step 2 — Cluster, Deduplicate, Rank

- Merge phrasing variants into **one canonical question** (keep the most natural
  visitor phrasing).
- Rank by frequency and journey value (Awareness → Consideration →
  Booking/Contact → Support).
- Filter noise per Rules 1 and 5; report exclusions.
- Record the **target page** for each question (from interaction sources).
- Small volumes are fine for FAQs: a single real question justifies an
  evergreen, in-scope FAQ. Frequency sets priority, not inclusion.

---

## Step 3 — Ground Every Answer

For each canonical question, retrieve the content the answer must be based on:

```bash
# Search the knowledge base for relevant content
branchly_list_nodes(query="<question terms>", locale="<locale>", limit=10)

# Check for an existing FAQ node saying the same thing
branchly_list_nodes(labels=["faq"], query="<question terms>", limit=10)

# Read the authoritative source content
branchly_read_node(node_id="...")
```

- Write the answer from the retrieved node text — the same content the assistant
  retrieves, so the FAQ page and the chatbot can never contradict each other.
- Existing near-duplicate FAQ node → plan a `branchly_update_node` (enrich the
  text) instead of a create.
- Nothing found → mark the question **"needs human input"** and collect it
  separately for the report (Rule 2). Do not write an answer.

---

## Step 4 — Write the FAQ Entries

For each publishable question, prepare:

- **Question:** the canonical visitor phrasing (Rule 1).
- **Answer:** 2–4 sentences, grounded in Step 3 content, in the tone from the
  prompts; include the source page URL when the node has one.
- **Locales:** every locale the question appeared in (within `valid_locales`).
- **Target page:** the website page this FAQ belongs to (for the section in
  Step 6).

---

## Step 5 — Publish and Verify via MCP

Create one node per question:

```bash
branchly_create_node(
  title={"en": "<canonical question>"},
  text={"en": "<grounded answer>"},
  label="faq",
  source="<target page URL, if the FAQ belongs to a specific page>"
)
```

- `title` and `text` are locale-keyed maps — a multi-locale FAQ is one node:
  `text={"en": "...", "de": "..."}`.
- `label="faq"` keeps FAQ nodes filterable and maintainable
  (`branchly_list_nodes(labels=["faq"])`).
- Enriching an existing node instead:
  `branchly_update_node(node_id="...", text={"en": "<improved answer>"})`.

Then **verify** (Rule 6):

```bash
branchly_list_nodes(query="<original visitor phrasing>", locale="en", limit=5)
```

Re-run with each original phrasing variant. Every variant should surface the new
node. If one does not, add the missing keywords to the question title and
re-verify.

---

## Step 6 — Deliver

Produce the FAQ creation report:

```markdown
# FAQ Creation Report — <Domain>

**Question source:** <analytics window | user-provided list from content-ideas>
**Result:** N FAQ nodes created · M nodes updated · K questions flagged "needs human input"
**Noise removed:** <n> test/technical queries excluded from the question pool.

| # | Question | Locale(s) | Node ID | Status | Target page |
|---|---|---|---|---|---|
| 1 | ... | en, de | ... | created / updated / needs human input | /pricing |

## Needs Human Input (no grounded content yet)
| Question | Evidence (who asked, how often) | Suggested owner |
|---|---|---|
| ... | ... | ... |

## Website FAQ Section (paste-ready)
<Markdown accordion with questions + answers, grouped by target page>

## FAQPage Structured Data (for search-engine rich results)
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "<canonical question>",
      "acceptedAnswer": { "@type": "Answer", "text": "<grounded answer>" }
    }
  ]
}
</script>
```

---

## Pitfalls to Avoid

- **Never invent answers.** Ground every answer in retrieved nodes or user-provided
  facts; ungrounded questions go to "needs human input".
- **One question per node.** A wall-of-text FAQ node destroys retrieval; one
  canonical question per node surfaces reliably.
- **Deduplicate before creating.** Always check `labels=["faq"]` first; update
  existing nodes instead of creating near-duplicates.
- **Don't copy crawler noise into answers.** Read the node text — if it is
  boilerplate-heavy, flag the source instead of laundering the noise into an FAQ.
- **Respect the domain scope.** No FAQs for sport results, stock prices, or
  trivia questions.
- **Never skip the post-publish check.** A published FAQ that does not retrieve is
  invisible to the assistant and the search interface.
- **Don't ignore locales.** A German question deserves a German answer; use the
  locale-keyed `text` map.
