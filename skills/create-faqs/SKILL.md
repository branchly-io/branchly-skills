---
name: create-faqs
description: |
  Create FAQ entries for a branchly-powered website from real visitor demand
  signals. Consumes question sets and demand evidence from content-ideas
  (searches, classification topics, tags, interaction sources, top cited nodes)
  or mines them via the branchly MCP server, verifies every answer 100% against
  website content — citing the exact source passages — and delivers the FAQs in
  the output format chosen upfront: a file, branchly nodes, or CMS-ready page
  content.

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

Use the branchly MCP server throughout this workflow: collect the demand signals
that show where FAQs are needed, verify every answer 100% against website
content, and deliver the finished FAQs in the output format the user chooses
upfront — optionally as knowledge-base nodes, so chat and search answer them
instantly.

---

## Goal

Turn real visitor demand into **published, fully verified FAQ entries**:

1. **Questions come from real demand signals** — searches, chat sessions,
   classification topics, tags, interaction sources, and top cited nodes,
   ideally aggregated upstream by `content-ideas`.
2. **Answers are 100% verified** — every answer is written strictly from website
   content retrieved via MCP and ships with the verbatim source passages that
   verify it. The FAQ page and the AI assistant can never contradict each other.
3. **Output format chosen upfront** — before anything is generated, the user
   picks the delivery: a **file**, **FAQ nodes in branchly**
   (`branchly_create_node`, so the assistant answers the question immediately),
   or **CMS-ready content** for the customer's page. Publishing to branchly is
   optional, never the default.
4. **Website-ready output** — a paste-ready FAQ section with extractable,
   self-contained answer blocks, plus optional FAQPage JSON-LD for machine
   readability (AI assistants parse it; Google retired FAQ rich results in
   May 2026 — the value is the answer content itself).

**Position in the skill family:** `content-ideas` aggregates the demand signals
(top searches, classification topics, tags, interaction sources, top cited
sources) into prioritized FAQ recommendations with target pages. This skill
consumes that output — or gathers the same signals itself — then verifies,
writes, and publishes. `optimize-application` handles retrieval tuning;
`website-insights` measures the impact.

**Scope:** This skill may create and update FAQ *nodes* via MCP — only when the
user chose that output format. It does not edit website pages on its own; page
delivery is paste-ready content for the site owner, or a direct CMS upload when
the user provides CMS access or tools.

---

## Rules — Non-Negotiable

1. **Real questions only.** FAQ questions come from actual visitor demand
   signals (or an explicit question list provided by the user, e.g. from
   `content-ideas`). Never invent questions. Keep the visitor's phrasing — clean
   it for grammar only.
2. **100% verified answers only.** Create an FAQ only when the *complete*
   answer — every fact, number, price, name, and condition — can be verified
   from website content retrieved via `branchly_list_nodes` /
   `branchly_read_node`. If any part cannot be verified, the question goes to
   "needs human input". Never publish a partially verified answer; never
   fabricate, round off, or extrapolate.
3. **Cite the passages.** Every suggested FAQ answer must include the verbatim
   passage(s) it rests on, plus the source node ID, title, and page URL. No
   passage, no FAQ.
4. **One canonical question per node.** Never create a wall-of-text FAQ
   mega-node; single-question nodes retrieve reliably, mega-nodes do not.
5. **No duplicates — in the KB or on the page.** Before creating or suggesting
   an FAQ, check two places: (a) the knowledge base for the question terms —
   existing FAQ nodes carry question-shaped titles; and (b) the **target page
   itself** and the site's existing FAQ page — pages often already carry
   question-answer blocks (accordions, embedded FAQs) that a new suggestion
   would duplicate. If the question is already answered in either place, do
   not create a new FAQ: mark it "already covered" in the report with a
   pointer to where it lives, and recommend enriching or linking the
   existing answer instead.
6. **Respect the use case, filter noise.** FAQs must fit the use case defined
   by the prompt personas (Step 0). No FAQs for out-of-scope topics (sport
   results, stocks, trivia). Exclude dev/localhost/test/gibberish queries and
   report them as "removed as test/technical noise (n)".
7. **Verify after publishing to branchly.** Re-query with the visitors'
   original phrasings; every phrasing variant must surface the new node. If it
   does not, tighten the question title with the keywords visitors actually
   type.
