# tech-digest

Claude Code skill that aggregates top developer RSS feeds and produces a daily digest filtered by vote count.

## Architecture

```
skills/digest/
  SKILL.md           # Instructions for Claude (runs fetch_feeds.py)
  sources.yml        # RSS source configuration (minimal YAML)
  fetch_feeds.py     # Python script: parallel fetch + XML parse + score filter + dedup
```

## How it works

1. User types `/digest [N]` (N = number of days, default 7)
2. Claude reads SKILL.md and runs `python3 fetch_feeds.py N`
3. The script reads sources.yml, fetches feeds in parallel, parses XML, filters by date,
   applies score-based limit per source, deduplicates by URL
4. Output TSV: `DATE\tTITLE\tLINK\tCATEGORY\tDESCRIPTION\tSOURCE`
5. Claude formats the TSV as markdown (grouped by day, sources in footer)

## Testing locally

```bash
# Test the script directly
python3 skills/digest/fetch_feeds.py 7

# Install and test the skill
cp skills/digest/* ~/.claude/skills/digest/
# Then /digest in Claude Code
```

## Key points

- Zero external Python dependencies (stdlib only, no pip install)
- The YAML parser in fetch_feeds.py is minimal: it only handles the specific format of sources.yml
- The `limit` field in sources.yml: keep the N highest-scored articles per source (sorted by vote count)
- Score parsing: extracts `Points: N` from HN descriptions (hnrss.org format)
- Upstream: https://github.com/CamilleRoux/veille-techno (French version, shares the same Python core)
