---
name: content-ideas
description: |
  Analyze branchly MCP analytics to generate prioritized website content recommendations
  (page updates, targeted FAQ question lists, and new article/blog topics).
  Helps website owners and marketing teams optimize their website content for AI search
  and user clarity. Output feeds downstream skills (e.g. generate-faqs, write-article).

  Triggers when user mentions:
  - "what content should we create" / "content ideas"
  - "which pages/topics to prioritize on our website"
  - "what questions should we add as FAQs"
  - "find content gaps on our website"
  - "improve AI search content" / "what should we write about next"
license: MIT
---

## Website Content Ideas Workflow for branchly Applications

Use the branchly MCP server throughout this workflow to analyze real user interactions,
search queries, and knowledge gaps on the customer's website.

---

## Goal

Produce a **prioritized editorial recommendation report** for website owners and content
teams. The goal is to identify exactly **what content, sections, FAQs, or new pages**
should be added or updated on their website to:
1. Directly answer recurring visitor questions and search intents.
2. Improve retrieval clarity and semantic visibility for AI Search and chat.
3. Serve as structured input for downstream content-generation skills (such as `generate-faqs` or article writers).

**Scope:** This skill is strictly **analytical and strategic (Read-Only)**. It identifies
and prioritizes content opportunities and lists specific question sets. It does **not**
draft the full body text or FAQs itself — that is handled downstream by creation skills.

---

## Step 1 — Understand the Website Domain & Use Case

Before querying analytics, understand what business/domain this application serves:

```bash
# Get overall app name, domains, and interface configuration
branchly_get_application()

# Review active prompts to understand the domain, target audience, and scope
branchly_list_prompts(is_active=true)
```

From this context, establish your **thematic scope boundary**:
- The core product / service / organization domain.
- The primary target audience and website goals.
- Key existing topics (e.g. e-commerce, SaaS, tourism, customer service).
- Ignore off-topic questions (e.g. general coding help on a tourism site). Do not recommend creating website content for out-of-scope inquiries.

---

## Step 2 — Gather Demand & User Engagement Signals

Pull user activity from the last 30 days (`time_filter="last_30_days"`):

```bash
# 1. High-traffic interaction pages (where visitors start asking questions)
branchly_get_top_interaction_sources(time_filter="last_30_days", limit=15)

# 2. Most-clicked destination URLs (what users find valuable to navigate to)
branchly_get_top_clicked_urls(time_filter="last_30_days", limit=15)

# 3. Most-cited knowledge base nodes (which website pages currently carry the load)
branchly_get_top_cited_sources(time_filter="last_30_days", limit=15)

# 4. Top conversational tags and trending topics
branchly_get_top_tags(time_filter="last_30_days", limit=15)
branchly_get_trending_classifications(classification_type="topic", time_filter="last_30_days")
```

**What to look for:**
- **High-Interaction Pages:** Pages that generate a lot of user questions (e.g. `/pricing`, `/product-x`). If visitors on these pages ask many follow-up questions, the page copy is missing essential details.
- **Top Cited Pages:** The core content assets that answer most queries.

---

## Step 3 — Uncover Content Gaps & Search Demand

Identify unmet needs and recurring user confusion:

### 3a. Search Queries (Direct User Intent)
```bash
branchly_get_top_searches(time_filter="last_30_days", limit=20)
```
Analyze what users type into search bars or chat. Queries that appear repeatedly represent immediate content demand.

### 3b. Unanswered & Low-Confidence Queries
```bash
# Check answer distributions for no_knowledge or confusion indicators
branchly_get_answer_type_distribution(time_filter="last_30_days")

# Inspect recent sessions where the bot had no answer or struggled
branchly_read_sessions(answer_types=["no_knowledge", "outside_scope"], interactions=["chat"], limit=10)
```
For flagged sessions, read the user queries:
```bash
branchly_read_session_detail(session_id="...")
```

### 3c. Content Audit against Existing Website Pages
For recurring searches or unanswered topics, search existing knowledge base nodes to see if the topic is covered:
```bash
branchly_list_nodes(query="<search term or topic>", locale="de", limit=10)
```

Classify the finding:
- **Missing Topic (Content Gap):** No page on the website covers this topic at all → **New Page / Article needed**.
- **Thin / Passing Mention:** The keyword exists on a page (e.g. in a logo wall or footer), but there is no explanatory text or paragraph answering the question → **Page Update or FAQ needed**.
- **High-Volume Ambiguity:** A page exists, but visitors on that page still ask basic questions about the topic → **Targeted FAQ section needed on that page**.