8. **Deliver in the right locales.** Provide each FAQ in every locale it was
   asked in (within `valid_locales`) — a question asked in German gets a German
   answer, whatever the output format.

---

## Step 0 — Context, Use Case & Output Format

**Ask before you start: which output format does the user want?** This choice is
made before any FAQ is written — it decides whether Step 5 runs and how Step 6
packages the result:

| Option | What gets delivered |
|---|---|
| **File** | The FAQ set as files in the working directory (Markdown report and/or CSV/JSON) for the site owner to place anywhere |
| **branchly nodes** | One node per question via `branchly_create_node` (Step 5), so chat and search answer instantly |
| **CMS / customer's page** | The FAQ section formatted for the customer's CMS (paste-ready HTML/Markdown for their page); uploaded directly only if the user provides CMS access or tools |

Publishing to branchly is optional, never the default. If the user is unsure,
default to the file option — nothing is published anywhere without their say-so.

```bash
# App: name, domains, valid_locales
branchly_get_application()

# Prompt personas for chat AND search — the use case definition
branchly_list_prompts(is_active=true)

# Data sources: which content is authoritative
branchly_list_data_sources()

# Active tools: actions visitors can take (contact form, booking, ...)
branchly_list_tools(active=true)
```

Read the **prompt personas for both chat and search** — especially the routing
instructions. They define the use case: domain positioning, target audience,
in-scope topics, out-of-scope guardrails, and tone of voice. The search persona
often serves a narrower scope than chat; an FAQ that fits one interface may be
out of scope for the other. Establish: domain, use case per interface, tone,
`valid_locales`, and the data sources that carry authoritative website content.

---

## Step 1 — Collect the Demand Signals

**Preferred input: the `content-ideas` report.** It already aggregates the
signals that decide where FAQs are needed:

- top searches and unanswered sessions → *what visitors ask, in their words*
- classification topics + tags → *which themes recur often enough to cover*
- interaction sources → *which pages provoke questions → FAQ target pages*
- top cited nodes → *which existing content carries the answers*

If no `content-ideas` output is at hand, pull the same signals directly
(default: trailing 30 days):

```bash
# Exact question phrasings
branchly_get_top_searches(time_filter="<start>,<end>", limit=20)

# Recurring themes worth covering
branchly_get_trending_classifications(classification_type="topic", time_filter="<start>,<end>")
branchly_get_trending_classifications(classification_type="intent", time_filter="<start>,<end>")
branchly_get_top_tags(time_filter="<start>,<end>", limit=15)

# Which pages need the FAQ section
branchly_get_top_interaction_sources(time_filter="<start>,<end>", limit=15)

# Load-bearing content that already answers most demand
branchly_get_top_cited_sources(time_filter="<start>,<end>", limit=15)

# How much unanswered demand exists
branchly_get_answer_type_distribution(time_filter="<start>,<end>")

# The actual unanswered and follow-up conversations
branchly_read_sessions(answer_types=["no_knowledge", "outside_scope", "follow_up_question"], interactions=["chat"], limit=10, time_filter="<start>,<end>")
```

For each flagged session, read the full detail:

```bash
branchly_read_session_detail(session_id="...")
```

**What to look for:**
- `follow_up_question` sessions are gold: the visitor got an answer but still
  needed more — exactly the nuance an FAQ should capture.
- **Suggested questions with a complete answer are a good proxy for finished
  Q&A pairs.** Session history entries carry an `is_suggested_question`
  indicator — a query that came from a question suggestion shown on the page.
  When such a question ends in a `complete` answer, the question is proven
  and the answering content exists: a ready-made Q&A pair and a prime FAQ
  candidate. Pull them via `branchly_read_sessions` /
  `branchly_read_session_detail` and still ground the answer via Step 3
  before publishing.
- A question whose theme appears in **several signals at once** — a search query,
  a trending topic or tag, and an interaction source all pointing at the same
  page — is the strongest FAQ candidate.
- A recurring question that overlaps a **top cited node** means the content
  exists but visitors still ask: prime FAQ material, and that node is the
  grounding anchor for the answer.

---

## Step 2 — Cluster, Deduplicate, Rank

