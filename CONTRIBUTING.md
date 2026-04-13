# Contributing to tech-digest

Thank you for your interest in this project! Here's how to contribute.

## Adding an RSS source

The most common contribution. A source must:

- Have a valid **RSS 2.0 or Atom** feed
- Be relevant for **developers**
- Publish at a reasonable pace (ideally a few articles per day, not hundreds)

### Steps

1. Fork the repo
2. Edit `skills/digest/sources.yml` and add your source:
   ```yaml
     - name: My Source
       url: https://example.com/feed.rss
       site: https://example.com
       description: Short description
       limit: 3  # optional: keep top N by score per period
   ```
3. Test locally: `python3 skills/digest/fetch_feeds.py 7`
4. Open a Pull Request

## Modifying the skill

### Local setup

```bash
git clone https://github.com/CamilleRoux/tech-digest.git
cd tech-digest

# Install the skill locally
cp skills/digest/* ~/.claude/skills/digest/

# Test the Python script
python3 skills/digest/fetch_feeds.py 7
```

### Standards

- **Python**: compatible with 3.10+, no external dependencies (stdlib only)
- **Bash**: `set -euo pipefail` at the top
- **Skill**: test with `/digest` in Claude Code after any change

## Reporting a bug

Open an [issue](https://github.com/CamilleRoux/tech-digest/issues/new?template=bug_report.yml) with:

- Your OS and Python version
- The command you ran
- The error message

## Proposing a feature

Open an [issue](https://github.com/CamilleRoux/tech-digest/issues/new?template=feature_request.yml) describing your idea.
