#!/usr/bin/env python3
"""Fetch and parse RSS feeds from sources.yml, output TSV sorted by date."""

import sys
import os
import re
import html
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


def load_sources():
    """Load sources from sources.yml next to this script (no PyYAML needed)."""
    sources_path = Path(__file__).parent / "sources.yml"
    sources = []
    current = None
    with open(sources_path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("#") or not stripped or stripped == "sources:":
                continue
            if stripped.startswith("- name:"):
                if current:
                    sources.append(current)
                current = {"name": stripped.split(":", 1)[1].strip()}
            elif current and ":" in stripped:
                key, val = stripped.split(":", 1)
                val = val.split("#")[0].strip()
                current[key.strip()] = val
    if current:
        sources.append(current)
    return sources


def strip_html(text):
    """Remove HTML tags and decode entities."""
    if not text:
        return ""
    text = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = " ".join(text.split())
    return text[:150]


def parse_rss_date(date_str):
    """Parse RFC 2822 or ISO 8601 date string to datetime."""
    if not date_str:
        return None
    try:
        return parsedate_to_datetime(date_str.strip())
    except Exception:
        pass
    # Try ISO 8601 (Atom feeds)
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str.strip(), fmt).replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            continue
    return None


def parse_score(raw_description):
    """Extract numeric score from description (e.g. HN hnrss.org 'Points: N')."""
    if not raw_description:
        return None
    m = re.search(r'Points:\s*(\d+)', raw_description)
    return int(m.group(1)) if m else None


def fetch_feed(source, cutoff_date):
    """Fetch a single RSS/Atom feed and return parsed articles."""
    url = source["url"]
    name = source["name"]
    articles = []

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "tech-digest/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
    except Exception as e:
        return articles, f"ERROR: {name} - {e}"

    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        return articles, f"ERROR: {name} - XML parse error: {e}"

    ns = {"dc": "http://purl.org/dc/elements/1.1/", "atom": "http://www.w3.org/2005/Atom"}
    items = root.findall(".//item")

    if items:
        # RSS 2.0
        for item in items:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            date_str = item.findtext("pubDate", "")
            raw_desc_text = item.findtext("description", "")
            score = parse_score(raw_desc_text)
            raw_desc = strip_html(raw_desc_text)
            # Filter out metadata-only descriptions (comment links, URLs, HN hnrss.org metadata)
            desc = "" if (
                raw_desc.startswith("Comments")
                or raw_desc.startswith("http")
                or raw_desc.startswith("Article URL:")
            ) else raw_desc
            categories = [c.text for c in item.findall("category") if c.text]
            category = categories[0] if categories else "N/A"

            pub_date = parse_rss_date(date_str)
            if pub_date and pub_date.date() >= cutoff_date:
                articles.append({
                    "date": pub_date,
                    "title": title,
                    "link": link,
                    "category": category,
                    "description": desc,
                    "source": name,
                    "score": score,
                })
    else:
        # Try Atom format
        atom_ns = "http://www.w3.org/2005/Atom"
        entries = root.findall(f".//{{{atom_ns}}}entry")
        for entry in entries:
            title = (entry.findtext(f"{{{atom_ns}}}title") or "").strip()
            link_el = entry.find(f"{{{atom_ns}}}link[@href]")
            link = link_el.get("href", "") if link_el is not None else ""
            date_str = entry.findtext(f"{{{atom_ns}}}updated") or entry.findtext(f"{{{atom_ns}}}published") or ""
            raw_content = entry.findtext(f"{{{atom_ns}}}summary") or entry.findtext(f"{{{atom_ns}}}content") or ""
            desc = strip_html(raw_content[:2000])
            cat_el = entry.find(f"{{{atom_ns}}}category")
            category = cat_el.get("term", "N/A") if cat_el is not None else "N/A"

            pub_date = parse_rss_date(date_str)
            if pub_date and pub_date.date() >= cutoff_date:
                articles.append({
                    "date": pub_date,
                    "title": title,
                    "link": link,
                    "category": category,
                    "description": desc,
                    "source": name,
                    "score": None,
                })

    # If limit is set: keep the top N by score (scored articles first, then by recency)
    limit = source.get("limit")
    if limit:
        articles.sort(
            key=lambda a: (a["score"] is not None, a["score"] or 0, a["date"]),
            reverse=True,
        )
        articles = articles[:int(limit)]

    return articles, None


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    cutoff_date = (datetime.now().date() - timedelta(days=days))

    sources = load_sources()
    all_articles = []
    errors = []

    # Fetch all feeds in parallel
    with ThreadPoolExecutor(max_workers=min(len(sources), 10)) as pool:
        futures = {pool.submit(fetch_feed, s, cutoff_date): s for s in sources}
        for future in as_completed(futures):
            articles, error = future.result()
            all_articles.extend(articles)
            if error:
                errors.append(error)

    # Deduplicate by URL (keep first occurrence, merge source names)
    seen = {}
    for a in all_articles:
        url = a["link"]
        if url in seen:
            if a["source"] not in seen[url]["source"]:
                seen[url]["source"] += f", {a['source']}"
        else:
            seen[url] = a
    unique_articles = sorted(seen.values(), key=lambda a: a["date"], reverse=True)

    # Output errors to stderr so stdout stays clean TSV
    for err in errors:
        print(err, file=sys.stderr)

    # Output articles as TSV
    for a in unique_articles:
        date_str = a["date"].strftime("%Y-%m-%d")
        desc = a["description"] or "N/A"
        # Sanitize tabs/newlines in fields
        title = a["title"].replace("\t", " ").replace("\n", " ")
        desc = desc.replace("\t", " ").replace("\n", " ")
        cat = a["category"].replace("\t", " ")
        src = a["source"].replace("\t", " ")
        print(f"{date_str}\t{title}\t{a['link']}\t{cat}\t{desc}\t{src}")

    # Output sources section
    print("SOURCES:")
    for s in sources:
        print(f"  {s['name']}\t{s.get('site', s['url'])}\t{s.get('description', '')}")


if __name__ == "__main__":
    main()