- Merge phrasing variants into **one canonical question** (keep the most natural
  visitor phrasing).
- Rank by frequency, cross-signal confirmation (how many independent signals
  point at this question/theme), and journey value (Awareness → Consideration →
  Booking/Contact → Support).
- Filter noise per Rules 1 and 6; report exclusions.
- Record the **target page** for each question (from interaction sources).
- Group the questions into **fact families** (the pricing facts, the
  compatibility facts, the cancellation facts) and give each family **one
  owning target page** — AI engines fan a single prompt out into several fact
  lookups, and one strong page can serve them all. Never a new page per
  question variant.
- Small volumes are fine for FAQs: a single real question justifies an
  evergreen, in-scope FAQ. Frequency sets priority, not inclusion.

---

## Step 3 — Verify Every Answer Against the Website

For each canonical question, retrieve the website content that must carry the
answer:

```bash
# Search the knowledge base for relevant content — this also surfaces
# existing FAQ nodes, whose question-shaped titles match the query
branchly_list_nodes(query="<question terms>", locale="<locale>", limit=10)

# Read the authoritative source content
branchly_read_node(node_id="...")
```

**Deduplicate against the page itself (Rule 5b):** before drafting, read the
node for the target page and for the site's existing FAQ page — both are
typically among the top cited sources. Scan their text for question-answer
blocks: if the question is already answered there, mark it **"already
covered"** with the URL and a pointer to the existing answer, skip the new
entry, and recommend enriching or linking what exists.

- Top cited nodes that match the topic are the preferred grounding anchors.
- Collect the **verbatim passages** that answer the question.
- **The 100% check (Rule 2):** can the complete answer be written strictly
  from these passages — every fact, number, price, name, and condition stated
  in them? Yes → publishable. No, or only partially → mark the question
  **"needs human input"** and collect it for the report. Do not blend passages
  into claims they do not state.
- Existing near-duplicate FAQ node → plan a `branchly_update_node` (enrich the
  text) instead of a create.

---

## Step 4 — Write the FAQ Entries

For each verified question, prepare:

- **Question:** the canonical visitor phrasing (Rule 1), kept as a natural
  search-style question — question words (what, how, why, when, where, who,
  which), "How do I…" not "How does one…" — because visitors who never opened
  the chat will type the same question into search.
- **Answer:** 2–4 sentences (~50–100 words), strictly verified (Rule 2), in the
  tone from the prompt personas.
- **Verification (Rule 3):** source node ID + title + page URL, and the verbatim
  passage(s) the answer rests on.
- **Locales:** every locale the question appeared in (within `valid_locales`).
- **Target page:** the website page this FAQ belongs to (for the section in
  Step 6).

**Answer style (non-negotiable):**

- **Answer first.** The first sentence answers the question. Conditions and
  details follow — never lead with throat-clearing. Answer boxes and AI engines
  lift the first sentence verbatim, so it must carry the answer alone.
- **Self-contained and extractable.** AI search and assistants quote answer
  blocks verbatim; each answer must stand alone without the question, the
  page, or surrounding text.
- **Specific over vague.** Use the exact numbers, names, prices, and timeframes
  from the verified passages. Never abstract them into "fast", "easy",
  "flexible", or "save time" — a generic answer helps no one and retrieves
  worse. Sourced figures also raise AI citation rates: when the passage states
  a number, keep the number (and where it comes from) in the answer.
- **Customer language.** Mirror the visitor's own words where the passages
  allow — other visitors search and ask the same way.
- **The swap test.** If a competitor could publish the same answer unchanged,
  it is too generic: tighten it with the specifics from the verified passage.
- **No AI tells.** No "it's not X, it's Y" contrast reveals, no "no X, no Y,
  no Z" negation lists, no self-answered questions or colon reveals, no stock
  openers ("In today's fast-paced world…"), no sentences trailing into extra
  comma clauses. Plain, declarative sentences; active voice; no weak
  intensifiers ("very", "really"). The FAQ questions themselves are fine as
  questions — that is the format.
- **Declined answers name their unlock.** When a question lands in "needs
  human input", state exactly what evidence would unlock it (a policy page, a
  price list, a spec table, a support macro) — an unlock path is an action
  item; without one it is a dead end.

