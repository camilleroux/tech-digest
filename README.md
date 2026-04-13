# /digest — Tech Digest for Claude Code

[![GitHub stars](https://img.shields.io/github/stars/CamilleRoux/tech-digest)](https://github.com/CamilleRoux/tech-digest/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://claude.ai/claude-code)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)

A [Claude Code](https://claude.ai/claude-code) skill that aggregates top developer RSS feeds and produces a structured daily digest — sorted by day, deduplicated, filtered by vote count.

![Demo of /digest](demo.gif)

## What it does

Type `/digest` in Claude Code and get a structured recap of the best tech articles from the last 3 days — sourced from Hacker News Daily and Lobste.rs.

```
# Tech Digest -- April 7 to April 13, 2026
> 12 articles from 3 sources over the last 7 days

## Sunday, April 13, 2026

- **The peril of laziness lost** -- `engineering` -- *Lobste.rs*
  On the hidden costs of over-engineering and how simplicity compounds...

## Saturday, April 12, 2026
- ...
```

## Features

- Aggregates **RSS 2.0 and Atom** feeds from top developer sources
- **Filters by vote count** — only the best articles per source, not just the most recent
- Recap grouped by **day**, with automatic deduplication
- Pure Python stdlib, **zero external dependencies** (no pip install)
- **Parallel feed fetching** (multi-thread)
- Fully configurable sources via a simple YAML file
- Works on **macOS and Linux**

## Installation

### Option A: Claude Code Plugin (recommended)

From Claude Code:

```
/plugin marketplace add CamilleRoux/tech-digest
/plugin install tech-digest@CamilleRoux-tech-digest
```

### Option B: Manual install (macOS / Linux)

```bash
git clone --depth 1 https://github.com/CamilleRoux/tech-digest.git
bash tech-digest/install.sh
```

<details>
<summary>One-liner (curl)</summary>

```bash
curl -fsSL https://raw.githubusercontent.com/CamilleRoux/tech-digest/main/install.sh | bash
```

Prefer the git clone method so you can inspect the script before running it.

</details>

## Usage

In Claude Code:

```
/digest          # Recap of the last 3 days (default)
/digest 7        # Recap of the last 7 days
/digest 14       # Recap of the last 14 days
```

## Sources included

| Source | Description |
|--------|-------------|
| [Hacker News](https://news.ycombinator.com) | Top 5 stories per day from Hacker News Daily |
| [Lobste.rs](https://lobste.rs) | Curated tech links voted on by the developer community |

## Add a source

Edit `~/.claude/skills/digest/sources.yml` and add a block:

```yaml
  - name: My Source
    url: https://example.com/feed.rss
    site: https://example.com
    description: Short description of the source
    limit: 3  # optional: keep top N articles by score per day
```

Any valid RSS 2.0 or Atom feed is supported. See [CONTRIBUTING.md](CONTRIBUTING.md) to propose a default source.

## Architecture

```
tech-digest/
├── skills/digest/
│   ├── SKILL.md           # Skill definition (instructions for Claude)
│   ├── sources.yml        # Configurable list of RSS feeds
│   └── fetch_feeds.py     # Python script (parallel fetch + XML parse + score filter)
├── .github/
│   ├── workflows/ci.yml   # Python syntax validation + feed test
│   └── ISSUE_TEMPLATE/    # Bug report / feature request templates
├── install.sh             # Installer (copies to ~/.claude/skills/digest/)
├── uninstall.sh           # Uninstaller
├── CHANGELOG.md           # Version history
├── CONTRIBUTING.md        # Contribution guide
└── README.md
```

**How it works:** when you type `/digest`, Claude Code reads `SKILL.md` which tells it to run `fetch_feeds.py`. The Python script fetches RSS feeds in parallel, parses XML, filters by date, ranks by score (vote count), deduplicates by URL, and returns articles as TSV. Claude then formats the result as markdown.

## Uninstall

```bash
rm -rf ~/.claude/skills/digest
```

Or via script:

```bash
curl -fsSL https://raw.githubusercontent.com/CamilleRoux/tech-digest/main/uninstall.sh | bash
```

## Version française

Looking for a French-language version? Check out [/veille](https://github.com/CamilleRoux/veille-techno) — the original skill that aggregates francophone tech sources.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

To add a source: open a PR modifying `skills/digest/sources.yml`.

## Author

Created by [Camille Roux](https://www.camilleroux.com) — developer, entrepreneur, and tech news enthusiast.

## License

[MIT](LICENSE)
