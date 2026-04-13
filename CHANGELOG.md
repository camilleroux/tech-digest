# Changelog

## [1.0.0] - 2026-04-13

### Added
- Initial release of the `/digest` skill for Claude Code
- RSS 2.0 and Atom feed support
- Parallel feed fetching (multi-thread, zero external dependencies)
- Score-based filtering via `limit` field in sources.yml (HN vote count)
- Deduplication by URL across sources
- Default sources: Hacker News (100+ points), Lobste.rs, The Changelog
- `install.sh` and `uninstall.sh` scripts
- GitHub Actions CI (syntax check + feed validation + dry run)