---

## Step 5 — Publish to branchly (only if chosen)

Run this step **only** when the user chose branchly nodes as the output format
in Step 0; otherwise skip to Step 6. Create one node per question:

```bash
branchly_create_node(
  title={"en": "<canonical question>"},
  text={"en": "<verified answer>"},
  source="<target page URL, if the FAQ belongs to a specific page>"
)
```

- `title` and `text` are locale-keyed maps — a multi-locale FAQ is one node:
  `text={"en": "...", "de": "..."}`.
- Do not pass `label`: node labels are a fixed set (`content`, `contact`, …)
  and FAQ nodes use the default `content`. Their question-shaped titles are
  what make them findable again (Rule 5).
- Enriching an existing node instead:
  `branchly_update_node(node_id="...", text={"en": "<improved answer>"})`.

Then **verify** (Rule 7):

```bash
branchly_list_nodes(query="<original visitor phrasing>", locale="en", limit=5)
```

Re-run with each original phrasing variant. Every variant should surface the new
node. If one does not, add the missing keywords to the question title and
re-verify.

---

## Step 6 — Deliver

Produce the FAQ creation report with an **auditable verification section**.
Package the FAQ content according to the format chosen in Step 0 — save files to
the working directory (file option), list the created node IDs (branchly
option), or expand the website section into the customer's CMS format (CMS
option):

```markdown
# FAQ Creation Report — <Domain>

**Question source:** <content-ideas output | analytics window>
**Result:** N FAQ nodes created · M nodes updated · K questions "needs human input"
**Noise removed:** <n> test/technical queries excluded from the question pool.

## Published / Updated FAQs
| # | Question | Locale(s) | Node ID | Status | Target page |
|---|---|---|---|---|---|
| 1 | ... | en, de | ... | created / updated | /pricing |

## Answer Verification (source passages per FAQ)
### <Question 1>
- **Answer:** <the verified answer>
- **Source:** node `<node-id>` — <node title> — <page URL>
- **Verbatim passage:**
  > "<the exact passage from the website content that verifies this answer>"

## Needs Human Input (could not be 100% verified from the website)
| Question | Evidence (who asked, how often) | Evidence needed to unlock the answer |
|---|---|---|
| ... | ... | ... |

## Already Covered (question exists on the page — no new FAQ)
| Question | Where it already lives | Suggested action |
|---|---|---|
| ... | <page URL> | enrich / link the existing answer |

## Website FAQ Section (paste-ready)
<Each question as a heading (###) with its answer paragraph directly below;
related questions grouped on their owning target page — one owning page per
fact family, never a page per question>

## FAQPage Structured Data (machine-readable, optional)
*Valid Schema.org that keeps the FAQ parseable by AI assistants and crawlers.
Google retired FAQ rich results in May 2026 — do not promise rich snippets.*
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "<canonical question>",
      "acceptedAnswer": { "@type": "Answer", "text": "<verified answer>" }
    }
  ]
}
</script>
```

---

## Pitfalls to Avoid

- **Never publish a partially verified answer.** If any claim in the answer is
  not backed by a retrieved passage, the question goes to "needs human input".
- **No passage, no FAQ.** Always attach the verbatim source passages — the site
  owner must be able to audit where every answer comes from.
- **No marketing fluff or AI tells in answers.** Answers are reference
  material, not promotion: generic adjectives ("seamless", "powerful",
  "flexible"), contrast reveals, and negation lists make answers sound like
  ads and quote terribly when AI engines extract them.
- **One question per node.** A wall-of-text FAQ node destroys retrieval; one
  canonical question per node surfaces reliably.
- **Deduplicate before creating.** Query the question terms first; update
  existing nodes instead of creating near-duplicates.
- **Don't copy crawler noise into answers.** Read the node text — if it is
  boilerplate-heavy, flag the source instead of laundering the noise into an FAQ.
- **Respect the use case from the prompt personas.** No FAQs for sport results,
  stock prices, trivia, or anything the chat and search personas declare
  out of scope.
- **Never skip the post-publish check.** A published FAQ that does not retrieve
  is invisible to the assistant and the search interface.
- **Don't ignore locales.** A German question deserves a German answer; use the
  locale-keyed `text` map.