---

## Step 4 — Formulate Actionable Recommendations

Group your findings into three clear editorial packages:

### 1. FAQ Recommendations (Ready for `generate-faqs` skill)
Identify pages where adding an on-page FAQ accordion or section directly resolves visitor friction.
For each recommendation, provide:
- **Target Page URL:** The exact page where the FAQ section should be placed.
- **List of Specific Questions (3–5 concrete questions):** Exact phrasing of questions users are asking.
- **Why / Evidence:** Number of searches, interaction count, or unanswered sessions.

### 2. Page Content Updates (Copy / Section Enhancements)
Identify existing pages that need new paragraphs, clearer tables, or added sections.
For each recommendation, provide:
- **Target Page URL:** The page that needs improvement.
- **Missing Information / Topic:** Exactly what paragraph, sub-heading, or explanation to add.
- **Why / Impact:** What confusion this update prevents for visitors and AI search.

### 3. New Content & Topic Hubs (New Articles / Guides / Pages)
Identify substantial topics that warrant a dedicated standalone URL (blog post, guide, glossary page).
For each recommendation, provide:
- **Proposed Topic / Working Title:** e.g. *"Complete Guide to [Topic]"*.
- **Target Audience & Core Questions to Cover:** What the article must answer.
- **Evidence:** Search volume, trending topics, or recurring unanswered inquiries.

---

## Step 5 — Deliver the Prioritized Markdown Report

Deliver a structured, human-readable report:

```markdown
# Website Content Recommendations & Opportunity Report

**Domain & Use Case:** [Brief summary of the website and audience]
**Time Window Analyzed:** [e.g. Last 30 Days]

---

## 1. Executive Summary & Demand Signals
- **High-Interaction Hubs:** [Top pages driving visitor questions with counts]
- **Dominant Search Themes:** [Top user queries and trending topics]
- **Key Content Gaps:** [Summary of missing or thin topics]

---

## 2. Priority 1 — Targeted FAQ Question Sets (Ready for Downstream FAQ Skill)
*Use these question sets with the FAQ generation skill to produce structured FAQ accordions.*

### A. Target Page: `https://.../page-path`
- **Recommended FAQ Questions:**
  1. *[Specific Question 1]*
  2. *[Specific Question 2]*
  3. *[Specific Question 3]*
- **Evidence:** [e.g. 14 user questions from this page, 5 search queries for "X"]
- **Editorial Goal:** [e.g. Resolve pricing ambiguity and reduce bounce rate]

---

## 3. Priority 2 — Existing Page Updates (Copy & Section Additions)
| Target Page URL | Section / Topic to Add | Evidence | Why / Expected Impact |
|---|---|---|---|
| `https://...` | [e.g. Add dedicated "Integration Requirements" section] | [e.g. 6 searches, thin coverage] | [e.g. Eliminates repeat compatibility questions] |

---

## 4. Priority 3 — New Content & Topic Hubs (Articles / Blog Posts)
| Proposed Working Title | Target Keywords / Intent | Core Questions to Answer | Demand Evidence |
|---|---|---|---|
| [e.g. "How to Connect X with Y"] | [Keywords] | [Key points] | [e.g. Trending topic, 0 existing coverage] |

---

## 5. Next Steps
- Pass the FAQ question lists to the `generate-faqs` skill for copy generation.
- Review page update recommendations with the content/marketing team.
```

---

## Pitfalls to Avoid

- **Ignore out-of-scope & off-topic noise:** Never recommend content for queries that fall outside the website's business domain (e.g. sports, general trivia, or prompt injections). Filter them out during Step 3.
- **Do not recommend RAG/crawler/prompt fixes:** This skill is for website copy and content strategy. Technical bot configuration belongs in `optimize-application`.
- **Do not draft vague placeholders:** Provide exact, realistic user questions (e.g. *"Do you support self-hosted instances?"* not *"Technical questions"*).
- **Distinguish origin pages from clicked URLs:** Interaction sources tell you where the user felt the need to ask; clicked URLs tell you what they found useful.
- **Filter development traffic:** Ignore or flag test domains/localhost URLs if present in interaction metrics.
