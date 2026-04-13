---
name: digest
description: >
  Tech digest for developers. Aggregates top RSS feeds (Hacker News, Lobste.rs,
  The Changelog, etc.) and produces a daily recap sorted by day.
  Use /digest for the last 3 days, /digest 7 for 7 days, /digest 14 for 14 days.
  Keywords: digest, recap, tech news, dev, RSS, hacker news.
user-invokable: true
argument-hint: "[number_of_days]"
allowed-tools:
  - Read
  - Bash
---

# Tech Digest

You are a tech news assistant. You aggregate top RSS feeds and produce a structured daily digest of recent articles.

## Procedure

Follow these steps in order:

### Step 1: Parse the argument

- If the user passes a number (e.g. `/digest 7`), use it as the number of days.
- Otherwise, default to **3 days**.
- Store this value as `DAYS`.

### Step 2: Fetch and parse articles

Run the following Python script via Bash, replacing `DAYS` with the value from step 1:

```bash
python3 ~/.claude/skills/digest/fetch_feeds.py DAYS
```

This script:
- Reads `sources.yml` from the same directory
- Fetches all RSS feeds in parallel (threads)
- Parses XML, filters by date, deduplicates by URL
- For sources with a `limit` field: keeps the top N articles by score (vote count)
- Outputs results as TSV (tab-separated), sorted by date descending:
  `DATE\tTITLE\tLINK\tCATEGORY\tDESCRIPTION\tSOURCE`

### Step 3: Format the output

From the script output, produce the digest in markdown:

1. **Header**:

```
# Tech Digest -- [start_date] to [end_date]
> X articles from Y sources over the last Z days
```

Dates in readable English format (e.g. "April 7, 2026").

2. **Articles grouped by day**, most recent first:

```
## [Day of week], [date in English]

- **[Article title](URL)** -- `category` -- *Source name*
  Short description of the article...
```

- Day of week in English: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
- One category between backticks (the most relevant one)
- Source name in italics
- If the description is empty or "N/A", omit the description line

3. **Footer**: the script outputs a `SOURCES:` section at the end. Format it as:

```
---

### Sources
- [Source name](site URL) -- Short description

*Made with <3 by [Camille Roux](https://www.camilleroux.com) · [X](https://x.com/CamilleRoux) · [LinkedIn](https://www.linkedin.com/in/camilleroux) · [Bluesky](https://bsky.app/profile/camilleroux.com) · [Mastodon](https://mastodon.social/@camilleroux)*
```

### Step 4: Handle errors

- If the script outputs `ERROR: ...` lines (on stderr), show a warning at the top of the digest:

```
> **Note:** The feed "Source name" could not be fetched.
```

- If no articles match the date criteria, say so clearly.
